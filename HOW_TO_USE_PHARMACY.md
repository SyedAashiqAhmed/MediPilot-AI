# 🏥 How to Use the Pharmacy Portal - Step by Step

## ⚠️ CRITICAL: Always Run app.py (NOT dpp.py!)

```bash
# CORRECT:
python app.py

# WRONG - DON'T USE:
python dpp.py  ← This causes 404 errors!
```

---

## 📋 Current Test Data Available

I've added **3 test prescriptions** for you to see:

### Prescription 1 (RX0001) - HIGH PRIORITY
- **Patient:** P1234511111111123
- **Doctor:** Dr. Smith
- **Status:** Pending
- **Medicines:**
  - Amoxicillin 500mg (3 times daily, 7 days)
  - Paracetamol 650mg (Twice daily, 5 days)
- **Notes:** Patient has mild fever and throat infection

### Prescription 2 (RX0002) - NORMAL PRIORITY
- **Patient:** P12345
- **Doctor:** Dr. Johnson
- **Status:** Preparing (by John Pharmacist)
- **Medicines:**
  - Ibuprofen 400mg (3 times daily, 10 days)
  - Vitamin D3 1000 IU (Once daily, 30 days)
  - Calcium Tablets 500mg (Twice daily, 30 days)
- **Notes:** Vitamin D deficiency and joint pain

### Prescription 3 (RX0003) - URGENT PRIORITY
- **Patient:** P99999
- **Doctor:** Dr. Williams
- **Status:** Ready for delivery
- **Medicines:**
  - Aspirin 75mg (Once daily, Ongoing)
- **Notes:** Long-term prescription for heart health

---

## 🚀 Step-by-Step Guide

### Step 1: Make Sure Correct Server is Running

1. **Stop any running Python:**
   ```bash
   taskkill /F /IM python.exe
   ```

2. **Start app.py:**
   ```bash
   python app.py
   ```

3. **Verify in terminal:**
   ```
   * Serving Flask app 'app'  ← Should say 'app' NOT 'dpp'!
   ```

---

### Step 2: Open Pharmacy Portal

1. **Go to:** http://127.0.0.1:5000/pharmacy
2. **Hard refresh:** Press `Ctrl + Shift + R`

---

### Step 3: View Prescriptions

You should now see:

**Dashboard Stats:**
- 📋 Pending: 1
- 🧪 Preparing: 1
- ✅ Ready: 1
- 💬 Messages: 2

**Prescription List:**
You'll see all 3 prescriptions with:
- ✅ Prescription ID (RX0001, RX0002, RX0003)
- ✅ Patient name
- ✅ Doctor name
- ✅ Priority badge (HIGH, NORMAL, URGENT)
- ✅ Status badge (Pending, Preparing, Ready)
- ✅ **All medicine details:**
  - Medicine name
  - Dosage
  - Frequency
  - Duration
  - Instructions
- ✅ Doctor's notes
- ✅ Action buttons

---

### Step 4: Filter Prescriptions

Use the filter buttons:
- **All** - Shows all 3 prescriptions
- **Pending** - Shows RX0001 only
- **Preparing** - Shows RX0002 only
- **Ready** - Shows RX0003 only

---

### Step 5: Update Prescription Status

#### For Pending Prescription (RX0001):
1. Find RX0001 in the list
2. Click **"Start Preparing"** button
3. Enter your pharmacist name (e.g., "John Doe")
4. Status changes to "Preparing"

#### For Preparing Prescription (RX0002):
1. Find RX0002 in the list
2. Click **"Mark Ready"** button
3. Status changes to "Ready"

#### For Ready Prescription (RX0003):
1. Find RX0003 in the list
2. Click **"Mark Delivered"** button
3. Status changes to "Delivered"

---

### Step 6: View Doctor Messages

Scroll down to **"Doctor Messages"** section:
- You'll see 2 messages from Dr. Smith
- Click **"Mark as Read"** to mark them

---

## 🎯 What You Should See

### Each Prescription Card Shows:

```
┌─────────────────────────────────────────┐
│ 💊 Prescription RX0001                  │
│ Prescribed by: Dr. Smith                │
│                                         │
│ ⚠️ HIGH Priority                        │
│                                         │
│ 💊 Medicines:                           │
│ ┌─────────────────────────────────────┐ │
│ │ Amoxicillin                         │ │
│ │ Dosage: 500mg                       │ │
│ │ Frequency: 3 times daily            │ │
│ │ Duration: 7 days                    │ │
│ │ 💡 Take after meals with water      │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ ┌─────────────────────────────────────┐ │
│ │ Paracetamol                         │ │
│ │ Dosage: 650mg                       │ │
│ │ Frequency: Twice daily              │ │
│ │ Duration: 5 days                    │ │
│ │ 💡 Take when fever occurs           │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ 📝 Doctor's Notes:                      │
│ Patient has mild fever and throat       │
│ infection. Monitor temperature.         │
│                                         │
│ [Start Preparing] button                │
└─────────────────────────────────────────┘
```

---

## 🔍 Troubleshooting

### Problem: "No prescriptions found"

**Causes:**
1. ❌ Running dpp.py instead of app.py
2. ❌ Browser cache showing old page
3. ❌ Server not restarted

**Solutions:**
1. ✅ Stop dpp.py, start app.py
2. ✅ Hard refresh: `Ctrl + Shift + R`
3. ✅ Check terminal shows "Serving Flask app 'app'"

---

### Problem: "Can't see medicine names"

**Causes:**
1. ❌ prescriptions.json was empty
2. ❌ Wrong server running

**Solutions:**
1. ✅ I just added 3 test prescriptions
2. ✅ Make sure app.py is running
3. ✅ Hard refresh browser

---

### Problem: "404 errors"

**Cause:** Running dpp.py

**Solution:**
```bash
# Stop wrong server
taskkill /F /IM python.exe

# Start correct server
python app.py
```

---

## 📊 Test Workflow

### Complete Test:

1. **Open Pharmacy Portal**
   - http://127.0.0.1:5000/pharmacy

2. **See Dashboard Stats**
   - Pending: 1
   - Preparing: 1
   - Ready: 1

3. **Click "Pending" Filter**
   - Should show only RX0001

4. **Click "Start Preparing" on RX0001**
   - Enter your name
   - Watch it move to "Preparing"

5. **Click "All" Filter**
   - Now see 2 preparing, 1 ready

6. **Click "Mark Ready" on any preparing**
   - Watch it move to "Ready"

7. **Click "Mark Delivered" on ready prescription**
   - Watch it move to "Delivered"

---

## ✅ Checklist

Before reporting issues:
- [ ] Running app.py (NOT dpp.py)
- [ ] Terminal shows "Serving Flask app 'app'"
- [ ] Hard refreshed browser (Ctrl + Shift + R)
- [ ] Checked http://127.0.0.1:5000/pharmacy
- [ ] prescriptions.json has data (3 prescriptions)

---

## 🎉 You Should Now See:

✅ **Dashboard with stats**
✅ **3 prescriptions in the list**
✅ **All medicine details:**
   - Medicine names
   - Dosages
   - Frequencies
   - Durations
   - Instructions
✅ **Doctor's notes**
✅ **Priority badges**
✅ **Status badges**
✅ **Action buttons**
✅ **Doctor messages**

**Everything should be working perfectly now!** 🚀
