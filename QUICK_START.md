# 🚀 MedCore AI - Quick Start Guide

## ✅ Step-by-Step Setup

### 1. Start the Flask Server

```bash
cd e:\clinicalAi
python app.py
```

**You should see:**
```
* Running on http://127.0.0.1:5000
* Debug mode: on
```

### 2. Open the Application

**Choose one of these URLs in your browser:**

| Portal | URL | Purpose |
|--------|-----|---------|
| 🏠 **Home** | http://127.0.0.1:5000/ | Landing page |
| 👤 **Patient Portal** | http://127.0.0.1:5000/patient | Submit data & request video calls |
| 👨‍⚕️ **Doctor Portal** | http://127.0.0.1:5000/doctor | View requests & schedule appointments |
| 🔧 **API Test Page** | http://127.0.0.1:5000/test-api | Test all API endpoints |

---

## 🎯 Testing the Video Call & Scheduling System

### **Scenario: Patient Requests Video Call → Doctor Schedules Appointment**

#### Step 1: Patient Requests Video Call
1. Open: http://127.0.0.1:5000/patient
2. Scroll to **"Consultation Services"** section
3. Enter Patient ID: `P12345` (in the form below)
4. Click **"Request Video Call"** button
5. Enter reason: `General health consultation`
6. Click OK
7. ✅ You should see: "Video Call Request Sent!"

#### Step 2: Doctor Views Request
1. Open: http://127.0.0.1:5000/doctor
2. Look at **"Video Call Requests"** card
3. You should see a **red notification badge** with "1 New"
4. The request from Patient P12345 will be displayed
5. Click **"Schedule"** button on the request

#### Step 3: Doctor Schedules Appointment
1. The form will auto-fill Patient ID: `P12345`
2. Select **Date**: Tomorrow's date
3. Select **Time**: `10:00 AM`
4. Select **Duration**: `30 minutes`
5. Add **Notes**: `Follow-up consultation`
6. Click **"Schedule Appointment"**
7. ✅ You should see: "Appointment Scheduled Successfully!"

#### Step 4: Patient Views Appointment
1. Go back to: http://127.0.0.1:5000/patient
2. Scroll to **"My Appointments"** section
3. Make sure Patient ID is still: `P12345`
4. Click **"Refresh"** button
5. ✅ You should see the scheduled appointment with:
   - Date and time
   - Doctor name
   - Duration
   - Notes
   - Status: SCHEDULED

---

## 🔍 Troubleshooting

### ❌ "HTTP error! status: 404"

**Solution:**
1. Make sure Flask server is running: `python app.py`
2. Restart the server if you made code changes
3. Use the correct URL: `http://127.0.0.1:5000/patient` (not `file:///`)

### ❌ "Server returned non-JSON response"

**Solution:**
1. Check if Flask is running in the terminal
2. Look for error messages in the Flask terminal
3. Visit http://127.0.0.1:5000/test-api to test all endpoints

### ❌ No appointments showing

**Solution:**
1. Make sure you entered the same Patient ID in both portals
2. Click "Refresh" button after scheduling
3. Check if `appointments.json` file exists and has data

---

## 📊 API Testing Dashboard

Visit: **http://127.0.0.1:5000/test-api**

This page lets you:
- ✅ Test each API endpoint individually
- ✅ See the exact JSON responses
- ✅ Verify all routes are working
- ✅ Debug any issues

Click each button to test:
1. **POST /api/request_video_call** - Create test video call request
2. **GET /api/get_video_call_requests** - View all requests
3. **POST /api/schedule_appointment** - Create test appointment
4. **GET /api/get_patient_appointments/TEST123** - View patient appointments
5. **GET /api/get_all_appointments** - View all appointments
6. **Test All Routes** - Quick test of all endpoints

---

## 📝 Data Files

The system creates these JSON files automatically:

```
e:\clinicalAi\
├── video_calls.json        # Video call requests
├── appointments.json       # Scheduled appointments
├── patients.json          # Patient data
└── patients_history.json  # Historical patient data
```

**To reset data:**
```bash
echo [] > video_calls.json
echo [] > appointments.json
```

---

## 🎨 Features Overview

### Patient Portal Features:
- ✅ Submit medical data
- ✅ Request video consultations
- ✅ View scheduled appointments
- ✅ Chat with AI assistant
- ✅ Upload medical reports

### Doctor Portal Features:
- ✅ View video call requests (with notifications)
- ✅ Schedule appointments
- ✅ View all appointments
- ✅ Mark appointments complete/cancelled
- ✅ Patient data lookup
- ✅ AI medical analysis
- ✅ Clinical insights
- ✅ Patient history comparison

---

## 🔄 Auto-Refresh

The doctor portal automatically:
- Refreshes video call requests every **30 seconds**
- Shows notification badge for unread requests
- Updates appointment list in real-time

---

## 💡 Tips

1. **Keep Flask running** - Don't close the terminal window
2. **Use Chrome/Edge** - Best compatibility with modern features
3. **Check console** - Press F12 to see detailed error messages
4. **Test API first** - Use http://127.0.0.1:5000/test-api before testing portals
5. **Same Patient ID** - Use the same ID in both portals to see the full workflow

---

## 🆘 Need Help?

1. Check `TROUBLESHOOTING.md` for detailed solutions
2. Visit http://127.0.0.1:5000/test-api to test APIs
3. Look at Flask terminal for error messages
4. Check browser console (F12) for frontend errors

---

## ✨ Next Steps

After testing the basic workflow:
1. Try different patient IDs
2. Schedule multiple appointments
3. Test marking appointments as complete
4. Explore the AI chat features
5. Upload medical reports

**Enjoy using MedCore AI! 🏥**
