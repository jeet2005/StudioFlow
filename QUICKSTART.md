# 🚀 StudioFlow Quick Start Guide

Get StudioFlow running in under 5 minutes!

---

## Prerequisites

- ✅ Python 3.8+ installed
- ✅ Firebase project created
- ✅ Git installed

---

## Step 1: Clone & Install

```bash
# Clone the repository
git clone https://github.com/yourusername/studioflow.git
cd studioflow

# Install Python dependencies
cd backend
pip install flask firebase-admin reportlab matplotlib
```

---

## Step 2: Configure Firebase

### A. Get Firebase Config

1. Go to [Firebase Console](https://console.firebase.google.com)
2. Select your project → ⚙️ Project Settings → General
3. Scroll to "Your apps" → Click **</>** (Web)
4. Copy the config object

### B. Create `firebase-config.js`

Create this file in the project root:

```javascript
const firebaseConfig = {
    apiKey: "YOUR_API_KEY",
    authDomain: "YOUR_PROJECT.firebaseapp.com",
    databaseURL: "https://YOUR_PROJECT-default-rtdb.firebaseio.com",
    projectId: "YOUR_PROJECT_ID",
    storageBucket: "YOUR_PROJECT.appspot.com",
    messagingSenderId: "123456789",
    appId: "1:123456789:web:abc123"
};
window.firebaseConfig = firebaseConfig;
```

### C. Get Admin SDK Key

1. Firebase Console → ⚙️ Project Settings → **Service accounts**
2. Click **Generate new private key**
3. Save the JSON file as `backend/firebase-adminsdk.json`

---

## Step 3: Enable Firebase Services

### A. Enable Authentication
1. Firebase Console → **Authentication** → Get Started
2. Sign-in method → Enable **Email/Password**

### B. Enable Realtime Database
1. Firebase Console → **Realtime Database** → Create Database
2. Choose location → Start in **test mode** (for now)

---

## Step 4: Run the App

```bash
# From the backend folder
python app.py
```

You should see:
```
✅ Firebase Admin SDK initialized successfully
 * Running on http://127.0.0.1:5000
```

---

## Step 5: Open & Use

1. Open http://localhost:5000
2. Click **Get Started** → Create an account
3. Start creating your workspace!

---

## 🎮 How to Use

### Create Content
- Type `/` to open block menu
- Select: text, heading, list, table, code, etc.
- Press **Enter** to create new blocks

### Work with Lists
- Type `/bullet` or `/numbered`
- Press **Enter** to continue the list
- Press **Enter** on empty item to exit list

### Add Charts
1. Click **Add Graph** in toolbar
2. Enter labels and values
3. Choose chart type
4. Click **Insert Graph**

### Charts from Tables
1. Create a table with data
2. Click **Create Graph** button below the table
3. Chart appears automatically!

### Export Graphs
- Click **PNG**, **JPG**, or **SVG** on any chart to download

### Team Collaboration
1. Go to **Team & Members**
2. Click **Invite Member**
3. Enter email address
4. They'll see **Accept** button on their Team page!

---

## 📂 Key Files

| File | Purpose |
|------|---------|
| `backend/app.py` | Flask server |
| `firebase-config.js` | Your Firebase credentials |
| `firebase-service.js` | All Firebase operations |
| `templates/workspace.html` | Main editor |
| `templates/team.html` | Team management |

---

## 🐛 Troubleshooting

### "Firebase SDK not loaded"
- Check that `firebase-config.js` exists and has correct values

### "Not authenticated"
- Make sure you're logged in
- Check that Firebase Auth is enabled

### "Permission denied" in database
- Update Firebase Realtime Database rules (see README.md)

### Charts not showing
- Make sure Chart.js is loaded (check browser console)

---

## 📤 Push to GitHub

```bash
# Initialize git (if not already)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - StudioFlow workspace app"

# Add remote (replace with your repo URL)
git remote add origin https://github.com/yourusername/studioflow.git

# Push
git push -u origin main
```

---

## 🎉 Done!

Your StudioFlow app is now running. Start creating amazing workspaces!

Need help? Check the full [README.md](README.md) for detailed documentation.
