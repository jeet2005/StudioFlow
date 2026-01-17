# Firebase Configuration Setup

## Create firebase-config.js

Create a file named `firebase-config.js` in the root directory with the following content:

```javascript
const firebaseConfig = {
    apiKey: "YOUR_API_KEY",
    authDomain: "YOUR_PROJECT.firebaseapp.com",
    databaseURL: "https://YOUR_PROJECT.firebaseio.com",
    projectId: "YOUR_PROJECT_ID",
    storageBucket: "YOUR_PROJECT.appspot.com",
    messagingSenderId: "YOUR_SENDER_ID",
    appId: "YOUR_APP_ID"
};
window.firebaseConfig = firebaseConfig;
```

## Enable Authentication in Firebase Console

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project: `to-do-8d03e`
3. Navigate to **Authentication** → **Sign-in method**
4. Enable:
   - **Email/Password**
   - **Google** (optional, for Google OAuth)

## Backend Credentials

Create `backend/firebase-credentials.json` with your Firebase Admin SDK credentials:

1. Go to Firebase Console → Project Settings → Service Accounts
2. Click "Generate new private key"
3. Save the JSON file as `firebase-credentials.json` in the `backend/` folder

## Environment Variables (Optional)

Create `backend/.env`:

```
FIREBASE_DATABASE_URL=FIREBASE_DATABASE_URL
JWT_SECRET_KEY=your-random-secret-key-here
```

## Start the Backend

```bash
cd backend
python app.py
```

The backend will run on `http://localhost:5000`
