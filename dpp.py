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

# ------------------- Flask App -------------------
app = Flask(__name__, template_folder="templates", static_folder="frontend/static")

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
    """Return a configured Gemini GenerativeModel or raise a helpful error if not configured."""
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Please set the environment variable to your Gemini API key."
        )
    # Configure the SDK and return the model instance
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-1.5-flash")

# ------------------- Ensure JSON files exist -------------------
for file in ["patients.json", "patients_history.json", "chat_sessions.json"]:
    path = _data_path(file)
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump([], f, indent=4)

# ------------------- Utility Functions -------------------
def _normalize_patient_id(value):
    try:
        return str(value).strip().upper()
    except Exception:
        return ""

# ------------------- Chat Session Management -------------------
def get_chat_session(session_id, patient_id):
    """Get or create a chat session"""
    sessions_path = _data_path("chat_sessions.json")
    
    # Load existing sessions
    if os.path.exists(sessions_path):
        with open(sessions_path, "r") as f:
            sessions = json.load(f)
    else:
        sessions = []
    
    # Find existing session
    for session in sessions:
        if session["session_id"] == session_id:
            return session
    
    # Create new session
    new_session = {
        "session_id": session_id,
        "patient_id": patient_id,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "messages": [],
        "patient_data": get_patient_data_internal(patient_id)
    }
    
    sessions.append(new_session)
    
    # Save updated sessions
    with open(sessions_path, "w") as f:
        json.dump(sessions, f, indent=4)
    
    return new_session

def update_chat_session(session_id, message):
    """Update a chat session with a new message"""
    sessions_path = _data_path("chat_sessions.json")
    
    # Load existing sessions
    with open(sessions_path, "r") as f:
        sessions = json.load(f)
    
    # Find and update session
    for session in sessions:
        if session["session_id"] == session_id:
            session["messages"].append(message)
            session["updated_at"] = datetime.now().isoformat()
            break
    
    # Save updated sessions
    with open(sessions_path, "w") as f:
        json.dump(sessions, f, indent=4)

def get_patient_data_internal(patient_id):
    """Internal function to get patient data"""
    normalized_query = _normalize_patient_id(patient_id)
    with open(_data_path("patients.json"), "r") as f:
        all_data = json.load(f)
        if isinstance(all_data, dict):
            all_data = [all_data]

    patient_data = [
        entry for entry in all_data
        if _normalize_patient_id(entry.get("patient_id")) == normalized_query
    ]
    
    return patient_data[0] if patient_data else {}

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

    # Load existing patient data
    with open(_data_path("patients.json"), "r") as f:
        patients = json.load(f)

    # Add timestamp if not present
    if "timestamp" not in data:
        data["timestamp"] = datetime.now().isoformat()

    # Append new patient data
    patients.append(data)

    # Save updated data
    with open(_data_path("patients.json"), "w") as f:
        json.dump(patients, f, indent=4)

    return jsonify({"status": "success", "message": "Patient data saved successfully!"})

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
        
        # Get Gemini model with vision capabilities
        model = genai.GenerativeModel("gemini-1.5-flash")
        
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
def get_patient_data(patient_id):
    normalized_query = _normalize_patient_id(patient_id)
    with open(_data_path("patients.json"), "r") as f:
        all_data = json.load(f)
        if isinstance(all_data, dict):
            all_data = [all_data]

    patient_data = [
        entry for entry in all_data
        if _normalize_patient_id(entry.get("patient_id")) == normalized_query
    ]

    if not patient_data:
        return jsonify({"error": "Patient not found"}), 404

    return jsonify(patient_data)

@app.route("/get_all_patients")
def get_all_patients():
    with open(_data_path("patients.json"), "r") as f:
        all_data = json.load(f)
        if isinstance(all_data, dict):
            all_data = [all_data]
    return jsonify(all_data)

# ------------------- Patient Comparison Plot -------------------
@app.route("/patient_compare_plot/<patient_id>")
def patient_compare_plot(patient_id):
    normalized_query = _normalize_patient_id(patient_id)
    with open(_data_path("patients.json"), "r") as f:
        current = json.load(f)
        if isinstance(current, dict):
            current = [current]

    with open(_data_path("patients_history.json"), "r") as f:
        history = json.load(f)
        if isinstance(history, dict):
            history = [history]

    current_data = [p for p in current if _normalize_patient_id(p.get("patient_id")) == normalized_query]
    history_data = [p for p in history if _normalize_patient_id(p.get("patient_id")) == normalized_query]

    if not current_data and not history_data:
        return "Patient not found", 404

    df_current = pd.DataFrame(current_data)
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

# ------------------- Enhanced Clinical Insights -------------------
@app.route("/clinical_insights/<patient_id>")
def clinical_insights(patient_id):
    print(f"DEBUG: Clinical insights requested for patient ID: {patient_id}")
    
    with open(_data_path("patients.json")) as f:
        current_data = json.load(f)
    with open(_data_path("patients_history.json")) as f:
        history_data = json.load(f)

    print(f"DEBUG: Loaded {len(current_data)} current records, {len(history_data)} history records")

    def _norm(pid): return str(pid).strip().upper()
    history = next((p for p in history_data if _norm(p.get("patient_id")) == _norm(patient_id)), {})
    current = next((p for p in current_data if _norm(p.get("patient_id")) == _norm(patient_id)), {})

    print(f"DEBUG: Found history data: {bool(history)}, current data: {bool(current)}")
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
        
        # Load patient data
        with open(_data_path("patients.json")) as f:
            current_data = json.load(f)
        
        # Try to load history data
        try:
            with open(_data_path("patients_history.json")) as f:
                history_data = json.load(f)
        except FileNotFoundError:
            history_data = []

        def _norm(pid): return str(pid).strip().upper()
        history = next((p for p in history_data if _norm(p.get("patient_id")) == _norm(patient_id)), {})
        current = next((p for p in current_data if _norm(p.get("patient_id")) == _norm(patient_id)), {})

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

# ------------------- Test Gemini API -------------------
@app.route("/test_gemini")
def test_gemini():
    try:
        model = _get_gemini_model()
        response = model.generate_content("Say 'Gemini API works' in exactly 3 words.")
        return jsonify({"status": "success", "response": response.text})
    except Exception as e:
        return jsonify({"status": "error", "details": str(e)}), 500

# ------------------- Run Flask App -------------------
if __name__ == "__main__":
    app.run(debug=True, port=5001)
