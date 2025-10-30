# MedCore AI - SQL Database Migration Guide

## Overview
The MedCore AI platform has been converted from JSON file storage to SQL database (SQLite/PostgreSQL). This provides better performance, data integrity, and scalability.

## What Changed

### New Files Created
1. **models.py** - SQLAlchemy database models
   - `Patient` - Patient records
   - `Vitals` - Patient vital signs (with history)
   - `LabResult` - Laboratory test results (with history)
   - `PatientHistory` - Historical medical records
   - `ChatSession` - Chat sessions for RAG AI
   - `ChatMessage` - Individual chat messages
   - `RAGDocument` - Documents for RAG retrieval

2. **database.py** - Database helper functions
   - init_db() - Initialize database
   - save_patient_data() - Save patient data
   - get_patient_by_id() - Retrieve patient
   - get_all_patients() - Get all patients
   - Chat session management functions
   - RAG document functions

3. **migrate_to_sql.py** - Migration script to convert JSON to SQL

### Modified Files
1. **dpp.py** - Main application file updated to use SQL
2. **app.py** - Alternative app file updated to use SQL
3. **requirements.txt** - Added Flask-SQLAlchemy and psycopg2-binary

## Migration Steps

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Backup Existing Data
```bash
# Create a backup folder
mkdir backup
cp patients.json backup/
cp patients_history.json backup/
cp chat_sessions.json backup/
```

### 3. Run Migration Script
```bash
python migrate_to_sql.py
```

This will:
- Create a new SQLite database (`medcore.db`)
- Migrate all data from JSON files to SQL
- Display migration statistics
- Preserve original JSON files (for safety)

### 4. Verify Migration
- Check the migration output for any errors
- Test the application with: `python dpp.py`
- Verify patient data is accessible
- Test chat functionality

### 5. Update .gitignore
Add the following to `.gitignore`:
```
medcore.db
*.db
*.sqlite
*.sqlite3
```

## Database Schema

### Patients Table
```sql
- id (Primary Key)
- patient_id (Unique, Indexed)
- name
- age
- gender
- symptoms
- timestamp
- created_at
- updated_at
```

### Vitals Table
```sql
- id (Primary Key)
- patient_db_id (Foreign Key -> patients.id)
- bp (blood pressure)
- hr (heart rate)
- spo2 (oxygen saturation)
- temperature
- respiratory_rate
- timestamp
```

### LabResults Table
```sql
- id (Primary Key)
- patient_db_id (Foreign Key -> patients.id)
- ecg
- troponin
- cholesterol
- blood_sugar
- hba1c
- hemoglobin
- wbc_count
- platelet_count
- creatinine
- timestamp
```

### ChatSessions & ChatMessages
```sql
ChatSessions:
- id (Primary Key)
- session_id (Unique, Indexed)
- patient_db_id (Foreign Key -> patients.id)
- patient_id (External ID)
- created_at
- updated_at

ChatMessages:
- id (Primary Key)
- session_db_id (Foreign Key -> chat_sessions.id)
- role (user/assistant)
- content
- timestamp
```

### RAGDocuments Table
```sql
- id (Primary Key)
- doc_type
- patient_db_id (Foreign Key -> patients.id)
- content
- metadata_json
- embedding (for future vector search)
- created_at
- updated_at
```

## Key Features

### 1. Automatic RAG Indexing
When a patient is added, their data is automatically indexed for RAG retrieval:
```python
index_patient_for_rag(patient_id)
```

### 2. Chat History with SQL
Chat sessions and messages are now stored in SQL with full history:
```python
session = get_or_create_chat_session(session_id, patient_id)
save_chat_message(session_id, "user", message)
history = get_chat_history(session_id)
```

### 3. Historical Data Tracking
Multiple vitals and lab results are stored over time for trend analysis:
```python
current_data, history_data = get_patient_comparison_data(patient_id)
```

### 4. Full-Text Search (Future)
The RAGDocument table supports content search:
```python
results = search_rag_documents(query, doc_type='patient_data', patient_id=patient_id)
```

## Configuration

### SQLite (Default)
No configuration needed. Database file is created automatically at `medcore.db`.

### PostgreSQL (Production)
Set environment variable:
```bash
DATABASE_URL=postgresql://username:password@localhost:5432/medcore_db
```

## API Changes

### None - Backward Compatible!
All existing API endpoints work the same way. The frontend doesn't need any changes.

- `/submit_patient` - Still accepts same JSON
- `/get_patient_data/<patient_id>` - Returns same format
- `/get_all_patients` - Returns same format
- `/chat_with_ai` - Works identically
- All other endpoints unchanged

## Performance Benefits

1. **Faster Queries** - Indexed lookups instead of JSON scanning
2. **Concurrent Access** - Multiple users can access data safely
3. **Data Integrity** - Foreign key constraints and transactions
4. **Scalability** - Ready for thousands of patients
5. **Historical Tracking** - Built-in versioning of vitals and labs

## Rollback (If Needed)

If you need to rollback to JSON:
1. Keep using old `app.py` without database imports
2. Restore JSON files from backup
3. Remove database initialization from code

But we recommend using SQL going forward!

## Production Deployment

### Option 1: SQLite (Small-Medium Scale)
- Database file is portable
- No external database server needed
- Good for up to 100K records

### Option 2: PostgreSQL (Large Scale)
```bash
# Install PostgreSQL
sudo apt-get install postgresql

# Create database
createdb medcore_db

# Set environment variable
export DATABASE_URL=postgresql://user:password@localhost/medcore_db

# Run application
python dpp.py
```

## Maintenance

### Backup Database
```bash
# SQLite
cp medcore.db backups/medcore_$(date +%Y%m%d).db

# PostgreSQL
pg_dump medcore_db > backups/medcore_$(date +%Y%m%d).sql
```

### Database Reset (Development Only)
```bash
rm medcore.db
python dpp.py  # Will create fresh database
python migrate_to_sql.py  # Re-import JSON data
```

## Troubleshooting

### Error: "No module named 'models'"
```bash
pip install Flask-SQLAlchemy
```

### Error: "Database is locked"
- Multiple processes accessing SQLite
- Use PostgreSQL for multi-user access

### Migration Errors
- Check JSON file format
- Ensure patient_id fields exist
- Review migration output for specifics

## Support

For issues or questions:
1. Check migration output for errors
2. Review database.py helper functions
3. Verify all dependencies installed
4. Test with a fresh database

## Next Steps

1. ✅ All data migrated to SQL
2. ✅ RAG chat uses SQL history
3. 🔄 Consider adding vector embeddings for semantic search
4. 🔄 Implement full-text search on symptoms/diagnoses
5. 🔄 Add database migrations with Alembic
6. 🔄 Set up automated backups

---

**Migration Date**: $(date)
**Version**: 2.0 (SQL)
**Previous Version**: 1.0 (JSON)
