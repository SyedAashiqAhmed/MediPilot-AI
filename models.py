"""
Database models for MedCore AI Platform
Uses SQLAlchemy ORM for database management
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class Patient(db.Model):
    """Patient records table"""
    __tablename__ = 'patients'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(20))
    symptoms = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    vitals = db.relationship('Vitals', backref='patient', lazy='dynamic', cascade='all, delete-orphan')
    lab_results = db.relationship('LabResult', backref='patient', lazy='dynamic', cascade='all, delete-orphan')
    history_records = db.relationship('PatientHistory', backref='patient', lazy='dynamic', cascade='all, delete-orphan')
    chat_sessions = db.relationship('ChatSession', backref='patient', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert patient record to dictionary"""
        latest_vitals = self.vitals.order_by(Vitals.timestamp.desc()).first()
        latest_labs = self.lab_results.order_by(LabResult.timestamp.desc()).first()
        
        return {
            'patient_id': self.patient_id,
            'name': self.name,
            'age': self.age,
            'gender': self.gender,
            'symptoms': self.symptoms,
            'vitals': latest_vitals.to_dict() if latest_vitals else {},
            'lab_results': latest_labs.to_dict() if latest_labs else {},
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
    
    def __repr__(self):
        return f'<Patient {self.patient_id}>'


class Vitals(db.Model):
    """Patient vital signs"""
    __tablename__ = 'vitals'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_db_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False, index=True)
    bp = db.Column(db.String(20))  # e.g., "120/80"
    hr = db.Column(db.Integer)  # heart rate
    spo2 = db.Column(db.Integer)  # oxygen saturation
    temperature = db.Column(db.Float)
    respiratory_rate = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        """Convert vitals to dictionary"""
        return {
            'bp': self.bp,
            'hr': self.hr,
            'spo2': self.spo2,
            'temperature': self.temperature,
            'respiratory_rate': self.respiratory_rate,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
    
    def __repr__(self):
        return f'<Vitals {self.id} for Patient {self.patient_db_id}>'


class LabResult(db.Model):
    """Patient laboratory results"""
    __tablename__ = 'lab_results'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_db_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False, index=True)
    ecg = db.Column(db.String(200))
    troponin = db.Column(db.String(50))
    cholesterol = db.Column(db.String(50))
    blood_sugar = db.Column(db.String(50))
    hba1c = db.Column(db.String(50))
    # Additional common lab values
    hemoglobin = db.Column(db.String(50))
    wbc_count = db.Column(db.String(50))
    platelet_count = db.Column(db.String(50))
    creatinine = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        """Convert lab results to dictionary"""
        result = {}
        if self.ecg:
            result['ecg'] = self.ecg
        if self.troponin:
            result['troponin'] = self.troponin
        if self.cholesterol:
            result['cholesterol'] = self.cholesterol
        if self.blood_sugar:
            result['blood_sugar'] = self.blood_sugar
        if self.hba1c:
            result['hba1c'] = self.hba1c
        if self.hemoglobin:
            result['hemoglobin'] = self.hemoglobin
        if self.wbc_count:
            result['wbc_count'] = self.wbc_count
        if self.platelet_count:
            result['platelet_count'] = self.platelet_count
        if self.creatinine:
            result['creatinine'] = self.creatinine
        result['timestamp'] = self.timestamp.isoformat() if self.timestamp else None
        return result
    
    def __repr__(self):
        return f'<LabResult {self.id} for Patient {self.patient_db_id}>'


class PatientHistory(db.Model):
    """Patient historical records"""
    __tablename__ = 'patient_history'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_db_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False, index=True)
    symptoms = db.Column(db.Text)
    vitals_json = db.Column(db.Text)  # JSON string of vitals
    labs_json = db.Column(db.Text)  # JSON string of lab results
    medications = db.Column(db.Text)  # JSON array of medications
    history = db.Column(db.Text)  # JSON array of medical history
    notes = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        """Convert history record to dictionary"""
        return {
            'symptoms': self.symptoms,
            'vitals': json.loads(self.vitals_json) if self.vitals_json else {},
            'lab_results': json.loads(self.labs_json) if self.labs_json else {},
            'medications': json.loads(self.medications) if self.medications else [],
            'history': json.loads(self.history) if self.history else [],
            'notes': self.notes,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
    
    def __repr__(self):
        return f'<PatientHistory {self.id} for Patient {self.patient_db_id}>'


class ChatSession(db.Model):
    """Chat session table for RAG AI conversations"""
    __tablename__ = 'chat_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), unique=True, nullable=False, index=True)
    patient_db_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=True, index=True)
    patient_id = db.Column(db.String(50), index=True)  # External patient ID
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    messages = db.relationship('ChatMessage', backref='session', lazy='dynamic', cascade='all, delete-orphan', order_by='ChatMessage.timestamp')
    
    def to_dict(self, include_messages=True):
        """Convert chat session to dictionary"""
        result = {
            'session_id': self.session_id,
            'patient_id': self.patient_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_messages:
            result['messages'] = [msg.to_dict() for msg in self.messages.all()]
        return result
    
    def __repr__(self):
        return f'<ChatSession {self.session_id}>'


class ChatMessage(db.Model):
    """Individual chat messages within a session"""
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    session_db_id = db.Column(db.Integer, db.ForeignKey('chat_sessions.id'), nullable=False, index=True)
    role = db.Column(db.String(20), nullable=False)  # 'user' or 'assistant'
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        """Convert chat message to dictionary"""
        return {
            'role': self.role,
            'content': self.content,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
    
    def __repr__(self):
        return f'<ChatMessage {self.id} in Session {self.session_db_id}>'


class RAGDocument(db.Model):
    """Store documents for RAG (Retrieval-Augmented Generation)"""
    __tablename__ = 'rag_documents'
    
    id = db.Column(db.Integer, primary_key=True)
    doc_type = db.Column(db.String(50), nullable=False, index=True)  # 'patient_data', 'medical_knowledge', etc.
    patient_db_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=True, index=True)
    content = db.Column(db.Text, nullable=False)
    metadata_json = db.Column(db.Text)  # JSON string for additional metadata
    embedding = db.Column(db.Text)  # Store embeddings as JSON array for vector search (optional)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        """Convert RAG document to dictionary"""
        return {
            'id': self.id,
            'doc_type': self.doc_type,
            'patient_db_id': self.patient_db_id,
            'content': self.content,
            'metadata': json.loads(self.metadata_json) if self.metadata_json else {},
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<RAGDocument {self.id} type={self.doc_type}>'
