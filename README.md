# ClinicalAI - Unified Medical Portal

A unified Flask web application that provides both patient and doctor portals with AI-powered medical consultations using Google's Gemini AI.

## 🚀 Features

- **Intro Portal**: Choose between Patient and Doctor interfaces
- **Patient Portal**: Submit medical symptoms, vitals, and lab results
- **Doctor Portal**: View patient data, generate comparison charts, and AI consultations
- **AI Chat**: Real-time streaming AI medical consultations
- **Secure API**: Environment-based API key management

## 📁 Project Structure

```
clinicalAi/
├── dpp.py                 # Main Flask application
├── app.py                 # Legacy app (can be removed)
├── requirements.txt       # Python dependencies
├── Procfile              # Deployment configuration
├── .env.example          # Environment variables template
├── README.md             # This file
├── test_app.py           # Test script
├── templates/            # HTML templates
│   ├── intro.html        # Landing page
│   ├── index.html        # Patient portal
│   ├── doctor.html       # Doctor portal
│   └── chat.html         # AI chat interface
├── frontend/             # Static frontend files
│   ├── static/
│   │   ├── script.js     # Patient form handling
│   │   └── styles.css    # Additional styles
│   ├── doctor.html       # Alternative doctor template
│   └── chat.html         # Alternative chat template
└── data files/           # Auto-generated JSON files
    ├── patients.json
    ├── patients_history.json
    └── chat_sessions.json
```

## 🛠️ Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

Copy the example environment file:
```bash
copy .env.example .env
```

Edit `.env` and add your Gemini API key:
```
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

**Alternative**: Set environment variable directly:
```bash
# Windows PowerShell
$env:GEMINI_API_KEY="your_actual_gemini_api_key_here"

# Windows Command Prompt
set GEMINI_API_KEY=your_actual_gemini_api_key_here
```

### 3. Run the Application

```bash
python dpp.py
```

The app will start on `http://127.0.0.1:5001`

### 4. Test the Application

```bash
python test_app.py
```

## 🌐 Available Routes

| Route | Description | Template |
|-------|-------------|----------|
| `/` | Landing page to choose portal | `intro.html` |
| `/patient` | Patient data submission form | `index.html` |
| `/doctor` | Doctor dashboard with AI features | `doctor.html` |
| `/chat` | Real-time AI consultation chat | `chat.html` |
| `/submit_patient` | POST endpoint for patient data | - |
| `/get_patient_data/<id>` | GET patient data by ID | - |
| `/get_all_patients` | GET all patients | - |
| `/patient_compare_plot/<id>` | Generate comparison charts | - |
| `/clinical_insights/<id>` | AI clinical analysis | - |
| `/ai_consultation/<id>` | Structured AI consultation | - |
| `/chat_consultation/<id>` | Streaming AI consultation | - |
| `/test_gemini` | Test Gemini API connectivity | - |

## 🤖 AI Features

### 1. Clinical Insights
- Structured medical analysis
- Diagnosis recommendations
- Test suggestions
- Management plans

### 2. AI Consultation
- Interactive chat-based consultation
- Patient history analysis
- Real-time recommendations

### 3. Streaming Chat
- Server-sent events for real-time updates
- Live AI analysis feedback
- Progressive consultation results

## 📊 Data Management

The app automatically creates and manages JSON files:

- `patients.json`: Current patient data
- `patients_history.json`: Historical patient records
- `chat_sessions.json`: AI consultation sessions

## 🔧 Configuration

### Environment Variables
- `GEMINI_API_KEY`: Required for AI features
- `FLASK_ENV`: Set to `development` for debug mode
- `PORT`: Server port (default: 5001)

### Deployment
The app includes a `Procfile` for deployment to platforms like Heroku:
```
web: gunicorn dpp:app
```

## 🧪 Testing

### Manual Testing
1. Start the app: `python dpp.py`
2. Visit `http://127.0.0.1:5001`
3. Test each portal and feature

### Automated Testing
```bash
python test_app.py
```

### API Testing
Test individual endpoints:
```bash
# Test Gemini API
curl http://127.0.0.1:5001/test_gemini

# Get all patients
curl http://127.0.0.1:5001/get_all_patients

# Submit patient data
curl -X POST http://127.0.0.1:5001/submit_patient \
  -H "Content-Type: application/json" \
  -d '{"patient_id":"P123","symptoms":"test"}'
```

## 🚨 Troubleshooting

### Common Issues

1. **Gemini API Error**
   - Ensure `GEMINI_API_KEY` is set correctly
   - Check API key validity at Google AI Studio

2. **Template Not Found**
   - Verify all templates exist in `templates/` folder
   - Check template names match route functions

3. **Port Already in Use**
   - Change port in `dpp.py`: `app.run(debug=True, port=5002)`
   - Or kill existing process on port 5001

4. **Import Errors**
   - Install missing dependencies: `pip install -r requirements.txt`
   - Check Python version compatibility

### Debug Mode
Enable debug mode for detailed error messages:
```python
if __name__ == "__main__":
    app.run(debug=True, port=5001)
```

## 📝 Usage Examples

### Patient Workflow
1. Visit `/` → Choose "Patient"
2. Fill out medical form with symptoms and vitals
3. Submit data → Stored in `patients.json`

### Doctor Workflow
1. Visit `/` → Choose "Doctor"
2. Enter patient ID to view data
3. Generate comparison charts
4. Start AI consultation for analysis

### AI Chat Workflow
1. Visit `/chat`
2. Enter patient ID
3. Get real-time streaming AI analysis

## 🔒 Security Notes

- Never commit API keys to version control
- Use environment variables for sensitive data
- Consider adding authentication for production use
- Validate all user inputs

## 📈 Future Enhancements

- User authentication and authorization
- Database integration (PostgreSQL/MongoDB)
- Advanced AI model integration
- Real-time notifications
- Mobile app support
- HIPAA compliance features

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is for educational and development purposes. Ensure compliance with medical data regulations in production use.
