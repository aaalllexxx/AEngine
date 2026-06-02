/**
 * AEngine Security Demo — Main App (SPA Router & Utilities)
 */

// ─── SPA Tab Router ───────────────────────────────────────────

function initRouter() {
    const navBtns = document.querySelectorAll('.nav-btn');
    const tabs = document.querySelectorAll('.tab-content');

    navBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabId = btn.dataset.tab;

            // Update nav buttons
            navBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            // Update tab content
            tabs.forEach(t => t.classList.remove('active'));
            const target = document.getElementById('tab-' + tabId);
            if (target) {
                target.classList.add('active');
            }

            // Trigger tab-specific init
            if (tabId === 'attacks' && typeof initAttacksTab === 'function') {
                initAttacksTab();
            } else if (tabId === 'architecture' && typeof initArchitectureTab === 'function') {
                initArchitectureTab();
            } else if (tabId === 'metrics' && typeof initMetricsTab === 'function') {
                initMetricsTab();
            }

            // Update URL hash
            window.location.hash = tabId;
        });
    });

    // Handle initial hash
    const hash = window.location.hash.replace('#', '');
    if (hash) {
        const btn = document.querySelector(`.nav-btn[data-tab="${hash}"]`);
        if (btn) btn.click();
    }
}

// ─── API Helper ───────────────────────────────────────────────

async function api(url, options = {}) {
    const defaults = {
        headers: { 'Content-Type': 'application/json' },
    };
    const config = { ...defaults, ...options };

    try {
        const response = await fetch(url, config);
        const data = await response.json();
        return { ok: response.ok, status: response.status, data };
    } catch (error) {
        console.error('API Error:', error);
        return { ok: false, status: 0, data: { error: error.message } };
    }
}

async function apiGet(url) {
    return api(url);
}

async function apiPost(url, body) {
    return api(url, {
        method: 'POST',
        body: JSON.stringify(body),
    });
}

// ─── Toast Notifications ─────────────────────────────────────

function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `<span>${type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️'}</span> ${message}`;
    container.appendChild(toast);

    setTimeout(() => {
        if (toast.parentNode) toast.parentNode.removeChild(toast);
    }, 3000);
}

// ─── Popup ────────────────────────────────────────────────────

function showPopup(html) {
    const overlay = document.getElementById('popup-overlay');
    const body = document.getElementById('popup-body');
    body.innerHTML = html;
    overlay.classList.remove('hidden');
}

function closePopup() {
    document.getElementById('popup-overlay').classList.add('hidden');
}

// Close popup on overlay click
document.addEventListener('click', (e) => {
    if (e.target.id === 'popup-overlay') {
        closePopup();
    }
});

// Close popup on Escape
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closePopup();
});

// ─── Utility Functions ────────────────────────────────────────

function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

function formatTimestamp(ts) {
    if (!ts) return '';
    // Extract just time part
    const parts = ts.split(' ');
    return parts.length > 1 ? parts[1] : ts;
}

function createElement(tag, className, innerHTML) {
    const el = document.createElement(tag);
    if (className) el.className = className;
    if (innerHTML) el.innerHTML = innerHTML;
    return el;
}

// ─── Init ─────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
    initRouter();

    // Initialize first tab
    if (typeof initAttacksTab === 'function') {
        initAttacksTab();
    }
});
