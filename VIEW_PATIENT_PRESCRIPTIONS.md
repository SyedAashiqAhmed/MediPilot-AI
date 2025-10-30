# 👨‍⚕️ How to View Patient Prescriptions

## 🎯 Where to Look

**IMPORTANT:** Patient prescriptions are shown in the **PATIENT PORTAL**, not the pharmacy portal!

---

## 📍 Step-by-Step Guide

### Step 1: Open Patient Portal

**URL:** http://127.0.0.1:5000/patient

**Hard Refresh:** Press `Ctrl + Shift + R`

---

### Step 2: Enter Patient ID

At the top of the page, you'll see:
```
┌─────────────────────────────┐
│ Patient ID: [___________]   │
│ [Submit]                    │
└─────────────────────────────┘
```

**Enter:** `P1234511111111123`

**Click:** Submit button

---

### Step 3: Scroll Down to "My Prescriptions & Deliveries"

After entering your Patient ID, scroll down until you see:

```
┌──────────────────────────────────────────┐
│ 💊 My Prescriptions & Deliveries         │
│                                          │
│ Track your medicine prescriptions and    │
│ delivery status                          │
│                                          │
│ [🔄 Refresh]                             │
└──────────────────────────────────────────┘
```

---

### Step 4: Click the Refresh Button

Click the **"🔄 Refresh"** button

---

### Step 5: View Your Prescription

You should now see:

```
┌─────────────────────────────────────────────────┐
│ 💊 Prescription RX0001                          │
│ Prescribed by: Dr. Smith                        │
│                                  [🧪 Preparing] │
│                                                 │
│ ⚠️ HIGH Priority                                │
│                                                 │
│ 💊 Medicines:                                   │
│ ┌─────────────────────────────────────────────┐ │
│ │ Amoxicillin                                 │ │
│ │ Dosage: 500mg | Frequency: 3 times daily   │ │
│ │ Duration: 7 days                            │ │
│ │ 💡 Take after meals with water              │ │
│ └─────────────────────────────────────────────┘ │
│                                                 │
│ ┌─────────────────────────────────────────────┐ │
│ │ Paracetamol                                 │ │
│ │ Dosage: 650mg | Frequency: Twice daily     │ │
│ │ Duration: 5 days                            │ │
│ │ 💡 Take when fever occurs                   │ │
│ └─────────────────────────────────────────────┘ │
│                                                 │
│ 📝 Doctor's Notes:                              │
│ Patient has mild fever and throat infection.    │
│ Monitor temperature.                            │
│                                                 │
│ 📅 PRESCRIBED: 10/30/2025                       │
│ 👨‍⚕️ PHARMACIST: Pharmacist                      │
└─────────────────────────────────────────────────┘
```

---

## 🔍 What You'll See

### Prescription Details:
- ✅ Prescription ID (RX0001)
- ✅ Doctor name (Dr. Smith)
- ✅ Status badge (Preparing - blue color)
- ✅ Priority badge (HIGH - red color)

### Medicine Information:
- ✅ **Medicine Name** (Amoxicillin, Paracetamol)
- ✅ **Dosage** (500mg, 650mg)
- ✅ **Frequency** (3 times daily, Twice daily)
- ✅ **Duration** (7 days, 5 days)
- ✅ **Instructions** (Take after meals, Take when fever occurs)

### Additional Info:
- ✅ Doctor's notes
- ✅ Prescribed date
- ✅ Pharmacist name
- ✅ Current status

---

## 📊 Status Colors

The status badge shows where your prescription is:

- 🟡 **Pending** (Orange) - At pharmacy, not started yet
- 🔵 **Preparing** (Blue) - Being prepared by pharmacist
- 🟢 **Ready** (Green) - Ready for pickup/delivery
- ⚫ **Delivered** (Gray) - Successfully delivered

---

## 🎯 Quick Test

### Test for Patient P1234511111111123:

1. **Open:** http://127.0.0.1:5000/patient
2. **Press:** `Ctrl + Shift + R` (hard refresh)
3. **Enter Patient ID:** P1234511111111123
4. **Click:** Submit
5. **Scroll down** to "My Prescriptions & Deliveries"
6. **Click:** 🔄 Refresh button
7. **See:** Prescription RX0001 with 2 medicines

---

## 🔄 Different Views

### Patient Portal (What YOU see):
- **URL:** http://127.0.0.1:5000/patient
- **Shows:** YOUR prescriptions only
- **Filter by:** Your Patient ID
- **Purpose:** Track your medicine deliveries

### Pharmacy Portal (What PHARMACY sees):
- **URL:** http://127.0.0.1:5000/pharmacy
- **Shows:** ALL prescriptions from all patients
- **Filter by:** Status (Pending, Preparing, Ready)
- **Purpose:** Manage all prescriptions

### Doctor Portal (What DOCTOR sees):
- **URL:** http://127.0.0.1:5000/doctor
- **Shows:** Form to SEND prescriptions
- **Can:** Create new prescriptions
- **Purpose:** Prescribe medicines to patients

---

## ❌ Common Mistakes

### Mistake 1: Looking in Wrong Portal
❌ **Wrong:** Opening pharmacy portal to see YOUR prescriptions
✅ **Right:** Open PATIENT portal with your Patient ID

### Mistake 2: Not Entering Patient ID
❌ **Wrong:** Just scrolling down without entering ID
✅ **Right:** Enter Patient ID first, then scroll and refresh

### Mistake 3: Not Clicking Refresh
❌ **Wrong:** Just scrolling to prescriptions section
✅ **Right:** Click the "🔄 Refresh" button

### Mistake 4: Browser Cache
❌ **Wrong:** Normal refresh (F5)
✅ **Right:** Hard refresh (Ctrl + Shift + R)

---

## 🐛 Troubleshooting

### Problem: "No prescriptions found"

**Check:**
1. ✅ Are you in PATIENT portal? (not pharmacy portal)
2. ✅ Did you enter Patient ID: P1234511111111123?
3. ✅ Did you click Submit?
4. ✅ Did you scroll down to prescriptions section?
5. ✅ Did you click the Refresh button?
6. ✅ Did you hard refresh browser (Ctrl + Shift + R)?

---

### Problem: "Can't see medicine details"

**Solution:**
1. Make sure app.py is running (not dpp.py)
2. Hard refresh: Ctrl + Shift + R
3. Check you're in patient portal
4. Click the Refresh button in prescriptions section

---

## ✅ Summary

**To see prescriptions for Patient P1234511111111123:**

1. Go to: http://127.0.0.1:5000/patient
2. Hard refresh: Ctrl + Shift + R
3. Enter Patient ID: P1234511111111123
4. Click: Submit
5. Scroll down to: "My Prescriptions & Deliveries"
6. Click: 🔄 Refresh button
7. See: Full prescription with all medicine details!

**You should see:**
- Prescription ID: RX0001
- 2 Medicines: Amoxicillin + Paracetamol
- All dosages, frequencies, durations
- Doctor's notes
- Status: Preparing

---

## 🎉 It's Working!

The API test confirmed the prescription exists and has all the data:
- ✅ Medicine names
- ✅ Dosages
- ✅ Frequencies
- ✅ Durations
- ✅ Instructions
- ✅ Doctor's notes

**Just follow the steps above to see it in the patient portal!** 🚀
