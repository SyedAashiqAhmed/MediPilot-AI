# 🔄 MedCore AI - Complete System Flow Diagram

## 📊 Overall System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        MEDCORE AI PLATFORM                       │
│                     (Smart City Healthcare)                      │
└─────────────────────────────────────────────────────────────────┘
                                 │
                ┌────────────────┼────────────────┐
                │                │                │
         ┌──────▼──────┐  ┌─────▼─────┐  ┌──────▼──────┐
         │   PATIENT   │  │   DOCTOR  │  │  PHARMACY   │
         │   PORTAL    │  │   PORTAL  │  │   PORTAL    │
         └──────┬──────┘  └─────┬─────┘  └──────┬──────┘
                │                │                │
                └────────────────┼────────────────┘
                                 │
                        ┌────────▼────────┐
                        │   FLASK SERVER  │
                        │   (Backend API) │
                        └────────┬────────┘
                                 │
                ┌────────────────┼────────────────┐
                │                │                │
         ┌──────▼──────┐  ┌─────▼─────┐  ┌──────▼──────┐
         │   DATABASE  │  │  GEMINI   │  │    JSON     │
         │  (SQLite)   │  │    AI     │  │   FILES     │
         └─────────────┘  └───────────┘  └─────────────┘
```

---

## 🔄 Complete User Journey Flow

### **1. PATIENT JOURNEY**

```
START: Patient Opens Portal
         │
         ▼
┌────────────────────┐
│  Homepage Loaded   │
│  - 3D DNA Helix    │
│  - Medical Icons   │
│  - AI Chat Ready   │
└─────────┬──────────┘
          │
          ▼
    ┌─────────┐
    │ OPTIONS │
    └────┬────┘
         │
    ┌────┴────┬────────────┬──────────────┐
    │         │            │              │
    ▼         ▼            ▼              ▼
┌───────┐ ┌──────┐  ┌──────────┐  ┌─────────────┐
│AI Chat│ │Video │  │View      │  │Track        │
│       │ │Call  │  │Records   │  │Prescription │
└───┬───┘ └──┬───┘  └────┬─────┘  └──────┬──────┘
    │        │           │                │
    │        │           │                │
    ▼        ▼           ▼                ▼
```

#### **Option A: AI Chat Flow**
```
Patient Types Question
         │
         ▼
Frontend Sends to /api/patient-chat
         │
         ▼
Backend Receives Message
         │
         ▼
Gemini AI Processes Query
         │
         ▼
AI Generates Response
         │
         ▼
Response Sent to Frontend
         │
         ▼
Patient Sees Answer
         │
         ▼
Can Continue Conversation
```

#### **Option B: Video Call Flow**
```
Patient Clicks "Request Video Call"
         │
         ▼
Enters Patient ID
         │
         ▼
System Validates ID
         │
         ▼
Creates Video Call Request
         │
         ▼
Notification Sent to Doctor
         │
         ▼
Doctor Accepts Request
         │
         ▼
Video Call Initiated
         │
         ▼
Consultation Happens
         │
         ▼
Doctor Sends Prescription
         │
         ▼
Patient Receives Notification
```

#### **Option C: View Medical Records**
```
Patient Enters Patient ID
         │
         ▼
System Queries Database
         │
         ▼
Retrieves Patient Data
         │
         ▼
Displays:
  - Vitals (BP, Heart Rate, etc.)
  - Lab Results
  - Medical History
  - Previous Consultations
         │
         ▼
Patient Can Download/Print
```

#### **Option D: Track Prescription**
```
Patient Enters Patient ID
         │
         ▼
System Queries Prescriptions
         │
         ▼
Displays All Prescriptions:
  - Medicine Names
  - Dosage
  - Status (Pending/Preparing/Ready/Delivered)
  - Pharmacy Details
         │
         ▼
Real-Time Status Updates
         │
         ▼
Notification When Ready
```

---

### **2. DOCTOR JOURNEY**

```
START: Doctor Opens Portal
         │
         ▼
┌────────────────────┐
│  Doctor Dashboard  │
│  - Patient Lookup  │
│  - AI Analysis     │
│  - Prescriptions   │
└─────────┬──────────┘
          │
          ▼
    ┌─────────┐
    │ OPTIONS │
    └────┬────┘
         │
    ┌────┴────┬────────────┬──────────────┐
    │         │            │              │
    ▼         ▼            ▼              ▼
┌────────┐ ┌──────┐  ┌──────────┐  ┌─────────────┐
│Patient │ │Video │  │Send      │  │Message      │
│Lookup  │ │Call  │  │Rx        │  │Pharmacy     │
└───┬────┘ └──┬───┘  └────┬─────┘  └──────┬──────┘
    │         │            │                │
    ▼         ▼            ▼                ▼
```

#### **Option A: Patient Lookup & AI Analysis**
```
Doctor Enters Patient ID
         │
         ▼
System Queries Database
         │
         ▼
Retrieves Complete Patient Data:
  - Demographics
  - Vitals
  - Lab Results
  - Medical History
         │
         ▼
Doctor Clicks "AI Analysis"
         │
         ▼
System Sends Data to Gemini AI
         │
         ▼
AI Analyzes Patient Data
         │
         ▼
AI Generates:
  - Diagnosis Suggestions
  - Recommended Tests
  - Treatment Plan
  - Risk Assessment
         │
         ▼
Doctor Reviews AI Suggestions
         │
         ▼
Doctor Makes Final Decision
```

#### **Option B: Send Prescription**
```
Doctor Fills Prescription Form:
  - Patient ID
  - Medicine Names (multiple)
  - Dosage
  - Frequency
  - Duration
  - Instructions
  - Priority (Normal/High/Urgent)
  - Doctor Notes
         │
         ▼
Clicks "Send to Pharmacy"
         │
         ▼
POST /api/send_prescription
         │
         ▼
System Saves to prescriptions.json
         │
         ▼
Notification Sent to Pharmacy
         │
         ▼
Notification Sent to Patient
         │
         ▼
Success Message to Doctor
```

#### **Option C: Message Pharmacy**
```
Doctor Clicks "Message Pharmacy"
         │
         ▼
Enters Message Text
         │
         ▼
System Asks: "Link to Prescription?"
         │
    ┌────┴────┐
    │         │
   YES       NO
    │         │
    ▼         ▼
Enter Rx ID  Send General Message
    │         │
    └────┬────┘
         │
         ▼
POST /api/send_pharmacy_message
         │
         ▼
Message Saved to pharmacy_messages.json
         │
         ▼
Pharmacy Receives Notification
         │
         ▼
Success Confirmation
```

---

### **3. PHARMACY JOURNEY**

```
START: Pharmacy Opens Portal
         │
         ▼
┌────────────────────┐
│ Pharmacy Dashboard │
│  - Stats Display   │
│  - Prescriptions   │
│  - Messages        │
└─────────┬──────────┘
          │
          ▼
Dashboard Shows:
  - Pending: X prescriptions
  - Preparing: Y prescriptions
  - Ready: Z prescriptions
  - Unread Messages: N
          │
          ▼
    ┌─────────┐
    │ OPTIONS │
    └────┬────┘
         │
    ┌────┴────┬────────────┐
    │         │            │
    ▼         ▼            ▼
┌────────┐ ┌──────┐  ┌──────────┐
│View All│ │Filter│  │View      │
│Rx      │ │Status│  │Messages  │
└───┬────┘ └──┬───┘  └────┬─────┘
    │         │            │
    ▼         ▼            ▼
```

#### **Option A: Process Prescription**
```
Pharmacist Sees New Prescription
         │
         ▼
Clicks "View Details"
         │
         ▼
Modal Shows:
  - Patient Info
  - Medicine List
  - Dosage & Instructions
  - Doctor Notes
  - Priority Level
         │
         ▼
Pharmacist Clicks "Start Preparing"
         │
         ▼
Status Changes: Pending → Preparing
         │
         ▼
POST /api/update_prescription_status
         │
         ▼
Patient Sees Updated Status
         │
         ▼
Pharmacist Prepares Medicines
         │
         ▼
Clicks "Mark as Ready"
         │
         ▼
Status Changes: Preparing → Ready
         │
         ▼
Patient Notified: "Medicine Ready"
         │
         ▼
Delivery/Pickup Arranged
         │
         ▼
Clicks "Mark as Delivered"
         │
         ▼
Status Changes: Ready → Delivered
         │
         ▼
Process Complete
```

#### **Option B: View Doctor Messages**
```
Pharmacist Clicks "Messages" Tab
         │
         ▼
GET /api/get_pharmacy_messages
         │
         ▼
Displays All Messages:
  - From Doctor
  - Timestamp
  - Message Text
  - Linked Prescription ID (if any)
         │
         ▼
Pharmacist Clicks Message
         │
    ┌────┴────┐
    │         │
Has Rx ID?  No Rx ID
    │         │
    ▼         ▼
"View Rx"  "Mark Read"
    │         │
    ▼         │
Opens Rx    │
Details     │
    │         │
    └────┬────┘
         │
         ▼
POST /api/mark_message_read
         │
         ▼
Message Marked as Read
```

---

## 🔄 Data Flow Diagram

### **Complete System Data Flow**

```
┌─────────────┐
│   PATIENT   │
└──────┬──────┘
       │
       │ 1. Request (HTTP)
       ▼
┌─────────────────────┐
│   FLASK SERVER      │
│   (app.py)          │
│                     │
│  Routes:            │
│  - /patient         │
│  - /doctor          │
│  - /pharmacy        │
│  - /api/*           │
└──────┬──────────────┘
       │
       │ 2. Process Request
       │
   ┌───┴───┬─────────┬──────────┐
   │       │         │          │
   ▼       ▼         ▼          ▼
┌──────┐ ┌────┐ ┌────────┐ ┌────────┐
│SQLite│ │JSON│ │Gemini  │ │Business│
│ DB   │ │Files│ │  AI    │ │ Logic  │
└──┬───┘ └─┬──┘ └───┬────┘ └───┬────┘
   │       │        │          │
   │ 3. Query/Store Data       │
   │       │        │          │
   └───────┴────────┴──────────┘
           │
           │ 4. Response Data
           ▼
    ┌──────────────┐
    │   FRONTEND   │
    │  (HTML/JS)   │
    └──────┬───────┘
           │
           │ 5. Display to User
           ▼
    ┌──────────────┐
    │     USER     │
    └──────────────┘
```

---

## 🔄 API Flow Diagram

### **Patient Chat API Flow**

```
Patient Types: "What are flu symptoms?"
         │
         ▼
┌─────────────────────────────────┐
│ Frontend (index.html)           │
│ JavaScript: ptSend()            │
└────────────┬────────────────────┘
             │
             │ POST /api/patient-chat
             │ Body: { "message": "..." }
             ▼
┌─────────────────────────────────┐
│ Backend (app.py)                │
│ @app.route("/api/patient-chat") │
└────────────┬────────────────────┘
             │
             │ 1. Validate message
             │ 2. Check API key
             ▼
┌─────────────────────────────────┐
│ Gemini AI                       │
│ model.generate_content()        │
└────────────┬────────────────────┘
             │
             │ AI Response
             ▼
┌─────────────────────────────────┐
│ Backend Formats Response        │
│ { "response": "...", "status": "success" }
└────────────┬────────────────────┘
             │
             │ JSON Response
             ▼
┌─────────────────────────────────┐
│ Frontend Displays Response      │
│ ptAddMessage(response, 'bot')   │
└─────────────────────────────────┘
```

### **Prescription Flow**

```
Doctor Sends Prescription
         │
         ▼
┌─────────────────────────────────┐
│ Doctor Portal (doctor.html)     │
│ sendPrescription()              │
└────────────┬────────────────────┘
             │
             │ POST /api/send_prescription
             │ Body: { patient_id, medicines[], priority, notes }
             ▼
┌─────────────────────────────────┐
│ Backend (app.py)                │
│ @app.route("/api/send_prescription")
└────────────┬────────────────────┘
             │
             │ 1. Generate Rx ID
             │ 2. Add timestamp
             │ 3. Set status: "Pending"
             ▼
┌─────────────────────────────────┐
│ Save to prescriptions.json      │
│ [{                              │
│   "rx_id": "RX0001",            │
│   "patient_id": "P123",         │
│   "medicines": [...],           │
│   "status": "Pending"           │
│ }]                              │
└────────────┬────────────────────┘
             │
             ├──────────┬──────────┐
             │          │          │
             ▼          ▼          ▼
      ┌─────────┐ ┌─────────┐ ┌─────────┐
      │ Doctor  │ │Pharmacy │ │ Patient │
      │Notified │ │Notified │ │Notified │
      └─────────┘ └─────────┘ └─────────┘
```

---

## 🔄 Real-Time Update Flow

```
Pharmacy Updates Prescription Status
         │
         ▼
POST /api/update_prescription_status
{ "rx_id": "RX0001", "status": "Ready" }
         │
         ▼
Backend Updates prescriptions.json
         │
         ▼
┌────────┴────────┐
│                 │
▼                 ▼
Patient Portal    Pharmacy Portal
Auto-Refresh      Auto-Refresh
(Every 30s)       (Every 30s)
│                 │
▼                 ▼
Shows Updated     Shows Updated
Status            Status
```

---

## 🔄 Database Schema Flow

```
┌─────────────────────────────────────────┐
│           SQLite Database               │
│         (medcore.db)                    │
└─────────────────────────────────────────┘
                    │
        ┌───────────┼───────────┐
        │           │           │
        ▼           ▼           ▼
┌──────────┐ ┌──────────┐ ┌──────────┐
│ Patients │ │  Vitals  │ │   Labs   │
│  Table   │ │  Table   │ │  Table   │
└────┬─────┘ └────┬─────┘ └────┬─────┘
     │            │            │
     │ patient_id │ patient_id │ patient_id
     │ name       │ bp         │ test_name
     │ age        │ heart_rate │ result
     │ gender     │ timestamp  │ timestamp
     └────────────┴────────────┘

┌─────────────────────────────────────────┐
│           JSON Files                    │
└─────────────────────────────────────────┘
                    │
        ┌───────────┼───────────┐
        │           │           │
        ▼           ▼           ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│prescriptions │ │  pharmacy_   │ │   patients   │
│   .json      │ │ messages.json│ │  _history    │
└──────────────┘ └──────────────┘ └──────────────┘
```

---

## 🎨 Visual System Architecture

```
┌────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   Patient    │  │    Doctor    │  │   Pharmacy   │    │
│  │   Portal     │  │    Portal    │  │    Portal    │    │
│  │ (index.html) │  │(doctor.html) │  │(pharmacy.html)│    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
└────────────────────────────────────────────────────────────┘
                            │
                            │ HTTP/HTTPS
                            ▼
┌────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                        │
│  ┌────────────────────────────────────────────────────┐   │
│  │              Flask Web Server (app.py)             │   │
│  │                                                     │   │
│  │  Routes:                    API Endpoints:         │   │
│  │  - /                        - /api/patient-chat    │   │
│  │  - /patient                 - /api/send_prescription│  │
│  │  - /doctor                  - /api/get_prescriptions│  │
│  │  - /pharmacy                - /api/update_status   │   │
│  │                             - /api/get_messages    │   │
│  └────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────┘
                            │
                ┌───────────┼───────────┐
                │           │           │
                ▼           ▼           ▼
┌────────────────────────────────────────────────────────────┐
│                      DATA LAYER                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   SQLite     │  │  JSON Files  │  │  Gemini AI   │    │
│  │  Database    │  │  (Storage)   │  │   (API)      │    │
│  │              │  │              │  │              │    │
│  │ - Patients   │  │ - Rx Data    │  │ - Chat       │    │
│  │ - Vitals     │  │ - Messages   │  │ - Analysis   │    │
│  │ - Labs       │  │ - History    │  │ - Diagnosis  │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
└────────────────────────────────────────────────────────────┘
```

---

## 🔄 Complete Workflow Summary

### **Scenario: Patient Gets Medicine**

```
1. PATIENT REQUESTS CONSULTATION
   Patient → Opens Portal → Requests Video Call
   
2. DOCTOR CONSULTATION
   Doctor → Accepts Call → Examines Patient → AI Analysis
   
3. PRESCRIPTION CREATED
   Doctor → Fills Prescription → Sends to Pharmacy
   
4. PHARMACY RECEIVES
   Pharmacy → Gets Notification → Views Prescription
   
5. PHARMACY PREPARES
   Pharmacy → Starts Preparing → Updates Status
   
6. PATIENT NOTIFIED
   Patient → Receives Notification → Tracks Status
   
7. MEDICINE READY
   Pharmacy → Marks Ready → Patient Notified
   
8. DELIVERY/PICKUP
   Patient → Receives Medicine → Status: Delivered
   
9. COMPLETE
   All parties updated → Process ends
```

---

## 📊 Technology Stack Flow

```
┌─────────────────────────────────────────┐
│          FRONTEND TECHNOLOGIES          │
│  - HTML5, CSS3, JavaScript              │
│  - FontAwesome Icons                    │
│  - Responsive Design                    │
│  - 3D Animations (DNA Helix)            │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│          BACKEND TECHNOLOGIES           │
│  - Python 3.x                           │
│  - Flask Web Framework                  │
│  - Google Generative AI (Gemini)        │
│  - SQLAlchemy ORM                       │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│          DATA TECHNOLOGIES              │
│  - SQLite Database                      │
│  - JSON File Storage                    │
│  - Pandas (Data Processing)             │
│  - Matplotlib (Charts)                  │
└─────────────────────────────────────────┘
```

---

## ✅ Summary

This flowchart shows:
- ✅ Complete user journeys (Patient, Doctor, Pharmacy)
- ✅ Data flow between components
- ✅ API request/response cycles
- ✅ Database interactions
- ✅ Real-time updates
- ✅ System architecture layers
- ✅ Technology stack integration

**Use this for presentations and documentation!**
