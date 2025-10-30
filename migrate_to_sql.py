"""
Migration script to convert JSON data to SQL database
Run this once to migrate existing patients.json, patients_history.json, and chat_sessions.json to SQL
"""
import json
import os
from flask import Flask
from models import db
from database import init_db, save_patient_data, save_patient_history, get_or_create_chat_session, save_chat_message
from datetime import datetime

def migrate_json_to_sql():
    """Migrate all JSON data to SQL database"""
    
    # Create Flask app for database context
    app = Flask(__name__)
    init_db(app)
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Track migration stats
    stats = {
        'patients': 0,
        'history_records': 0,
        'chat_sessions': 0,
        'chat_messages': 0,
        'errors': []
    }
    
    with app.app_context():
        print("=" * 60)
        print("MedCore AI - JSON to SQL Migration")
        print("=" * 60)
        
        # 1. Migrate patients.json
        patients_file = os.path.join(base_dir, 'patients.json')
        if os.path.exists(patients_file):
            print("\n[1/3] Migrating patients.json...")
            try:
                with open(patients_file, 'r') as f:
                    patients_data = json.load(f)
                
                if isinstance(patients_data, dict):
                    patients_data = [patients_data]
                
                for patient_data in patients_data:
                    try:
                        # Normalize patient_id
                        if 'patient_id' in patient_data:
                            patient_data['patient_id'] = str(patient_data['patient_id']).strip().upper()
                            save_patient_data(patient_data)
                            stats['patients'] += 1
                            print(f"  ✓ Migrated patient: {patient_data['patient_id']}")
                    except Exception as e:
                        error_msg = f"Error migrating patient {patient_data.get('patient_id', 'unknown')}: {str(e)}"
                        print(f"  ✗ {error_msg}")
                        stats['errors'].append(error_msg)
                
                print(f"  Total patients migrated: {stats['patients']}")
            except Exception as e:
                error_msg = f"Error reading patients.json: {str(e)}"
                print(f"  ✗ {error_msg}")
                stats['errors'].append(error_msg)
        else:
            print("\n[1/3] patients.json not found - skipping")
        
        # 2. Migrate patients_history.json
        history_file = os.path.join(base_dir, 'patients_history.json')
        if os.path.exists(history_file):
            print("\n[2/3] Migrating patients_history.json...")
            try:
                with open(history_file, 'r') as f:
                    history_data = json.load(f)
                
                if isinstance(history_data, dict):
                    history_data = [history_data]
                
                for history_record in history_data:
                    try:
                        patient_id = history_record.get('patient_id')
                        if patient_id:
                            patient_id = str(patient_id).strip().upper()
                            save_patient_history(patient_id, history_record)
                            stats['history_records'] += 1
                            print(f"  ✓ Migrated history for patient: {patient_id}")
                    except Exception as e:
                        error_msg = f"Error migrating history for {history_record.get('patient_id', 'unknown')}: {str(e)}"
                        print(f"  ✗ {error_msg}")
                        stats['errors'].append(error_msg)
                
                print(f"  Total history records migrated: {stats['history_records']}")
            except Exception as e:
                error_msg = f"Error reading patients_history.json: {str(e)}"
                print(f"  ✗ {error_msg}")
                stats['errors'].append(error_msg)
        else:
            print("\n[2/3] patients_history.json not found - skipping")
        
        # 3. Migrate chat_sessions.json
        chat_file = os.path.join(base_dir, 'chat_sessions.json')
        if os.path.exists(chat_file):
            print("\n[3/3] Migrating chat_sessions.json...")
            try:
                with open(chat_file, 'r') as f:
                    chat_sessions = json.load(f)
                
                if isinstance(chat_sessions, dict):
                    chat_sessions = [chat_sessions]
                
                for session_data in chat_sessions:
                    try:
                        session_id = session_data.get('session_id')
                        patient_id = session_data.get('patient_id')
                        
                        if session_id:
                            # Create session
                            session = get_or_create_chat_session(session_id, patient_id)
                            stats['chat_sessions'] += 1
                            
                            # Migrate messages
                            messages = session_data.get('messages', [])
                            for msg in messages:
                                role = msg.get('role', 'user')
                                content = msg.get('content', '')
                                save_chat_message(session_id, role, content)
                                stats['chat_messages'] += 1
                            
                            print(f"  ✓ Migrated session: {session_id} ({len(messages)} messages)")
                    except Exception as e:
                        error_msg = f"Error migrating chat session {session_data.get('session_id', 'unknown')}: {str(e)}"
                        print(f"  ✗ {error_msg}")
                        stats['errors'].append(error_msg)
                
                print(f"  Total chat sessions migrated: {stats['chat_sessions']}")
                print(f"  Total chat messages migrated: {stats['chat_messages']}")
            except Exception as e:
                error_msg = f"Error reading chat_sessions.json: {str(e)}"
                print(f"  ✗ {error_msg}")
                stats['errors'].append(error_msg)
        else:
            print("\n[3/3] chat_sessions.json not found - skipping")
        
        # Print summary
        print("\n" + "=" * 60)
        print("Migration Summary")
        print("=" * 60)
        print(f"Patients migrated:        {stats['patients']}")
        print(f"History records migrated: {stats['history_records']}")
        print(f"Chat sessions migrated:   {stats['chat_sessions']}")
        print(f"Chat messages migrated:   {stats['chat_messages']}")
        print(f"Errors encountered:       {len(stats['errors'])}")
        
        if stats['errors']:
            print("\nErrors:")
            for error in stats['errors']:
                print(f"  - {error}")
        
        print("\n" + "=" * 60)
        print("Migration completed!")
        print("=" * 60)
        
        # Ask about backing up JSON files
        print("\n⚠️  IMPORTANT: Your JSON files are still in place.")
        print("After verifying the migration, you may want to:")
        print("  1. Backup JSON files to a safe location")
        print("  2. Delete or rename them to avoid confusion")
        print("  3. Update .gitignore to exclude medcore.db")
        print("\nThe application will now use the SQL database (medcore.db)")
        
        return stats

if __name__ == "__main__":
    print("\n⚠️  WARNING: This will migrate JSON data to SQL database")
    print("Make sure you have backed up your JSON files before proceeding.\n")
    
    response = input("Do you want to continue? (yes/no): ")
    
    if response.lower() in ['yes', 'y']:
        migrate_json_to_sql()
    else:
        print("Migration cancelled.")
