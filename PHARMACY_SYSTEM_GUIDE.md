# 💊 MedCore AI - Pharmacy System Guide

## Overview

The Pharmacy-Employee Portal is a complete prescription management and medicine delivery tracking system that integrates seamlessly with the existing Doctor-Patient workflow.

---

## 🎯 System Workflow

### Complete Patient Journey:

```
1. Patient → Requests Video Call
2. Doctor → Sees Request & Schedules Appointment
3. Doctor → Conducts Video Consultation
4. Doctor → Sends Prescription to Pharmacy
5. Pharmacy → Receives & Prepares Medicines
6. Pharmacy → Marks Ready for Delivery
7. Pharmacy → Delivers to Patient
8. Patient → Tracks Delivery Status
```

---

## 🏥 Three-Portal System

### 1. **Patient Portal** (http://127.0.0.1:5000/patient)
- Request video consultations
- View scheduled appointments
- **NEW:** Track medicine prescriptions & deliveries
- Real-time delivery status updates

### 2. **Doctor Portal** (http://127.0.0.1:5000/doctor)
- View video call requests
- Schedule appointments
- **NEW:** Send prescriptions to pharmacy
- **NEW:** Message pharmacy directly
- Add multiple medicines with dosage details

### 3. **Pharmacy Portal** (http://127.0.0.1:5000/pharmacy)
- **NEW:** View all prescriptions
- **NEW:** Manage prescription status
- **NEW:** Receive doctor messages
- **NEW:** Track deliveries

---

## 📊 Features Breakdown

### Doctor Features:

#### Send Prescription to Pharmacy
- **Patient ID**: Enter patient identifier
- **Priority Levels**: Normal, High, Urgent
- **Multiple Medicines**: Add unlimited medicines
- **Medicine Details**:
  - Name (e.g., Amoxicillin)
  - Dosage (e.g., 500mg)
  - Frequency (e.g., 3 times daily)
  - Duration (e.g., 7 days)
  - Instructions (e.g., Take after meals)
- **Special Notes**: Add pharmacy instructions

#### Direct Messaging
- Send urgent messages to pharmacy
- Link messages to specific prescriptions
- Real-time communication

---

### Pharmacy Features:

#### Dashboard Statistics
- **Pending Orders**: New prescriptions waiting
- **Preparing**: Currently being prepared
- **Ready**: Ready for delivery
- **Unread Messages**: Doctor communications

#### Prescription Management
- **Filter by Status**: View specific prescription types
- **Priority Sorting**: Urgent prescriptions first
- **Status Updates**:
  - Pending → Preparing
  - Preparing → Ready
  - Ready → Delivered
- **Pharmacist Assignment**: Track who handled each prescription

#### Doctor Messages
- View all messages from doctors
- Mark messages as read
- Link to related prescriptions

---

### Patient Features:

#### Prescription Tracking
- View all prescriptions
- Real-time status updates
- Medicine details with dosage
- Doctor's notes and instructions
- Delivery tracking
- Priority indicators

#### Status Indicators:
- 🕐 **Pending**: At pharmacy, not started
- 🧪 **Preparing**: Being prepared by pharmacist
- ✅ **Ready**: Ready for pickup/delivery
- 🚚 **Delivered**: Successfully delivered

---

## 🔄 API Endpoints

### Prescription Routes:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/send_prescription` | POST | Doctor sends prescription |
| `/api/get_prescriptions` | GET | Pharmacy gets all prescriptions |
| `/api/update_prescription_status` | POST | Update prescription status |
| `/api/get_patient_prescriptions/<id>` | GET | Patient views their prescriptions |

### Messaging Routes:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/send_pharmacy_message` | POST | Doctor sends message |
| `/api/get_pharmacy_messages` | GET | Pharmacy gets messages |
| `/api/mark_message_read/<id>` | POST | Mark message as read |

---

## 📁 Data Storage

### New JSON Files:

#### `prescriptions.json`
```json
[
  {
    "id": "RX0001",
    "patient_id": "P12345",
    "patient_name": "Patient P12345",
    "doctor_name": "Dr. Smith",
    "medicines": [
      {
        "name": "Amoxicillin",
        "dosage": "500mg",
        "frequency": "3 times daily",
        "duration": "7 days",
        "instructions": "Take after meals"
      }
    ],
    "notes": "Patient has penicillin allergy - use alternative",
    "priority": "urgent",
    "status": "pending",
    "created_at": "2025-10-30T12:00:00",
    "pharmacist_name": "John Doe"
  }
]
```

#### `pharmacy_messages.json`
```json
[
  {
    "id": "MSG0001",
    "from_name": "Dr. Smith",
    "message": "Please prepare RX0001 urgently",
    "prescription_id": "RX0001",
    "created_at": "2025-10-30T12:05:00",
    "read": false
  }
]
```

---

## 🚀 Quick Start Guide

### Step 1: Start Server
```bash
cd e:\clinicalAi
python app.py
```

### Step 2: Test Complete Workflow

#### As Doctor:
1. Open: http://127.0.0.1:5000/doctor
2. Scroll to "Send Prescription to Pharmacy"
3. Enter Patient ID: `P12345`
4. Select Priority: `Urgent`
5. Click "Add Medicine"
6. Fill in medicine details:
   - Name: `Amoxicillin`
   - Dosage: `500mg`
   - Frequency: `3 times daily`
   - Duration: `7 days`
   - Instructions: `Take after meals`
7. Add notes: `Patient allergic to penicillin`
8. Click "Send to Pharmacy"

#### As Pharmacy:
1. Open: http://127.0.0.1:5000/pharmacy
2. View prescription in dashboard
3. Click "Start Preparing"
4. Enter pharmacist name
5. After preparation, click "Mark Ready"
6. When delivered, click "Mark Delivered"

#### As Patient:
1. Open: http://127.0.0.1:5000/patient
2. Enter Patient ID: `P12345`
3. Scroll to "My Prescriptions & Deliveries"
4. Click "Refresh"
5. View prescription status and details

---

## 🎨 UI Features

### Professional Design:
- ✅ Color-coded status indicators
- ✅ Priority badges (Urgent/High/Normal)
- ✅ Real-time updates
- ✅ Responsive layout
- ✅ Professional medical icons
- ✅ Auto-refresh (30 seconds)

### Status Colors:
- 🟡 **Pending**: Orange (#f59e0b)
- 🔵 **Preparing**: Blue (#3b82f6)
- 🟢 **Ready**: Green (#10b981)
- ⚫ **Delivered**: Gray (#6b7280)

---

## 💡 Usage Tips

### For Doctors:
1. **After Video Call**: Immediately send prescription
2. **Priority Setting**: Use "Urgent" for critical cases
3. **Clear Instructions**: Add detailed medicine instructions
4. **Direct Messaging**: Use for urgent pharmacy communications

### For Pharmacists:
1. **Check Priority**: Handle urgent prescriptions first
2. **Update Status**: Keep patients informed
3. **Read Messages**: Check doctor messages regularly
4. **Add Your Name**: Track who handled each prescription

### For Patients:
1. **Regular Checks**: Refresh to see status updates
2. **Follow Instructions**: Read medicine instructions carefully
3. **Track Delivery**: Know when medicines are ready
4. **Contact Doctor**: If questions about prescription

---

## 🔐 Security Features

- Patient ID validation
- Prescription ID tracking
- Pharmacist accountability
- Timestamped actions
- Message read receipts

---

## 📈 Future Enhancements

Potential additions:
- [ ] SMS notifications for status updates
- [ ] Barcode scanning for medicines
- [ ] Inventory management
- [ ] Delivery address tracking
- [ ] Payment integration
- [ ] Medicine interaction warnings
- [ ] Refill reminders
- [ ] Prescription history analytics

---

## 🐛 Troubleshooting

### Prescription Not Showing:
1. Verify Patient ID is correct
2. Click "Refresh" button
3. Check Flask server is running
4. Verify `prescriptions.json` exists

### Status Not Updating:
1. Check internet connection
2. Refresh the page
3. Verify API endpoints are working
4. Check browser console for errors

### Messages Not Appearing:
1. Verify `pharmacy_messages.json` exists
2. Check message was sent successfully
3. Click "Refresh" in pharmacy portal
4. Check Flask terminal for errors

---

## 📞 Support

For issues or questions:
1. Check `TROUBLESHOOTING.md`
2. Check Flask terminal output
3. Use browser console (F12) for errors
4. Visit http://127.0.0.1:5000/debug for API testing

---

## ✅ System Status

**All Features Implemented:**
- ✅ Prescription sending (Doctor → Pharmacy)
- ✅ Prescription management (Pharmacy)
- ✅ Delivery tracking (Patient)
- ✅ Direct messaging (Doctor → Pharmacy)
- ✅ Status updates (All roles)
- ✅ Priority handling
- ✅ Real-time notifications

**System is fully operational and ready for use!** 🎉
