/**
 * Firebase Service - Centralized Data Layer
 * Handles all Firebase Realtime Database operations for the workspace application.
 * 
 * Include this file in layout.html to make it available across all pages.
 * Access via: window.firebaseService
 */

class FirebaseService {
    constructor() {
        this.db = null;
        this.auth = null;
        this.currentUser = null;
        this.currentWorkspaceId = null;
        this.listeners = {};
    }

    /**
     * Initialize Firebase and set up auth listener
     */
    async initialize() {
        if (!window.firebase) {
            console.error('❌ Firebase SDK not loaded');
            return false;
        }

        try {
            // Initialize Firebase if not already done
            if (!firebase.apps.length) {
                firebase.initializeApp(window.firebaseConfig);
            }

            this.db = firebase.database();
            this.auth = firebase.auth();

            // Return a promise that resolves when auth state is determined
            return new Promise((resolve) => {
                this.auth.onAuthStateChanged((user) => {
                    this.currentUser = user;
                    if (user) {
                        console.log('✅ Firebase Service: User authenticated -', user.email);
                        // Load saved workspace ID from localStorage
                        this.currentWorkspaceId = localStorage.getItem('currentWorkspaceId') || null;
                        window.dispatchEvent(new CustomEvent('firebaseReady', { detail: user }));
                    }
                    resolve(!!user);
                });
            });
        } catch (error) {
            console.error('❌ Firebase initialization error:', error);
            return false;
        }
    }

    /**
     * Get current user's auth token for API calls
     */
    async getToken() {
        if (!this.currentUser) return null;
        return await this.currentUser.getIdToken();
    }

    // ========================================================================
    // WORKSPACE MANAGEMENT
    // ========================================================================

    /**
     * Create a new workspace
     * @param {string} name - Workspace name
     * @returns {Promise<{id: string, name: string}>}
     */
    async createWorkspace(name) {
        if (!this.currentUser) throw new Error('Not authenticated');

        const uid = this.currentUser.uid;
        const workspaceRef = this.db.ref('workspaces').push();

        const workspaceData = {
            name: name,
            owner: uid,
            members: { [uid]: 'owner' },
            content: { blocks: [], title: name },
            createdAt: firebase.database.ServerValue.TIMESTAMP,
            updatedAt: firebase.database.ServerValue.TIMESTAMP
        };

        await workspaceRef.set(workspaceData);

        // Add to user's workspace list
        await this.db.ref(`users/${uid}/workspaces/${workspaceRef.key}`).set({
            name: name,
            role: 'owner',
            joinedAt: firebase.database.ServerValue.TIMESTAMP
        });

        console.log('✅ Created workspace:', workspaceRef.key);
        return { id: workspaceRef.key, name: name };
    }

    /**
     * Get all workspaces for current user
     * @returns {Promise<Array>}
     */
    async listWorkspaces() {
        if (!this.currentUser) return [];

        const uid = this.currentUser.uid;
        const snapshot = await this.db.ref(`users/${uid}/workspaces`).once('value');
        const workspaces = [];

        if (snapshot.exists()) {
            snapshot.forEach((child) => {
                workspaces.push({
                    id: child.key,
                    ...child.val()
                });
            });
        }

        return workspaces;
    }

    /**
     * Get workspace details
     * @param {string} workspaceId 
     * @returns {Promise<Object>}
     */
    async getWorkspace(workspaceId) {
        const snapshot = await this.db.ref(`workspaces/${workspaceId}`).once('value');
        if (snapshot.exists()) {
            return { id: workspaceId, ...snapshot.val() };
        }
        return null;
    }

    /**
     * Set current active workspace
     * @param {string} workspaceId 
     */
    setCurrentWorkspace(workspaceId) {
        this.currentWorkspaceId = workspaceId;
        localStorage.setItem('currentWorkspaceId', workspaceId);
    }

    /**
     * Get current workspace ID
     */
    getCurrentWorkspaceId() {
        return this.currentWorkspaceId || localStorage.getItem('currentWorkspaceId');
    }

    // ========================================================================
    // WORKSPACE CONTENT (Editor Blocks)
    // ========================================================================

    /**
     * Save workspace content (blocks and title)
     * @param {string} workspaceId 
     * @param {Object} content - { title: string, blocks: Array }
     */
    async saveWorkspaceContent(workspaceId, content) {
        if (!workspaceId) throw new Error('No workspace ID provided');

        await this.db.ref(`workspaces/${workspaceId}/content`).set(content);
        await this.db.ref(`workspaces/${workspaceId}/updatedAt`).set(firebase.database.ServerValue.TIMESTAMP);

        console.log('✅ Saved workspace content:', workspaceId);
    }

    /**
     * Load workspace content
     * @param {string} workspaceId 
     * @returns {Promise<Object>} - { title: string, blocks: Array }
     */
    async loadWorkspaceContent(workspaceId) {
        if (!workspaceId) return { title: 'Untitled', blocks: [] };

        const snapshot = await this.db.ref(`workspaces/${workspaceId}/content`).once('value');
        if (snapshot.exists()) {
            return snapshot.val();
        }
        return { title: 'Untitled', blocks: [] };
    }

    /**
     * Subscribe to real-time content updates
     * @param {string} workspaceId 
     * @param {Function} callback 
     */
    subscribeToContent(workspaceId, callback) {
        const ref = this.db.ref(`workspaces/${workspaceId}/content`);
        ref.on('value', (snapshot) => {
            if (snapshot.exists()) {
                callback(snapshot.val());
            }
        });
        this.listeners[`content_${workspaceId}`] = ref;
    }

    /**
     * Unsubscribe from content updates
     * @param {string} workspaceId 
     */
    unsubscribeFromContent(workspaceId) {
        const key = `content_${workspaceId}`;
        if (this.listeners[key]) {
            this.listeners[key].off();
            delete this.listeners[key];
        }
    }

    // ========================================================================
    // TEAM & COLLABORATION
    // ========================================================================

    /**
     * Invite a user to a workspace
     * @param {string} workspaceId 
     * @param {string} email 
     */
    async inviteToWorkspace(workspaceId, email) {
        if (!this.currentUser) throw new Error('Not authenticated');

        const safeEmail = email.replace(/\./g, ',');
        const inviteId = this.db.ref().push().key;

        // Get workspace name
        const wsSnapshot = await this.db.ref(`workspaces/${workspaceId}/name`).once('value');
        const workspaceName = wsSnapshot.val() || 'Unnamed Workspace';

        // Add invite to workspace
        await this.db.ref(`workspaces/${workspaceId}/invites/${inviteId}`).set({
            email: email,
            status: 'pending',
            invitedBy: this.currentUser.uid,
            inviterEmail: this.currentUser.email,
            timestamp: firebase.database.ServerValue.TIMESTAMP
        });

        // Add to global invites (indexed by email for target user to find)
        await this.db.ref(`invites/${safeEmail}/${inviteId}`).set({
            workspaceId: workspaceId,
            workspaceName: workspaceName,
            invitedBy: this.currentUser.uid,
            inviterEmail: this.currentUser.email,
            status: 'pending',
            timestamp: firebase.database.ServerValue.TIMESTAMP
        });

        console.log('✅ Invite sent to:', email);
        return { inviteId, email };
    }

    /**
     * Get pending invites for current user
     * @returns {Promise<Array>}
     */
    async getPendingInvites() {
        if (!this.currentUser || !this.currentUser.email) return [];

        const safeEmail = this.currentUser.email.replace(/\./g, ',');
        const snapshot = await this.db.ref(`invites/${safeEmail}`).once('value');
        const invites = [];

        if (snapshot.exists()) {
            snapshot.forEach((child) => {
                const invite = child.val();
                if (invite.status === 'pending') {
                    invites.push({
                        id: child.key,
                        ...invite
                    });
                }
            });
        }

        return invites;
    }

    /**
     * Respond to an invite
     * @param {string} inviteId 
     * @param {string} workspaceId 
     * @param {string} action - 'accept' or 'reject'
     */
    async respondToInvite(inviteId, workspaceId, action) {
        if (!this.currentUser) throw new Error('Not authenticated');

        const uid = this.currentUser.uid;
        const safeEmail = this.currentUser.email.replace(/\./g, ',');

        if (action === 'accept') {
            // Add user as member
            await this.db.ref(`workspaces/${workspaceId}/members/${uid}`).set('member');

            // Add workspace to user's list
            const wsSnapshot = await this.db.ref(`workspaces/${workspaceId}/name`).once('value');
            await this.db.ref(`users/${uid}/workspaces/${workspaceId}`).set({
                name: wsSnapshot.val() || 'Workspace',
                role: 'member',
                joinedAt: firebase.database.ServerValue.TIMESTAMP
            });
        }

        // Update invite status
        await this.db.ref(`workspaces/${workspaceId}/invites/${inviteId}/status`).set(action === 'accept' ? 'accepted' : 'rejected');
        await this.db.ref(`invites/${safeEmail}/${inviteId}/status`).set(action === 'accept' ? 'accepted' : 'rejected');

        console.log(`✅ Invite ${action}ed`);
    }

    /**
     * Get workspace members
     * @param {string} workspaceId 
     * @returns {Promise<Array>}
     */
    async getWorkspaceMembers(workspaceId) {
        const snapshot = await this.db.ref(`workspaces/${workspaceId}/members`).once('value');
        const members = [];

        if (snapshot.exists()) {
            const membersData = snapshot.val();
            for (const [uid, role] of Object.entries(membersData)) {
                // Try to get user info
                const userSnapshot = await this.db.ref(`users/${uid}/profile`).once('value');
                const userInfo = userSnapshot.val() || {};

                members.push({
                    uid: uid,
                    role: role,
                    displayName: userInfo.displayName || 'User',
                    email: userInfo.email || 'Unknown'
                });
            }
        }

        return members;
    }

    /**
     * Get workspace invites (pending)
     * @param {string} workspaceId 
     */
    async getWorkspaceInvites(workspaceId) {
        const snapshot = await this.db.ref(`workspaces/${workspaceId}/invites`).once('value');
        const invites = [];

        if (snapshot.exists()) {
            snapshot.forEach((child) => {
                invites.push({ id: child.key, ...child.val() });
            });
        }

        return invites;
    }

    // ========================================================================
    // USER PROFILE
    // ========================================================================

    /**
     * Save user profile to database
     */
    async saveUserProfile() {
        if (!this.currentUser) return;

        await this.db.ref(`users/${this.currentUser.uid}/profile`).set({
            displayName: this.currentUser.displayName || '',
            email: this.currentUser.email,
            photoURL: this.currentUser.photoURL || '',
            lastLogin: firebase.database.ServerValue.TIMESTAMP
        });
    }

    // ========================================================================
    // NOTIFICATIONS
    // ========================================================================

    /**
     * Get notification count (pending invites for now)
     * @returns {Promise<number>}
     */
    async getNotificationCount() {
        const invites = await this.getPendingInvites();
        return invites.length;
    }

    /**
     * Subscribe to notification changes
     * @param {Function} callback 
     */
    subscribeToNotifications(callback) {
        if (!this.currentUser || !this.currentUser.email) return;

        const safeEmail = this.currentUser.email.replace(/\./g, ',');
        const ref = this.db.ref(`invites/${safeEmail}`);

        ref.on('value', async () => {
            const count = await this.getNotificationCount();
            callback(count);
        });

        this.listeners['notifications'] = ref;
    }

    /**
     * Cleanup all listeners
     */
    cleanup() {
        Object.values(this.listeners).forEach(ref => ref.off());
        this.listeners = {};
    }
}

// Create global instance
window.firebaseService = new FirebaseService();

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', async () => {
    await window.firebaseService.initialize();
});
