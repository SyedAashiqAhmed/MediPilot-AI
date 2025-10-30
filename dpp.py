from flask import Flask, request, jsonify, render_template, redirect, url_for
import json
import os
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
import google.generativeai as genai
import uuid
from datetime import datetime
from PIL import Image
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import re

# Database imports
from models import db
from database import (init_db, save_patient_data, get_patient_by_id, get_all_patients,
                      get_patient_history, save_patient_history, get_or_create_chat_session,
                      save_chat_message, get_chat_history, get_patient_comparison_data,
                      index_patient_for_rag, search_rag_documents)

# Load environment variables from .env (development convenience)
load_dotenv()

# ------------------- Flask App -------------------
app = Flask(__name__, template_folder="templates", static_folder="frontend/static")

# Initialize database
init_db(app)

# ------------------- Configuration -------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}

# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

def _data_path(filename):
    return os.path.join(BASE_DIR, filename)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ------------------- Gemini API Configuration -------------------
# Load the Gemini API key from environment. Do NOT hardcode secrets in code.
def _get_gemini_model():
    """Return a configured Gemini GenerativeModel. Chooses a valid model for generateContent.
    Falls back across known names and consults list_models.
    """
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Please set the environment variable to your Gemini API key."
        )
    genai.configure(api_key=api_key)

    # Candidate short names in order of preference (prefer broadly available first)
    # Include models observed in the user's account via DEBUG list
    candidates = [
        "gemini-pro-latest",
        "gemini-flash-latest",
        "gemini-2.5-pro",
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-1.5-flash",
        "gemini-1.5-pro",
        "gemini-1.5-flash-latest",
        "gemini-1.5-pro-latest",
        "gemini-pro",
    ]

    try:
        # Query available models and supported methods
        available = genai.list_models()
        # Build a set of short names that support generateContent
        supported = set()
        for m in available:
            # m.name is like 'models/gemini-1.5-flash'; normalize
            name = str(getattr(m, "name", ""))
            short = name.split("/")[-1] if name else ""
            methods = set(getattr(m, "supported_generation_methods", []) or [])
            if "generateContent" in methods:
                supported.add(short)
        
        print(f"DEBUG: Available Gemini models with generateContent: {supported}")

        for c in candidates:
            if c in supported:
                print(f"DEBUG: Using Gemini model: {c}")
                return genai.GenerativeModel(c)

        # If none matched supported set, try first candidate directly
        print(f"DEBUG: No match in supported set, trying: {candidates[0]}")
        try:
            return genai.GenerativeModel(candidates[0])
        except Exception as e:
            print(f"DEBUG: Fallback init failed for {candidates[0]}: {e}. Trying gemini-flash-latest")
            return genai.GenerativeModel("gemini-flash-latest")
    except Exception as e:
        # As a last resort, try a broadly available text model
        print(f"DEBUG: Model selection error: {e}. Falling back to gemini-pro")
        return genai.GenerativeModel("gemini-pro")

def _has_gemini() -> bool:
    try:
        return bool(os.getenv("GEMINI_API_KEY", "").strip())
    except Exception:
        return False

# Database is initialized above - no need for JSON files

# ------------------- Utility Functions -------------------
def _normalize_patient_id(value):
    try:
        return str(value).strip().upper()
    except Exception:
        return ""

# ------------------- Chat Session Management -------------------
# Now using SQL database functions from database.py

def update_chat_session(session_id, message):
    """Update a chat session with a new message"""
    role = message.get('role', 'user')
    content = message.get('content', '')
    save_chat_message(session_id, role, content)

def get_patient_data_internal(patient_id):
    """Internal function to get patient data"""
    return get_patient_by_id(patient_id) or {}

# ------------------- Routes -------------------
@app.route("/")
def index():
    """Main intro page to choose between patient and doctor portals"""
    return render_template("intro.html")

@app.route("/patient")
def patient_portal():
    """Patient portal for submitting medical data"""
    return render_template("index.html")

@app.route("/doctor")
def doctor_portal():
    """Doctor portal for viewing patient data and AI consultations"""
    return render_template("doctor.html")

@app.route("/chat")
def chat_portal():
    """Chat interface for AI consultations"""
    return render_template("chat.html")

# ------------------- Patient Data Submission -------------------
@app.route("/submit_patient", methods=["POST"])
def submit_patient():
    """Handle patient data submission from the patient portal"""
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "No data received"}), 400

    # Add timestamp if not present
    if "timestamp" not in data:
        data["timestamp"] = datetime.now().isoformat()
    
    # Normalize patient_id
    if 'patient_id' in data:
        data['patient_id'] = _normalize_patient_id(data['patient_id'])

    # Save to SQL database
    try:
        patient = save_patient_data(data)
        # Index for RAG
        index_patient_for_rag(patient.patient_id)
        return jsonify({"status": "success", "message": "Patient data saved successfully!"})
    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to save patient data: {str(e)}"}), 500

# ------------------- Image Upload and AI Extraction -------------------
@app.route("/upload_report", methods=["POST"])
def upload_report():
    """Handle medical report image upload and extract key information using AI"""
    try:
        if 'report_image' not in request.files:
            return jsonify({"status": "error", "message": "No image file provided"}), 400
        
        file = request.files['report_image']
        if file.filename == '':
            return jsonify({"status": "error", "message": "No file selected"}), 400
        
        if not allowed_file(file.filename):
            return jsonify({"status": "error", "message": "Invalid file type. Please upload an image file."}), 400
        
        # Save the uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Process image with AI
        extracted_data = extract_medical_data_from_image(filepath)
        
        # Clean up - remove uploaded file after processing
        try:
            os.remove(filepath)
        except:
            pass  # Don't fail if cleanup fails
        
        return jsonify({
            "status": "success", 
            "message": "Medical report processed successfully!",
            "extracted_data": extracted_data
        })
        
    except Exception as e:
        return jsonify({"status": "error", "message": f"Error processing image: {str(e)}"}), 500

def extract_medical_data_from_image(image_path):
    """Extract medical information from image using Gemini Vision AI"""
    try:
        # Load and prepare the image
        image = Image.open(image_path)
        
        # Get Gemini model with vision capabilities (use the helper function)
        model = _get_gemini_model()
        
        # Create prompt for medical data extraction
        prompt = """
        Analyze this medical report image and extract the following information in JSON format:
        
        {
            "patient_id": "extracted patient ID if visible, otherwise null",
            "symptoms": "list of symptoms mentioned",
            "vitals": {
                "bp": "blood pressure reading (e.g., 120/80)",
                "hr": "heart rate number only",
                "spo2": "oxygen saturation number only"
            },
            "lab_results": {
                "ecg": "ECG findings if mentioned",
                "troponin": "troponin level if mentioned", 
                "cholesterol": "cholesterol level if mentioned"
            }
        }
        
        Rules:
        - Extract only information that is clearly visible in the image
        - Use null for missing information
        - For vitals, extract only numeric values
        - For symptoms, combine all mentioned symptoms into a single string
        - Be accurate and don't hallucinate information
        """
        
        # Generate content with image
        response = model.generate_content([prompt, image])
        
        # Parse the response to extract JSON
        response_text = response.text.strip()
        
        # Try to extract JSON from the response
        import re
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            extracted_data = json.loads(json_str)
        else:
            # Fallback: create structured data from text response
            extracted_data = {
                "patient_id": None,
                "symptoms": "Unable to extract from image",
                "vitals": {"bp": None, "hr": None, "spo2": None},
                "lab_results": {"ecg": None, "troponin": None, "cholesterol": None},
                "ai_analysis": response_text
            }
        
        return extracted_data
        
    except Exception as e:
        return {
            "patient_id": None,
            "symptoms": f"Error extracting data: {str(e)}",
            "vitals": {"bp": None, "hr": None, "spo2": None},
            "lab_results": {"ecg": None, "troponin": None, "cholesterol": None}
        }

@app.route("/get_patient_data/<patient_id>")
def get_patient_data_route(patient_id):
    """Get patient data by ID from SQL database"""
    patient_data = get_patient_by_id(patient_id)
    
    if not patient_data:
        return jsonify({"error": "Patient not found"}), 404
    
    # Return as array for backwards compatibility with frontend
    return jsonify([patient_data])

@app.route("/get_all_patients")
def get_all_patients_route():
    """Get all patients from SQL database"""
    all_patients = get_all_patients()
    return jsonify(all_patients)

# ------------------- Patient Comparison Plot -------------------
@app.route("/patient_compare_plot/<patient_id>")
def patient_compare_plot(patient_id):
    """Generate comparison plot using SQL database"""
    current_data, history_data = get_patient_comparison_data(patient_id)
    
    if not current_data and not history_data:
        return jsonify({"error": "Patient not found"}), 404
    
    # Convert to lists for DataFrame
    current_list = [current_data] if current_data else []
    
    df_current = pd.DataFrame(current_list)
    df_history = pd.DataFrame(history_data)

    # Helper functions
    def bp_systolic(bp):
        try: return int(bp.split("/")[0])
        except: return 0
    def bp_diastolic(bp):
        try: return int(bp.split("/")[1])
        except: return 0
    def _to_number(value, default=0):
        try:
            if value is None: return default
            if isinstance(value, (int, float)): return float(value)
            return float(str(value).strip())
        except: return default
    def hr(vitals): return _to_number(vitals.get('hr', 0))
    def spo2(vitals): return _to_number(vitals.get('spo2', 0))
    def cholesterol(lab): return _to_number(lab.get('cholesterol', 0))
    def blood_sugar(lab):
        if 'blood_sugar' in lab: return _to_number(lab.get('blood_sugar', 0))
        if 'hba1c' in lab: return _to_number(lab.get('hba1c', 0))
        return 0

    metrics = ['BP Systolic', 'BP Diastolic', 'Heart Rate', 'SpO2', 'Cholesterol', 'Blood Sugar']
    current_values = [
        df_current['vitals'].apply(lambda x: bp_systolic(x['bp'])).mean() if not df_current.empty else 0,
        df_current['vitals'].apply(lambda x: bp_diastolic(x['bp'])).mean() if not df_current.empty else 0,
        df_current['vitals'].apply(lambda x: hr(x)).mean() if not df_current.empty else 0,
        df_current['vitals'].apply(lambda x: spo2(x)).mean() if not df_current.empty else 0,
        df_current['lab_results'].apply(lambda x: cholesterol(x)).mean() if not df_current.empty else 0,
        df_current['lab_results'].apply(lambda x: blood_sugar(x)).mean() if not df_current.empty else 0,
    ]
    history_values = [
        df_history['vitals'].apply(lambda x: bp_systolic(x['bp'])).mean() if not df_history.empty else 0,
        df_history['vitals'].apply(lambda x: bp_diastolic(x['bp'])).mean() if not df_history.empty else 0,
        df_history['vitals'].apply(lambda x: hr(x)).mean() if not df_history.empty else 0,
        df_history['vitals'].apply(lambda x: spo2(x)).mean() if not df_history.empty else 0,
        df_history['lab_results'].apply(lambda x: cholesterol(x)).mean() if not df_history.empty else 0,
        df_history['lab_results'].apply(lambda x: blood_sugar(x)).mean() if not df_history.empty else 0,
    ]

    fig, ax = plt.subplots(figsize=(10,6))
    x = range(len(metrics))
    width = 0.35
    ax.bar([i - width/2 for i in x], history_values, width, color='skyblue', label='History')
    ax.bar([i + width/2 for i in x], current_values, width, color='orange', label='Current')
    ax.set_xticks(x)
    ax.set_xticklabels(metrics, rotation=45, ha='right')
    ax.set_ylabel("Values")
    ax.set_title(f"Patient {patient_id} - Current vs Historical Averages")
    ax.legend()
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    for i in range(len(metrics)):
        if history_values[i] > 0:
            ax.text(i - width/2, history_values[i]+0.01*max(max(history_values), max(current_values)), f'{history_values[i]:.1f}', ha='center')
        if current_values[i] > 0:
            ax.text(i + width/2, current_values[i]+0.01*max(max(history_values), max(current_values)), f'{current_values[i]:.1f}', ha='center')

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return jsonify({"image": img_base64})

# ------------------- RAG Chat with AI (JSON-backed) -------------------
@app.route("/chat_with_ai", methods=["POST"])
def chat_with_ai():
    """Lightweight chat endpoint that grounds answers in patients.json for the current patient.
    Persists messages in chat_sessions.json and returns a concise, clinically-oriented reply.
    """
    try:
        payload = request.get_json(force=True) or {}
        user_message = str(payload.get("message", "")).strip()
        patient_id = str(payload.get("patientId", "")).strip()
        client_patient_data = payload.get("patientData") or {}
        session_id = payload.get("sessionId") or f"sess-{uuid.uuid4().hex[:8]}"
        general_ai_enabled = bool(payload.get("generalAi", True))

        if not user_message:
            return jsonify({"error": "No message provided"}), 400

        # Retrieve authoritative patient data from JSON if patient_id is provided
        patient_data = client_patient_data or {}
        if patient_id:
            authoritative = get_patient_data_internal(patient_id)
            if authoritative:
                patient_data = authoritative

        # Get or create chat session and persist user message
        session = get_or_create_chat_session(session_id, patient_id)
        save_chat_message(session_id, "user", user_message)

        # JSON Q&A: try to directly answer about fields in the patient's JSON
        json_qa_text = _json_qa_answer(user_message, patient_data)

        # Generate grounded response (text + optional structured insights)
        response_packet = _generate_grounded_packet(user_message, patient_data)
        response_text = json_qa_text or response_packet.get("response", "")

        # Optional: augment with Gemini for open-ended or explanatory questions
        if _has_gemini() and (general_ai_enabled or _looks_like_open_question(user_message)):
            try:
                # Get chat history from SQL
                history_messages = get_chat_history(session_id)
                llm_text = _call_gemini_chat(user_message, patient_data, history_messages)
            except Exception as _e:
                llm_text = None
            if llm_text:
                response_text = llm_text

    
        save_chat_message(session_id, "assistant", response_text)

        return jsonify({
            "response": response_text,
            "structured": response_packet.get("structured"),
            "sessionId": session_id,
            "patient_id": patient_id
        })
    except Exception as e:
        return jsonify({"error": f"chat processing failed: {str(e)}"}), 500


def _generate_grounded_reply(message: str, patient: dict) -> str:
    """Heuristic, safe, retrieval-augmented reply grounded in patient JSON."""
    msg = (message or "").lower()
    # Friendly greeting fallback (works even without GEMINI_API_KEY)
    if any(g in msg for g in ["hi", "hello", "hey", "good morning", "good evening", "good afternoon"]):
        return (
            "Hello doctor. I can help with patient-specific questions (vitals, labs, symptoms, insights) "
            "and general medical queries. Ask me anything or use the quick action buttons below."
        )
    if not patient:
        # Generic but safe response when no patient context is available
        if any(k in msg for k in ["hello", "hi", "hey"]):
            return "Hello doctor. Please load a patient ID to enable data-grounded assistance."
        return (
            "I need the patient's data to provide grounded insights. "
            "Load a patient first, then ask about vitals, symptoms, labs, trends, or recommended tests."
        )

    # Build a small knowledge snippet from patient JSON (acts as RAG context)
    name = patient.get("name")
    age = patient.get("age")
    gender = patient.get("gender")
    symptoms = (patient.get("symptoms") or "").strip()
    vitals = patient.get("vitals") or {}
    labs = patient.get("lab_results") or {}

    bp = vitals.get("bp")
    hr = vitals.get("hr")
    spo2 = vitals.get("spo2")
    ecg = labs.get("ecg")
    troponin = labs.get("troponin")
    cholesterol = labs.get("cholesterol")

    # Common intents
    if any(k in msg for k in ["patient info", "patient details", "summary", "overview"]):
        lines = ["Patient summary:"]
        if name: lines.append(f"- Name: {name}")
        if age: lines.append(f"- Age: {age}")
        if gender: lines.append(f"- Gender: {gender}")
        if symptoms: lines.append(f"- Symptoms: {symptoms}")
        if bp or hr or spo2:
            lines.append("- Vitals:")
            if bp: lines.append(f"  • BP: {bp} mmHg")
            if hr: lines.append(f"  • HR: {hr} bpm")
            if spo2: lines.append(f"  • SpO2: {spo2}%")
        if any([ecg, troponin, cholesterol]):
            lines.append("- Labs:")
            if ecg: lines.append(f"  • ECG: {ecg}")
            if troponin: lines.append(f"  • Troponin: {troponin} ng/mL")
            if cholesterol: lines.append(f"  • Cholesterol: {cholesterol} mg/dL")
        return "\n".join(lines)

    if any(k in msg for k in ["bp", "blood pressure"]):
        if bp:
            try:
                systolic = int(str(bp).split("/")[0])
            except Exception:
                systolic = None
            flag = "normal"
            if systolic and systolic >= 140:
                flag = "high—monitor and evaluate for hypertension"
            elif systolic and systolic >= 130:
                flag = "elevated—lifestyle counseling and follow-up"
            return f"BP: {bp} mmHg ({flag}). Consider trend and symptoms."
        return "No blood pressure recorded."

    if any(k in msg for k in ["hr", "heart rate", "pulse"]):
        if hr:
            try:
                hr_val = int(str(hr))
            except Exception:
                hr_val = None
            status = "within expected range"
            if hr_val and (hr_val > 100 or hr_val < 60):
                status = "outside resting range—correlate clinically"
            return f"Heart rate: {hr} bpm ({status})."
        return "No heart rate recorded."

    if "spo2" in msg or "oxygen" in msg:
        if spo2:
            try:
                s = int(str(spo2))
            except Exception:
                s = None
            status = "acceptable"
            if s and s < 95:
                status = "low—assess respiratory status immediately"
            return f"SpO2: {spo2}% ({status})."
        return "No oxygen saturation recorded."

    if any(k in msg for k in ["diagnose", "analysis", "what's wrong", "assessment"]):
        # Non-diagnostic advice—safe, grounded summary and next steps
        base = ["Assessment summary (not a diagnosis):"]
        if symptoms: base.append(f"- Reported symptoms: {symptoms}")
        if bp or hr or spo2:
            base.append("- Vitals summary:")
            if bp: base.append(f"  • BP {bp} mmHg")
            if hr: base.append(f"  • HR {hr} bpm")
            if spo2: base.append(f"  • SpO2 {spo2}%")
        if any([ecg, troponin, cholesterol]):
            base.append("- Key labs:")
            if ecg: base.append(f"  • ECG: {ecg}")
            if troponin: base.append(f"  • Troponin: {troponin} ng/mL")
            if cholesterol: base.append(f"  • Cholesterol: {cholesterol} mg/dL")
        base.append("Next steps: correlate clinically, consider targeted tests, and monitor vitals.")
        return "\n".join(base)

    # Default
    return (
        "I can answer questions grounded in this patient's JSON data—ask about vitals, labs, "
        "symptoms, or request a brief assessment summary."
    )

def _looks_like_open_question(message: str) -> bool:
    msg = (message or "").lower()
    triggers = ["what", "why", "how", "explain", "interpret", "risk", "prognosis", "could it be", "diagnosis", "differential"]
    return any(t in msg for t in triggers)

def _flatten_json(obj, parent_key="", sep="."):
    items = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else str(k)
            items.update(_flatten_json(v, new_key, sep=sep))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            new_key = f"{parent_key}{sep}{i}" if parent_key else str(i)
            items.update(_flatten_json(v, new_key, sep=sep))
    else:
        items[parent_key] = obj
    return items

def _json_qa_answer(message: str, patient: dict) -> str:
    """Very simple key-based QA over patient JSON. Returns text lines or empty string.
    Looks for key names in the user's message and returns values for matches.
    """
    if not patient:
        return ""
    msg = (message or "").lower()
    flat = _flatten_json(patient)
    # Extract alphanumeric tokens from the message
    tokens = [t for t in re.findall(r"[a-zA-Z0-9_]+", msg) if len(t) >= 2]
    if not tokens:
        return ""
    # Score keys by token overlap
    scored = []
    for k in flat.keys():
        key_tokens = set(re.findall(r"[a-zA-Z0-9_]+", k.lower()))
        overlap = len([t for t in tokens if t in key_tokens])
        if overlap > 0:
            scored.append((overlap, k))
    scored.sort(reverse=True)
    if not scored:
        return ""
    # Return top few matches
    top = scored[:5]
    lines = ["Relevant patient data:"]
    for _, k in top:
        val = flat.get(k)
        # Format key for display
        nice_k = k.replace(".", " → ")
        lines.append(f"- {nice_k}: {val}")
    return "\n".join(lines)

def _call_gemini_chat(message: str, patient: dict, history: list) -> str:
    """Call Gemini with patient JSON as context to provide general AI explanation/answer.
    History is a list of {role, content}.
    """
    model = _get_gemini_model()
    system_rules = (
        "You are a clinical assistant. Use the provided patient JSON as the primary source. "
        "Be accurate, concise, and avoid definitive diagnoses. Emphasize that outputs are informational, not medical advice."
    )
    context_json = json.dumps(patient or {}, indent=2)
    convo = [
        {"role": "user", "parts": [system_rules]},
        {"role": "user", "parts": [f"Patient JSON context:\n{context_json}"]},
    ]
    # Append recent history (limit to last 8 exchanges)
    for m in history[-16:]:
        role = "model" if m.get("role") == "assistant" else "user"
        convo.append({"role": role, "parts": [m.get("content", "")]})
    convo.append({"role": "user", "parts": [message]})
    resp = model.generate_content(convo)
    return (resp.text or "").strip()

def _generate_grounded_packet(message: str, patient: dict) -> dict:
    """Return {'response': text, 'structured': optional_dict} for rich chat rendering.
    Structured format:
    {
      'summary': str,
      'vitals': {'bp':..., 'hr':..., 'spo2':...},
      'labs': {'ecg':..., 'troponin':..., 'cholesterol':...},
      'insights': {'notes': [str, ...]},
      'tests': [{'test': str, 'reason': str, 'urgency': str}],
      'precautions': [str, ...],
      'red_flags': [str, ...]
    }
    """
    text = _generate_grounded_reply(message, patient)
    msg = (message or "").lower()
    structured = None

    if patient and any(k in msg for k in [
        "insight", "diagnose", "analysis", "assessment", "clinical",
        "disease", "diagnosis", "differential", "condition", "what could it be",
        "test", "tests", "recommended tests", "precaution", "precautions", "red flags", "redflags"
    ]):
        vitals = patient.get("vitals") or {}
        labs = patient.get("lab_results") or {}
        symptoms = (patient.get("symptoms") or "").strip()

        # Build heuristics for insights, tests, precautions, red flags
        insights_notes = []
        tests = []
        precautions = []
        red_flags = []
        diagnoses = []

        # BP
        bp = vitals.get("bp")
        try:
            systolic = int(str(bp).split("/")[0]) if bp else None
            diastolic = int(str(bp).split("/")[1]) if bp else None
        except Exception:
            systolic = diastolic = None
        if systolic and (systolic >= 140 or (diastolic and diastolic >= 90)):
            insights_notes.append("Elevated blood pressure; assess for hypertension and end-organ risk.")
            tests.append({"test": "Repeat BP and basic metabolic panel", "reason": "Confirm elevation and assess impact", "urgency": "Within 24-48 hours"})
            precautions.append("Limit sodium intake, ensure medication adherence, and monitor BP at home.")
            red_flags.append("Severe headache, chest pain, or neurological deficits with high BP—seek urgent care.")
            diagnoses.append({
                "condition": "Hypertension (possible)",
                "confidence": "Medium",
                "reasoning": f"BP reading {bp} meets elevated thresholds."
            })

        # HR
        hr = vitals.get("hr")
        try:
            hr_val = int(str(hr)) if hr is not None else None
        except Exception:
            hr_val = None
        if hr_val and (hr_val > 100 or hr_val < 60):
            insights_notes.append("Abnormal resting heart rate; correlate with symptoms and ECG.")
            tests.append({"test": "12‑lead ECG", "reason": "Evaluate rhythm or ischemia", "urgency": "Within 24h"})
            diagnoses.append({
                "condition": "Cardiac rhythm issue (possible)",
                "confidence": "Low",
                "reasoning": f"Resting HR {hr} outside normal range; requires correlation with ECG/clinical context."
            })

        # SpO2
        spo2 = vitals.get("spo2")
        try:
            spo2_val = int(str(spo2)) if spo2 is not None else None
        except Exception:
            spo2_val = None
        if spo2_val and spo2_val < 95:
            insights_notes.append("Low oxygen saturation; assess respiratory status.")
            tests.append({"test": "Chest X‑ray / ABG as indicated", "reason": "Investigate hypoxemia cause", "urgency": "Immediate"})
            red_flags.append("SpO2 < 92% or worsening dyspnea—urgent evaluation.")
            diagnoses.append({
                "condition": "Respiratory compromise (possible)",
                "confidence": "Medium",
                "reasoning": f"SpO2 {spo2}% is below normal; evaluate for pneumonia/COPD/PE as clinically indicated."
            })

        # Chest pain or concerning symptoms
        if any(x in (symptoms.lower()) for x in ["chest pain", "chest discomfort", "angina"]):
            insights_notes.append("Chest pain reported; rule out acute coronary syndrome if risk factors present.")
            tests.append({"test": "Serial troponins and ECG", "reason": "Assess myocardial injury", "urgency": "Immediate"})
            precautions.append("Avoid exertion; seek care if pain persists or worsens.")
            red_flags.append("Chest pain with diaphoresis, radiation, or dyspnea—call emergency services.")
            # Heuristic differential based on available labs
            ecg = labs.get("ecg")
            troponin = labs.get("troponin")
            troponin_high = False
            try:
                troponin_high = float(str(troponin)) > 0.04 if troponin is not None else False
            except Exception:
                troponin_high = False
            if troponin_high or (ecg and any(k in str(ecg).lower() for k in ["st", "ischemia", "t-wave"])):
                diagnoses.append({
                    "condition": "Acute Coronary Syndrome (rule out)",
                    "confidence": "Medium",
                    "reasoning": "Chest pain with abnormal biomarkers/ECG patterns."
                })
            else:
                diagnoses.append({
                    "condition": "Musculoskeletal or non-cardiac chest pain (possible)",
                    "confidence": "Low",
                    "reasoning": "Chest pain without clear cardiac markers; requires clinical correlation."
                })

        # Labs
        troponin = labs.get("troponin")
        cholesterol = labs.get("cholesterol")
        if cholesterol:
            try:
                chol_val = float(str(cholesterol))
            except Exception:
                chol_val = None
            if chol_val and chol_val > 200:
                insights_notes.append("Elevated cholesterol; optimize lipid-lowering therapy and lifestyle.")
                precautions.append("Adopt heart‑healthy diet and regular moderate exercise as tolerated.")
                diagnoses.append({
                    "condition": "Hyperlipidemia (likely)",
                    "confidence": "High",
                    "reasoning": f"Cholesterol {cholesterol} mg/dL above target."
                })

        # Fever + headache heuristic
        if any(k in symptoms.lower() for k in ["fever"]) and any(k in symptoms.lower() for k in ["headache"]):
            diagnoses.append({
                "condition": "Infectious syndrome (e.g., viral) - consider meningitis if red flags",
                "confidence": "Low",
                "reasoning": "Fever with headache; evaluate for neck stiffness/photophobia and systemic signs."
            })

        structured = {
            "summary": text if text else "Patient insights",
            "vitals": {"bp": bp, "hr": hr, "spo2": spo2},
            "labs": {"ecg": labs.get("ecg"), "troponin": troponin, "cholesterol": cholesterol},
            "insights": {"notes": insights_notes} if insights_notes else None,
            "diagnoses": diagnoses if diagnoses else None,
            "tests": tests if tests else None,
            "precautions": precautions if precautions else None,
            "red_flags": red_flags if red_flags else None,
        }

    packet = {"response": text}
    if structured:
        packet["structured"] = structured
    return packet

# ------------------- Enhanced Clinical Insights -------------------
@app.route("/clinical_insights/<patient_id>")
def clinical_insights(patient_id):
    print(f"DEBUG: Clinical insights requested for patient ID: {patient_id}")
    
    # Get data from SQL database
    current = get_patient_by_id(patient_id)
    history_data = get_patient_history(patient_id)
    history = history_data[0] if history_data else {}

    print(f"DEBUG: Found current data: {bool(current)}, history records: {len(history_data)}")
    print(f"DEBUG: Current data: {current}")
    print(f"DEBUG: History data: {history}")

    if not history and not current:
        print(f"DEBUG: No data found for patient {patient_id}")
        return jsonify({"error": "Patient data not found"}), 404

    # Extract key information
    current_symptoms = current.get('symptoms', 'None reported')
    current_vitals = current.get('vitals', {})
    current_labs = current.get('lab_results', {})
    history_conditions = history.get('history', []) if history else []
    medications = history.get('medications', []) if history else []
    age = current.get('age', 'Unknown')
    gender = current.get('gender', 'Unknown')
    
    # Calculate differences
    diffs = {}
    for k in ["vitals", "lab_results"]:
        diffs[k] = {}
        if current.get(k):
            for key, c_val in current.get(k, {}).items():
                h_val = history.get(k, {}).get(key) if history else None
                if c_val != h_val:
                    diffs[k][key] = {"previous": h_val, "current": c_val}
    diffs["symptoms"] = {
        "previous": history.get("symptoms", "") if history else "",
        "current": current.get("symptoms", "")
    }

    prompt = f"""
You are Dr. AI, an expert clinical assistant. A doctor is consulting with you about patient {patient_id}.

**PATIENT BACKGROUND:**
- Age: {age}
- Gender: {gender}
- Medical History: {history_conditions}
- Current Medications: {medications}

**CURRENT PRESENTATION:**
- Chief Complaint: {current_symptoms}
- Current Vitals: {current_vitals}
- Lab Results: {current_labs}

**CHANGES SINCE LAST VISIT:**
{diffs}

**INSTRUCTIONS:**
1. Analyze the symptoms, vitals, and lab results to identify the MOST LIKELY condition(s)
2. Consider the patient's medical history and medications in your assessment
3. Recommend specific additional tests needed for confirmation/differential diagnosis
4. Provide clear precautions and management recommendations
5. Structure your response in the exact JSON format specified below

**RESPONSE FORMAT:**
{{
  "greeting": "Brief opening statement",
  "likely_diagnosis": [
    {{
      "condition": "Primary likely condition name",
      "confidence": "High/Medium/Low",
      "reasoning": "Explanation based on symptoms, vitals, labs and history"
    }},
    {{
      "condition": "Secondary possible condition",
      "confidence": "High/Medium/Low", 
      "reasoning": "Brief explanation"
    }}
  ],
  "additional_tests": [
    {{
      "test_name": "Specific test name",
      "purpose": "Why this test is needed",
      "urgency": "Immediate/Within 24-48 hours/Routine"
    }}
  ],
  "precautions": [
    {{
      "category": "Activity/Lifestyle/Diet/Medication",
      "recommendation": "Specific precaution",
      "importance": "Critical/Important/Advisory"
    }}
  ],
  "management_plan": [
    "Immediate actions (first 24 hours)",
    "Short-term management (next few days)",
    "Follow-up requirements"
  ],
  "red_flags": [
    "Symptoms or changes that warrant immediate attention",
    "When to seek emergency care"
  ]
}}

Focus on clinical relevance and actionable recommendations. Be concise but thorough.
"""

    try:
        print("DEBUG: Calling Gemini API...")
        model = _get_gemini_model()
        response = model.generate_content(prompt)
        ai_text = response.text
        print(f"DEBUG: Gemini response length: {len(ai_text)}")
        print(f"DEBUG: Gemini response preview: {ai_text[:200]}...")

        try:
            ai_json = json.loads(ai_text)
            print("DEBUG: Successfully parsed JSON from Gemini")
        except json.JSONDecodeError as e:
            print(f"DEBUG: JSON parsing failed: {e}")
            print(f"DEBUG: Raw AI text: {ai_text}")
            # Create a structured fallback response
            ai_json = {
                "likely_diagnosis": [
                    {
                        "condition": "Requires clinical evaluation",
                        "confidence": "Unknown",
                        "reasoning": "AI analysis incomplete - manual review needed"
                    }
                ],
                "additional_tests": [
                    {
                        "test_name": "Complete clinical examination",
                        "purpose": "Thorough assessment of current symptoms",
                        "urgency": "Immediate"
                    }
                ],
                "precautions": [
                    {
                        "category": "General",
                        "recommendation": "Monitor symptoms closely and seek care if worsening",
                        "importance": "Important"
                    }
                ],
                "management_plan": [
                    "Review all available patient data",
                    "Consider specialist referral based on symptoms",
                    "Schedule follow-up within 24-48 hours"
                ],
                "red_flags": [
                    "Worsening of primary symptoms",
                    "Development of new concerning symptoms",
                    "Vital sign deterioration"
                ],
                "fallback_analysis": ai_text
            }

        print("DEBUG: Returning AI analysis")
        return jsonify(ai_json)

    except Exception as e:
        # Enhanced fallback analysis
        fallback_analysis = {
            "likely_diagnosis": [
                {
                    "condition": "Clinical evaluation required",
                    "confidence": "Unknown",
                    "reasoning": "AI analysis unavailable - manual assessment needed"
                }
            ],
            "additional_tests": [
                {
                    "test_name": "Comprehensive physical examination",
                    "purpose": "Base assessment on current symptoms and history",
                    "urgency": "Immediate"
                }
            ],
            "precautions": [
                {
                    "category": "General",
                    "recommendation": "Monitor symptoms and seek care if condition changes",
                    "importance": "Important"
                }
            ],
            "management_plan": [
                "Review patient vitals and lab results",
                "Compare current vs historical data",
                "Assess symptom progression",
                "Apply clinical guidelines",
                "Consider specialist consultation"
            ],
            "red_flags": [
                "Significant vital sign abnormalities",
                "Worsening pain or discomfort",
                "New neurological symptoms"
            ],
            "error_details": f"Gemini AI analysis failed: {str(e)}"
        }
        
        return jsonify(fallback_analysis)

# ------------------- Medical Diagnosis AI -------------------
@app.route("/ai_consultation/<patient_id>")
def ai_consultation(patient_id):
    """Provide comprehensive medical diagnosis and recommendations"""
    try:
        print(f"DEBUG: Medical diagnosis for patient {patient_id}")
        
        # Get data from SQL database
        current = get_patient_by_id(patient_id)
        history_data = get_patient_history(patient_id)
        history = history_data[0] if history_data else {}

        if not current:
            return jsonify({"error": "Patient data not found"}), 404

        # Extract current patient information
        symptoms = current.get('symptoms', 'None reported')
        vitals = current.get('vitals', {})
        labs = current.get('lab_results', {})
        
        # Get vital signs
        bp = vitals.get('bp', 'Not recorded')
        hr = vitals.get('hr', 'Not recorded')
        spo2 = vitals.get('spo2', 'Not recorded')
        
        # Get lab results
        ecg = labs.get('ecg', 'Not done')
        troponin = labs.get('troponin', 'Not tested')
        cholesterol = labs.get('cholesterol', 'Not tested')

        # Create medical analysis prompt
        prompt = f"""
You are Dr. AI, an expert medical diagnostician. Analyze this patient's data and provide a comprehensive medical assessment.

PATIENT DATA:
- Symptoms: {symptoms}
- Blood Pressure: {bp}
- Heart Rate: {hr} bpm
- Oxygen Saturation: {spo2}%
- ECG: {ecg}
- Troponin: {troponin}
- Cholesterol: {cholesterol}

INSTRUCTIONS:
Based on the symptoms and clinical data, provide a detailed medical analysis in JSON format with:

1. Most likely diseases/conditions
2. Confidence level for each diagnosis
3. Reasoning based on symptoms and vitals
4. Recommended tests
5. Immediate precautions
6. Treatment recommendations
7. Warning signs to watch for

RESPONSE FORMAT (JSON only):
{{
  "primary_diagnosis": {{
    "condition": "Most likely condition name",
    "confidence": "High/Medium/Low",
    "reasoning": "Detailed explanation based on symptoms, vitals, and lab results"
  }},
  "differential_diagnosis": [
    {{
      "condition": "Alternative condition 1",
      "confidence": "High/Medium/Low",
      "reasoning": "Brief explanation"
    }},
    {{
      "condition": "Alternative condition 2", 
      "confidence": "High/Medium/Low",
      "reasoning": "Brief explanation"
    }}
  ],
  "recommended_tests": [
    {{
      "test": "Specific test name",
      "reason": "Why this test is needed",
      "urgency": "Immediate/Within 24h/Routine"
    }}
  ],
  "immediate_precautions": [
    "Specific precaution 1",
    "Specific precaution 2",
    "Specific precaution 3"
  ],
  "treatment_plan": [
    "Immediate action 1",
    "Short-term management 2", 
    "Long-term care 3"
  ],
  "red_flags": [
    "Warning sign 1 - seek immediate care",
    "Warning sign 2 - call emergency",
    "Warning sign 3 - urgent medical attention"
  ],
  "lifestyle_advice": [
    "Diet recommendation",
    "Activity modification",
    "Monitoring advice"
  ]
}}

Focus on practical, actionable medical advice. Be specific about the conditions based on the presented symptoms and vitals.
"""

        # Call Gemini AI
        model = _get_gemini_model()
        response = model.generate_content(prompt)
        ai_text = response.text.strip()
        
        print(f"DEBUG: AI response: {ai_text[:200]}...")
        
        try:
            # Try to parse JSON response
            import re
            json_match = re.search(r'\{.*\}', ai_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                ai_diagnosis = json.loads(json_str)
                print("DEBUG: Successfully parsed medical diagnosis JSON")
                return jsonify(ai_diagnosis)
            else:
                raise ValueError("No JSON found in response")
                
        except (json.JSONDecodeError, ValueError) as e:
            print(f"DEBUG: JSON parsing failed: {e}")
            # Create structured fallback response
            fallback_diagnosis = {
                "primary_diagnosis": {
                    "condition": "Clinical evaluation needed",
                    "confidence": "Medium",
                    "reasoning": f"Based on symptoms: {symptoms}. Requires further clinical assessment."
                },
                "differential_diagnosis": [
                    {
                        "condition": "Viral syndrome",
                        "confidence": "Medium", 
                        "reasoning": "Common cause of fatigue, headache, and nausea"
                    },
                    {
                        "condition": "Hypertension",
                        "confidence": "Medium",
                        "reasoning": f"Blood pressure reading: {bp}"
                    }
                ],
                "recommended_tests": [
                    {
                        "test": "Complete Blood Count (CBC)",
                        "reason": "Evaluate for infection or anemia",
                        "urgency": "Within 24h"
                    },
                    {
                        "test": "Basic Metabolic Panel",
                        "reason": "Check electrolytes and kidney function",
                        "urgency": "Within 24h"
                    }
                ],
                "immediate_precautions": [
                    "Monitor blood pressure regularly",
                    "Stay hydrated",
                    "Rest and avoid strenuous activity"
                ],
                "treatment_plan": [
                    "Symptomatic treatment for nausea and headache",
                    "Blood pressure monitoring",
                    "Follow-up with primary care physician"
                ],
                "red_flags": [
                    "Severe chest pain - seek immediate care",
                    "Difficulty breathing - call emergency",
                    "Severe headache with vision changes - urgent medical attention"
                ],
                "lifestyle_advice": [
                    "Low sodium diet for blood pressure control",
                    "Gradual increase in physical activity",
                    "Regular blood pressure monitoring"
                ],
                "raw_ai_response": ai_text
            }
            return jsonify(fallback_diagnosis)
            
    except Exception as e:
        print(f"DEBUG: Error in AI consultation: {e}")
        error_response = {
            "primary_diagnosis": {
                "condition": "Unable to analyze - system error",
                "confidence": "Low",
                "reasoning": "AI analysis system encountered an error"
            },
            "differential_diagnosis": [],
            "recommended_tests": [
                {
                    "test": "Clinical examination",
                    "reason": "Manual assessment needed",
                    "urgency": "Immediate"
                }
            ],
            "immediate_precautions": [
                "Seek medical attention if symptoms worsen"
            ],
            "treatment_plan": [
                "Consult with healthcare provider"
            ],
            "red_flags": [
                "Any worsening of symptoms"
            ],
            "lifestyle_advice": [
                "Monitor symptoms closely"
            ],
            "error": str(e)
        }
        return jsonify(error_response)

# ------------------- New API Routes for Doctor and Patient -------------------
@app.route("/api/doctor-chat", methods=["POST"])
def api_doctor_chat():
    """Doctor chat endpoint - routes to the existing chat_with_ai logic with Gemini"""
    try:
        data = request.get_json() or {}
        # Map to the format chat_with_ai expects
        payload = {
            "message": data.get("message", ""),
            "patientId": data.get("patientId", ""),
            "patientData": data.get("patientData", {}),
            "generalAi": data.get("generalAi", True)
        }
        # Call the existing chat_with_ai logic
        return chat_with_ai()
    except Exception as e:
        return jsonify({"error": f"Doctor chat failed: {str(e)}"}), 500

@app.route("/api/patient-inference", methods=["POST"])
def api_patient_inference():
    """Patient inference endpoint - simple Q&A using Gemini"""
    try:
        data = request.get_json() or {}
        inputs = data.get("inputs", {})
        user_message = inputs.get("message", "").strip()
        patient_id = inputs.get("patientId", "")
        patient_data = inputs.get("patientData", {})
        
        if not user_message:
            return jsonify({"error": "No message provided"}), 400
        
        # Use Gemini for patient queries
        if not _has_gemini():
            return jsonify({
                "error": "AI not configured",
                "result": "Please set GEMINI_API_KEY in .env to enable AI chat."
            }), 500
        
        try:
            model = _get_gemini_model()
            # Simple prompt for patient-facing chat
            prompt = f"""
You are a helpful medical assistant for patients. Answer the patient's question clearly and compassionately.
Keep answers simple, avoid complex medical jargon, and always remind them to consult their doctor for medical advice.

Patient's question: {user_message}

Provide a helpful, clear answer.
"""
            response = model.generate_content(prompt)
            result_text = (response.text or "").strip()
            
            return jsonify({
                "result": result_text,
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            return jsonify({
                "error": "AI processing error",
                "result": f"I'm having trouble processing your request. Error: {str(e)}"
            }), 500
            
    except Exception as e:
        return jsonify({"error": f"Patient inference failed: {str(e)}"}), 500

# ------------------- Test Gemini API -------------------
@app.route("/test_gemini")
def test_gemini():
    try:
        model = _get_gemini_model()
        response = model.generate_content("Say 'Gemini API works' in exactly 3 words.")
        return jsonify({"status": "success", "response": response.text})
    except Exception as e:
        # Include available models to aid debugging
        try:
            models = genai.list_models()
            models_info = [
                {
                    "name": getattr(m, "name", ""),
                    "methods": getattr(m, "supported_generation_methods", [])
                }
                for m in models
            ]
        except Exception as e2:
            models_info = {"error": f"Unable to list models: {str(e2)}"}
        return jsonify({
            "status": "error",
            "details": str(e),
            "available_models": models_info
        }), 500

# ------------------- Run Flask App -------------------
if __name__ == "__main__":
    app.run(debug=True, port=5001)
