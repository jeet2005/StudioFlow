# Firebase Configuration Setup

## Create firebase-config.js

Create a file named `firebase-config.js` in the root directory with the following content:

```javascript
const firebaseConfig = {
  apiKey: "AIzaSyBLMEco0gu32CUtYI88TGz5CJtdKnrkw7g",
  authDomain: "to-do-8d03e.firebaseapp.com",
  databaseURL: "https://to-do-8d03e-default-rtdb.firebaseio.com",
  projectId: "to-do-8d03e",
  storageBucket: "to-do-8d03e.firebasestorage.app",
  messagingSenderId: "156052254494",
  appId: "1:156052254494:web:e298f63d3617ec46c3a30f",
  measurementId: "G-KL08TW2JH6"
};

export default firebaseConfig;
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
FIREBASE_DATABASE_URL=https://to-do-8d03e-default-rtdb.firebaseio.com
JWT_SECRET_KEY=your-random-secret-key-here
```

## Start the Backend

```bash
cd backend
python app.py
```

The backend will run on `http://localhost:5000`
