# 🚨 IMPORTANT: Read This First!

## ⚠️ Critical Information

### You Have TWO Python Files:

1. **`app.py`** ✅ **USE THIS ONE!**
   - Has ALL features
   - Video calls, appointments, pharmacy
   - This is the CORRECT file

2. **`dpp.py`** ❌ **DON'T USE THIS!**
   - Old version
   - Missing new features
   - Causes 404 errors

---

## 🚀 How to Start Server

### Option 1: Double-click (Easiest)
```
Double-click: START.bat
```

### Option 2: Command Line
```bash
python app.py
```

### Option 3: PowerShell
```powershell
cd e:\clinicalAi
python app.py
```

---

## ✅ Verify Server is Running Correctly

**Check terminal output:**
```
* Serving Flask app 'app'  ← Should say 'app' not 'dpp'!
* Running on http://127.0.0.1:5000
```

**Test in browser:**
1. Open: http://127.0.0.1:5000/patient
2. Enter Patient ID: P12345
3. Click "Request Video Call"
4. Should work without errors! ✅

---

## 🎯 All Available Portals

| Portal | URL | Features |
|--------|-----|----------|
| **Home** | http://127.0.0.1:5000/ | Landing page with all portal links |
| **Patient** | http://127.0.0.1:5000/patient | Video calls, appointments, prescriptions |
| **Doctor** | http://127.0.0.1:5000/doctor | Scheduling, prescriptions, messaging |
| **Pharmacy** | http://127.0.0.1:5000/pharmacy | Prescription management, delivery |

---

## 📊 Complete System Features

### Patient Portal:
- ✅ Request video consultations
- ✅ View scheduled appointments
- ✅ Track medicine prescriptions
- ✅ Monitor delivery status
- ✅ AI health assistant

### Doctor Portal:
- ✅ View video call requests
- ✅ Schedule appointments
- ✅ Send prescriptions to pharmacy
- ✅ Message pharmacy directly
- ✅ Patient data analysis
- ✅ AI medical assistant

### Pharmacy Portal:
- ✅ Receive prescriptions
- ✅ Manage medicine preparation
- ✅ Update delivery status
- ✅ View doctor messages
- ✅ Priority handling

---

## 🔄 Complete Workflow

```
1. PATIENT → Requests video call
   └─> Doctor receives notification

2. DOCTOR → Schedules appointment
   └─> Patient sees appointment

3. DOCTOR → Conducts consultation
   └─> Sends prescription to pharmacy

4. PHARMACY → Prepares medicines
   └─> Updates status (Pending → Preparing → Ready → Delivered)

5. PATIENT → Tracks delivery
   └─> Sees real-time status updates
```

---

## 📁 Important Files

### Run These:
- ✅ `START.bat` - Easy server start
- ✅ `app.py` - Main application

### Read These:
- 📖 `START_SERVER.md` - Detailed server instructions
- 📖 `PHARMACY_SYSTEM_GUIDE.md` - Complete pharmacy guide
- 📖 `PHARMACY_SUMMARY.md` - Quick reference
- 📖 `TROUBLESHOOTING.md` - Fix common issues
- 📖 `QUICK_START.md` - Getting started guide

### Don't Use:
- ❌ `dpp.py` - Old version, causes errors

---

## 🐛 Common Errors & Solutions

### Error: "Unexpected token '<', "<!doctype "... is not valid JSON"
**Cause:** Running dpp.py instead of app.py
**Solution:** 
```bash
# Stop dpp.py
Get-Process python | Stop-Process -Force

# Start app.py
python app.py
```

### Error: "HTTP error! status: 404"
**Cause:** Wrong server running or server not started
**Solution:**
```bash
# Make sure app.py is running
python app.py
```

### Error: Video calls/appointments not working
**Cause:** Running dpp.py
**Solution:** Switch to app.py

---

## 🎨 System Design

- Professional medical UI
- MedCore AI branding
- Color-coded status indicators
- Real-time updates
- Auto-refresh features
- Responsive design

---

## 💾 Data Storage

All data stored in JSON files:
- `video_calls.json` - Video call requests
- `appointments.json` - Scheduled appointments
- `prescriptions.json` - Medicine prescriptions
- `pharmacy_messages.json` - Doctor-pharmacy messages
- `patients.json` - Patient data
- `patients_history.json` - Historical data

---

## 🆘 Need Help?

1. **Check:** `START_SERVER.md` for server issues
2. **Check:** `TROUBLESHOOTING.md` for errors
3. **Check:** `PHARMACY_SYSTEM_GUIDE.md` for pharmacy features
4. **Test:** http://127.0.0.1:5000/debug for API testing

---

## ✅ Quick Checklist

Before using the system:
- [ ] Running `app.py` (not dpp.py)
- [ ] Server shows "Serving Flask app 'app'"
- [ ] Can access http://127.0.0.1:5000/
- [ ] All 3 portals visible on homepage
- [ ] No 404 errors in browser

---

## 🎉 You're Ready!

**Server is running correctly with app.py!**

All features are operational:
- ✅ Patient portal
- ✅ Doctor portal  
- ✅ Pharmacy portal
- ✅ Video calls
- ✅ Appointments
- ✅ Prescriptions
- ✅ Delivery tracking

**Start using MedCore AI now!** 🏥
