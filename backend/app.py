from flask import Flask, request, jsonify, send_file, render_template, redirect
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, db
import os
import json
from io import BytesIO
from services.export_service import ExportService
from services.auth_service import AuthService, require_auth
from services.csv_service import CSVService
from services.graph_service import GraphService

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Serve static files from the parent directory (project root)
app = Flask(__name__,
            static_folder='../',
            static_url_path='',
            template_folder='../templates')
CORS(app)  # Enable CORS for frontend access

@app.route('/')
def home():
    return send_file('../landing.html')

@app.route('/auth')
def auth_page():
    return send_file('../auth.html')

# ============================================================================
# APP ROUTES (MPA)
# ============================================================================
@app.route('/app')
def app_home():
    return redirect('/app/workspace')

@app.route('/app/workspace')
def view_workspace():
    return render_template('workspace.html', page='workspace')

@app.route('/app/team')
def view_team():
    return render_template('team.html', page='team')

@app.route('/app/settings')
def view_settings():
    return render_template('settings.html', page='settings')

@app.route('/app/profile')
def view_profile():
    return render_template('profile.html', page='profile')

@app.route('/app/help')
def view_help():
    return render_template('help.html', page='help')

@app.route('/app/workspaces')
def view_workspaces():
    return render_template('workspaces.html', page='workspaces')

# Initialize Firebase Admin SDK
def init_firebase():
    try:
        cred_path = os.path.join(os.path.dirname(__file__), 'firebase-credentials.json')
        if os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred, {
                'databaseURL': os.getenv('FIREBASE_DATABASE_URL', 'https://YOUR_PROJECT_ID.firebaseio.com')
            })
            print('✅ Firebase Admin SDK initialized')
        else:
            print('⚠️  Firebase credentials not found. Some features may not work.')
    except Exception as e:
        print(f'❌ Firebase initialization error: {e}')

init_firebase()

# Initialize services
export_service = ExportService()
auth_service = AuthService()
csv_service = CSVService()
graph_service = GraphService()


# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@app.route('/api/auth/verify', methods=['POST'])
def verify_token():
    """Verify Firebase ID token and create session"""
    try:
        data = request.json
        id_token = data.get('idToken')
        
        if not id_token:
            return jsonify({'error': 'No token provided'}), 400
        
        decoded = auth_service.verify_firebase_token(id_token)
        if not decoded:
            return jsonify({'error': 'Invalid token'}), 401
        
        # Create session token
        session_token = auth_service.create_session_token(
            decoded['uid'],
            decoded.get('email', '')
        )
        
        # Get user info
        user_info = auth_service.get_user_info(decoded['uid'])
        
        return jsonify({
            'sessionToken': session_token,
            'user': user_info
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/user', methods=['GET'])
@require_auth
def get_current_user():
    """Get current authenticated user info"""
    try:
        user_id = request.user.get('uid') or request.user.get('user_id')
        user_info = auth_service.get_user_info(user_id)
        return jsonify({'user': user_info})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/profile', methods=['POST'])
@require_auth
def update_profile():
    """Update user profile"""
    try:
        data = request.json
        uid = request.user.get('uid') or request.user.get('user_id')
        
        updates = {}
        if 'displayName' in data:
            updates['display_name'] = data['displayName']
        if 'photoURL' in data:
            updates['photo_url'] = data['photoURL']
        if 'email' in data:
            updates['email'] = data['email']
            
        updated_user = auth_service.update_user(uid, **updates)
        return jsonify({'success': True, 'user': updated_user})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/user/password', methods=['POST'])
@require_auth
def update_password():
    """Update user password"""
    try:
        data = request.json
        password = data.get('password')
        uid = request.user.get('uid') or request.user.get('user_id')
        
        if not password or len(password) < 6:
             return jsonify({'error': 'Password must be at least 6 characters'}), 400
             
        auth_service.update_user(uid, password=password)
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# ============================================================================
# CSV IMPORT/EXPORT ENDPOINTS
# ============================================================================

@app.route('/api/csv/import', methods=['POST'])
@require_auth
def import_csv():
    """Import CSV file"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Read file content
        file_content = file.read()
        
        # Import CSV
        result = csv_service.import_csv(file_content)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/csv/export', methods=['POST'])
@require_auth
def export_csv():
    """Export data to CSV"""
    try:
        data = request.json
        csv_bytes = csv_service.export_to_csv(data)
        
        return send_file(
            BytesIO(csv_bytes),
            mimetype='text/csv',
            as_attachment=True,
            download_name='export.csv'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/csv/validate', methods=['POST'])
@require_auth
def validate_csv():
    """Validate CSV file"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        file_content = file.read()
        
        result = csv_service.validate_csv(file_content)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500





# History Routes
@app.route('/api/history/<workspace_id>', methods=['GET'])
@require_auth
def get_history(workspace_id):
    try:
        from services.history_service import HistoryService
        history_service = HistoryService()
        history = history_service.get_history(workspace_id)
        return jsonify(history)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/history/<workspace_id>/restore/<snapshot_id>', methods=['POST'])
@require_auth
def restore_version(workspace_id, snapshot_id):
    try:
        from services.history_service import HistoryService
        history_service = HistoryService()
        success = history_service.restore_version(workspace_id, snapshot_id)
        if success:
             return jsonify({'success': True})
        return jsonify({'error': 'Failed to restore'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/history/<workspace_id>/save', methods=['POST'])
@require_auth
def save_snapshot(workspace_id):
    try:
        from services.history_service import HistoryService
        data = request.json
        content = data.get('content')
        user_id = data.get('userId') # Or use request.user['uid']
        
        if not content:
             return jsonify({'error': 'Content required'}), 400
             
        history_service = HistoryService()
        snap_id = history_service.save_snapshot(workspace_id, content, user_id)
        return jsonify({'snapshotId': snap_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500




# ============================================================================
# EXPORT ENDPOINTS
# ============================================================================

@app.route('/api/export/document', methods=['POST'])
@require_auth
def export_document():
    """Export document to various formats"""
    try:
        data = request.json
        export_format = data.get('format', 'markdown')
        content = data.get('content', {})
        title = data.get('title', 'Untitled Document')
        
        if export_format == 'pdf':
            pdf_bytes = export_service.export_to_pdf(content, title)
            return send_file(
                BytesIO(pdf_bytes),
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f'{title}.pdf'
            )
        
        elif export_format == 'markdown':
            markdown_text = export_service.export_to_markdown(content)
            return send_file(
                BytesIO(markdown_text.encode('utf-8')),
                mimetype='text/markdown',
                as_attachment=True,
                download_name=f'{title}.md'
            )
        
        elif export_format == 'html':
            html_text = export_service.export_to_html(content, title)
            return send_file(
                BytesIO(html_text.encode('utf-8')),
                mimetype='text/html',
                as_attachment=True,
                download_name=f'{title}.html'
            )
        
        elif export_format == 'json':
            json_data = json.dumps(content, indent=4)
            return send_file(
                BytesIO(json_data.encode('utf-8')),
                mimetype='application/json',
                as_attachment=True,
                download_name=f'{title}.json'
            )
        
        else:
            return jsonify({'error': 'Unsupported format'}), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# WORKSPACE ENDPOINTS
# ============================================================================

@app.route('/api/workspace/<workspace_id>', methods=['GET'])
@require_auth
def get_workspace(workspace_id):
    """Get workspace data from Firebase"""
    try:
        if not firebase_admin._apps:
            return jsonify({'error': 'Firebase not initialized'}), 500
        
        ref = db.reference(f'workspaces/{workspace_id}')
        data = ref.get()
        
        return jsonify({
            'workspaceId': workspace_id,
            'data': data
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'Notion Clone Backend',
        'version': '2.0.0',
        'features': [
            'authentication',
            'csv-import-export',
            'reminders',
            'notifications',
            'pdf-export'
        ]
    })

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


# ============================================================================
# TEAM ENDPOINTS
# ============================================================================

@app.route('/api/team/invite', methods=['POST'])
@require_auth
def invite_member():
    try:
        data = request.json
        email = data.get('email')
        workspace_id = data.get('workspaceId')
        
        if not email or not workspace_id:
            return jsonify({'error': 'Email and Workspace ID required'}), 400
            
        # 1. Save to Workspace node
        inv_ref = db.reference(f'workspaces/{workspace_id}/invites')
        new_invite = inv_ref.push({
            'email': email, 
            'status': 'pending', 
            'invitedBy': request.user.get('uid'),
            'timestamp': {'.sv': 'timestamp'}
        })
        
        # 2. Save to Global Invites node (indexed by email) for the target user to find
        safe_email = email.replace('.', ',')
        user_inv_ref = db.reference(f'invites/{safe_email}')
        user_inv_ref.child(new_invite.key).set({
            'workspaceId': workspace_id,
            'workspaceName': db.reference(f'workspaces/{workspace_id}/name').get() or "Unnamed Workspace",
            'invitedBy': request.user.get('uid'),
            'status': 'pending',
            'timestamp': {'.sv': 'timestamp'}
        })
        
        return jsonify({
            'success': True, 
            'message': f'Invite sent to {email}',
            'inviteId': new_invite.key
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/invites', methods=['GET'])
@require_auth
def get_user_invites():
    """Get all pending invites for the current user's email"""
    try:
        user_email = request.user.get('email')
        if not user_email:
            return jsonify({'invites': []})
            
        safe_email = user_email.replace('.', ',')
        invites = db.reference(f'invites/{safe_email}').get()
        
        if not invites:
            return jsonify({'invites': []})
            
        return jsonify({'invites': invites})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/invites/respond', methods=['POST'])
@require_auth
def respond_to_invite():
    """Accept or Reject an invite"""
    try:
        data = request.json
        invite_id = data.get('inviteId')
        action = data.get('action') # 'accept' or 'reject'
        workspace_id = data.get('workspaceId')
        user_email = request.user.get('email')
        uid = request.user.get('uid') or request.user.get('user_id')
        
        if not invite_id or not action or not workspace_id:
             return jsonify({'error': 'Missing required fields'}), 400
             
        safe_email = user_email.replace('.', ',')
        
        if action == 'accept':
            # 1. Add user to workspace members
            db.reference(f'workspaces/{workspace_id}/members').update({uid: 'member'})
            # 2. Update invite status in workspace
            db.reference(f'workspaces/{workspace_id}/invites/{invite_id}').update({'status': 'accepted'})
            # 3. Update invite status in global invites
            db.reference(f'invites/{safe_email}/{invite_id}').update({'status': 'accepted'})
        else:
            # Update status to rejected
            db.reference(f'workspaces/{workspace_id}/invites/{invite_id}').update({'status': 'rejected'})
            db.reference(f'invites/{safe_email}/{invite_id}').update({'status': 'rejected'})
            
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/workspaces/list', methods=['GET'])
@require_auth
def list_workspaces():
    """List all workspaces the user is a member of"""
    try:
        uid = request.user.get('uid') or request.user.get('user_id')
        # This is a bit slow in RTDB (scanning all workspaces)
        # In a real app, we'd have a /users/{uid}/workspaces list
        all_workspaces = db.reference('workspaces').get()
        
        user_workspaces = []
        if all_workspaces:
            for wid, wdata in all_workspaces.items():
                members = wdata.get('members', {})
                if uid in members:
                    user_workspaces.append({
                        'id': wid,
                        'name': wdata.get('name', 'Unnamed'),
                        'role': members[uid]
                    })
        
        return jsonify({'workspaces': user_workspaces})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/workspaces/create', methods=['POST'])
@require_auth
def create_workspace():
    """Create a new workspace in Firebase"""
    try:
        data = request.json
        name = data.get('name', 'New Workspace')
        uid = request.user.get('uid') or request.user.get('user_id')
        
        workspace_ref = db.reference('workspaces').push({
            'name': name,
            'owner': uid,
            'members': {uid: 'owner'},
            'createdAt': {'.sv': 'timestamp'}
        })
        
        return jsonify({
            'success': True,
            'workspaceId': workspace_ref.key,
            'name': name
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/graphs/process', methods=['POST'])
@require_auth
def process_graph():
    """Process graph data and return Matplotlib image"""
    try:
        data = request.json
        # Use the NEW matplotlib generation method
        result = graph_service.generate_matplotlib_plot(data)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print('🚀 Starting Notion Clone Backend Server...')
    print('📡 Server running on http://localhost:5000')
    print('📝 API Endpoints:')
    print('   Authentication:')
    print('     - POST /api/auth/verify')
    print('     - GET  /api/auth/user')
    print('   CSV:')
    print('     - POST /api/csv/import')
    print('     - POST /api/csv/export')
    print('     - POST /api/csv/validate')

    print('   Export:')
    print('     - POST /api/export/document')
    print('   Workspace:')
    print('     - GET  /api/workspace/<id>')
    print('')
    app.run(debug=True, host='0.0.0.0', port=5000)
