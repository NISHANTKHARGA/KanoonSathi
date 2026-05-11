/**
 * KanoonSathi — app.js
 * Loaded by ALL HTML pages via <script src="/app.js">
 * Provides: fetchJson(), escapeHtml(), KanoonAuth
 */

const API_BASE = 'http://127.0.0.1:5000';

/** Make an API call and return parsed JSON */
async function fetchJson(url, options = {}) {
    const fullUrl = url.startsWith('http') ? url : API_BASE + url;

    // Auto-attach token if user is logged in
    const token = localStorage.getItem('token');
    if (token) {
        options.headers = options.headers || {};
        options.headers['Authorization'] = 'Bearer ' + token;
    }

    const response = await fetch(fullUrl, options);
    let data;
    try { data = await response.json(); }
    catch { throw new Error('Server error — could not parse response.'); }

    if (!response.ok) {
        throw new Error(data.error || data.message || `Error ${response.status}`);
    }
    return data;
}

/** Prevent XSS — always use this when putting user data in HTML */
function escapeHtml(str) {
    if (str == null) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

/** Authentication helpers */
window.KanoonAuth = {
    /** Save user data after login/signup */
    saveAuth(data) {
        localStorage.setItem('token', data.token);
        localStorage.setItem('user', JSON.stringify({
            id:    data.id,
            name:  data.name,
            email: data.email,
            role:  data.role,
        }));
    },

    /** Get the currently logged-in user object, or null */
    getUser() {
        try { return JSON.parse(localStorage.getItem('user')); }
        catch { return null; }
    },

    /** Check if any user is logged in */
    isLoggedIn() {
        return !!localStorage.getItem('token');
    },

    /** Log out and redirect to login page */
    logout() {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = '/login.html';
    }
};
