# 🚀 MedCore AI - Advanced Features Integration Guide

## New Features Added

### 1. **Real-Time Dashboard** 📊
- Live patient status monitoring (Critical/Warning/Stable)
- Color-coded patient classification
- Quick statistics overview
- Auto-refresh every 30 seconds

### 2. **Patient Trends & Analytics** 📈
- Historical vitals tracking (BP, HR, SpO2)
- Lab results over time
- Visual trend charts
- 30-day historical data

### 3. **Advanced Search** 🔍
- Search by name, ID, symptoms
- Filter by age range, gender, status
- Date range filtering
- Multi-criteria search

### 4. **Patient Alerts System** 🔔
- Critical/Warning alerts
- Real-time vital sign monitoring
- Abnormal lab result detection
- Priority-based alert sorting

### 5. **PDF Medical Reports** 📄
- Professional PDF generation
- Comprehensive patient summary
- Vitals and labs included
- Downloadable reports

### 6. **Appointment System** 📅
- Track upcoming appointments
- Appointment management
- Status tracking (scheduled/completed/cancelled)

### 7. **Medication Tracker** 💊
- Patient medication history
- Current medications list
- Medication count tracking

---

## Installation Steps

### Step 1: Install Dependencies

```bash
pip install reportlab
```

All other dependencies are already installed!

### Step 2: Update Your dpp.py

Add these lines to your `dpp.py` file:

```python
# At the top, after other imports
from routes_advanced import register_advanced_routes

# After creating the Flask app, add:
register_advanced_routes(app)

# Add dashboard route
@app.route("/dashboard")
def dashboard():
    """Advanced dashboard page"""
    return render_template("dashboard.html")
```

**Complete example:**

```python
from flask import Flask, render_template
from database import init_db
from routes_advanced import register_advanced_routes

app = Flask(__name__, template_folder="templates", static_folder="frontend/static")

# Initialize database
init_db(app)

# Register advanced routes
register_advanced_routes(app)

# Your existing routes...

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

if __name__ == "__main__":
    app.run(debug=True, port=5001)
```

### Step 3: Test the Features

```bash
python dpp.py
```

Then visit:
- **Dashboard**: http://localhost:5001/dashboard
- **All API endpoints** are now available!

---

## API Endpoints Reference

### 📊 Dashboard API
```
GET /api/dashboard
```
Returns real-time patient statistics and classifications

**Response:**
```json
{
  "total_patients": 3,
  "critical": [...],
  "warning": [...],
  "stable": [...],
  "statistics": {
    "avg_age": 35.5,
    "high_bp_count": 2,
    "low_spo2_count": 0
  }
}
```

### 📈 Trends API
```
GET /api/patient_trends/<patient_id>
```
Get historical trends for patient

**Response:**
```json
{
  "patient_id": "P12345",
  "vitals": {
    "dates": ["2025-10-01", "2025-10-15"],
    "blood_pressure": {
      "systolic": [120, 130],
      "diastolic": [80, 85]
    },
    "heart_rate": [75, 82],
    "spo2": [98, 97]
  }
}
```

### 🔍 Search API
```
POST /api/search
GET /api/search?q=query&status=critical
```
Advanced patient search

**Request:**
```json
{
  "query": "headache",
  "filters": {
    "status": "critical",
    "min_age": 30,
    "max_age": 60,
    "gender": "male"
  }
}
```

### 🔔 Alerts API
```
GET /api/alerts
```
Get all active patient alerts

**Response:**
```json
{
  "alerts": [
    {
      "patient_id": "P12345",
      "patient_name": "John Doe",
      "alerts": [
        {
          "type": "critical",
          "category": "Blood Pressure",
          "message": "Critical high BP: 180/95 mmHg",
          "recommendation": "Immediate medical attention required"
        }
      ],
      "highest_severity": "critical"
    }
  ],
  "total_alerts": 5,
  "critical_count": 2
}
```

### 📄 PDF Report API
```
GET /api/report/<patient_id>/pdf
```
Download PDF medical report for patient

### 📅 Appointments API
```
GET /api/appointments?days=7
```
Get upcoming appointments

### 💊 Medications API
```
GET /api/medications/<patient_id>
```
Get patient medication history

### 📊 Statistics API
```
GET /api/statistics
```
Get overall system statistics

**Response:**
```json
{
  "patients": {
    "total": 50,
    "today": 3
  },
  "vitals_recorded": 150,
  "lab_tests": 75,
  "chat_sessions": 108,
  "active_alerts": 5
}
```

### 🔄 Compare API
```
GET /api/compare?ids=P12345,P67890
```
Compare multiple patients

### 📤 Export API
```
GET /api/export/<patient_id>
```
Export patient data as JSON

---

## Frontend Integration Examples

### Example 1: Load Dashboard Data

```javascript
async function loadDashboard() {
    const response = await fetch('/api/dashboard');
    const data = await response.json();
    
    console.log('Total patients:', data.total_patients);
    console.log('Critical:', data.critical.length);
    console.log('Statistics:', data.statistics);
}
```

### Example 2: Get Patient Alerts

```javascript
async function getAlerts() {
    const response = await fetch('/api/alerts');
    const data = await response.json();
    
    data.alerts.forEach(alert => {
        console.log(`${alert.patient_name}: ${alert.alert_count} alerts`);
    });
}
```

### Example 3: Download PDF Report

```javascript
function downloadReport(patientId) {
    window.location.href = `/api/report/${patientId}/pdf`;
}
```

### Example 4: Search Patients

```javascript
async function searchPatients(query, filters) {
    const response = await fetch('/api/search', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({query, filters})
    });
    
    const data = await response.json();
    console.log(`Found ${data.count} patients`);
    return data.results;
}
```

### Example 5: Get Trends Chart Data

```javascript
async function loadTrends(patientId) {
    const response = await fetch(`/api/patient_trends/${patientId}`);
    const trends = await response.json();
    
    // Use with Chart.js or any charting library
    const chartData = {
        labels: trends.vitals.dates,
        datasets: [{
            label: 'Systolic BP',
            data: trends.vitals.blood_pressure.systolic
        }]
    };
}
```

---

## Usage Examples

### 1. Dashboard Usage

Visit: `http://localhost:5001/dashboard`

Features:
- View all patients with color-coded status
- See active alerts in real-time
- Click on any patient to view details
- Search patients instantly
- Auto-refreshes every 30 seconds

### 2. Generate PDF Report

```python
# In your Flask route or script
from advanced_features import generate_patient_report_pdf

pdf_buffer = generate_patient_report_pdf('P12345')
# Save or send the PDF
```

### 3. Get Patient Trends

```python
from advanced_features import get_patient_trends

trends = get_patient_trends('P12345')
print(f"Blood pressure over time: {trends['vitals']['blood_pressure']}")
```

### 4. Search Patients

```python
from advanced_features import advanced_patient_search

# Search by symptoms
results = advanced_patient_search('headache')

# Search with filters
results = advanced_patient_search('', {
    'status': 'critical',
    'min_age': 40
})
```

### 5. Get Alerts

```python
from advanced_features import get_patient_alerts

alerts = get_patient_alerts()
for alert in alerts:
    print(f"Patient {alert['patient_name']} has {alert['alert_count']} alerts")
```

---

## Customization

### Change Alert Thresholds

Edit `advanced_features.py`:

```python
def classify_patient_status(vitals):
    # Customize these values
    if systolic >= 180:  # Change from 180 to your threshold
        return 'critical'
```

### Modify Dashboard Colors

Edit `templates/dashboard.html` CSS:

```css
.status-box.critical {
    background: #your-color;
    border-left: 5px solid #your-border-color;
}
```

### Add More Statistics

Edit `routes_advanced.py`:

```python
@app.route("/api/statistics")
def api_statistics():
    stats = {
        "your_metric": calculate_your_metric()
    }
    return jsonify(stats)
```

---

## Performance Tips

1. **Pagination**: For large patient lists, add pagination
2. **Caching**: Cache dashboard data for 10-30 seconds
3. **Indexes**: Database is already indexed on patient_id
4. **Lazy Loading**: Load trends/charts only when needed

---

## Troubleshooting

### Error: Module 'reportlab' not found
```bash
pip install reportlab
```

### Error: Routes not working
Make sure you added:
```python
from routes_advanced import register_advanced_routes
register_advanced_routes(app)
```

### Dashboard not loading
- Check if `/api/dashboard` returns data
- Open browser console for errors
- Ensure database has patients

### PDF not generating
- Install reportlab: `pip install reportlab`
- Check patient exists in database

---

## Next Steps

1. ✅ Install reportlab
2. ✅ Update dpp.py with routes
3. ✅ Test dashboard at /dashboard
4. ✅ Try API endpoints
5. ✅ Customize as needed

## Screenshots

The dashboard includes:
- 📊 Real-time statistics cards
- 🎨 Color-coded patient status
- 🔔 Active alerts section
- 📋 Searchable patient list
- 📈 Visual charts
- 🔄 Auto-refresh

---

**Enjoy your upgraded MedCore AI platform!** 🚀
