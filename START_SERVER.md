# ⚠️ IMPORTANT: Which File to Run

## ✅ CORRECT FILE TO RUN:

```bash
python app.py
```

**This file has ALL features:**
- ✅ Video call requests
- ✅ Appointment scheduling
- ✅ Pharmacy system
- ✅ Prescription management
- ✅ All API endpoints

---

## ❌ DO NOT RUN:

```bash
python dpp.py  ← WRONG! Don't use this!
```

**This file is OLD and missing:**
- ❌ Video call routes
- ❌ Appointment routes
- ❌ Pharmacy routes
- ❌ Prescription routes

**Result if you run dpp.py:**
- 404 errors everywhere
- "Unexpected token '<'" JSON errors
- Video calls won't work
- Appointments won't work
- Pharmacy won't work

---

## 🚀 How to Start Server Correctly

### Step 1: Stop Any Running Python
```bash
# Press Ctrl+C in terminal
# OR run:
Get-Process python | Stop-Process -Force
```

### Step 2: Start Correct Server
```bash
cd e:\clinicalAi
python app.py
```

### Step 3: Verify It's Running
You should see:
```
Database initialized at: E:\clinicalAi\medcore.db
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

**Look for:** `Serving Flask app 'app'` ← Should say **'app'** not 'dpp'!

---

## 🎯 Quick Test After Starting

1. **Open:** http://127.0.0.1:5000/
2. **Click:** Patient Portal
3. **Try:** Request Video Call
4. **Result:** Should work! ✅

If you see 404 errors, you're running the wrong file!

---

## 📋 File Comparison

| Feature | app.py | dpp.py |
|---------|--------|--------|
| Video Calls | ✅ YES | ❌ NO |
| Appointments | ✅ YES | ❌ NO |
| Pharmacy | ✅ YES | ❌ NO |
| Prescriptions | ✅ YES | ❌ NO |
| Patient Portal | ✅ YES | ✅ YES |
| Doctor Portal | ✅ YES | ✅ YES |

**Conclusion:** ALWAYS use `app.py`!

---

## 🔍 How to Tell Which Server is Running

### Check Terminal Output:

**✅ CORRECT (app.py):**
```
* Serving Flask app 'app'
```

**❌ WRONG (dpp.py):**
```
* Serving Flask app 'dpp'
```

### Check Browser:
- If you get 404 errors → Wrong server (dpp.py)
- If everything works → Correct server (app.py)

---

## 💡 Remember:

**ALWAYS RUN:**
```bash
python app.py
```

**NEVER RUN:**
```bash
python dpp.py  ← Don't use this!
```

---

## 🆘 If You Accidentally Run dpp.py

1. **Stop it:** Press Ctrl+C or close terminal
2. **Start correct one:**
   ```bash
   python app.py
   ```
3. **Refresh browser:** Press Ctrl+F5
4. **Test:** Try video call request

---

## ✅ Current Status

**Server is NOW running correctly with app.py!**

All features are working:
- ✅ Video calls
- ✅ Appointments
- ✅ Pharmacy
- ✅ Prescriptions
- ✅ All portals

**You're good to go!** 🎉
