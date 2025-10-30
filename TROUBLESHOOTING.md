# MedCore AI - Troubleshooting Guide

## Common Errors

### ❌ Error: "Unexpected token '<', "<!doctype "... is not valid JSON"

**Cause:** The frontend is receiving HTML instead of JSON from the server.

**Solutions:**

1. **Make sure Flask server is running:**
   ```bash
   python app.py
   ```
   You should see:
   ```
   * Running on http://127.0.0.1:5000
   * Debug mode: on
   ```

2. **Check the correct URL:**
   - Patient Portal: http://127.0.0.1:5000/patient
   - Doctor Portal: http://127.0.0.1:5000/doctor
   - Home: http://127.0.0.1:5000/

3. **Verify JSON files exist:**
   ```bash
   # These files should exist in your project root:
   - video_calls.json
   - appointments.json
   - patients.json
   - patients_history.json
   ```

4. **Check browser console:**
   - Open Developer Tools (F12)
   - Look at Console tab for specific error messages
   - Check Network tab to see which API call is failing

### 🔧 How to Test the System

#### Test Video Call Request (Patient Side):
1. Start Flask server: `python app.py`
2. Open Patient Portal: http://127.0.0.1:5000/patient
3. Enter Patient ID: `P12345`
4. Click "Request Video Call"
5. Enter reason and submit

#### Test Scheduling (Doctor Side):
1. Open Doctor Portal: http://127.0.0.1:5000/doctor
2. Click "Refresh Requests" in Video Call Requests section
3. You should see the patient's request
4. Click "Schedule" button
5. Fill in date, time, and notes
6. Submit appointment

#### Test Appointment View (Patient Side):
1. Go back to Patient Portal
2. Enter same Patient ID: `P12345`
3. Click "Refresh" in My Appointments section
4. You should see the scheduled appointment

### 📝 API Endpoints Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/request_video_call` | POST | Patient requests video call |
| `/api/get_video_call_requests` | GET | Doctor gets pending requests |
| `/api/mark_request_read/<id>` | POST | Mark request as read |
| `/api/schedule_appointment` | POST | Doctor schedules appointment |
| `/api/get_patient_appointments/<patient_id>` | GET | Get patient's appointments |
| `/api/get_all_appointments` | GET | Doctor gets all appointments |
| `/api/update_appointment_status` | POST | Update appointment status |

### 🐛 Debug Mode

If you're still having issues, check the Flask terminal output for error messages:

```bash
# Run with verbose output
python app.py
```

Look for:
- `404 Not Found` - API endpoint doesn't exist
- `500 Internal Server Error` - Server-side error
- Python traceback - Shows exact error location

### 💡 Quick Fixes

**Clear browser cache:**
- Press Ctrl+Shift+Delete
- Clear cached images and files
- Reload page (Ctrl+F5)

**Reset JSON files:**
If data is corrupted, reset the files:
```bash
echo [] > video_calls.json
echo [] > appointments.json
```

**Check Python dependencies:**
```bash
pip install flask python-dotenv pandas matplotlib pillow
```

### 📞 Support

If issues persist:
1. Check Flask terminal for errors
2. Check browser console (F12)
3. Verify all files are in correct location
4. Ensure no other service is using port 5000
