from flask import Flask, request, jsonify, render_template, redirect, url_for
import json
import os
import io
import base64
import pandas as pd
import matplotlib.pyplot as plt

app = Flask(__name__, template_folder="templates", static_folder="frontend/static")

# Resolve data file paths relative to this script's directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def _data_path(filename):
    return os.path.join(BASE_DIR, filename)

def _normalize_patient_id(value):
    try:
        return str(value).strip().upper()
    except Exception:
        return ""

# Ensure JSON files exist
for file in ["patients.json", "patients_history.json"]:
    path = _data_path(file)
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump([], f, indent=4)

@app.route("/")
def intro():
    return render_template("intro.html")

@app.route("/patient")
def patient():
    return render_template("index.html")

@app.route("/doctor")
def doctor():
    return render_template("doctor.html")

@app.route("/submit_patient", methods=["POST"])
def submit_patient():
    data = request.get_json()
    if not data:
        return jsonify({"status":"error","message":"No data received"}), 400

    with open(_data_path("patients.json"), "r") as f:
        patients = json.load(f)

    patients.append(data)

    with open(_data_path("patients.json"), "w") as f:
        json.dump(patients, f, indent=4)

    return jsonify({"status": "success", "message": "Patient data saved!"})

# ------------------- Doctor APIs (to support doctor.html on this server) -------------------
@app.route("/get_patient_data/<patient_id>")
def get_patient_data(patient_id):
    normalized_query = _normalize_patient_id(patient_id)
    with open(_data_path("patients.json"), "r") as f:
        all_data = json.load(f)
        if isinstance(all_data, dict):
            all_data = [all_data]
    patient_data = [entry for entry in all_data if _normalize_patient_id(entry.get("patient_id")) == normalized_query]
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
        return jsonify({"error": "Patient not found"}), 404

    df_current = pd.DataFrame(current_data)
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

if __name__ == "__main__":
    app.run(debug=True)