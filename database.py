"""
Database configuration and helper functions for MedCore AI Platform
"""
import os
from models import db, Patient, Vitals, LabResult, PatientHistory, ChatSession, ChatMessage, RAGDocument
from datetime import datetime
import json

def init_db(app):
    """Initialize database with Flask app"""
    # Configure SQLite database (can easily switch to PostgreSQL later)
    basedir = os.path.abspath(os.path.dirname(__file__))
    database_path = os.path.join(basedir, 'medcore.db')
    
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', f'sqlite:///{database_path}')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = False  # Set to True for debugging SQL queries
    
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        print(f"Database initialized at: {database_path}")

def get_or_create_patient(patient_id, **kwargs):
    """Get existing patient or create new one"""
    patient = Patient.query.filter_by(patient_id=patient_id).first()
    
    if not patient:
        patient = Patient(patient_id=patient_id, **kwargs)
        db.session.add(patient)
        db.session.commit()
    
    return patient

def save_patient_data(patient_data):
    """
    Save patient data from JSON format to SQL database
    Expected format: {patient_id, name, age, gender, symptoms, vitals{}, lab_results{}}
    """
    patient_id = patient_data.get('patient_id')
    if not patient_id:
        raise ValueError("patient_id is required")
    
    # Get or create patient
    patient = Patient.query.filter_by(patient_id=patient_id).first()
    
    if patient:
        # Update existing patient
        patient.name = patient_data.get('name', patient.name)
        patient.age = patient_data.get('age', patient.age)
        patient.gender = patient_data.get('gender', patient.gender)
        patient.symptoms = patient_data.get('symptoms', patient.symptoms)
        patient.updated_at = datetime.utcnow()
    else:
        # Create new patient
        patient = Patient(
            patient_id=patient_id,
            name=patient_data.get('name'),
            age=patient_data.get('age'),
            gender=patient_data.get('gender'),
            symptoms=patient_data.get('symptoms'),
            timestamp=datetime.fromisoformat(patient_data['timestamp']) if patient_data.get('timestamp') else datetime.utcnow()
        )
        db.session.add(patient)
        db.session.flush()  # Get patient.id without committing
    
    # Save vitals if present
    vitals_data = patient_data.get('vitals')
    if vitals_data:
        vitals = Vitals(
            patient_db_id=patient.id,
            bp=vitals_data.get('bp'),
            hr=vitals_data.get('hr'),
            spo2=vitals_data.get('spo2'),
            temperature=vitals_data.get('temperature'),
            respiratory_rate=vitals_data.get('respiratory_rate'),
            timestamp=datetime.utcnow()
        )
        db.session.add(vitals)
    
    # Save lab results if present
    labs_data = patient_data.get('lab_results')
    if labs_data:
        lab_result = LabResult(
            patient_db_id=patient.id,
            ecg=labs_data.get('ecg'),
            troponin=labs_data.get('troponin'),
            cholesterol=labs_data.get('cholesterol'),
            blood_sugar=labs_data.get('blood_sugar'),
            hba1c=labs_data.get('hba1c'),
            hemoglobin=labs_data.get('hemoglobin'),
            wbc_count=labs_data.get('wbc_count'),
            platelet_count=labs_data.get('platelet_count'),
            creatinine=labs_data.get('creatinine'),
            timestamp=datetime.utcnow()
        )
        db.session.add(lab_result)
    
    db.session.commit()
    return patient

def get_patient_by_id(patient_id):
    """Get patient data by patient_id"""
    patient = Patient.query.filter_by(patient_id=patient_id.strip().upper()).first()
    return patient.to_dict() if patient else None

def get_all_patients():
    """Get all patients"""
    patients = Patient.query.all()
    return [patient.to_dict() for patient in patients]

def get_patient_history(patient_id):
    """Get patient historical records"""
    patient = Patient.query.filter_by(patient_id=patient_id.strip().upper()).first()
    if not patient:
        return []
    
    history_records = PatientHistory.query.filter_by(patient_db_id=patient.id).order_by(PatientHistory.timestamp.desc()).all()
    return [record.to_dict() for record in history_records]

def save_patient_history(patient_id, history_data):
    """Save patient history record"""
    patient = get_or_create_patient(patient_id)
    
    history = PatientHistory(
        patient_db_id=patient.id,
        symptoms=history_data.get('symptoms'),
        vitals_json=json.dumps(history_data.get('vitals', {})),
        labs_json=json.dumps(history_data.get('lab_results', {})),
        medications=json.dumps(history_data.get('medications', [])),
        history=json.dumps(history_data.get('history', [])),
        notes=history_data.get('notes'),
        timestamp=datetime.utcnow()
    )
    db.session.add(history)
    db.session.commit()
    return history

def get_or_create_chat_session(session_id, patient_id=None):
    """Get existing chat session or create new one"""
    session = ChatSession.query.filter_by(session_id=session_id).first()
    
    if not session:
        # Get patient if patient_id provided
        patient_db_id = None
        if patient_id:
            patient = Patient.query.filter_by(patient_id=patient_id.strip().upper()).first()
            patient_db_id = patient.id if patient else None
        
        session = ChatSession(
            session_id=session_id,
            patient_db_id=patient_db_id,
            patient_id=patient_id
        )
        db.session.add(session)
        db.session.commit()
    
    return session

def save_chat_message(session_id, role, content):
    """Save a chat message to a session"""
    session = ChatSession.query.filter_by(session_id=session_id).first()
    
    if not session:
        raise ValueError(f"Chat session {session_id} not found")
    
    message = ChatMessage(
        session_db_id=session.id,
        role=role,
        content=content,
        timestamp=datetime.utcnow()
    )
    db.session.add(message)
    
    # Update session timestamp
    session.updated_at = datetime.utcnow()
    db.session.commit()
    
    return message

def get_chat_history(session_id, limit=50):
    """Get chat history for a session"""
    session = ChatSession.query.filter_by(session_id=session_id).first()
    
    if not session:
        return []
    
    messages = ChatMessage.query.filter_by(session_db_id=session.id).order_by(ChatMessage.timestamp.asc()).limit(limit).all()
    return [msg.to_dict() for msg in messages]

def save_rag_document(doc_type, content, patient_id=None, metadata=None):
    """Save a document for RAG retrieval"""
    patient_db_id = None
    if patient_id:
        patient = Patient.query.filter_by(patient_id=patient_id.strip().upper()).first()
        patient_db_id = patient.id if patient else None
    
    doc = RAGDocument(
        doc_type=doc_type,
        patient_db_id=patient_db_id,
        content=content,
        metadata_json=json.dumps(metadata) if metadata else None
    )
    db.session.add(doc)
    db.session.commit()
    return doc

def search_rag_documents(query, doc_type=None, patient_id=None, limit=10):
    """
    Simple text search for RAG documents
    For production, consider using vector embeddings with pgvector or similar
    """
    query_obj = RAGDocument.query
    
    if doc_type:
        query_obj = query_obj.filter_by(doc_type=doc_type)
    
    if patient_id:
        patient = Patient.query.filter_by(patient_id=patient_id.strip().upper()).first()
        if patient:
            query_obj = query_obj.filter_by(patient_db_id=patient.id)
    
    # Simple text search (for better results, use full-text search or vector embeddings)
    query_obj = query_obj.filter(RAGDocument.content.like(f'%{query}%'))
    
    documents = query_obj.order_by(RAGDocument.updated_at.desc()).limit(limit).all()
    return [doc.to_dict() for doc in documents]

def get_patient_comparison_data(patient_id):
    """
    Get current and historical data for patient comparison
    Returns: (current_data, history_data_list)
    """
    patient = Patient.query.filter_by(patient_id=patient_id.strip().upper()).first()
    
    if not patient:
        return None, []
    
    current_data = patient.to_dict()
    
    # Get all historical vitals and labs
    history_vitals = Vitals.query.filter_by(patient_db_id=patient.id).order_by(Vitals.timestamp.desc()).all()
    history_labs = LabResult.query.filter_by(patient_db_id=patient.id).order_by(LabResult.timestamp.desc()).all()
    
    # Combine into history records format
    history_data = []
    
    # Use historical records if they exist
    history_records = PatientHistory.query.filter_by(patient_db_id=patient.id).order_by(PatientHistory.timestamp.desc()).all()
    for record in history_records:
        history_data.append(record.to_dict())
    
    return current_data, history_data

def index_patient_for_rag(patient_id):
    """
    Index patient data for RAG retrieval
    Creates searchable documents from patient data
    """
    patient = Patient.query.filter_by(patient_id=patient_id.strip().upper()).first()
    
    if not patient:
        return None
    
    # Create comprehensive text for RAG
    patient_dict = patient.to_dict()
    
    content_parts = [
        f"Patient ID: {patient.patient_id}",
        f"Name: {patient.name or 'Unknown'}",
        f"Age: {patient.age or 'Unknown'}",
        f"Gender: {patient.gender or 'Unknown'}",
        f"Symptoms: {patient.symptoms or 'None reported'}"
    ]
    
    # Add vitals
    latest_vitals = patient.vitals.order_by(Vitals.timestamp.desc()).first()
    if latest_vitals:
        content_parts.append(f"Blood Pressure: {latest_vitals.bp or 'Not recorded'}")
        content_parts.append(f"Heart Rate: {latest_vitals.hr or 'Not recorded'} bpm")
        content_parts.append(f"SpO2: {latest_vitals.spo2 or 'Not recorded'}%")
    
    # Add labs
    latest_labs = patient.lab_results.order_by(LabResult.timestamp.desc()).first()
    if latest_labs:
        content_parts.append(f"ECG: {latest_labs.ecg or 'Not done'}")
        content_parts.append(f"Troponin: {latest_labs.troponin or 'Not tested'}")
        content_parts.append(f"Cholesterol: {latest_labs.cholesterol or 'Not tested'}")
    
    content = "\n".join(content_parts)
    
    # Save as RAG document
    metadata = {
        'patient_id': patient.patient_id,
        'indexed_at': datetime.utcnow().isoformat()
    }
    
    return save_rag_document('patient_data', content, patient.patient_id, metadata)
