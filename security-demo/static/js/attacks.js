/**
 * AEngine Security Demo — Attacks Tab (Tab 1)
 * Симулятор атак с каталогом, запуском и логированием результатов
 */

let attacksCatalog = [];
let attacksInitialized = false;

async function initAttacksTab() {
    if (attacksInitialized) return;
    attacksInitialized = true;

    const container = document.getElementById('attacks-container');
    container.innerHTML = '<div style="text-align:center;padding:40px;color:var(--text-muted)"><div class="spinner"></div><br>Загрузка каталога атак...</div>';

    const res = await apiGet('/api/attacks/catalog');
    if (!res.ok) {
        container.innerHTML = '<p style="color:var(--accent-red)">Ошибка загрузки каталога атак</p>';
        return;
    }

    attacksCatalog = res.data;
    renderAttackCards(container);
}

function renderAttackCards(container) {
    container.innerHTML = '';

    attacksCatalog.forEach((attack, index) => {
        const card = document.createElement('div');
        card.className = 'attack-card';
        card.id = `attack-card-${attack.id}`;

        const payloadsHtml = attack.payloads.length > 0
            ? `<div class="attack-payloads">
                <div class="attack-payloads-title">Payloads</div>
                ${attack.payloads.map((p, i) =>
                    `<span class="payload-chip" data-attack="${attack.id}" data-index="${i}" onclick="selectPayload(this, '${attack.id}', ${i})">${escapeHtml(p)}</span>`
                ).join('')}
               </div>`
            : '';

        let actionsHtml = '';
        if (attack.id === 'ddos') {
            actionsHtml = `
                <div class="attack-actions">
                    <button class="btn btn-danger btn-full" onclick="runFloodAttack('${attack.id}')">
                        🌊 Запустить DDoS (150 запросов)
                    </button>
                </div>`;
        } else if (attack.id === 'dlp') {
            actionsHtml = `
                <div class="attack-actions">
                    <button class="btn btn-danger btn-full" onclick="runDLPTest('${attack.id}')">
                        🔒 Тест утечки данных
                    </button>
                </div>`;
        } else if (attack.id === 'chain') {
            actionsHtml = `
                <div class="attack-actions">
                    <button class="btn btn-danger btn-full" onclick="runChainAttack('${attack.id}')">
                        ⛓️ Запустить цепочку атак
                    </button>
                </div>`;
        } else {
            actionsHtml = `
                <div class="attack-actions">
                    <button class="btn btn-danger" onclick="runSingleAttack('${attack.id}')" id="btn-run-${attack.id}">
                        ⚔️ Атаковать
                    </button>
                    <button class="btn btn-primary" onclick="runAllPayloads('${attack.id}')">
                        🔄 Все payloads
                    </button>
                </div>`;
        }

        card.innerHTML = `
            <div class="attack-card-header">
                <div class="attack-card-info">
                    <span class="attack-card-icon">${attack.icon}</span>
                    <div>
                        <div class="attack-card-name">${attack.name}</div>
                    </div>
                </div>
                <span class="severity-badge severity-${attack.severity}">${attack.severity}</span>
            </div>
            <div class="attack-card-body">
                <p class="attack-card-desc">${attack.description}</p>
                ${payloadsHtml}
                ${actionsHtml}
                <div class="attack-result" id="result-${attack.id}">
                    <span style="color:var(--text-muted)">Ожидание запуска атаки...</span>
                </div>
            </div>
        `;

        container.appendChild(card);
    });
}

// ─── Payload Selection ────────────────────────────────────────

const selectedPayloads = {};

function selectPayload(el, attackId, index) {
    // Toggle selection
    const chips = document.querySelectorAll(`.payload-chip[data-attack="${attackId}"]`);
    chips.forEach(c => c.classList.remove('selected'));
    el.classList.add('selected');

    const attack = attacksCatalog.find(a => a.id === attackId);
    if (attack) {
        selectedPayloads[attackId] = attack.payloads[index];
    }
}

// ─── Run Single Attack ───────────────────────────────────────

async function runSingleAttack(attackId) {
    const attack = attacksCatalog.find(a => a.id === attackId);
    if (!attack) return;

    const payload = selectedPayloads[attackId] || attack.payloads[0];
    if (!payload) {
        showToast('Выберите payload для атаки', 'error');
        return;
    }

    const resultDiv = document.getElementById(`result-${attackId}`);
    resultDiv.innerHTML = '<div class="spinner"></div> Выполнение атаки...';

    const res = await apiPost('/api/attack/run', {
        attack_type: attackId,
        payload: payload,
    });

    if (!res.ok) {
        resultDiv.innerHTML = `<span class="line-warn">Ошибка: ${res.data.error || 'Unknown'}</span>`;
        return;
    }

    const r = res.data;
    const statusClass = r.blocked ? 'line-blocked' : 'line-passed';
    const statusIcon = r.blocked ? '🛑 BLOCKED' : '✅ PASSED';
    const statusText = r.blocked ? 'ЗАБЛОКИРОВАНО' : 'ПРОПУЩЕНО';

    resultDiv.innerHTML = `
        <div class="${statusClass}"><strong>${statusIcon} ${statusText}</strong></div>
        <div class="line-info">Detector: ${r.detector}</div>
        <div class="line-info">Score: ${r.score}/100</div>
        <div>Payload: <code>${escapeHtml(r.payload)}</code></div>
        <div>Details: ${r.details || 'N/A'}</div>
        <div style="color:var(--text-muted)">HTTP ${r.status_code}</div>
    `;

    showToast(
        `${attack.name}: ${statusText} (${r.detector})`,
        r.blocked ? 'success' : 'error'
    );
}

// ─── Run All Payloads ─────────────────────────────────────────

async function runAllPayloads(attackId) {
    const attack = attacksCatalog.find(a => a.id === attackId);
    if (!attack || attack.payloads.length === 0) return;

    const resultDiv = document.getElementById(`result-${attackId}`);
    resultDiv.innerHTML = '<div class="spinner"></div> Тестирование всех payloads...';

    let html = '';
    let blockedCount = 0;

    for (let i = 0; i < attack.payloads.length; i++) {
        const payload = attack.payloads[i];
        const res = await apiPost('/api/attack/run', {
            attack_type: attackId,
            payload: payload,
        });

        if (res.ok) {
            const r = res.data;
            if (r.blocked) blockedCount++;
            const statusClass = r.blocked ? 'line-blocked' : 'line-passed';
            const statusIcon = r.blocked ? '🛑' : '✅';
            html += `<div class="${statusClass}">${statusIcon} <code>${escapeHtml(payload)}</code> → ${r.detector} (score: ${r.score})</div>`;
        }
    }

    const allBlocked = blockedCount === attack.payloads.length;
    html = `<div class="line-info"><strong>Результат: ${blockedCount}/${attack.payloads.length} заблокировано</strong></div>` + html;
    resultDiv.innerHTML = html;

    showToast(
        `${attack.name}: ${blockedCount}/${attack.payloads.length} заблокировано`,
        allBlocked ? 'success' : 'error'
    );
}

// ─── DDoS / Flood Attack ─────────────────────────────────────

async function runFloodAttack(attackId) {
    const resultDiv = document.getElementById(`result-${attackId}`);
    resultDiv.innerHTML = '<div class="spinner"></div> Запуск DDoS-атаки (150 запросов)...';

    const res = await apiPost('/api/attack/flood', {
        count: 150,
        interval_ms: 30,
    });

    if (!res.ok) {
        resultDiv.innerHTML = `<span class="line-warn">Ошибка: ${res.data.error || 'Unknown'}</span>`;
        return;
    }

    const r = res.data;

    // Draw mini rate limiter chart
    const canvasId = `flood-canvas-${Date.now()}`;

    resultDiv.innerHTML = `
        <div class="line-info"><strong>📊 Результаты DDoS-теста</strong></div>
        <div>Всего запросов: <strong>${r.total}</strong></div>
        <div class="line-passed">✅ Пропущено: <strong>${r.passed}</strong></div>
        <div class="line-blocked">🛑 Заблокировано: <strong>${r.blocked}</strong></div>
        <div class="line-warn">⚠️ Rate Limit сработал на запросе: <strong>#${r.rate_limit_triggered_at || 'N/A'}</strong></div>
        <div>Лимит: ${r.max_requests_per_window} запросов / ${r.window_seconds} сек</div>
        <div style="margin-top:8px">
            <canvas id="${canvasId}" width="300" height="80"></canvas>
        </div>
    `;

    // Draw mini flood chart
    setTimeout(() => {
        drawFloodChart(canvasId, r.timeline || []);
    }, 50);

    showToast(`DDoS: ${r.blocked}/${r.total} заблокировано Rate Limiter`, 'success');
}

function drawFloodChart(canvasId, timeline) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const w = canvas.width;
    const h = canvas.height;

    ctx.fillStyle = '#0a0a1a';
    ctx.fillRect(0, 0, w, h);

    if (timeline.length === 0) return;

    const barWidth = Math.max(2, (w - 10) / timeline.length);

    timeline.forEach((item, i) => {
        const x = 5 + i * barWidth;
        const barH = h - 10;

        ctx.fillStyle = item.status === 'blocked'
            ? 'rgba(233, 69, 96, 0.7)'
            : 'rgba(0, 230, 118, 0.7)';
        ctx.fillRect(x, 5, barWidth - 1, barH);
    });
}

// ─── DLP Test ─────────────────────────────────────────────────

async function runDLPTest(attackId) {
    const resultDiv = document.getElementById(`result-${attackId}`);
    resultDiv.innerHTML = '<div class="spinner"></div> Тестирование DLP маскирования...';

    const res = await apiGet('/api/attack/dlp-test');
    if (!res.ok) {
        resultDiv.innerHTML = `<span class="line-warn">Ошибка</span>`;
        return;
    }

    const r = res.data;
    const actions = r.dlp_actions;

    resultDiv.innerHTML = `
        <div class="line-info"><strong>🔒 Результаты DLP-теста</strong></div>
        <div class="line-blocked">Email обнаружен и замаскирован: ${actions.email_detected ? '✅ Да' : '❌ Нет'}</div>
        <div class="line-blocked">Телефон обнаружен и замаскирован: ${actions.phone_detected ? '✅ Да' : '❌ Нет'}</div>
        <div class="line-blocked">Паспорт обнаружен и замаскирован: ${actions.passport_detected ? '✅ Да' : '❌ Нет'}</div>
        <div style="margin-top:8px;color:var(--text-muted)">Замаскированные данные:</div>
        <div style="margin-top:4px"><code style="color:var(--accent-cyan);word-break:break-all;font-size:11px">${escapeHtml(JSON.stringify(r.masked_data, null, 2).substring(0, 500))}</code></div>
    `;

    showToast(`DLP: ${actions.total_masked} типа данных замаскировано`, 'success');
}

// ─── Chain Attack ─────────────────────────────────────────────

async function runChainAttack(attackId) {
    const resultDiv = document.getElementById(`result-${attackId}`);
    resultDiv.innerHTML = '<div class="spinner"></div> Запуск цепочки APT-атаки...';

    // Animated step-by-step execution
    const phases = ['🔍 Фаза 1: Разведка (LFI)...', '💥 Фаза 2: Эксплуатация (RCE)...', '📤 Фаза 3: Эксфильтрация (DLP)...'];

    for (let i = 0; i < phases.length; i++) {
        resultDiv.innerHTML = `<div class="spinner"></div> ${phases[i]}`;
        await new Promise(r => setTimeout(r, 800));
    }

    const res = await apiPost('/api/attack/chain', {});

    if (!res.ok) {
        resultDiv.innerHTML = `<span class="line-warn">Ошибка</span>`;
        return;
    }

    const r = res.data;
    let html = `<div class="line-info"><strong>⛓️ Результаты APT-цепочки</strong></div>`;

    r.steps.forEach((step, i) => {
        const statusClass = step.blocked ? 'line-blocked' : 'line-passed';
        const statusIcon = step.blocked ? '🛑' : '✅';
        html += `
            <div style="margin: 6px 0; padding: 6px; border-left: 3px solid ${step.blocked ? 'var(--accent-red)' : 'var(--accent-green)'}; padding-left: 10px;">
                <div class="${statusClass}"><strong>${statusIcon} ${step.phase}</strong>: ${step.attack}</div>
                <div style="color:var(--text-muted);font-size:11px">Payload: <code>${escapeHtml(step.payload)}</code></div>
                <div style="color:var(--text-muted);font-size:11px">Detector: ${step.detector}${step.result_data ? ' | Masked: ' + escapeHtml(step.result_data.substring(0, 60)) : ''}</div>
            </div>
        `;
    });

    const summaryClass = r.chain_blocked ? 'line-blocked' : 'line-passed';
    html += `<div class="${summaryClass}" style="margin-top:8px"><strong>${r.summary}</strong></div>`;

    resultDiv.innerHTML = html;

    showToast(
        `APT Chain: ${r.chain_blocked ? 'Полностью заблокирована' : 'Частично прошла'}`,
        r.chain_blocked ? 'success' : 'error'
    );
}
