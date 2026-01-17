# StudioFlow - Real-Time Collaborative Workspace

A Notion-like collaborative workspace application with real-time synchronization, team collaboration, and rich content editing.

![StudioFlow](https://img.shields.io/badge/StudioFlow-Collaborative%20Workspace-teal)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Firebase](https://img.shields.io/badge/Firebase-Realtime%20Database-orange)

## ✨ Features

### 📝 Rich Content Editor
- **Block-based editing** - Text, headings, lists, quotes, code blocks, tables
- **Slash commands** - Type `/` to insert any block type
- **MS Word-style lists** - Auto-numbering and bullet continuation
- **Drag & drop** - Reorder blocks by dragging
- **Right-click menu** - Copy, cut, paste, delete blocks
- **Auto-save** - Changes saved automatically to cloud

### 📊 Data Visualization
- **7 chart types** - Bar, Line, Pie, Doughnut, Radar, Polar Area, Scatter
- **Table to Graph** - Generate charts from table data with one click  
- **Export graphs** - Download as PNG, JPG, or SVG
- **CSV Import/Export** - Work with spreadsheet data

### 👥 Team Collaboration
- **Invite teammates** - Send email invitations
- **Accept/Decline invites** - Manage invitations from Team page
- **Role-based access** - Owner and Member roles
- **Real-time notifications** - Badge shows pending invites

### 🔐 Authentication & Security
- **Firebase Authentication** - Email/password login
- **Secure API** - Token-based authentication
- **User profiles** - Manage your account settings

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | HTML5, CSS3, JavaScript, Bootstrap 5, TailwindCSS |
| Backend | Python, Flask |
| Database | Firebase Realtime Database |
| Auth | Firebase Authentication |
| Charts | Chart.js |
| Export | ReportLab (PDF), Matplotlib |

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Firebase project with Realtime Database enabled
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/studioflow.git
   cd studioflow
   ```

2. **Install Python dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Configure Firebase**
   
   Create `firebase-config.js` in the root folder:
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

4. **Set up Firebase Admin SDK**
   
   Download your service account key from Firebase Console and save as:
   ```
   backend/firebase-adminsdk.json
   ```

5. **Run the application**
   ```bash
   cd backend
   python app.py
   ```

6. **Open in browser**
   ```
   http://localhost:5000
   ```

## 📁 Project Structure

```
studioflow/
├── backend/
│   ├── app.py              # Flask server
│   ├── requirements.txt    # Python dependencies
│   └── firebase-adminsdk.json
├── templates/
│   ├── layout.html         # Base template
│   ├── workspace.html      # Main editor
│   ├── workspaces.html     # Workspace list
│   ├── team.html           # Team management
│   ├── profile.html        # User profile
│   ├── settings.html       # Settings
│   └── help.html           # Help & support
├── firebase-config.js      # Firebase client config
├── firebase-service.js     # Firebase data layer
├── styles.css              # Global styles
├── auth.html               # Login/signup page
├── landing.html            # Landing page
└── README.md
```

## 🎯 Usage

### Creating Content
1. Click on the workspace area
2. Type `/` to open the block menu
3. Select a block type (text, heading, list, table, etc.)
4. Start typing - changes auto-save!

### Working with Tables
1. Type `/table` to insert a table
2. Click cells to edit content
3. Click "Create Graph" below the table to visualize data

### Team Collaboration
1. Go to **Team & Members**
2. Click **Invite Member**
3. Enter teammate's email
4. They'll see the invite and can accept from their Team page

### Exporting
- **PDF** - Click "Export PDF" in toolbar
- **CSV** - Click "Export CSV" for table data
- **Graph Images** - Click PNG/JPG/SVG on any chart

## 🔧 Configuration

### Environment Variables (optional)
```bash
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=your-secret-key
```

### Firebase Rules
```json
{
  "rules": {
    "users": {
      "$uid": {
        ".read": "$uid === auth.uid",
        ".write": "$uid === auth.uid"
      }
    },
    "workspaces": {
      "$workspaceId": {
        ".read": "data.child('members').child(auth.uid).exists()",
        ".write": "data.child('members').child(auth.uid).exists() || !data.exists()"
      }
    },
    "invites": {
      "$email": {
        ".read": "auth.token.email.replace('.', ',') === $email",
        ".write": true
      }
    }
  }
}
```

## 📝 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/csv/import` | POST | Import CSV file |
| `/api/csv/export` | POST | Export data as CSV |
| `/api/export/document` | POST | Export as PDF |
| `/api/user/profile` | POST | Update user profile |
| `/api/user/password` | POST | Change password |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Firebase](https://firebase.google.com/) - Backend as a Service
- [Chart.js](https://www.chartjs.org/) - Charts library
- [Bootstrap](https://getbootstrap.com/) - UI framework
- [Bootstrap Icons](https://icons.getbootstrap.com/) - Icon library
