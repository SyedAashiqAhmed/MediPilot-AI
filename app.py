from flask import Flask, request, jsonify, render_template, redirect, url_for
import json
import os
import io
import base64
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import requests
from dotenv import load_dotenv
import google.generativeai as genai

# Database imports
from models import db
from database import (init_db, save_patient_data, get_patient_by_id, get_all_patients,
                      get_patient_comparison_data)

load_dotenv()
app = Flask(__name__, template_folder="templates", static_folder="frontend/static")

# Initialize database
init_db(app)

# Resolve data file paths relative to this script's directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def _data_path(filename):
    return os.path.join(BASE_DIR, filename)

def _normalize_patient_id(value):
    try:
        return str(value).strip().upper()
    except Exception:
        return ""

def _call_external_api(url, api_key, payload, timeout=20):
    headers = {
        "Content-Type": "application/json",
    }
    # Support common auth patterns
    if api_key:
        # Prefer Bearer unless the upstream expects a custom header
        headers["Authorization"] = f"Bearer {api_key}"
    resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
    # Raise for non-2xx to be handled by caller
    resp.raise_for_status()
    return resp.json()

# Database is initialized above - no need for JSON files

@app.route("/")
def intro():
    return render_template("intro.html")

@app.route("/patient")
def patient():
    return render_template("index.html")

@app.route("/doctor")
def doctor():
    return render_template("doctor.html")

@app.route("/test-api")
def test_api():
    return render_template("test_api.html")

@app.route("/debug")
def debug():
    return render_template("debug.html")

@app.route("/submit_patient", methods=["POST"])
def submit_patient():
    data = request.get_json()
    if not data:
        return jsonify({"status":"error","message":"No data received"}), 400

    # Normalize patient_id
    if 'patient_id' in data:
        data['patient_id'] = _normalize_patient_id(data['patient_id'])
    
    # Add timestamp if not present
    if "timestamp" not in data:
        data["timestamp"] = datetime.now().isoformat()

    # Save to SQL database
    try:
        save_patient_data(data)
        return jsonify({"status": "success", "message": "Patient data saved!"})
    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to save: {str(e)}"}), 500

# ------------------- Doctor APIs (to support doctor.html on this server) -------------------
@app.route("/get_patient_data/<patient_id>")
def get_patient_data(patient_id):
    patient_data = get_patient_by_id(patient_id)
    if not patient_data:
        return jsonify({"error": "Patient not found"}), 404
    return jsonify([patient_data])  # Return as array for backwards compatibility

@app.route("/get_all_patients")
def get_all_patients_route():
    all_patients = get_all_patients()
    return jsonify(all_patients)

@app.route("/patient_compare_plot/<patient_id>")
def patient_compare_plot(patient_id):
    # Get data from SQL database
    current_data, history_data = get_patient_comparison_data(patient_id)
    
    if not current_data and not history_data:
        return jsonify({"error": "Patient not found"}), 404
    
    # Convert to lists for DataFrame
    current_list = [current_data] if current_data else []
    
    df_current = pd.DataFrame(current_list)
    df_history = pd.DataFrame(history_data)

    def bp_systolic(bp):
        try:
            return int(str(bp).split("/")[0])
        except Exception:
            return 0

    def bp_diastolic(bp):
        try:
            return int(str(bp).split("/")[1])
        except Exception:
            return 0

    def _to_number(value, default=0):
        try:
            if value is None:
                return default
            if isinstance(value, (int, float)):
                return float(value)
            return float(str(value).strip())
        except Exception:
            return default

    def hr(vitals):
        return _to_number(vitals.get('hr', 0), 0)

    def spo2(vitals):
        return _to_number(vitals.get('spo2', 0), 0)

    def cholesterol(lab_results):
        return _to_number(lab_results.get('cholesterol', 0), 0)

    def blood_sugar(lab_results):
        if 'blood_sugar' in lab_results:
            return _to_number(lab_results.get('blood_sugar', 0), 0)
        if 'hba1c' in lab_results:
            return _to_number(lab_results.get('hba1c', 0), 0)
        return 0

    metrics = ['BP Systolic', 'BP Diastolic', 'Heart Rate', 'SpO2', 'Cholesterol', 'Blood Sugar']

    if not df_current.empty:
        current_values = [
            df_current['vitals'].apply(lambda x: bp_systolic(x.get('bp'))).mean(),
            df_current['vitals'].apply(lambda x: bp_diastolic(x.get('bp'))).mean(),
            df_current['vitals'].apply(lambda x: hr(x)).mean(),
            df_current['vitals'].apply(lambda x: spo2(x)).mean(),
            df_current['lab_results'].apply(lambda x: cholesterol(x)).mean(),
            df_current['lab_results'].apply(lambda x: blood_sugar(x)).mean()
        ]
    else:
        current_values = [0] * len(metrics)

    if not df_history.empty:
        history_values = [
            df_history['vitals'].apply(lambda x: bp_systolic(x.get('bp'))).mean(),
            df_history['vitals'].apply(lambda x: bp_diastolic(x.get('bp'))).mean(),
            df_history['vitals'].apply(lambda x: hr(x)).mean(),
            df_history['vitals'].apply(lambda x: spo2(x)).mean(),
            df_history['lab_results'].apply(lambda x: cholesterol(x)).mean(),
            df_history['lab_results'].apply(lambda x: blood_sugar(x)).mean()
        ]
    else:
        history_values = [0] * len(metrics)

    fig, ax = plt.subplots(figsize=(10, 6))
    x = range(len(metrics))
    width = 0.35

    ax.bar([i - width/2 for i in x], history_values, width=width, color='skyblue', label='History', alpha=0.8)
    ax.bar([i + width/2 for i in x], current_values, width=width, color='orange', label='Current', alpha=0.8)

    ax.set_xticks(list(x))
    ax.set_xticklabels(metrics, rotation=45, ha='right')
    ax.set_ylabel("Values")
    ax.set_title(f"Patient {patient_id} - Current vs Historical Averages")
    ax.legend()
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    plt.close(fig)

    return jsonify({"image": img_base64})

@app.route("/chat_with_ai", methods=["POST"])
def chat_with_ai():
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        patient_id = data.get('patientId', '')
        patient_data = data.get('patientData', {})
        
        if not user_message:
            return jsonify({"error": "No message provided"}), 400
            
        # Simple response generation based on keywords in the message
        response = generate_ai_response(user_message, patient_data, patient_id)
        
        return jsonify({
            "response": response,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        print(f"Error in chat_with_ai: {str(e)}")
        return jsonify({"error": "An error occurred while processing your request"}), 500

@app.route("/api/doctor-chat", methods=["POST"])
def api_doctor_chat():
    """Doctor chat endpoint.
    If DOCTOR_API_URL is configured, forward the request to that external chat model.
    Otherwise, fall back to local generate_ai_response for compatibility.
    Expected JSON: { message: str, patientId?: str, patientData?: object }
    """
    try:
        data = request.get_json() or {}
        user_message = (data.get("message") or "").strip()
        patient_id = data.get("patientId", "")
        patient_data = data.get("patientData", {})
        if not user_message:
            return jsonify({"error": "No message provided"}), 400

        doctor_api_url = os.getenv("DOCTOR_API_URL", "").strip()
        doctor_api_key = (os.getenv("DOCTOR_API_KEY") or os.getenv("AI_API_KEY") or "").strip()

        if doctor_api_url:
            # Construct a generic payload; you can adapt this to the exact upstream contract
            payload = {
                "role": "doctor_assistant",
                "message": user_message,
                "context": {
                    "patientId": patient_id,
                    "patientData": patient_data,
                },
            }
            try:
                result = _call_external_api(doctor_api_url, doctor_api_key, payload)
                return jsonify({
                    "response": result.get("response") or result.get("text") or result,
                    "raw": result,
                    "timestamp": datetime.now().isoformat(),
                })
            except requests.HTTPError as http_err:
                return jsonify({"error": "Doctor model HTTP error", "details": str(http_err)}), 502
            except requests.RequestException as req_err:
                return jsonify({"error": "Doctor model request error", "details": str(req_err)}), 502

        # Fallback: local rules-based response
        response = generate_ai_response(user_message, patient_data, patient_id)
        return jsonify({
            "response": response,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        print(f"Error in api_doctor_chat: {str(e)}")
        return jsonify({"error": "An error occurred while processing your request"}), 500

@app.route("/api/patient-inference", methods=["POST"])
def api_patient_inference():
    """Patient-facing inference endpoint with fallback to local responses.
    If PATIENT_API_URL is configured, forwards to external API.
    Otherwise, provides basic health information responses.
    """
    try:
        data = request.get_json() or {}
        inputs = data.get("inputs", {})
        message = inputs.get("message", "").lower()
        
        patient_api_url = os.getenv("PATIENT_API_URL", "").strip()
        patient_api_key = (os.getenv("PATIENT_API_KEY") or os.getenv("AI_API_KEY") or "").strip()

        # If external API is configured, use it
        if patient_api_url:
            payload = {"inputs": inputs}
            try:
                result = _call_external_api(patient_api_url, patient_api_key, payload)
                return jsonify({
                    "result": result,
                    "timestamp": datetime.now().isoformat(),
                })
            except requests.HTTPError as http_err:
                print(f"Patient API HTTP error: {http_err}")
                # Fall through to local response
            except requests.RequestException as req_err:
                print(f"Patient API request error: {req_err}")
                # Fall through to local response

        # Fallback: Local health information responses
        response_text = generate_patient_health_response(message)
        
        return jsonify({
            "result": response_text,
            "timestamp": datetime.now().isoformat(),
        })
    except Exception as e:
        print(f"Error in api_patient_inference: {str(e)}")
        return jsonify({"error": "An error occurred while processing your request"}), 500

def generate_patient_health_response(message):
    """Generate basic health information responses for patients"""
    message = message.lower()
    
    # General health tips
    if any(word in message for word in ["health tips", "healthy", "wellness", "general health"]):
        return """Here are some general health tips:

🥗 **Nutrition:**
- Eat a balanced diet with plenty of fruits and vegetables
- Stay hydrated - drink 8 glasses of water daily
- Limit processed foods and added sugars

🏃 **Physical Activity:**
- Aim for 150 minutes of moderate exercise per week
- Include strength training 2-3 times weekly
- Take breaks from sitting every hour

😴 **Sleep:**
- Get 7-9 hours of quality sleep each night
- Maintain a consistent sleep schedule
- Avoid screens 1 hour before bedtime

🧘 **Mental Health:**
- Practice stress management techniques
- Stay socially connected
- Seek help if feeling overwhelmed

💊 **Preventive Care:**
- Schedule regular check-ups
- Keep vaccinations up to date
- Monitor your blood pressure and cholesterol

Remember: This is general information. Always consult your doctor for personalized medical advice."""

    # Symptoms inquiry
    if any(word in message for word in ["symptoms", "feeling sick", "not well", "pain"]):
        return """I understand you're experiencing symptoms. Here's what you should know:

⚠️ **When to See a Doctor:**
- Severe or persistent pain
- High fever (over 103°F/39.4°C)
- Difficulty breathing
- Chest pain or pressure
- Sudden severe headache
- Unexplained weight loss
- Symptoms lasting more than a week

🚨 **Emergency Signs (Call 911):**
- Chest pain with shortness of breath
- Sudden weakness or numbness
- Difficulty speaking or confusion
- Severe bleeding
- Loss of consciousness

📝 **Track Your Symptoms:**
- When they started
- How severe they are (1-10 scale)
- What makes them better or worse
- Any other accompanying symptoms

Please consult a healthcare provider for proper diagnosis and treatment. This chat is for information only."""

    # When to see doctor
    if any(word in message for word in ["see a doctor", "doctor", "medical help", "appointment"]):
        return """You should see a doctor if you experience:

🔴 **Urgent (Within 24 hours):**
- High fever with rash
- Severe abdominal pain
- Persistent vomiting or diarrhea
- Signs of dehydration
- Severe allergic reaction

🟡 **Soon (Within a few days):**
- Persistent cough or cold
- Minor injuries not healing
- Skin changes or new moles
- Ongoing digestive issues
- Sleep problems

🟢 **Routine Check-ups:**
- Annual physical exam
- Preventive screenings
- Chronic condition management
- Medication reviews

📞 **How to Prepare:**
- List your symptoms and when they started
- Bring current medications
- Note any questions you have
- Bring your insurance card

You can also use our video consultation feature to connect with a doctor remotely!"""

    # Medication questions
    if any(word in message for word in ["medication", "medicine", "pills", "drugs"]):
        return """Important information about medications:

💊 **Taking Medications Safely:**
- Follow prescribed dosages exactly
- Take at the same time each day
- Don't skip doses
- Complete full antibiotic courses

⚠️ **Never:**
- Share prescription medications
- Take expired medications
- Mix medications without doctor approval
- Stop medications suddenly without consulting your doctor

📋 **Keep Track:**
- Maintain a list of all medications
- Note any side effects
- Check for drug interactions
- Store properly (temperature, light)

🤔 **Questions to Ask Your Doctor:**
- What is this medication for?
- How and when should I take it?
- What are possible side effects?
- Can I take it with my other medications?

For specific medication questions, please consult your doctor or pharmacist."""

    # Diet and nutrition
    if any(word in message for word in ["diet", "nutrition", "food", "eating"]):
        return """Nutrition guidelines for better health:

🥗 **Balanced Diet Includes:**
- Fruits and vegetables (5+ servings daily)
- Whole grains (brown rice, whole wheat)
- Lean proteins (fish, chicken, beans)
- Healthy fats (nuts, avocado, olive oil)
- Low-fat dairy or alternatives

🚫 **Limit:**
- Added sugars and sweetened beverages
- Saturated and trans fats
- Sodium (less than 2,300mg daily)
- Processed and fast foods
- Alcohol consumption

💧 **Hydration:**
- Drink water throughout the day
- Limit caffeine intake
- Avoid sugary drinks

🍽️ **Healthy Eating Habits:**
- Eat regular meals
- Practice portion control
- Read nutrition labels
- Cook at home more often
- Eat mindfully without distractions

For personalized nutrition advice, consider consulting a registered dietitian."""

    # Exercise and fitness
    if any(word in message for word in ["exercise", "workout", "fitness", "physical activity"]):
        return """Exercise recommendations for adults:

🏃 **Cardio (Aerobic):**
- 150 minutes moderate intensity per week
- OR 75 minutes vigorous intensity
- Examples: brisk walking, swimming, cycling
- Break into 10-minute sessions if needed

💪 **Strength Training:**
- 2 or more days per week
- Work all major muscle groups
- Use weights, resistance bands, or body weight
- Allow rest days between sessions

🧘 **Flexibility & Balance:**
- Stretching exercises daily
- Yoga or tai chi
- Important for injury prevention
- Especially important as you age

⚠️ **Safety Tips:**
- Start slowly and progress gradually
- Warm up before and cool down after
- Stay hydrated
- Listen to your body
- Consult doctor before starting new program

🎯 **Getting Started:**
- Find activities you enjoy
- Set realistic goals
- Track your progress
- Exercise with friends for motivation

Remember: Any movement is better than none!"""

    # Mental health
    if any(word in message for word in ["stress", "anxiety", "depression", "mental health", "mood"]):
        return """Mental health is just as important as physical health:

🧠 **Signs to Watch For:**
- Persistent sadness or anxiety
- Changes in sleep or appetite
- Loss of interest in activities
- Difficulty concentrating
- Feelings of hopelessness

💚 **Self-Care Strategies:**
- Practice mindfulness or meditation
- Exercise regularly
- Maintain social connections
- Get adequate sleep
- Limit alcohol and avoid drugs

🆘 **When to Seek Help:**
- Symptoms interfere with daily life
- Thoughts of self-harm
- Substance abuse issues
- Trauma or major life changes

📞 **Resources:**
- Talk to your doctor
- Mental health professionals
- Support groups
- Crisis hotlines (988 in US)
- Employee assistance programs

🌟 **Remember:**
- Mental health conditions are treatable
- Seeking help is a sign of strength
- You're not alone
- Recovery is possible

If you're in crisis, please call 988 (Suicide & Crisis Lifeline) or go to your nearest emergency room."""

    # Default response
    return """Hello! I'm here to provide general health information. I can help with:

💡 **Topics I can discuss:**
- General health tips and wellness
- When to see a doctor
- Healthy lifestyle habits
- Nutrition and exercise
- Medication safety
- Mental health resources

❓ **You can ask me about:**
- "What are some general health tips?"
- "When should I see a doctor?"
- "How much exercise do I need?"
- "What's a healthy diet?"
- "How can I manage stress?"

⚠️ **Important:**
This chat provides general information only and is NOT a substitute for professional medical advice, diagnosis, or treatment. Always consult your healthcare provider for medical concerns.

🚨 **For emergencies, call 911 or go to the nearest emergency room.**

How can I help you today?"""

def generate_ai_response(message, patient_data, patient_id):
    """Generate a response based on the user's message and patient data"""
    message = message.lower()
    
    # Greeting
    if any(word in message for word in ["hello", "hi", "hey"]):
        return "Hello! I'm your AI medical assistant. How can I help you with this patient today?"
    
    # Patient information
    if any(word in message for word in ["patient info", "patient details", "patient data"]):
        if not patient_data:
            return "I don't have any patient data to analyze. Please load a patient's data first."
        
        response = ["Here's what I know about this patient:"]
        
        # Basic info
        if 'name' in patient_data:
            response.append(f"- Name: {patient_data.get('name')}")
        if 'age' in patient_data:
            response.append(f"- Age: {patient_data.get('age')}")
        if 'gender' in patient_data:
            response.append(f"- Gender: {patient_data.get('gender')}")
            
        # Vitals
        if 'vitals' in patient_data and patient_data['vitals']:
            response.append("\nVital Signs:")
            for key, value in patient_data['vitals'].items():
                if value:
                    response.append(f"- {key.upper()}: {value}")
                    
        # Symptoms
        if 'symptoms' in patient_data and patient_data['symptoms']:
            response.append("\nReported Symptoms:")
            response.append(f"- {patient_data['symptoms']}")
            
        return "\n".join(response)
    
    # Medical advice (very basic - in a real app, this would use a proper medical AI)
    if any(word in message for word in ["diagnose", "what's wrong", "analysis"]):
        if not patient_data:
            return "I need to see the patient's data first. Please load the patient's information."
            
        # Very basic diagnostic logic - in a real app, this would use proper medical AI
        symptoms = patient_data.get('symptoms', '').lower()
        vitals = patient_data.get('vitals', {})
        
        if 'chest pain' in symptoms or 'chest discomfort' in symptoms:
            return "Based on the reported chest pain, I recommend immediate evaluation for possible cardiac issues. Please consider ordering an ECG and cardiac enzymes. This could be a medical emergency if accompanied by shortness of breath, sweating, or pain radiating to the arm or jaw."
        
        if 'headache' in symptoms and 'fever' in symptoms:
            return "The combination of headache and fever could indicate an infection such as influenza or possibly meningitis if accompanied by neck stiffness. Consider monitoring temperature and checking for other signs of infection."
            
        return "Based on the available information, I recommend a thorough physical examination and possibly some diagnostic tests. The symptoms could be related to various conditions, and more information is needed for an accurate assessment."
    
    # Default response
    return "I'm here to help analyze patient data and provide medical insights. You can ask me about the patient's information, request an analysis, or ask general medical questions. How can I assist you with this patient?"

@app.route("/clinical_insights/<patient_id>")
def clinical_insights(patient_id):
    normalized_query = _normalize_patient_id(patient_id)
    
    # Load patient data
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
        return jsonify({"error": "Patient not found"}), 404
    
    # Get latest current data
    latest_current = current_data[-1] if current_data else {}
    latest_history = history_data[-1] if history_data else {}
    
    # Generate clinical insights based on data
    insights = []
    
    # Blood Pressure Analysis
    if latest_current.get('vitals', {}).get('bp'):
        try:
            bp = latest_current['vitals']['bp']
            if '/' in str(bp):
                systolic, diastolic = map(int, str(bp).split('/'))
                if systolic >= 140 or diastolic >= 90:
                    insights.append("⚠️ High blood pressure detected. Consider lifestyle changes and medication review.")
                elif systolic >= 130 or diastolic >= 80:
                    insights.append("⚠️ Elevated blood pressure. Monitor closely and consider dietary modifications.")
                else:
                    insights.append("✅ Blood pressure within normal range.")
        except:
            pass
    
    # Heart Rate Analysis
    if latest_current.get('vitals', {}).get('hr'):
        try:
            hr = int(latest_current['vitals']['hr'])
            if hr > 100:
                insights.append("⚠️ Elevated heart rate. Consider stress management and physical activity assessment.")
            elif hr < 60:
                insights.append("⚠️ Low heart rate. Monitor for symptoms and consider cardiac evaluation.")
            else:
                insights.append("✅ Heart rate within normal range.")
        except:
            pass
    
    # Oxygen Saturation Analysis
    if latest_current.get('vitals', {}).get('spo2'):
        try:
            spo2 = int(latest_current['vitals']['spo2'])
            if spo2 < 95:
                insights.append("⚠️ Low oxygen saturation. Consider respiratory evaluation and oxygen therapy.")
            else:
                insights.append("✅ Oxygen saturation normal.")
        except:
            pass
    
    # Cholesterol Analysis
    if latest_current.get('lab_results', {}).get('cholesterol'):
        try:
            cholesterol = int(latest_current['lab_results']['cholesterol'])
            if cholesterol > 200:
                insights.append("⚠️ High cholesterol levels. Consider statin therapy and dietary modifications.")
            elif cholesterol > 180:
                insights.append("⚠️ Borderline high cholesterol. Monitor and consider lifestyle changes.")
            else:
                insights.append("✅ Cholesterol levels within target range.")
        except:
            pass
    
    # Symptoms Analysis
    if latest_current.get('symptoms'):
        symptoms = latest_current['symptoms'].lower()
        if any(word in symptoms for word in ['chest pain', 'chest discomfort', 'angina']):
            insights.append("🚨 Chest pain reported. Immediate cardiac evaluation recommended.")
        if any(word in symptoms for word in ['shortness of breath', 'dyspnea', 'breathing difficulty']):
            insights.append("⚠️ Respiratory symptoms noted. Consider pulmonary function tests.")
        if any(word in symptoms for word in ['dizziness', 'fainting', 'syncope']):
            insights.append("⚠️ Neurological symptoms present. Consider neurological evaluation.")
    
    # Historical Comparison
    if latest_history and latest_current:
        try:
            # Compare blood pressure trends
            if (latest_history.get('vitals', {}).get('bp') and 
                latest_current.get('vitals', {}).get('bp')):
                hist_bp = latest_history['vitals']['bp']
                curr_bp = latest_current['vitals']['bp']
                if '/' in str(hist_bp) and '/' in str(curr_bp):
                    hist_sys, hist_dia = map(int, str(hist_bp).split('/'))
                    curr_sys, curr_dia = map(int, str(curr_bp).split('/'))
                    if curr_sys > hist_sys + 10 or curr_dia > hist_dia + 5:
                        insights.append("📈 Blood pressure trending upward. Consider medication adjustment.")
                    elif curr_sys < hist_sys - 10 or curr_dia < hist_dia - 5:
                        insights.append("📉 Blood pressure improving. Continue current management.")
        except:
            pass
    
    # Default insight if no specific issues found
    if not insights:
        insights.append("✅ No immediate clinical concerns identified. Continue routine monitoring.")
    
    return jsonify({
        "patient_id": patient_id,
        "insights": insights,
        "timestamp": latest_current.get('timestamp', 'Unknown'),
        "recommendations": [
            "Continue regular monitoring",
            "Follow up as scheduled",
            "Report any new symptoms immediately"
        ]
    })

# ------------------- Video Call & Appointment Routes -------------------
@app.route("/api/request_video_call", methods=["POST"])
def request_video_call():
    """Patient requests a video call with doctor"""
    try:
        data = request.get_json()
        patient_id = data.get('patient_id', '')
        patient_name = data.get('patient_name', 'Unknown Patient')
        reason = data.get('reason', 'General consultation')
        
        if not patient_id:
            return jsonify({"status": "error", "message": "Patient ID required"}), 400
        
        # Load existing video call requests
        video_calls_file = _data_path("video_calls.json")
        try:
            with open(video_calls_file, "r") as f:
                video_calls = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            video_calls = []
        
        # Create new video call request
        new_request = {
            "id": f"VC{len(video_calls) + 1:04d}",
            "patient_id": patient_id,
            "patient_name": patient_name,
            "reason": reason,
            "status": "pending",
            "requested_at": datetime.now().isoformat(),
            "read": False
        }
        
        video_calls.append(new_request)
        
        # Save updated video calls
        with open(video_calls_file, "w") as f:
            json.dump(video_calls, f, indent=2)
        
        return jsonify({
            "status": "success",
            "message": "Video call request sent to doctor",
            "request_id": new_request["id"]
        })
    except Exception as e:
        print(f"Error in request_video_call: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/get_video_call_requests", methods=["GET"])
def get_video_call_requests():
    """Doctor gets all pending video call requests"""
    try:
        video_calls_file = _data_path("video_calls.json")
        try:
            with open(video_calls_file, "r") as f:
                video_calls = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            video_calls = []
        
        # Filter pending requests
        pending_requests = [vc for vc in video_calls if vc.get('status') == 'pending']
        unread_count = len([vc for vc in pending_requests if not vc.get('read', False)])
        
        return jsonify({
            "status": "success",
            "requests": pending_requests,
            "unread_count": unread_count,
            "total_count": len(pending_requests)
        })
    except Exception as e:
        print(f"Error in get_video_call_requests: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/mark_request_read/<request_id>", methods=["POST"])
def mark_request_read(request_id):
    """Mark a video call request as read"""
    try:
        video_calls_file = _data_path("video_calls.json")
        with open(video_calls_file, "r") as f:
            video_calls = json.load(f)
        
        for vc in video_calls:
            if vc.get('id') == request_id:
                vc['read'] = True
                break
        
        with open(video_calls_file, "w") as f:
            json.dump(video_calls, f, indent=2)
        
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/schedule_appointment", methods=["POST"])
def schedule_appointment():
    """Doctor schedules an appointment with a patient"""
    try:
        data = request.get_json()
        patient_id = data.get('patient_id', '')
        patient_name = data.get('patient_name', 'Unknown Patient')
        doctor_name = data.get('doctor_name', 'Dr. Smith')
        appointment_date = data.get('appointment_date', '')
        appointment_time = data.get('appointment_time', '')
        duration = data.get('duration', '30')
        notes = data.get('notes', '')
        
        if not patient_id or not appointment_date or not appointment_time:
            return jsonify({"status": "error", "message": "Missing required fields"}), 400
        
        # Load existing appointments
        appointments_file = _data_path("appointments.json")
        try:
            with open(appointments_file, "r") as f:
                appointments = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            appointments = []
        
        # Create new appointment
        new_appointment = {
            "id": f"APT{len(appointments) + 1:04d}",
            "patient_id": patient_id,
            "patient_name": patient_name,
            "doctor_name": doctor_name,
            "appointment_date": appointment_date,
            "appointment_time": appointment_time,
            "duration": duration,
            "notes": notes,
            "status": "scheduled",
            "created_at": datetime.now().isoformat(),
            "patient_notified": False
        }
        
        appointments.append(new_appointment)
        
        # Save updated appointments
        with open(appointments_file, "w") as f:
            json.dump(appointments, f, indent=2)
        
        return jsonify({
            "status": "success",
            "message": "Appointment scheduled successfully",
            "appointment": new_appointment
        })
    except Exception as e:
        print(f"Error in schedule_appointment: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/get_patient_appointments/<patient_id>", methods=["GET"])
def get_patient_appointments(patient_id):
    """Get all appointments for a specific patient"""
    try:
        appointments_file = _data_path("appointments.json")
        try:
            with open(appointments_file, "r") as f:
                appointments = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            appointments = []
        
        # Filter appointments for this patient
        patient_appointments = [apt for apt in appointments if apt.get('patient_id') == patient_id]
        
        # Sort by date and time
        patient_appointments.sort(key=lambda x: (x.get('appointment_date', ''), x.get('appointment_time', '')), reverse=True)
        
        return jsonify({
            "status": "success",
            "appointments": patient_appointments,
            "total_count": len(patient_appointments)
        })
    except Exception as e:
        print(f"Error in get_patient_appointments: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/get_all_appointments", methods=["GET"])
def get_all_appointments():
    """Doctor gets all appointments"""
    try:
        appointments_file = _data_path("appointments.json")
        try:
            with open(appointments_file, "r") as f:
                appointments = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            appointments = []
        
        # Sort by date and time
        appointments.sort(key=lambda x: (x.get('appointment_date', ''), x.get('appointment_time', '')), reverse=True)
        
        return jsonify({
            "status": "success",
            "appointments": appointments,
            "total_count": len(appointments)
        })
    except Exception as e:
        print(f"Error in get_all_appointments: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/update_appointment_status", methods=["POST"])
def update_appointment_status():
    """Update appointment status (complete, cancel, etc.)"""
    try:
        data = request.get_json()
        appointment_id = data.get('appointment_id', '')
        new_status = data.get('status', '')
        
        if not appointment_id or not new_status:
            return jsonify({"status": "error", "message": "Missing required fields"}), 400
        
        appointments_file = _data_path("appointments.json")
        with open(appointments_file, "r") as f:
            appointments = json.load(f)
        
        for apt in appointments:
            if apt.get('id') == appointment_id:
                apt['status'] = new_status
                apt['updated_at'] = datetime.now().isoformat()
                break
        
        with open(appointments_file, "w") as f:
            json.dump(appointments, f, indent=2)
        
        return jsonify({"status": "success", "message": "Appointment updated"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ------------------- Pharmacy Routes -------------------
@app.route("/pharmacy")
def pharmacy():
    return render_template("pharmacy.html")

@app.route("/api/send_prescription", methods=["POST"])
def send_prescription():
    """Doctor sends prescription to pharmacy"""
    try:
        data = request.get_json()
        patient_id = data.get('patient_id', '')
        patient_name = data.get('patient_name', 'Unknown Patient')
        doctor_name = data.get('doctor_name', 'Dr. Smith')
        medicines = data.get('medicines', [])
        notes = data.get('notes', '')
        priority = data.get('priority', 'normal')
        
        if not patient_id or not medicines:
            return jsonify({"status": "error", "message": "Patient ID and medicines required"}), 400
        
        # Load existing prescriptions
        prescriptions_file = _data_path("prescriptions.json")
        try:
            with open(prescriptions_file, "r") as f:
                prescriptions = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            prescriptions = []
        
        # Create new prescription
        new_prescription = {
            "id": f"RX{len(prescriptions) + 1:04d}",
            "patient_id": patient_id,
            "patient_name": patient_name,
            "doctor_name": doctor_name,
            "medicines": medicines,
            "notes": notes,
            "priority": priority,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "prepared_at": None,
            "delivered_at": None,
            "pharmacist_name": None
        }
        
        prescriptions.append(new_prescription)
        
        # Save updated prescriptions
        with open(prescriptions_file, "w") as f:
            json.dump(prescriptions, f, indent=2)
        
        return jsonify({
            "status": "success",
            "message": "Prescription sent to pharmacy",
            "prescription_id": new_prescription["id"]
        })
    except Exception as e:
        print(f"Error in send_prescription: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/get_prescriptions", methods=["GET"])
def get_prescriptions():
    """Pharmacy gets all prescriptions"""
    try:
        status_filter = request.args.get('status', None)
        
        prescriptions_file = _data_path("prescriptions.json")
        try:
            with open(prescriptions_file, "r") as f:
                prescriptions = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            prescriptions = []
        
        # Filter by status if provided
        if status_filter:
            prescriptions = [p for p in prescriptions if p.get('status') == status_filter]
        
        # Sort by priority and date
        priority_order = {'urgent': 0, 'high': 1, 'normal': 2, 'low': 3}
        prescriptions.sort(key=lambda x: (priority_order.get(x.get('priority', 'normal'), 2), x.get('created_at', '')), reverse=True)
        
        # Count by status
        pending_count = len([p for p in prescriptions if p.get('status') == 'pending'])
        preparing_count = len([p for p in prescriptions if p.get('status') == 'preparing'])
        ready_count = len([p for p in prescriptions if p.get('status') == 'ready'])
        
        return jsonify({
            "status": "success",
            "prescriptions": prescriptions,
            "total_count": len(prescriptions),
            "pending_count": pending_count,
            "preparing_count": preparing_count,
            "ready_count": ready_count
        })
    except Exception as e:
        print(f"Error in get_prescriptions: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/update_prescription_status", methods=["POST"])
def update_prescription_status():
    """Pharmacy updates prescription status"""
    try:
        data = request.get_json()
        prescription_id = data.get('prescription_id', '')
        new_status = data.get('status', '')
        pharmacist_name = data.get('pharmacist_name', 'Pharmacist')
        
        if not prescription_id or not new_status:
            return jsonify({"status": "error", "message": "Missing required fields"}), 400
        
        prescriptions_file = _data_path("prescriptions.json")
        with open(prescriptions_file, "r") as f:
            prescriptions = json.load(f)
        
        for prescription in prescriptions:
            if prescription.get('id') == prescription_id:
                prescription['status'] = new_status
                prescription['pharmacist_name'] = pharmacist_name
                prescription['updated_at'] = datetime.now().isoformat()
                
                if new_status == 'preparing':
                    prescription['preparing_at'] = datetime.now().isoformat()
                elif new_status == 'ready':
                    prescription['prepared_at'] = datetime.now().isoformat()
                elif new_status == 'delivered':
                    prescription['delivered_at'] = datetime.now().isoformat()
                
                break
        
        with open(prescriptions_file, "w") as f:
            json.dump(prescriptions, f, indent=2)
        
        return jsonify({"status": "success", "message": "Prescription status updated"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/get_patient_prescriptions/<patient_id>", methods=["GET"])
def get_patient_prescriptions(patient_id):
    """Get all prescriptions for a specific patient"""
    try:
        prescriptions_file = _data_path("prescriptions.json")
        try:
            with open(prescriptions_file, "r") as f:
                prescriptions = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            prescriptions = []
        
        # Filter prescriptions for this patient
        patient_prescriptions = [p for p in prescriptions if p.get('patient_id') == patient_id]
        
        # Sort by date
        patient_prescriptions.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        return jsonify({
            "status": "success",
            "prescriptions": patient_prescriptions,
            "total_count": len(patient_prescriptions)
        })
    except Exception as e:
        print(f"Error in get_patient_prescriptions: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/send_pharmacy_message", methods=["POST"])
def send_pharmacy_message():
    """Doctor sends message to pharmacy"""
    try:
        data = request.get_json()
        from_name = data.get('from_name', 'Doctor')
        message = data.get('message', '')
        prescription_id = data.get('prescription_id', None)
        
        if not message:
            return jsonify({"status": "error", "message": "Message required"}), 400
        
        # Load existing messages
        messages_file = _data_path("pharmacy_messages.json")
        try:
            with open(messages_file, "r") as f:
                messages = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            messages = []
        
        # Create new message
        new_message = {
            "id": f"MSG{len(messages) + 1:04d}",
            "from_name": from_name,
            "message": message,
            "prescription_id": prescription_id,
            "created_at": datetime.now().isoformat(),
            "read": False
        }
        
        messages.append(new_message)
        
        # Save updated messages
        with open(messages_file, "w") as f:
            json.dump(messages, f, indent=2)
        
        return jsonify({
            "status": "success",
            "message": "Message sent to pharmacy",
            "message_id": new_message["id"]
        })
    except Exception as e:
        print(f"Error in send_pharmacy_message: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/get_pharmacy_messages", methods=["GET"])
def get_pharmacy_messages():
    """Pharmacy gets all messages"""
    try:
        messages_file = _data_path("pharmacy_messages.json")
        try:
            with open(messages_file, "r") as f:
                messages = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            messages = []
        
        # Sort by date
        messages.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        unread_count = len([m for m in messages if not m.get('read', False)])
        
        return jsonify({
            "status": "success",
            "messages": messages,
            "total_count": len(messages),
            "unread_count": unread_count
        })
    except Exception as e:
        print(f"Error in get_pharmacy_messages: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/mark_message_read/<message_id>", methods=["POST"])
def mark_message_read(message_id):
    """Mark a pharmacy message as read"""
    try:
        messages_file = _data_path("pharmacy_messages.json")
        with open(messages_file, "r") as f:
            messages = json.load(f)
        
        for msg in messages:
            if msg.get('id') == message_id:
                msg['read'] = True
                break
        
        with open(messages_file, "w") as f:
            json.dump(messages, f, indent=2)
        
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ------------------- AI Chat for Patients -------------------
# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    # Use Gemini 2.0 Flash - stable and fast model
    patient_chat_model = genai.GenerativeModel('models/gemini-2.0-flash')
else:
    patient_chat_model = None

@app.route("/api/patient-chat", methods=["POST"])
def patient_chat():
    """Patient AI chat using Gemini API"""
    try:
        data = request.json
        message = data.get("message", "")
        
        if not message:
            return jsonify({"error": "No message provided"}), 400
        
        # Check if Gemini API is configured
        if not patient_chat_model:
            return jsonify({
                "error": "AI service not configured. Please add GEMINI_API_KEY to your .env file.",
                "response": "I'm sorry, but the AI service is not currently configured. Please contact support or add your Gemini API key to enable this feature."
            }), 503
        
        # Create a general AI assistant prompt (like ChatGPT)
        system_prompt = """You are a helpful, friendly AI assistant for MedCore AI platform. 
        You can chat about anything - health topics, general questions, daily life, technology, etc.
        
        GUIDELINES:
        - Be helpful, friendly, and conversational
        - Answer any questions the user has
        - For health questions: provide helpful information but remind users to consult doctors for medical advice
        - For general questions: provide accurate, helpful information
        - Be empathetic and supportive
        - Keep responses clear and easy to understand
        - You can discuss any topic, not just health
        
        Remember: You're a general AI assistant that can help with anything!"""
        
        # Send message directly to Gemini (no need to combine prompts)
        full_prompt = f"{system_prompt}\n\nUser: {message}\n\nAssistant:"
        
        # Generate response using Gemini
        response = patient_chat_model.generate_content(full_prompt)
        
        # Extract text from response
        ai_response = response.text if hasattr(response, 'text') else str(response)
        
        return jsonify({
            "response": ai_response,
            "status": "success"
        })
        
    except Exception as e:
        print(f"Error in patient chat: {str(e)}")
        return jsonify({
            "error": str(e),
            "response": "I'm sorry, I encountered an error. Please try again or contact support if the problem persists."
        }), 500

# ------------------- Admin Portal Routes -------------------
@app.route("/admin")
def admin():
    return render_template("admin.html")

@app.route("/api/admin/users", methods=["GET"])
def get_all_users():
    """Get all registered users (patients, doctors, pharmacists)"""
    try:
        users_file = _data_path("users.json")
        try:
            with open(users_file, "r") as f:
                users = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            users = []
        
        # Filter by role if specified
        role_filter = request.args.get('role', None)
        if role_filter:
            users = [u for u in users if u.get('role') == role_filter]
        
        # Count by role
        patients_count = len([u for u in users if u.get('role') == 'patient'])
        doctors_count = len([u for u in users if u.get('role') == 'doctor'])
        pharmacists_count = len([u for u in users if u.get('role') == 'pharmacist'])
        active_count = len([u for u in users if u.get('status') == 'active'])
        
        return jsonify({
            "status": "success",
            "users": users,
            "total_count": len(users),
            "patients_count": patients_count,
            "doctors_count": doctors_count,
            "pharmacists_count": pharmacists_count,
            "active_count": active_count
        })
    except Exception as e:
        print(f"Error in get_all_users: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/admin/user/<user_id>/status", methods=["POST"])
def update_user_status(user_id):
    """Activate or deactivate a user account"""
    try:
        data = request.get_json()
        new_status = data.get('status', 'active')
        
        users_file = _data_path("users.json")
        with open(users_file, "r") as f:
            users = json.load(f)
        
        for user in users:
            if user.get('id') == user_id or user.get('user_id') == user_id:
                user['status'] = new_status
                user['updated_at'] = datetime.now().isoformat()
                break
        
        with open(users_file, "w") as f:
            json.dump(users, f, indent=2)
        
        return jsonify({"status": "success", "message": f"User status updated to {new_status}"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/admin/user/<user_id>", methods=["DELETE"])
def delete_user(user_id):
    """Remove a user account"""
    try:
        users_file = _data_path("users.json")
        with open(users_file, "r") as f:
            users = json.load(f)
        
        users = [u for u in users if u.get('id') != user_id and u.get('user_id') != user_id]
        
        with open(users_file, "w") as f:
            json.dump(users, f, indent=2)
        
        return jsonify({"status": "success", "message": "User removed successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/admin/appointments", methods=["GET"])
def admin_get_appointments():
    """Get all appointments with filtering"""
    try:
        appointments_file = _data_path("appointments.json")
        try:
            with open(appointments_file, "r") as f:
                appointments = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            appointments = []
        
        # Filter by status if specified
        status_filter = request.args.get('status', None)
        if status_filter:
            appointments = [a for a in appointments if a.get('status') == status_filter]
        
        # Count by status
        scheduled_count = len([a for a in appointments if a.get('status') == 'scheduled'])
        completed_count = len([a for a in appointments if a.get('status') == 'completed'])
        cancelled_count = len([a for a in appointments if a.get('status') == 'cancelled'])
        
        # Get today's appointments
        today = datetime.now().date().isoformat()
        today_appointments = [a for a in appointments if a.get('appointment_date') == today]
        
        return jsonify({
            "status": "success",
            "appointments": appointments,
            "total_count": len(appointments),
            "scheduled_count": scheduled_count,
            "completed_count": completed_count,
            "cancelled_count": cancelled_count,
            "today_count": len(today_appointments)
        })
    except Exception as e:
        print(f"Error in admin_get_appointments: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/admin/appointment/<appointment_id>/reassign", methods=["POST"])
def reassign_appointment(appointment_id):
    """Reassign appointment to different doctor"""
    try:
        data = request.get_json()
        new_doctor = data.get('doctor_name', '')
        
        if not new_doctor:
            return jsonify({"status": "error", "message": "Doctor name required"}), 400
        
        appointments_file = _data_path("appointments.json")
        with open(appointments_file, "r") as f:
            appointments = json.load(f)
        
        for apt in appointments:
            if apt.get('id') == appointment_id:
                apt['doctor_name'] = new_doctor
                apt['reassigned_at'] = datetime.now().isoformat()
                apt['reassigned'] = True
                break
        
        with open(appointments_file, "w") as f:
            json.dump(appointments, f, indent=2)
        
        return jsonify({"status": "success", "message": f"Appointment reassigned to {new_doctor}"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/admin/prescriptions/stats", methods=["GET"])
def get_prescription_stats():
    """Get pharmacy/prescription statistics"""
    try:
        prescriptions_file = _data_path("prescriptions.json")
        try:
            with open(prescriptions_file, "r") as f:
                prescriptions = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            prescriptions = []
        
        # Count by status
        pending_count = len([p for p in prescriptions if p.get('status') == 'pending'])
        preparing_count = len([p for p in prescriptions if p.get('status') == 'preparing'])
        ready_count = len([p for p in prescriptions if p.get('status') == 'ready'])
        delivered_count = len([p for p in prescriptions if p.get('status') == 'delivered'])
        
        # Get today's prescriptions
        today = datetime.now().date().isoformat()
        today_prescriptions = [p for p in prescriptions if p.get('created_at', '').startswith(today)]
        
        return jsonify({
            "status": "success",
            "total_count": len(prescriptions),
            "pending_count": pending_count,
            "preparing_count": preparing_count,
            "ready_count": ready_count,
            "delivered_count": delivered_count,
            "today_count": len(today_prescriptions),
            "prescriptions": prescriptions
        })
    except Exception as e:
        print(f"Error in get_prescription_stats: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/admin/analytics", methods=["GET"])
def get_admin_analytics():
    """Get comprehensive analytics for admin dashboard"""
    try:
        # Load all data files
        users_file = _data_path("users.json")
        appointments_file = _data_path("appointments.json")
        prescriptions_file = _data_path("prescriptions.json")
        
        # Users data
        try:
            with open(users_file, "r") as f:
                users = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            users = []
        
        # Appointments data
        try:
            with open(appointments_file, "r") as f:
                appointments = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            appointments = []
        
        # Prescriptions data
        try:
            with open(prescriptions_file, "r") as f:
                prescriptions = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            prescriptions = []
        
        # Calculate analytics
        today = datetime.now().date().isoformat()
        
        analytics = {
            "users": {
                "total": len(users),
                "patients": len([u for u in users if u.get('role') == 'patient']),
                "doctors": len([u for u in users if u.get('role') == 'doctor']),
                "pharmacists": len([u for u in users if u.get('role') == 'pharmacist']),
                "active": len([u for u in users if u.get('status') == 'active']),
                "inactive": len([u for u in users if u.get('status') == 'inactive'])
            },
            "appointments": {
                "total": len(appointments),
                "today": len([a for a in appointments if a.get('appointment_date') == today]),
                "scheduled": len([a for a in appointments if a.get('status') == 'scheduled']),
                "completed": len([a for a in appointments if a.get('status') == 'completed']),
                "cancelled": len([a for a in appointments if a.get('status') == 'cancelled'])
            },
            "prescriptions": {
                "total": len(prescriptions),
                "today": len([p for p in prescriptions if p.get('created_at', '').startswith(today)]),
                "pending": len([p for p in prescriptions if p.get('status') == 'pending']),
                "preparing": len([p for p in prescriptions if p.get('status') == 'preparing']),
                "ready": len([p for p in prescriptions if p.get('status') == 'ready']),
                "delivered": len([p for p in prescriptions if p.get('status') == 'delivered'])
            }
        }
        
        return jsonify({
            "status": "success",
            "analytics": analytics
        })
    except Exception as e:
        print(f"Error in get_admin_analytics: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/admin/emergency-alerts", methods=["GET"])
def get_emergency_alerts():
    """Get all emergency alerts"""
    try:
        alerts_file = _data_path("emergency_alerts.json")
        try:
            with open(alerts_file, "r") as f:
                alerts = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            alerts = []
        
        # Filter by status if specified
        status_filter = request.args.get('status', None)
        if status_filter:
            alerts = [a for a in alerts if a.get('status') == status_filter]
        
        # Sort by severity and date
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        alerts.sort(key=lambda x: (severity_order.get(x.get('severity', 'low'), 3), x.get('created_at', '')), reverse=True)
        
        # Count by status
        pending_count = len([a for a in alerts if a.get('status') == 'pending'])
        forwarded_count = len([a for a in alerts if a.get('forwarded_to_hospital')])
        
        return jsonify({
            "status": "success",
            "alerts": alerts,
            "total_count": len(alerts),
            "pending_count": pending_count,
            "forwarded_count": forwarded_count
        })
    except Exception as e:
        print(f"Error in get_emergency_alerts: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/admin/emergency-alert/<alert_id>/forward", methods=["POST"])
def forward_emergency_alert(alert_id):
    """Forward emergency alert to hospital"""
    try:
        data = request.get_json()
        hospital_name = data.get('hospital_name', '')
        
        if not hospital_name:
            return jsonify({"status": "error", "message": "Hospital name required"}), 400
        
        alerts_file = _data_path("emergency_alerts.json")
        with open(alerts_file, "r") as f:
            alerts = json.load(f)
        
        for alert in alerts:
            if alert.get('id') == alert_id:
                alert['forwarded_to_hospital'] = True
                alert['hospital_name'] = hospital_name
                alert['forwarded_at'] = datetime.now().isoformat()
                alert['status'] = 'forwarded'
                break
        
        with open(alerts_file, "w") as f:
            json.dump(alerts, f, indent=2)
        
        return jsonify({"status": "success", "message": f"Alert forwarded to {hospital_name}"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/admin/emergency-alert/<alert_id>/resolve", methods=["POST"])
def resolve_emergency_alert(alert_id):
    """Mark emergency alert as resolved"""
    try:
        alerts_file = _data_path("emergency_alerts.json")
        with open(alerts_file, "r") as f:
            alerts = json.load(f)
        
        for alert in alerts:
            if alert.get('id') == alert_id:
                alert['status'] = 'resolved'
                alert['resolved_at'] = datetime.now().isoformat()
                break
        
        with open(alerts_file, "w") as f:
            json.dump(alerts, f, indent=2)
        
        return jsonify({"status": "success", "message": "Alert marked as resolved"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/admin/patient-analytics/<patient_id>", methods=["GET"])
def get_patient_analytics(patient_id):
    """Get detailed analytics for a specific patient"""
    try:
        # Get patient data
        patient_data = get_patient_by_id(patient_id)
        
        # Get appointments
        appointments_file = _data_path("appointments.json")
        try:
            with open(appointments_file, "r") as f:
                appointments = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            appointments = []
        
        patient_appointments = [a for a in appointments if a.get('patient_id') == patient_id]
        
        # Get prescriptions
        prescriptions_file = _data_path("prescriptions.json")
        try:
            with open(prescriptions_file, "r") as f:
                prescriptions = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            prescriptions = []
        
        patient_prescriptions = [p for p in prescriptions if p.get('patient_id') == patient_id]
        
        analytics = {
            "patient_id": patient_id,
            "patient_data": patient_data,
            "appointments": {
                "total": len(patient_appointments),
                "completed": len([a for a in patient_appointments if a.get('status') == 'completed']),
                "scheduled": len([a for a in patient_appointments if a.get('status') == 'scheduled']),
                "cancelled": len([a for a in patient_appointments if a.get('status') == 'cancelled'])
            },
            "prescriptions": {
                "total": len(patient_prescriptions),
                "delivered": len([p for p in patient_prescriptions if p.get('status') == 'delivered']),
                "pending": len([p for p in patient_prescriptions if p.get('status') == 'pending'])
            }
        }
        
        return jsonify({
            "status": "success",
            "analytics": analytics
        })
    except Exception as e:
        print(f"Error in get_patient_analytics: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)