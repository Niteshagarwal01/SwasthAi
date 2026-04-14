# SwasthAI — API Integration & Setup Documentation

Complete guide to obtaining API keys and configuring WhatsApp, Twilio, and Vapi for the SwasthAI rural health assistant.

---

## Table of Contents
1. [WhatsApp Cloud API (Free)](#1-whatsapp-cloud-api-free)
2. [Twilio (Phone Number)](#2-twilio-phone-number)
3. [Vapi AI Voice Agent](#3-vapi-ai-voice-agent)
4. [Connecting Everything](#4-connecting-everything)
5. [Testing Locally with ngrok](#5-testing-locally-with-ngrok)
6. [Environment Variables Reference](#6-environment-variables-reference)

---

## 1. WhatsApp Cloud API (Free)

The Meta WhatsApp Cloud API is **completely free** for development and provides 1,000 free conversations per month.

### Step 1: Create a Meta Developer Account
1. Go to **[developers.facebook.com](https://developers.facebook.com/)**
2. Click **"Get Started"** or **"My Apps"** in the top right
3. Sign in with your Facebook account (or create one)
4. Complete the developer registration if prompted

### Step 2: Create an App
1. Click **"Create App"**
2. Select **"Other"** as the use case → Click **Next**
3. Select **"Business"** as the app type → Click **Next**
4. App name: **"SwasthAI"** → Click **Create App**

### Step 3: Add WhatsApp Product
1. In your app dashboard, scroll down to **"Add products to your app"**
2. Find **"WhatsApp"** → Click **"Set Up"**
3. You'll be redirected to the **WhatsApp Getting Started** page

### Step 4: Get Your Credentials
On the Getting Started page, you'll immediately see:

| Credential | Location | Example |
|---|---|---|
| **Temporary Access Token** | Under "Temporary access token" section → Click **"Copy"** | `EAAGxyz...` |
| **Phone Number ID** | Under "From" dropdown → The numeric ID shown | `123456789012345` |
| **Test Phone Number** | Meta provides a sandbox number automatically | `+1 555 xxx xxxx` |

> ⚠️ **The temporary token expires every 24 hours.** For the hackathon, just regenerate it before your demo. For production, you'd create a System User token.

### Step 5: Add Test Recipients
1. On the same Getting Started page, look for the **"To"** field
2. Click **"Manage phone number list"**
3. Click **"Add phone number"**
4. Enter your personal WhatsApp number (e.g., `+91XXXXXXXXXX`)
5. You'll receive a verification code on WhatsApp — enter it
6. You can add up to **5 test numbers** for free

### Step 6: Configure Webhook (After Deploying Backend)
1. In the left sidebar, go to **WhatsApp → Configuration**
2. Under **Webhook**, click **"Edit"**
3. Enter:
   - **Callback URL:** `https://your-backend-url.com/webhook/whatsapp`
   - **Verify Token:** `swasthai_webhook_verify_2024`
4. Click **"Verify and Save"**
5. Under **Webhook fields**, click **"Subscribe"** next to **"messages"**

### Step 7: Update Your `.env`
```env
WHATSAPP_TOKEN=EAAGxyz...your_temporary_token_here
WHATSAPP_PHONE_NUMBER_ID=123456789012345
WHATSAPP_VERIFY_TOKEN=swasthai_webhook_verify_2024
```

### Quick Test (After Backend is Running)
Send a WhatsApp message to the sandbox number from a verified phone. You should see:
- The message arrives at your backend (`/webhook/whatsapp`)
- The AI engine processes symptoms
- A response is sent back to WhatsApp

---

## 2. Twilio (Phone Number)

Twilio provides the **actual phone number** that users call. Trial accounts are free.

### Step 1: Create a Twilio Account
1. Go to **[twilio.com/try-twilio](https://www.twilio.com/try-twilio)**
2. Sign up with email
3. Verify your email address
4. Verify your phone number (Twilio sends an SMS code)
5. Answer the onboarding questions (select "Voice" as your product)

### Step 2: Get Your Credentials
After login, you land on the **Console Dashboard**. You'll see:

| Credential | Location | Format |
|---|---|---|
| **Account SID** | Displayed on dashboard | `AC` + 32 hex characters |
| **Auth Token** | Click **"Show"** to reveal | 32 hex characters |

### Step 3: Get a Free Phone Number
1. In the Console, go to **Phone Numbers → Manage → Buy a number**
2. Or click the **"Get a trial number"** button on the dashboard
3. Twilio will assign you a free US number with Voice capability
4. Click **"Choose this number"**

### Step 4: Add Verified Caller IDs
> ⚠️ On trial accounts, you can only make/receive calls from **verified numbers**.

1. Go to **Phone Numbers → Manage → Verified Caller IDs**
2. Click **"Add a new Caller ID"**
3. Enter your phone number → Twilio sends a verification call
4. Enter the code → Done

### Step 5: Update Your `.env`
```env
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_PHONE_NUMBER=+1xxxxxxxxxx
```

---

## 3. Vapi AI Voice Agent

Vapi is the **AI voice layer** that sits between Twilio and your Groq AI engine. It handles:
- **Speech-to-Text**: Converts what the caller says into text
- **LLM Call**: Sends text to your AI engine (Groq via your backend)
- **Text-to-Speech**: Converts AI response back to speech

### How the Call Flow Works
```
User dials Twilio number
    ↓
Twilio routes call to Vapi (auto-configured)
    ↓
Vapi records caller's speech → converts to text
    ↓
Vapi sends text to your backend: POST /webhook/vapi
    ↓
Your backend sends symptoms to Groq AI engine
    ↓
Groq returns health assessment
    ↓
Your backend returns text response to Vapi
    ↓
Vapi speaks the response to the caller via TTS
    ↓
Conversation continues until caller hangs up
    ↓
Vapi sends end-of-call report → Your backend saves to DB
```

### Step 1: Create a Vapi Account
1. Go to **[vapi.ai](https://vapi.ai/)**
2. Click **"Sign Up"** (free tier includes 10 minutes of calls)
3. Complete registration

### Step 2: Get Your API Key
1. After login, go to **Dashboard** or **Organization Settings**
2. Find and copy your **API Key**

### Step 3: Create a Voice Assistant
1. Go to **Assistants** in the sidebar
2. Click **"Create Assistant"** → Start from scratch
3. Configure it:

| Setting | Value |
|---|---|
| **Name** | `SwasthAI Voice Agent` |
| **Model / Provider** | Select **"Custom LLM"** |
| **Custom LLM URL** | `https://your-backend-url.com/webhook/vapi` |
| **First Message** | `Namaste! Main SwasthAI hoon. Aap mujhe apni takleef bataiye, main aapki madad karunga. Hello, I'm SwasthAI. Please describe your symptoms and I'll help you.` |
| **Voice Provider** | `Azure` or `ElevenLabs` |
| **Voice** | For Hindi: `hi-IN-SwaraNeural` (Azure) or any Hindi voice |
| **Language** | `Hindi (hi-IN)` or `Multilingual` |
| **End Call Phrases** | `Thank you, Dhanyavaad, Bye, Shukriya` |
| **Max Duration** | `300` (5 minutes per call) |

4. Click **Save**
5. Copy the **Assistant ID** from the URL or assistant details

### Step 4: Import Your Twilio Number into Vapi
1. In Vapi sidebar, go to **Phone Numbers**
2. Click **"Import"** → Select **"Twilio"**
3. Paste your **Twilio Account SID** and **Auth Token**
4. Your Twilio phone number will appear in the list
5. Click on it → **Assign** it to your `SwasthAI Voice Agent` assistant
6. Done! Vapi now handles all calls to that number.

### Step 5: Update Your `.env`
```env
VAPI_API_KEY=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
VAPI_ASSISTANT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

### Alternative: Use Groq Directly in Vapi (Simpler)
If you don't want to route through your backend for voice calls:
1. Instead of "Custom LLM", select **"Groq"** as the model provider
2. Paste your **Groq API Key**
3. Select model: `llama-3.3-70b-versatile`
4. Paste the system prompt from the assistant configuration
5. This skips your backend entirely — Vapi talks directly to Groq

> **Trade-off:** Simpler setup, but voice calls won't be logged in your database or dashboard. Best for quick demo.

---

## 4. Connecting Everything

### Architecture Diagram
```
                    ┌─────────────────┐
                    │   Your Phone     │
                    │  (WhatsApp app)  │
                    └────────┬────────┘
                             │ sends message
                             ▼
                    ┌─────────────────┐
                    │  Meta Cloud API  │
                    │  (WhatsApp)      │
                    └────────┬────────┘
                             │ POST /webhook/whatsapp
                             ▼
┌─────────────┐    ┌─────────────────┐    ┌──────────────┐
│  Twilio     │───▶│  YOUR BACKEND   │───▶│  Groq API    │
│  (phone #)  │    │  FastAPI :8000  │    │  LLaMA 3.3   │
└──────┬──────┘    └────────┬────────┘    └──────────────┘
       │                    │
       ▼                    ▼
┌─────────────┐    ┌─────────────────┐
│  Vapi       │    │  Neon PostgreSQL │
│  (voice AI) │    │  (cases, alerts) │
└─────────────┘    └─────────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  React Dashboard │
                    │  localhost:5173   │
                    └─────────────────┘
```

### Order of Configuration
1. ✅ Groq API key (already done)
2. ✅ Neon database (already done)
3. ✅ Clerk auth (already done)
4. 🔧 Meta WhatsApp Cloud API → get token + phone number ID
5. 🔧 Twilio → get SID + auth token + phone number
6. 🔧 Vapi → create assistant + import Twilio number
7. 🔧 Deploy backend (or use ngrok) → set webhook URLs
8. 🔧 Set Meta webhook URL → subscribe to messages

---

## 5. Testing Locally with ngrok

For local development, you need a public URL for webhooks. **ngrok** gives you one for free.

### Install ngrok
```bash
# Windows (via chocolatey)
choco install ngrok

# Or download from https://ngrok.com/download
```

### Expose Your Backend
```bash
# Start your backend first
cd backend
uvicorn api.main:app --reload --port 8000

# In another terminal, expose it
ngrok http 8000
```

ngrok will output something like:
```
Forwarding  https://a1b2c3d4.ngrok.io → http://localhost:8000
```

### Use the ngrok URL for Webhooks
- **WhatsApp webhook:** `https://a1b2c3d4.ngrok.io/webhook/whatsapp`
- **Vapi Custom LLM:** `https://a1b2c3d4.ngrok.io/webhook/vapi`

> ⚠️ The ngrok URL changes every time you restart it (on free tier). Update your webhook URLs accordingly.

---

## 6. Environment Variables Reference

Here's your complete `.env` file with all variables:

```env
# ── ALREADY CONFIGURED ✅ ──────────────────────────────────

# Groq AI
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Neon PostgreSQL (asyncpg format)
DATABASE_URL=postgresql+asyncpg://user:password@ep-xxx-pooler.region.aws.neon.tech/neondb?ssl=true

# Clerk Auth
CLERK_SECRET_KEY=sk_test_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
CLERK_PUBLISHABLE_KEY=pk_test_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# ── NEED TO CONFIGURE 🔧 ──────────────────────────────────

# Meta WhatsApp Cloud API
WHATSAPP_TOKEN=                    ← Get from developers.facebook.com
WHATSAPP_PHONE_NUMBER_ID=          ← Get from developers.facebook.com
WHATSAPP_VERIFY_TOKEN=swasthai_webhook_verify_2024

# Twilio
TWILIO_ACCOUNT_SID=                ← Get from twilio.com console
TWILIO_AUTH_TOKEN=                 ← Get from twilio.com console
TWILIO_PHONE_NUMBER=               ← Get from twilio.com (buy free number)

# Vapi
VAPI_API_KEY=                      ← Get from vapi.ai dashboard
VAPI_ASSISTANT_ID=                 ← Run: python -m scripts.setup_vapi

# ── APP CONFIG ─────────────────────────────────────────────
APP_ENV=development
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:5173
```

---

## Quick Start Checklist

- [ ] Sign up at [developers.facebook.com](https://developers.facebook.com)
- [ ] Create app → Add WhatsApp → Copy token + phone number ID
- [ ] Add your phone as test recipient
- [ ] Sign up at [twilio.com](https://www.twilio.com/try-twilio)
- [ ] Copy Account SID + Auth Token + Get phone number
- [ ] Sign up at [vapi.ai](https://vapi.ai)
- [ ] Create assistant (Custom LLM mode)
- [ ] Import Twilio number into Vapi
- [ ] Update `.env` with all credentials
- [ ] Start backend: `uvicorn api.main:app --reload --port 8000`
- [ ] Start frontend: `npm run dev`
- [ ] Expose backend with ngrok: `ngrok http 8000`
- [ ] Set webhook URLs in Meta + Vapi
- [ ] Send a test WhatsApp message!
