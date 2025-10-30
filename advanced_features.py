"""
Advanced Features for MedCore AI Platform
Add these routes to your Flask application for enhanced functionality
"""
from flask import jsonify, request, send_file
from models import Patient, Vitals, LabResult, ChatSession, ChatMessage
from database import db, get_patient_by_id, get_all_patients
from datetime import datetime, timedelta
import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch

# ==================== FEATURE 1: REAL-TIME DASHBOARD ====================

def get_patient_dashboard():
    """Real-time dashboard with all patients and their health status"""
    patients = get_all_patients()
    
    dashboard = {
        "total_patients": len(patients),
        "critical": [],
        "warning": [],
        "stable": [],
        "statistics": {
            "avg_age": 0,
            "high_bp_count": 0,
            "low_spo2_count": 0,
            "high_hr_count": 0,
            "male_count": 0,
            "female_count": 0
        }
    }
    
    ages = []
    for patient in patients:
        vitals = patient.get('vitals', {})
        
        # Age statistics
        if patient.get('age'):
            ages.append(int(patient['age']))
        
        # Gender statistics
        gender = patient.get('gender', '').lower()
        if 'male' in gender and 'female' not in gender:
            dashboard['statistics']['male_count'] += 1
        elif 'female' in gender:
            dashboard['statistics']['female_count'] += 1
        
        # Vitals statistics
        bp = vitals.get('bp', '')
        hr = vitals.get('hr', 0)
        spo2 = vitals.get('spo2', 100)
        
        try:
            if bp and '/' in str(bp):
                systolic = int(str(bp).split('/')[0])
                if systolic >= 140:
                    dashboard['statistics']['high_bp_count'] += 1
        except:
            pass
        
        try:
            if hr and int(hr) > 100:
                dashboard['statistics']['high_hr_count'] += 1
        except:
            pass
        
        try:
            if spo2 and int(spo2) < 95:
                dashboard['statistics']['low_spo2_count'] += 1
        except:
            pass
        
        # Classify patient status
        status = classify_patient_status(vitals)
        patient['status'] = status
        patient['status_color'] = get_status_color(status)
        
        if status == 'critical':
            dashboard['critical'].append(patient)
        elif status == 'warning':
            dashboard['warning'].append(patient)
        else:
            dashboard['stable'].append(patient)
    
    # Calculate average age
    if ages:
        dashboard['statistics']['avg_age'] = round(sum(ages) / len(ages), 1)
    
    return dashboard

def classify_patient_status(vitals):
    """Classify patient as critical, warning, or stable based on vitals"""
    bp = vitals.get('bp', '')
    hr = vitals.get('hr', 0)
    spo2 = vitals.get('spo2', 100)
    
    try:
        # Check blood pressure
        if bp and '/' in str(bp):
            systolic = int(str(bp).split('/')[0])
            diastolic = int(str(bp).split('/')[1])
            
            # Critical BP
            if systolic >= 180 or systolic < 90 or diastolic >= 120 or diastolic < 60:
                return 'critical'
            # Warning BP
            if systolic >= 140 or systolic < 100 or diastolic >= 90 or diastolic < 70:
                return 'warning'
        
        # Check heart rate
        hr_val = int(hr) if hr else 0
        if hr_val >= 120 or hr_val < 50:
            return 'critical'
        if hr_val >= 100 or hr_val < 60:
            return 'warning'
        
        # Check SpO2
        spo2_val = int(spo2) if spo2 else 100
        if spo2_val < 90:
            return 'critical'
        if spo2_val < 95:
            return 'warning'
            
    except Exception as e:
        print(f"Error classifying patient status: {e}")
        return 'stable'
    
    return 'stable'

def get_status_color(status):
    """Get color code for patient status"""
    colors_map = {
        'critical': '#dc3545',  # Red
        'warning': '#ffc107',   # Yellow
        'stable': '#28a745'     # Green
    }
    return colors_map.get(status, '#6c757d')


# ==================== FEATURE 2: PATIENT TRENDS ====================

def get_patient_trends(patient_id):
    """Get historical trends for patient vitals and labs"""
    patient = Patient.query.filter_by(patient_id=patient_id.upper()).first()
    if not patient:
        return None
    
    # Get all historical vitals (last 30 days or all records)
    cutoff_date = datetime.now() - timedelta(days=30)
    vitals_history = Vitals.query.filter(
        Vitals.patient_db_id == patient.id,
        Vitals.timestamp >= cutoff_date
    ).order_by(Vitals.timestamp.asc()).all()
    
    # Get lab results history
    labs_history = LabResult.query.filter(
        LabResult.patient_db_id == patient.id,
        LabResult.timestamp >= cutoff_date
    ).order_by(LabResult.timestamp.asc()).all()
    
    trends = {
        "patient_id": patient_id,
        "patient_name": patient.name,
        "vitals": {
            "dates": [],
            "blood_pressure": {"systolic": [], "diastolic": []},
            "heart_rate": [],
            "spo2": [],
            "temperature": []
        },
        "labs": {
            "dates": [],
            "cholesterol": [],
            "troponin": [],
            "blood_sugar": []
        }
    }
    
    # Process vitals
    for vital in vitals_history:
        date_str = vital.timestamp.strftime("%Y-%m-%d %H:%M")
        trends["vitals"]["dates"].append(date_str)
        
        if vital.bp:
            try:
                sys, dia = vital.bp.split('/')
                trends["vitals"]["blood_pressure"]["systolic"].append(int(sys))
                trends["vitals"]["blood_pressure"]["diastolic"].append(int(dia))
            except:
                trends["vitals"]["blood_pressure"]["systolic"].append(None)
                trends["vitals"]["blood_pressure"]["diastolic"].append(None)
        
        trends["vitals"]["heart_rate"].append(vital.hr if vital.hr else None)
        trends["vitals"]["spo2"].append(vital.spo2 if vital.spo2 else None)
        trends["vitals"]["temperature"].append(vital.temperature if vital.temperature else None)
    
    # Process labs
    for lab in labs_history:
        date_str = lab.timestamp.strftime("%Y-%m-%d")
        trends["labs"]["dates"].append(date_str)
        
        try:
            trends["labs"]["cholesterol"].append(float(lab.cholesterol) if lab.cholesterol else None)
        except:
            trends["labs"]["cholesterol"].append(None)
        
        try:
            trends["labs"]["troponin"].append(float(lab.troponin) if lab.troponin else None)
        except:
            trends["labs"]["troponin"].append(None)
        
        try:
            trends["labs"]["blood_sugar"].append(float(lab.blood_sugar) if lab.blood_sugar else None)
        except:
            trends["labs"]["blood_sugar"].append(None)
    
    return trends


# ==================== FEATURE 3: ADVANCED SEARCH ====================

def advanced_patient_search(query, filters=None):
    """Advanced search for patients with multiple filters"""
    filters = filters or {}
    
    # Base query
    query_obj = Patient.query
    
    # Text search in name, patient_id, symptoms
    if query:
        search_term = f"%{query}%"
        query_obj = query_obj.filter(
            db.or_(
                Patient.name.like(search_term),
                Patient.patient_id.like(search_term),
                Patient.symptoms.like(search_term)
            )
        )
    
    # Age filter
    if filters.get('min_age'):
        query_obj = query_obj.filter(Patient.age >= int(filters['min_age']))
    if filters.get('max_age'):
        query_obj = query_obj.filter(Patient.age <= int(filters['max_age']))
    
    # Gender filter
    if filters.get('gender'):
        query_obj = query_obj.filter(Patient.gender.like(f"%{filters['gender']}%"))
    
    # Date range filter
    if filters.get('start_date'):
        start_date = datetime.fromisoformat(filters['start_date'])
        query_obj = query_obj.filter(Patient.timestamp >= start_date)
    if filters.get('end_date'):
        end_date = datetime.fromisoformat(filters['end_date'])
        query_obj = query_obj.filter(Patient.timestamp <= end_date)
    
    patients = query_obj.all()
    
    # Apply vitals filters (requires join)
    if filters.get('status'):
        filtered_patients = []
        for patient in patients:
            patient_dict = patient.to_dict()
            status = classify_patient_status(patient_dict.get('vitals', {}))
            if status == filters['status']:
                patient_dict['status'] = status
                filtered_patients.append(patient_dict)
        return filtered_patients
    
    return [p.to_dict() for p in patients]


# ==================== FEATURE 4: PATIENT ALERTS ====================

def get_patient_alerts():
    """Get all critical alerts for patients"""
    alerts = []
    patients = get_all_patients()
    
    for patient in patients:
        vitals = patient.get('vitals', {})
        labs = patient.get('lab_results', {})
        patient_alerts = []
        
        # Check vitals
        bp = vitals.get('bp', '')
        hr = vitals.get('hr', 0)
        spo2 = vitals.get('spo2', 100)
        
        try:
            if bp and '/' in str(bp):
                systolic = int(str(bp).split('/')[0])
                if systolic >= 180:
                    patient_alerts.append({
                        "type": "critical",
                        "category": "Blood Pressure",
                        "message": f"Critical high BP: {bp} mmHg",
                        "recommendation": "Immediate medical attention required"
                    })
                elif systolic >= 140:
                    patient_alerts.append({
                        "type": "warning",
                        "category": "Blood Pressure",
                        "message": f"Elevated BP: {bp} mmHg",
                        "recommendation": "Monitor closely and consider medication adjustment"
                    })
        except:
            pass
        
        try:
            hr_val = int(hr) if hr else 0
            if hr_val >= 120:
                patient_alerts.append({
                    "type": "critical",
                    "category": "Heart Rate",
                    "message": f"Critical tachycardia: {hr} bpm",
                    "recommendation": "ECG and cardiac evaluation needed"
                })
            elif hr_val >= 100:
                patient_alerts.append({
                    "type": "warning",
                    "category": "Heart Rate",
                    "message": f"Elevated heart rate: {hr} bpm",
                    "recommendation": "Monitor and assess for underlying causes"
                })
        except:
            pass
        
        try:
            spo2_val = int(spo2) if spo2 else 100
            if spo2_val < 90:
                patient_alerts.append({
                    "type": "critical",
                    "category": "Oxygen Saturation",
                    "message": f"Critical low SpO2: {spo2}%",
                    "recommendation": "Oxygen therapy required immediately"
                })
            elif spo2_val < 95:
                patient_alerts.append({
                    "type": "warning",
                    "category": "Oxygen Saturation",
                    "message": f"Low SpO2: {spo2}%",
                    "recommendation": "Respiratory assessment needed"
                })
        except:
            pass
        
        # Check labs
        try:
            troponin = labs.get('troponin')
            if troponin:
                troponin_val = float(troponin)
                if troponin_val > 0.04:
                    patient_alerts.append({
                        "type": "critical",
                        "category": "Cardiac Markers",
                        "message": f"Elevated troponin: {troponin} ng/mL",
                        "recommendation": "Rule out acute coronary syndrome"
                    })
        except:
            pass
        
        if patient_alerts:
            alerts.append({
                "patient_id": patient.get('patient_id'),
                "patient_name": patient.get('name'),
                "alerts": patient_alerts,
                "alert_count": len(patient_alerts),
                "highest_severity": "critical" if any(a['type'] == 'critical' for a in patient_alerts) else "warning"
            })
    
    # Sort by severity (critical first)
    alerts.sort(key=lambda x: (x['highest_severity'] != 'critical', x['alert_count']), reverse=False)
    
    return alerts


# ==================== FEATURE 5: PDF MEDICAL REPORT ====================

def generate_patient_report_pdf(patient_id):
    """Generate comprehensive PDF medical report for patient"""
    patient_data = get_patient_by_id(patient_id)
    if not patient_data:
        return None
    
    # Create PDF buffer
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2c5aa0'),
        spaceAfter=30
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#2c5aa0'),
        spaceAfter=12
    )
    
    # Title
    elements.append(Paragraph("MedCore AI - Medical Report", title_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Patient Information
    elements.append(Paragraph("Patient Information", heading_style))
    patient_info_data = [
        ['Patient ID:', patient_data.get('patient_id', 'N/A')],
        ['Name:', patient_data.get('name', 'N/A')],
        ['Age:', str(patient_data.get('age', 'N/A'))],
        ['Gender:', patient_data.get('gender', 'N/A')],
        ['Report Date:', datetime.now().strftime('%Y-%m-%d %H:%M')]
    ]
    
    patient_table = Table(patient_info_data, colWidths=[2*inch, 4*inch])
    patient_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e3f2fd')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey)
    ]))
    elements.append(patient_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Chief Complaint
    elements.append(Paragraph("Chief Complaint & Symptoms", heading_style))
    symptoms_text = patient_data.get('symptoms', 'No symptoms reported')
    elements.append(Paragraph(symptoms_text, styles['Normal']))
    elements.append(Spacer(1, 0.3*inch))
    
    # Vital Signs
    vitals = patient_data.get('vitals', {})
    elements.append(Paragraph("Vital Signs", heading_style))
    vitals_data = [
        ['Parameter', 'Value', 'Status'],
        ['Blood Pressure', vitals.get('bp', 'Not recorded'), classify_vital_status('bp', vitals.get('bp'))],
        ['Heart Rate', f"{vitals.get('hr', 'N/A')} bpm", classify_vital_status('hr', vitals.get('hr'))],
        ['SpO2', f"{vitals.get('spo2', 'N/A')}%", classify_vital_status('spo2', vitals.get('spo2'))],
    ]
    
    vitals_table = Table(vitals_data, colWidths=[2*inch, 2*inch, 2*inch])
    vitals_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey)
    ]))
    elements.append(vitals_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Laboratory Results
    labs = patient_data.get('lab_results', {})
    if labs and any(labs.values()):
        elements.append(Paragraph("Laboratory Results", heading_style))
        labs_data = [['Test', 'Result']]
        if labs.get('ecg'):
            labs_data.append(['ECG', labs.get('ecg')])
        if labs.get('troponin'):
            labs_data.append(['Troponin', f"{labs.get('troponin')} ng/mL"])
        if labs.get('cholesterol'):
            labs_data.append(['Cholesterol', f"{labs.get('cholesterol')} mg/dL"])
        
        labs_table = Table(labs_data, colWidths=[3*inch, 3*inch])
        labs_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        elements.append(labs_table)
        elements.append(Spacer(1, 0.3*inch))
    
    # Footer
    elements.append(Spacer(1, 0.5*inch))
    footer_text = "This report is generated by MedCore AI - Enterprise Medical Intelligence Platform"
    elements.append(Paragraph(footer_text, styles['Italic']))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer

def classify_vital_status(vital_type, value):
    """Classify vital sign as Normal, Warning, or Critical"""
    if not value:
        return 'Not recorded'
    
    try:
        if vital_type == 'bp':
            systolic = int(str(value).split('/')[0])
            if systolic >= 180:
                return 'CRITICAL'
            elif systolic >= 140:
                return 'WARNING'
            else:
                return 'Normal'
        
        elif vital_type == 'hr':
            hr_val = int(value)
            if hr_val >= 120 or hr_val < 50:
                return 'CRITICAL'
            elif hr_val >= 100 or hr_val < 60:
                return 'WARNING'
            else:
                return 'Normal'
        
        elif vital_type == 'spo2':
            spo2_val = int(value)
            if spo2_val < 90:
                return 'CRITICAL'
            elif spo2_val < 95:
                return 'WARNING'
            else:
                return 'Normal'
    except:
        return 'Unknown'
    
    return 'Normal'


# ==================== FEATURE 6: APPOINTMENT SYSTEM ====================

from models import db

# You'll need to add this model to models.py
"""
class Appointment(db.Model):
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_db_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    appointment_date = db.Column(db.DateTime, nullable=False)
    doctor_name = db.Column(db.String(100))
    appointment_type = db.Column(db.String(50))  # consultation, follow-up, emergency
    status = db.Column(db.String(20), default='scheduled')  # scheduled, completed, cancelled
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
"""

def get_upcoming_appointments(days=7):
    """Get upcoming appointments for next N days"""
    # This requires the Appointment model
    # Return mock data for now
    return {
        "upcoming": [],
        "message": "Appointment system ready - add Appointment model to activate"
    }


# ==================== FEATURE 7: MEDICATION TRACKER ====================

def get_patient_medications(patient_id):
    """Track patient medications (from history)"""
    patient = Patient.query.filter_by(patient_id=patient_id.upper()).first()
    if not patient:
        return None
    
    from database import get_patient_history
    history = get_patient_history(patient_id)
    
    medications = []
    for record in history:
        meds = record.get('medications', [])
        if meds:
            medications.extend(meds)
    
    return {
        "patient_id": patient_id,
        "patient_name": patient.name,
        "current_medications": medications,
        "medication_count": len(set(medications))
    }
