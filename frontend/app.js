// API Configuration
const API_BASE = '/api';

// State Management
const state = {
    token: localStorage.getItem('token') || null,
    user: null,
    currentView: 'translations',
    translations: [],
    currentTranslationIndex: 0,
    reports: [],
    prompts: [],
    executions: [],
    ratings: {
        coherence: 0,
        fidelity: 0,
        naturalness: 0
    }
};

// API Helper
async function apiRequest(endpoint, options = {}) {
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };

    if (state.token) {
        headers['Authorization'] = `Bearer ${state.token}`;
    }

    const response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers
    });

    if (response.status === 401) {
        logout();
        throw new Error('Unauthorized');
    }

    if (!response.ok) {
        const error = await response.json();
        // Handle FastAPI validation errors
        if (Array.isArray(error.detail)) {
            const messages = error.detail.map(err => `${err.loc.join('.')}: ${err.msg}`).join(', ');
            throw new Error(messages);
        }
        throw new Error(error.detail || 'Request failed');
    }

    return response.json();
}

// Authentication
async function login(username, password) {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    const response = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData
    });

    if (!response.ok) {
        throw new Error('Invalid credentials');
    }

    const data = await response.json();
    state.token = data.access_token;
    localStorage.setItem('token', data.access_token);

    // Get user info
    state.user = await apiRequest('/auth/me');
    showMainScreen();
}

function logout() {
    state.token = null;
    state.user = null;
    localStorage.removeItem('token');
    showLoginScreen();
}

// Screen Management
function showLoginScreen() {
    document.getElementById('login-screen').classList.remove('hidden');
    document.getElementById('main-screen').classList.add('hidden');
}

function showMainScreen() {
    document.getElementById('login-screen').classList.add('hidden');
    document.getElementById('main-screen').classList.remove('hidden');
    document.getElementById('current-user').textContent = state.user.username;

    // Show/hide admin menu
    if (state.user.is_admin) {
        document.querySelectorAll('.admin-only').forEach(el => el.classList.remove('hidden'));
    }

    loadInitialData();
}

function showView(viewName) {
    // Update navigation
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    document.querySelector(`[data-view="${viewName}"]`).classList.add('active');

    // Update views
    document.querySelectorAll('.view').forEach(view => {
        view.classList.add('hidden');
    });
    document.getElementById(`${viewName}-view`).classList.remove('hidden');

    state.currentView = viewName;

    // Load view data
    if (viewName === 'translations') {
        // Use paginated version if available
        if (typeof loadTranslationsPaginated === 'function') {
            loadTranslationsPaginated();
        } else {
            loadTranslations();
        }
    } else if (viewName === 'reports') {
        loadReports();
    } else if (viewName === 'admin') {
        loadUsers();
    }
}

// Load Initial Data
async function loadInitialData() {
    try {
        // Load prompts and executions for filters
        state.prompts = await apiRequest('/prompts/');
        const execData = await apiRequest('/translations/executions/list');
        state.executions = execData;

        populateFilters();

        // Load paginated translations if available
        if (typeof loadTranslationsPaginated === 'function') {
            loadTranslationsPaginated();
        } else {
            loadTranslations();
        }
    } catch (error) {
        console.error('Error loading initial data:', error);
    }
}

function populateFilters() {
    // Populate execution filters
    const executionFilters = [
        document.getElementById('execution-filter'),
        document.getElementById('report-execution-filter')
    ].filter(el => el !== null);

    executionFilters.forEach(select => {
        select.innerHTML = '<option value="">All Executions</option>';
        state.executions.forEach(exec => {
            const option = document.createElement('option');
            option.value = exec.execution_id;
            option.textContent = `${exec.execution_id} (${exec.count} translations)`;
            select.appendChild(option);
        });
    });

    // Populate prompt filters
    const promptFilters = [
        document.getElementById('prompt-filter'),
        document.getElementById('report-prompt-filter')
    ].filter(el => el !== null);

    promptFilters.forEach(select => {
        select.innerHTML = '<option value="">All Prompts</option>';
        state.prompts.forEach(prompt => {
            const option = document.createElement('option');
            option.value = prompt.id;
            option.textContent = prompt.name;
            select.appendChild(option);
        });
    });
}

// Translations
async function loadTranslations() {
    try {
        const executionId = document.getElementById('execution-filter').value;
        const promptId = document.getElementById('prompt-filter').value;

        let url = '/translations/?limit=100';
        if (executionId) url += `&execution_id=${executionId}`;
        if (promptId) url += `&prompt_id=${promptId}`;

        state.translations = await apiRequest(url);
        renderTranslations();
    } catch (error) {
        console.error('Error loading translations:', error);
        document.getElementById('translations-list').innerHTML =
            '<div class="loading">Error loading translations</div>';
    }
}

function renderTranslations() {
    const container = document.getElementById('translations-list');

    if (state.translations.length === 0) {
        container.innerHTML = '<div class="loading">No translations found</div>';
        return;
    }

    container.innerHTML = state.translations.map(trans => `
        <div class="translation-card" onclick="showTranslationDetail(${trans.id})">
            <div class="translation-header">
                <div>
                    <strong>${trans.prompt.name}</strong>
                    <div class="translation-meta">
                        Execution: ${trans.execution_id} |
                        ${trans.source_language} → ${trans.target_language}
                    </div>
                </div>
                ${trans.manual_score ? '<span class="user-badge badge-admin">Scored</span>' : ''}
            </div>
            <div class="translation-content">
                <div class="content-section">
                    <div class="content-label">Original:</div>
                    <div class="content-text">${escapeHtml(trans.original_content.substring(0, 150))}${trans.original_content.length > 150 ? '...' : ''}</div>
                </div>
                <div class="content-section">
                    <div class="content-label">Translation:</div>
                    <div class="content-text">${escapeHtml(trans.translated_content.substring(0, 150))}${trans.translated_content.length > 150 ? '...' : ''}</div>
                </div>
            </div>
            <div class="scores-section">
                ${renderScoreItem('Coherence', trans.automated_coherence, trans.manual_score?.coherence)}
                ${renderScoreItem('Fidelity', trans.automated_fidelity, trans.manual_score?.fidelity)}
                ${renderScoreItem('Naturalness', trans.automated_naturalness, trans.manual_score?.naturalness)}
                ${renderScoreItem('Overall', trans.automated_overall, trans.manual_score?.overall)}
            </div>
        </div>
    `).join('');
}

function renderScoreItem(label, autoScore, manualScore) {
    const displayScore = manualScore !== null && manualScore !== undefined ? manualScore : autoScore;
    const scoreClass = manualScore !== null && manualScore !== undefined ? 'manual' : '';

    return `
        <div class="score-item">
            <div class="score-label">${label}</div>
            <div class="score-value ${scoreClass}">
                ${displayScore !== null && displayScore !== undefined ? displayScore.toFixed(1) : 'N/A'}
            </div>
        </div>
    `;
}

function showTranslationDetail(translationId) {
    const translation = state.translations.find(t => t.id === translationId);
    if (!translation) return;

    const modal = document.getElementById('translation-modal');
    const detailContainer = document.getElementById('translation-detail');

    detailContainer.innerHTML = `
        <div class="translation-meta" style="margin-bottom: 20px;">
            <strong>Prompt:</strong> ${translation.prompt.name}<br>
            <strong>Execution ID:</strong> ${translation.execution_id.split('/').pop()}<br>
            <strong>Languages:</strong> ${translation.source_language} → ${translation.target_language}
        </div>

        <div class="content-section" style="margin-bottom: 20px;">
            <div class="content-label">Original Content:</div>
            <div class="content-text">${escapeHtml(translation.original_content)}</div>
        </div>

        <div class="content-section" style="margin-bottom: 20px;">
            <div class="content-label">Translated Content:</div>
            <div class="content-text">${escapeHtml(translation.translated_content)}</div>
        </div>

        <div class="scores-section" style="margin-bottom: 30px;">
            <div>
                <h4 style="margin-bottom: 10px;">Automated Scores</h4>
                ${renderScoreItem('Coherence', translation.automated_coherence, null)}
                ${renderScoreItem('Fidelity', translation.automated_fidelity, null)}
                ${renderScoreItem('Naturalness', translation.automated_naturalness, null)}
                ${renderScoreItem('Overall', translation.automated_overall, null)}
            </div>
        </div>

        <div class="score-form">
            <h3>${translation.manual_score ? 'Edit Your Score' : 'Add Your Score'}</h3>
            <form id="score-form" onsubmit="submitScore(event, ${translation.id}, ${translation.manual_score?.id || null})">
                <div class="score-inputs">
                    <div class="score-input-group">
                        <label>Coherence (0-10)</label>
                        <input type="number" name="coherence" min="0" max="10" step="0.1"
                               value="${translation.manual_score?.coherence || ''}" placeholder="0.0">
                    </div>
                    <div class="score-input-group">
                        <label>Fidelity (0-10)</label>
                        <input type="number" name="fidelity" min="0" max="10" step="0.1"
                               value="${translation.manual_score?.fidelity || ''}" placeholder="0.0">
                    </div>
                    <div class="score-input-group">
                        <label>Naturalness (0-10)</label>
                        <input type="number" name="naturalness" min="0" max="10" step="0.1"
                               value="${translation.manual_score?.naturalness || ''}" placeholder="0.0">
                    </div>
                    <div class="score-input-group">
                        <label>Overall (0-10)</label>
                        <input type="number" name="overall" min="0" max="10" step="0.1"
                               value="${translation.manual_score?.overall || ''}" placeholder="0.0">
                    </div>
                </div>
                <div class="score-input-group" style="grid-column: 1 / -1;">
                    <label>Notes (optional)</label>
                    <textarea name="notes" placeholder="Add any notes about this translation...">${translation.manual_score?.notes || ''}</textarea>
                </div>
                <button type="submit" class="btn btn-success" style="margin-top: 15px;">
                    ${translation.manual_score ? 'Update Score' : 'Submit Score'}
                </button>
                <div id="score-message" class="message"></div>
            </form>
        </div>
    `;

    modal.classList.remove('hidden');
}

async function submitScore(event, translationId, scoreId) {
    event.preventDefault();

    const form = event.target;
    const formData = new FormData(form);

    const scoreData = {
        coherence: formData.get('coherence') ? parseFloat(formData.get('coherence')) : null,
        fidelity: formData.get('fidelity') ? parseFloat(formData.get('fidelity')) : null,
        naturalness: formData.get('naturalness') ? parseFloat(formData.get('naturalness')) : null,
        overall: formData.get('overall') ? parseFloat(formData.get('overall')) : null,
        notes: formData.get('notes') || null
    };

    try {
        if (scoreId) {
            // Update existing score
            await apiRequest(`/scores/${scoreId}`, {
                method: 'PUT',
                body: JSON.stringify(scoreData)
            });
        } else {
            // Create new score
            await apiRequest('/scores/', {
                method: 'POST',
                body: JSON.stringify({
                    translation_id: translationId,
                    ...scoreData
                })
            });
        }

        const message = document.getElementById('score-message');
        message.textContent = 'Score saved successfully!';
        message.className = 'message success';

        // Reload translations
        await loadTranslations();

        setTimeout(() => {
            document.getElementById('translation-modal').classList.add('hidden');
        }, 1500);
    } catch (error) {
        const message = document.getElementById('score-message');
        message.textContent = `Error: ${error.message}`;
        message.className = 'message error';
    }
}

// Reports
async function loadReports() {
    try {
        const executionId = document.getElementById('report-execution-filter').value;
        const promptId = document.getElementById('report-prompt-filter').value;
        const manualOnly = document.getElementById('manual-only-filter').checked;

        let url = '/reports/?';
        if (executionId) url += `execution_id=${executionId}&`;
        if (promptId) url += `prompt_id=${promptId}&`;
        if (manualOnly) url += `manual_only=true&`;

        state.reports = await apiRequest(url);
        renderReports();
    } catch (error) {
        console.error('Error loading reports:', error);
        document.getElementById('reports-list').innerHTML =
            '<div class="loading">Error loading reports</div>';
    }
}

function renderReports() {
    const container = document.getElementById('reports-list');

    if (state.reports.length === 0) {
        container.innerHTML = '<div class="loading">No reports found</div>';
        return;
    }

    container.innerHTML = state.reports.map(report => `
        <div class="report-card">
            <div class="report-header">
                <h3>${report.prompt_name}</h3>
                <div style="color: #7f8c8d; font-size: 14px;">Execution: ${report.execution_id}</div>
            </div>

            <div class="report-stats">
                <div class="stat-item">
                    <div class="stat-label">Total Translations</div>
                    <div class="stat-value">${report.total_translations}</div>
                </div>
                <div class="stat-item" style="border-left-color: #27ae60;">
                    <div class="stat-label">Manual Scores</div>
                    <div class="stat-value">${report.translations_with_manual_scores}</div>
                </div>
                <div class="stat-item" style="border-left-color: #e74c3c;">
                    <div class="stat-label">Coverage</div>
                    <div class="stat-value">${report.manual_score_percentage}%</div>
                </div>
            </div>

            <div class="scores-grid">
                ${renderReportScoreGroup('Automated Scores', {
                    Coherence: report.avg_automated_coherence,
                    Fidelity: report.avg_automated_fidelity,
                    Naturalness: report.avg_automated_naturalness,
                    Overall: report.avg_automated_overall
                })}

                ${renderReportScoreGroup('Manual Scores', {
                    Coherence: report.avg_manual_coherence,
                    Fidelity: report.avg_manual_fidelity,
                    Naturalness: report.avg_manual_naturalness,
                    Overall: report.avg_manual_overall
                })}

                ${renderReportScoreGroup('Combined Scores', {
                    Coherence: report.avg_combined_coherence,
                    Fidelity: report.avg_combined_fidelity,
                    Naturalness: report.avg_combined_naturalness,
                    Overall: report.avg_combined_overall
                })}
            </div>
        </div>
    `).join('');
}

function renderReportScoreGroup(title, scores) {
    return `
        <div class="score-group">
            <h4>${title}</h4>
            ${Object.entries(scores).map(([label, value]) => `
                <div class="score-row">
                    <span>${label}:</span>
                    <span>${value !== null && value !== undefined ? value.toFixed(2) : 'N/A'}</span>
                </div>
            `).join('')}
        </div>
    `;
}

// Admin
async function loadUsers() {
    try {
        const users = await apiRequest('/auth/users');
        renderUsers(users);
    } catch (error) {
        console.error('Error loading users:', error);
    }
}

function renderUsers(users) {
    const container = document.getElementById('users-list');

    container.innerHTML = users.map(user => `
        <div class="user-item">
            <div class="user-info">
                <div class="user-name">${user.username}</div>
                <div class="user-email">${user.email}</div>
            </div>
            <div class="user-badge ${user.is_admin ? 'badge-admin' : 'badge-user'}">
                ${user.is_admin ? 'Admin' : 'User'}
            </div>
        </div>
    `).join('');
}

async function createUser(event) {
    event.preventDefault();

    const form = event.target;
    const formData = new FormData(form);

    const userData = {
        username: formData.get('username'),
        email: formData.get('email'),
        password: formData.get('password'),
        is_admin: formData.get('is_admin') === 'on'
    };

    try {
        await apiRequest('/auth/register', {
            method: 'POST',
            body: JSON.stringify(userData)
        });

        const message = document.getElementById('create-user-message');
        message.textContent = 'User created successfully!';
        message.className = 'message success';

        form.reset();
        loadUsers();

        setTimeout(() => {
            message.textContent = '';
            message.className = 'message';
        }, 3000);
    } catch (error) {
        const message = document.getElementById('create-user-message');
        message.textContent = `Error: ${error.message}`;
        message.className = 'message error';
    }
}

// Utility Functions
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    // Login form
    document.getElementById('login-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        try {
            await login(username, password);
        } catch (error) {
            document.getElementById('login-error').textContent = error.message;
        }
    });

    // Logout button
    document.getElementById('logout-btn').addEventListener('click', logout);

    // Navigation
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const view = e.target.getAttribute('data-view');
            showView(view);
        });
    });

    // Filters (removed for new design)
    // document.getElementById('apply-filters').addEventListener('click', loadTranslations);
    document.getElementById('apply-report-filters').addEventListener('click', loadReports);

    // Modal close
    document.querySelector('.close').addEventListener('click', () => {
        document.getElementById('translation-modal').classList.add('hidden');
    });

    window.addEventListener('click', (e) => {
        const modal = document.getElementById('translation-modal');
        if (e.target === modal) {
            modal.classList.add('hidden');
        }
    });

    // Admin form
    document.getElementById('create-user-form').addEventListener('submit', createUser);

    // Check if already logged in
    if (state.token) {
        apiRequest('/auth/me')
            .then(user => {
                state.user = user;
                showMainScreen();
            })
            .catch(() => {
                logout();
            });
    } else {
        showLoginScreen();
    }
});

// Make functions globally available
window.showTranslationDetail = showTranslationDetail;
window.submitScore = submitScore;
