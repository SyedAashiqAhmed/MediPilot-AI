# 🤖 Setup Gemini AI for Patient Chat

## ✨ What's New

The patient portal now has a fully functional AI chat powered by Google's Gemini API!

---

## 🎯 What It Does

### Patient AI Chat Features:
- ✅ Real-time AI responses
- ✅ Health information and guidance
- ✅ Symptom discussions
- ✅ General medical questions
- ✅ Empathetic and supportive responses
- ✅ Safety reminders (not a substitute for doctors)

---

## 🔑 How to Get Gemini API Key

### Step 1: Go to Google AI Studio
```
https://makersuite.google.com/app/apikey
```

### Step 2: Sign in with Google Account
- Use your Google account
- Accept terms of service

### Step 3: Create API Key
1. Click "Create API Key"
2. Select "Create API key in new project" (or use existing)
3. Copy the API key (starts with "AIza...")

### Step 4: Add to .env File

Create or edit `.env` file in your project root:

```env
GEMINI_API_KEY=AIzaSyC...your_actual_key_here...
```

**IMPORTANT:** Never commit `.env` file to Git!

---

## 📝 Setup Instructions

### Method 1: Create .env File

1. **Copy the example file:**
   ```bash
   copy .env.example .env
   ```

2. **Edit .env file:**
   ```env
   GEMINI_API_KEY=your_actual_gemini_api_key_here
   ```

3. **Save the file**

4. **Restart the server:**
   ```bash
   python app.py
   ```

### Method 2: Manual Creation

1. **Create new file** named `.env` in project root

2. **Add this line:**
   ```
   GEMINI_API_KEY=AIzaSyC...your_key...
   ```

3. **Save and restart server**

---

## ✅ Verify It's Working

### Step 1: Check Server Logs

When you start the server, you should see:
```
Database initialized at: E:\clinicalAi\medcore.db
 * Serving Flask app 'app'
 * Debug mode: on
```

No errors about Gemini API = Good!

### Step 2: Test Patient Chat

1. **Open patient portal:**
   ```
   http://127.0.0.1:5000/patient
   ```

2. **Scroll to "AI Health Assistant" section**

3. **Type a question:**
   ```
   What are common symptoms of flu?
   ```

4. **Click Send**

5. **See AI response!**

---

## 🎨 What You'll See

### With API Key (Working):
```
You: What are common symptoms of flu?

AI: Common flu symptoms include:
• Fever (usually high)
• Chills and sweats
• Headache
• Dry cough
• Muscle aches
• Fatigue
• Nasal congestion

Remember, if symptoms are severe or persist, please consult a healthcare professional.
```

### Without API Key (Not Working):
```
You: What are common symptoms of flu?

AI: I'm sorry, but the AI service is not currently configured. 
Please contact support or add your Gemini API key to enable this feature.
```

---

## 🔧 Troubleshooting

### Problem: "AI service not configured"

**Solution:**
1. Check `.env` file exists
2. Check `GEMINI_API_KEY` is set
3. Check no typos in key
4. Restart server

### Problem: "Invalid API key"

**Solution:**
1. Verify key from Google AI Studio
2. Make sure you copied full key
3. Check no extra spaces
4. Generate new key if needed

### Problem: "Quota exceeded"

**Solution:**
1. Gemini has free tier limits
2. Wait for quota reset
3. Or upgrade to paid plan

### Problem: Server won't start

**Solution:**
1. Check Python packages installed:
   ```bash
   pip install google-generativeai
   ```
2. Check .env file format
3. Check no syntax errors

---

## 📦 Required Package

Make sure you have the Gemini package installed:

```bash
pip install google-generativeai
```

Or add to `requirements.txt`:
```
google-generativeai
```

---

## 🎯 API Endpoint Details

### Endpoint: `/api/patient-chat`
- **Method:** POST
- **Content-Type:** application/json
- **Body:**
  ```json
  {
    "message": "What are symptoms of flu?"
  }
  ```
- **Response:**
  ```json
  {
    "response": "AI response here...",
    "status": "success"
  }
  ```

---

## 🛡️ Safety Features

The AI chat includes:
- ✅ Health-focused prompts
- ✅ Safety disclaimers
- ✅ Empathetic responses
- ✅ Recommends seeing doctors for serious issues
- ✅ Simple, non-technical language
- ✅ Error handling

---

## 💡 Example Questions

Try asking:
- "What are common symptoms of flu?"
- "How can I improve my sleep?"
- "What should I do for a headache?"
- "When should I see a doctor?"
- "How much water should I drink daily?"
- "What are signs of dehydration?"

---

## 🎨 Features

### System Prompt:
The AI is configured to:
- Provide helpful health information
- Be empathetic and supportive
- Remind users it's not medical advice
- Advise seeing doctors for serious symptoms
- Keep responses concise
- Use simple language

### Quick Action Buttons:
- 🤒 Common Symptoms
- 💊 Medication Info
- 🏥 When to See Doctor

---

## 📊 Free Tier Limits

Google Gemini Free Tier:
- **60 requests per minute**
- **1,500 requests per day**
- **1 million tokens per month**

This is usually enough for:
- Small clinics
- Testing
- Development
- Personal use

---

## 🚀 Quick Start

### 1. Get API Key
```
https://makersuite.google.com/app/apikey
```

### 2. Add to .env
```env
GEMINI_API_KEY=your_key_here
```

### 3. Install Package
```bash
pip install google-generativeai
```

### 4. Restart Server
```bash
python app.py
```

### 5. Test Chat
```
http://127.0.0.1:5000/patient
```

---

## ✅ Summary

**What You Need:**
1. Google account
2. Gemini API key (free)
3. `.env` file with key
4. `google-generativeai` package

**What You Get:**
- ✅ Fully functional AI chat
- ✅ Health information
- ✅ Symptom guidance
- ✅ Professional responses
- ✅ Safety features

**Get your API key and start chatting!** 🎉
