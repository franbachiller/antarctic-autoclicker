const API_BASE_URL = '';
let adminKey = localStorage.getItem('admin_key') || '';
let allLicenses = [];
let generatedLicenses = [];

const loginScreen = document.getElementById('login-screen');
const adminPanel = document.getElementById('admin-panel');
const adminKeyInput = document.getElementById('admin-key');
const loginBtn = document.getElementById('login-btn');
const loginError = document.getElementById('login-error');
const logoutBtn = document.getElementById('logout-btn');
const refreshBtn = document.getElementById('refresh-btn');
const generateBtn = document.getElementById('generate-btn');
const exportBtn = document.getElementById('export-btn');
const searchInput = document.getElementById('search-input');

function checkAuth() {
    // Don't auto-login, always show login screen first
    // User can manually login with their admin key
    console.log('Admin panel loaded. Please login with your admin key.');
}

async function login() {
    const key = adminKeyInput.value.trim();

    if (!key) {
        showError('Please enter admin key');
        return;
    }

    loginBtn.textContent = 'CHECKING...';
    loginBtn.disabled = true;

    try {
        const response = await fetch(`${API_BASE_URL}/api/admin/stats`, {
            headers: {
                'X-Admin-Key': key.trim()
            }
        });

        if (response.ok) {
            adminKey = key.trim();
            localStorage.setItem('admin_key', key.trim());
            loginScreen.classList.add('hidden');
            adminPanel.classList.remove('hidden');
            loadDashboard();
        } else {
            showError('Invalid admin key');
            loginBtn.textContent = 'LOGIN';
            loginBtn.disabled = false;
        }
    } catch (error) {
        console.error('Login error:', error);
        showError('Connection error: ' + error.message);
        loginBtn.textContent = 'LOGIN';
        loginBtn.disabled = false;
    }
}

function showError(message) {
    loginError.textContent = message;
    setTimeout(() => {
        loginError.textContent = '';
    }, 3000);
}

function logout() {
    localStorage.removeItem('admin_key');
    adminKey = '';
    adminPanel.classList.add('hidden');
    loginScreen.classList.remove('hidden');
    adminKeyInput.value = '';
}

async function loadDashboard() {
    await Promise.all([
        loadStats(),
        loadLicenses()
    ]);
}

async function loadStats() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/admin/stats`, {
            headers: {
                'X-Admin-Key': adminKey
            }
        });

        if (response.ok) {
            const stats = await response.json();
            document.getElementById('total-licenses').textContent = stats.total || 0;
            document.getElementById('active-licenses').textContent = stats.active || 0;
            document.getElementById('expired-licenses').textContent = stats.expired || 0;
            document.getElementById('banned-licenses').textContent = stats.banned || 0;
        } else {
            showNotification('Failed to load stats', 'error');
        }
    } catch (error) {
        console.error('Error loading stats:', error);
        showNotification('Error loading stats', 'error');
    }
}

async function loadLicenses() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/admin/licenses`, {
            headers: {
                'X-Admin-Key': adminKey
            }
        });

        if (response.ok) {
            allLicenses = await response.json();
            renderLicenses(allLicenses);
        } else {
            showNotification('Failed to load licenses', 'error');
        }
    } catch (error) {
        console.error('Error loading licenses:', error);
        showNotification('Error loading licenses', 'error');
    }
}

function renderLicenses(licenses) {
    const tbody = document.getElementById('licenses-table-body');

    if (licenses.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9" class="loading">No licenses found</td></tr>';
        return;
    }

    tbody.innerHTML = licenses.map(license => {
        // Handle both old and new schema formats
        const isBanned = license.is_banned || license.status === 'banned';
        const isExpired = license.status === 'expired' ||
                         (license.expires_at && new Date(license.expires_at) < new Date());
        const isActive = license.status === 'active' && !isExpired && !isBanned;

        let statusClass, statusText;
        if (isBanned) {
            statusClass = 'banned';
            statusText = 'banned';
        } else if (isExpired) {
            statusClass = 'expired';
            statusText = 'expired';
        } else {
            statusClass = 'active';
            statusText = 'active';
        }

        return `
            <tr>
                <td><span class="license-key" onclick="copyToClipboard('${license.license_key}')">${license.license_key}</span></td>
                <td>${license.license_type}</td>
                <td><span class="status-badge ${statusClass}">${statusText}</span></td>
                <td>${formatDate(license.created_at)}</td>
                <td>${formatDate(license.expires_at)}</td>
                <td>${license.last_used ? formatDate(license.last_used) : '—'}</td>
                <td>${license.usage_count || 0}</td>
                <td>${license.notes || '—'}</td>
                <td>
                    ${!isBanned ?
                        `<button class="btn-action ban" onclick="banLicense('${license.license_key}')">BAN</button>` :
                        `<button class="btn-action delete" onclick="deleteLicense('${license.license_key}')">DELETE</button>`
                    }
                </td>
            </tr>
        `;
    }).join('');
}

async function generateLicenses() {
    const type = document.getElementById('license-type').value;
    const count = parseInt(document.getElementById('license-count').value);
    const notes = document.getElementById('license-notes').value.trim();

    if (count < 1 || count > 100) {
        showNotification('Count must be between 1 and 100', 'error');
        return;
    }

    generateBtn.textContent = 'GENERATING...';
    generateBtn.disabled = true;

    try {
        const response = await fetch(`${API_BASE_URL}/api/admin/create-license`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Admin-Key': adminKey
            },
            body: JSON.stringify({
                licenseType: type,
                count: count,
                notes: notes || undefined
            })
        });

        if (response.ok) {
            const result = await response.json();
            generatedLicenses = result.licenses || [];
            
            showGeneratedLicenses();
            showNotification(`Successfully generated ${generatedLicenses.length} license(s)`, 'success');
            
            document.getElementById('license-notes').value = '';
            
            await loadDashboard();
        } else {
            const error = await response.json();
            showNotification(error.error || 'Failed to generate licenses', 'error');
        }
    } catch (error) {
        console.error('Error generating licenses:', error);
        showNotification('Error generating licenses', 'error');
    } finally {
        generateBtn.textContent = 'GENERATE LICENSE(S)';
        generateBtn.disabled = false;
    }
}

function showGeneratedLicenses() {
    const section = document.getElementById('generated-licenses');
    const list = document.getElementById('generated-list');
    
    if (generatedLicenses.length === 0) {
        section.classList.add('hidden');
        return;
    }

    list.innerHTML = generatedLicenses.map(license => `
        <div class="generated-item">
            <div class="generated-info">
                <div class="generated-key">${license.license_key}</div>
                <div class="generated-meta">
                    Type: ${license.license_type} | 
                    Expires: ${formatDate(license.expires_at)}
                </div>
            </div>
            <button class="btn-copy" onclick="copyToClipboard('${license.license_key}')">COPY KEY</button>
        </div>
    `).join('');

    section.classList.remove('hidden');
}

function exportToTextFile() {
    if (generatedLicenses.length === 0) {
        showNotification('No licenses to export', 'error');
        return;
    }

    const now = new Date();
    const dateStr = now.toLocaleDateString('en-GB').replace(/\//g, '/');
    const timeStr = now.toLocaleTimeString('en-GB');
    
    let content = '======================================================================\n';
    content += 'ANTARCTIC - GENERATED LICENSES\n';
    content += '======================================================================\n\n';
    content += `Generated: ${dateStr} ${timeStr}\n`;
    content += `Total: ${generatedLicenses.length} license(s)\n\n`;

    generatedLicenses.forEach((license, index) => {
        content += `LICENSE #${index + 1}\n`;
        content += '----------------------------------------------------------------------\n';
        content += `Key:     ${license.license_key}\n`;
        content += `Type:    ${license.license_type}\n`;
        content += `Expires: ${formatDate(license.expires_at)}\n`;
        content += `Status:  active\n\n`;
    });

    content += '======================================================================\n';
    content += 'ANTARCTIC License Management System\n';
    content += '======================================================================\n';

    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    const timestamp = now.toISOString().replace(/[:.]/g, '-').slice(0, 19);
    a.href = url;
    a.download = `antarctic-licenses-${timestamp}.txt`;
    a.click();
    URL.revokeObjectURL(url);

    showNotification('Licenses exported successfully', 'success');
}

async function banLicense(licenseKey) {
    if (!confirm(`Are you sure you want to ban license:\n${licenseKey}?`)) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/api/admin/ban-license`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Admin-Key': adminKey
            },
            body: JSON.stringify({ licenseKey })
        });

        if (response.ok) {
            showNotification('License banned successfully', 'success');
            await loadDashboard();
        } else {
            const error = await response.json();
            showNotification(error.error || 'Failed to ban license', 'error');
        }
    } catch (error) {
        console.error('Error banning license:', error);
        showNotification('Error banning license', 'error');
    }
}

async function deleteLicense(licenseKey) {
    if (!confirm(`Are you sure you want to DELETE license:\n${licenseKey}?\n\nThis action cannot be undone.`)) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/api/admin/delete-license`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Admin-Key': adminKey
            },
            body: JSON.stringify({ licenseKey })
        });

        if (response.ok) {
            showNotification('License deleted successfully', 'success');
            await loadDashboard();
        } else {
            const error = await response.json();
            showNotification(error.error || 'Failed to delete license', 'error');
        }
    } catch (error) {
        console.error('Error deleting license:', error);
        showNotification('Error deleting license', 'error');
    }
}

function searchLicenses() {
    const query = searchInput.value.toLowerCase().trim();

    if (!query) {
        renderLicenses(allLicenses);
        return;
    }

    const filtered = allLicenses.filter(license => {
        // Handle both old and new schema formats for status
        const isBanned = license.is_banned || license.status === 'banned';
        const isExpired = license.status === 'expired' ||
                         (license.expires_at && new Date(license.expires_at) < new Date());
        const statusText = isBanned ? 'banned' : (isExpired ? 'expired' : 'active');

        return license.license_key.toLowerCase().includes(query) ||
               license.license_type.toLowerCase().includes(query) ||
               (license.notes && license.notes.toLowerCase().includes(query)) ||
               statusText.includes(query);
    });

    renderLicenses(filtered);
}

function copyToClipboard(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(() => {
            showNotification('License key copied to clipboard', 'info');
        }).catch(err => {
            fallbackCopy(text);
        });
    } else {
        fallbackCopy(text);
    }
}

function fallbackCopy(text) {
    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.style.position = 'fixed';
    textarea.style.opacity = '0';
    document.body.appendChild(textarea);
    textarea.select();
    
    try {
        document.execCommand('copy');
        showNotification('License key copied to clipboard', 'info');
    } catch (err) {
        showNotification('Failed to copy to clipboard', 'error');
    }
    
    document.body.removeChild(textarea);
}

function showNotification(message, type = 'info') {
    const notification = document.getElementById('notification');
    const messageEl = notification.querySelector('.notification-message');
    
    notification.className = `notification ${type}`;
    messageEl.textContent = message;
    notification.classList.remove('hidden');

    setTimeout(() => {
        notification.classList.add('hidden');
    }, 5000);
}

function formatDate(dateString) {
    if (!dateString) return '—';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-GB', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
    });
}

loginBtn.addEventListener('click', login);
adminKeyInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        login();
    }
});
logoutBtn.addEventListener('click', logout);
refreshBtn.addEventListener('click', loadDashboard);
generateBtn.addEventListener('click', generateLicenses);
exportBtn.addEventListener('click', exportToTextFile);
searchInput.addEventListener('input', searchLicenses);

setInterval(() => {
    if (adminKey) {
        loadStats();
    }
}, 30000);

checkAuth();
