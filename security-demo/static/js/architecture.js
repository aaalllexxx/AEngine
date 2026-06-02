/**
 * AEngine Security Demo — Architecture Tab (Tab 2)
 * Интерактивная SVG-схема архитектуры модуля sec
 */

let architectureInitialized = false;

function initArchitectureTab() {
    if (architectureInitialized) return;
    architectureInitialized = true;

    const container = document.getElementById('architecture-container');
    container.innerHTML = '';

    const wrapper = document.createElement('div');
    wrapper.className = 'arch-svg-wrapper';
    wrapper.innerHTML = buildArchitectureSVG();
    container.appendChild(wrapper);

    // Attach click handlers
    document.querySelectorAll('.arch-block').forEach(block => {
        block.addEventListener('click', () => {
            const id = block.dataset.component;
            showComponentPopup(id);
        });
    });
}

function buildArchitectureSVG() {
    return `
    <svg viewBox="0 0 1100 700" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:auto;min-height:500px;">
        <defs>
            <!-- Gradients -->
            <linearGradient id="grad-cyan" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#00d4ff;stop-opacity:0.2"/>
                <stop offset="100%" style="stop-color:#00d4ff;stop-opacity:0.05"/>
            </linearGradient>
            <linearGradient id="grad-red" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#e94560;stop-opacity:0.2"/>
                <stop offset="100%" style="stop-color:#e94560;stop-opacity:0.05"/>
            </linearGradient>
            <linearGradient id="grad-green" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#00e676;stop-opacity:0.2"/>
                <stop offset="100%" style="stop-color:#00e676;stop-opacity:0.05"/>
            </linearGradient>
            <linearGradient id="grad-purple" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#b388ff;stop-opacity:0.2"/>
                <stop offset="100%" style="stop-color:#b388ff;stop-opacity:0.05"/>
            </linearGradient>
            <linearGradient id="grad-yellow" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#ffd600;stop-opacity:0.2"/>
                <stop offset="100%" style="stop-color:#ffd600;stop-opacity:0.05"/>
            </linearGradient>
            <linearGradient id="grad-orange" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#ff9100;stop-opacity:0.2"/>
                <stop offset="100%" style="stop-color:#ff9100;stop-opacity:0.05"/>
            </linearGradient>

            <!-- Glow filter -->
            <filter id="glow">
                <feGaussianBlur stdDeviation="3" result="blur"/>
                <feMerge>
                    <feMergeNode in="blur"/>
                    <feMergeNode in="SourceGraphic"/>
                </feMerge>
            </filter>

            <!-- Animated arrow marker -->
            <marker id="arrow-cyan" viewBox="0 0 10 7" refX="9" refY="3.5" markerWidth="8" markerHeight="6" orient="auto-start-auto">
                <path d="M 0 0 L 10 3.5 L 0 7 z" fill="#00d4ff"/>
            </marker>
            <marker id="arrow-red" viewBox="0 0 10 7" refX="9" refY="3.5" markerWidth="8" markerHeight="6" orient="auto-start-auto">
                <path d="M 0 0 L 10 3.5 L 0 7 z" fill="#e94560"/>
            </marker>
            <marker id="arrow-green" viewBox="0 0 10 7" refX="9" refY="3.5" markerWidth="8" markerHeight="6" orient="auto-start-auto">
                <path d="M 0 0 L 10 3.5 L 0 7 z" fill="#00e676"/>
            </marker>
        </defs>

        <!-- Background -->
        <rect width="1100" height="700" fill="#0a0a1a" rx="12"/>

        <!-- Title -->
        <text x="550" y="35" fill="#e0e0e0" font-size="18" font-weight="700" text-anchor="middle" font-family="system-ui, sans-serif">Архитектура модуля безопасности AEngine (sec)</text>
        <text x="550" y="55" fill="#5a6478" font-size="12" text-anchor="middle" font-family="system-ui, sans-serif">Нажмите на компонент для подробной информации</text>

        <!-- ═══ Incoming Request ═══ -->
        <g class="arch-block" data-component="request" style="cursor:pointer">
            <rect x="20" y="170" width="120" height="60" rx="8" fill="url(#grad-cyan)" stroke="#00d4ff" stroke-width="1.5"/>
            <text x="80" y="195" fill="#00d4ff" font-size="13" text-anchor="middle" font-weight="600" font-family="system-ui">🌐 Входящий</text>
            <text x="80" y="212" fill="#00d4ff" font-size="13" text-anchor="middle" font-weight="600" font-family="system-ui">запрос</text>
        </g>

        <!-- Arrow: Request → Rate Limiter -->
        <line x1="140" y1="200" x2="190" y2="200" stroke="#00d4ff" stroke-width="2" marker-end="url(#arrow-cyan)" stroke-dasharray="6,3">
            <animate attributeName="stroke-dashoffset" from="18" to="0" dur="1s" repeatCount="indefinite"/>
        </line>

        <!-- ═══ Rate Limiter ═══ -->
        <g class="arch-block" data-component="rate_limiter" style="cursor:pointer">
            <rect x="195" y="150" width="160" height="100" rx="10" fill="url(#grad-red)" stroke="#e94560" stroke-width="1.5"/>
            <text x="275" y="178" fill="#e94560" font-size="14" text-anchor="middle" font-weight="700" font-family="system-ui">🚦 Rate Limiter</text>
            <text x="275" y="198" fill="#8892a4" font-size="11" text-anchor="middle" font-family="system-ui">Фильтр по IP</text>
            <text x="275" y="215" fill="#8892a4" font-size="11" text-anchor="middle" font-family="system-ui">100 req/60s</text>
            <text x="275" y="240" fill="#e94560" font-size="10" text-anchor="middle" font-family="monospace">→ 429 Too Many</text>
        </g>

        <!-- Arrow: Rate Limiter → IPS/IDS -->
        <line x1="355" y1="200" x2="415" y2="200" stroke="#00d4ff" stroke-width="2" marker-end="url(#arrow-cyan)" stroke-dasharray="6,3">
            <animate attributeName="stroke-dashoffset" from="18" to="0" dur="1s" repeatCount="indefinite"/>
        </line>

        <!-- ═══ IPS/IDS ═══ -->
        <g class="arch-block" data-component="ips_ids" style="cursor:pointer">
            <rect x="420" y="80" width="260" height="240" rx="10" fill="url(#grad-cyan)" stroke="#00d4ff" stroke-width="1.5"/>
            <text x="550" y="108" fill="#00d4ff" font-size="14" text-anchor="middle" font-weight="700" font-family="system-ui">🛡️ IPS / IDS</text>
            <text x="550" y="126" fill="#5a6478" font-size="10" text-anchor="middle" font-family="system-ui">Обнаружение и предотвращение вторжений</text>

            <!-- Detector boxes -->
            <rect x="440" y="140" width="105" height="34" rx="6" fill="rgba(233,69,96,0.15)" stroke="#e94560" stroke-width="1"/>
            <text x="492" y="161" fill="#e94560" font-size="11" text-anchor="middle" font-family="monospace">SQLiDetector</text>

            <rect x="555" y="140" width="105" height="34" rx="6" fill="rgba(255,145,0,0.15)" stroke="#ff9100" stroke-width="1"/>
            <text x="607" y="161" fill="#ff9100" font-size="11" text-anchor="middle" font-family="monospace">XSSDetector</text>

            <rect x="440" y="182" width="105" height="34" rx="6" fill="rgba(255,214,0,0.15)" stroke="#ffd600" stroke-width="1"/>
            <text x="492" y="203" fill="#ffd600" font-size="11" text-anchor="middle" font-family="monospace">LFIDetector</text>

            <rect x="555" y="182" width="105" height="34" rx="6" fill="rgba(179,136,255,0.15)" stroke="#b388ff" stroke-width="1"/>
            <text x="607" y="203" fill="#b388ff" font-size="11" text-anchor="middle" font-family="monospace">RCEDetector</text>

            <rect x="440" y="224" width="105" height="34" rx="6" fill="rgba(0,212,255,0.15)" stroke="#00d4ff" stroke-width="1"/>
            <text x="492" y="245" fill="#00d4ff" font-size="11" text-anchor="middle" font-family="monospace">Signatures</text>

            <rect x="555" y="224" width="105" height="34" rx="6" fill="rgba(0,230,118,0.15)" stroke="#00e676" stroke-width="1"/>
            <text x="607" y="245" fill="#00e676" font-size="11" text-anchor="middle" font-family="monospace">RuleDetector</text>

            <text x="550" y="300" fill="#e94560" font-size="10" text-anchor="middle" font-family="monospace">→ 400 Bad Request</text>
        </g>

        <!-- Arrow: IPS → Application -->
        <line x1="680" y1="200" x2="740" y2="200" stroke="#00e676" stroke-width="2" marker-end="url(#arrow-green)" stroke-dasharray="6,3">
            <animate attributeName="stroke-dashoffset" from="18" to="0" dur="1s" repeatCount="indefinite"/>
        </line>

        <!-- ═══ Application ═══ -->
        <g class="arch-block" data-component="application" style="cursor:pointer">
            <rect x="745" y="155" width="140" height="90" rx="10" fill="url(#grad-green)" stroke="#00e676" stroke-width="1.5"/>
            <text x="815" y="185" fill="#00e676" font-size="14" text-anchor="middle" font-weight="700" font-family="system-ui">⚙️ Application</text>
            <text x="815" y="205" fill="#8892a4" font-size="11" text-anchor="middle" font-family="system-ui">AEngineApps</text>
            <text x="815" y="222" fill="#8892a4" font-size="11" text-anchor="middle" font-family="system-ui">App + API + Screen</text>
        </g>

        <!-- Arrow: Application → DLP (response) -->
        <line x1="885" y1="200" x2="940" y2="200" stroke="#00e676" stroke-width="2" marker-end="url(#arrow-green)" stroke-dasharray="6,3">
            <animate attributeName="stroke-dashoffset" from="18" to="0" dur="1s" repeatCount="indefinite"/>
        </line>

        <!-- ═══ DLP ═══ -->
        <g class="arch-block" data-component="dlp" style="cursor:pointer">
            <rect x="945" y="140" width="130" height="120" rx="10" fill="url(#grad-purple)" stroke="#b388ff" stroke-width="1.5"/>
            <text x="1010" y="168" fill="#b388ff" font-size="14" text-anchor="middle" font-weight="700" font-family="system-ui">🔒 DLP</text>
            <text x="1010" y="188" fill="#8892a4" font-size="10" text-anchor="middle" font-family="system-ui">Маскирование</text>
            <text x="1010" y="203" fill="#8892a4" font-size="10" text-anchor="middle" font-family="system-ui">Email, Phone</text>
            <text x="1010" y="218" fill="#8892a4" font-size="10" text-anchor="middle" font-family="system-ui">Passport</text>
            <text x="1010" y="248" fill="#b388ff" font-size="10" text-anchor="middle" font-family="monospace">after_request</text>
        </g>

        <!-- ═══ Response arrow back ═══ -->
        <text x="1010" y="285" fill="#00e676" font-size="12" text-anchor="middle" font-family="system-ui">↓ Response</text>

        <!-- ═══════ Bottom Row: Background Services ═══════ -->

        <!-- ═══ OS Protection ═══ -->
        <g class="arch-block" data-component="os_protection" style="cursor:pointer">
            <rect x="50" y="400" width="200" height="120" rx="10" fill="url(#grad-yellow)" stroke="#ffd600" stroke-width="1.5"/>
            <text x="150" y="428" fill="#ffd600" font-size="14" text-anchor="middle" font-weight="700" font-family="system-ui">🖥️ OS Protection</text>
            <text x="150" y="450" fill="#8892a4" font-size="11" text-anchor="middle" font-family="system-ui">Мониторинг CPU / RAM</text>
            <text x="150" y="467" fill="#8892a4" font-size="11" text-anchor="middle" font-family="system-ui">Root-check привилегий</text>
            <text x="150" y="484" fill="#8892a4" font-size="11" text-anchor="middle" font-family="system-ui">Анти-DoS на уровне ОС</text>
            <text x="150" y="508" fill="#ffd600" font-size="10" text-anchor="middle" font-family="monospace">→ 503 Service Unavailable</text>
        </g>

        <!-- ═══ System Protection ═══ -->
        <g class="arch-block" data-component="sys_protection" style="cursor:pointer">
            <rect x="280" y="400" width="220" height="120" rx="10" fill="url(#grad-orange)" stroke="#ff9100" stroke-width="1.5"/>
            <text x="390" y="428" fill="#ff9100" font-size="14" text-anchor="middle" font-weight="700" font-family="system-ui">🔍 System Protection</text>
            <text x="390" y="450" fill="#8892a4" font-size="11" text-anchor="middle" font-family="system-ui">Сканер процессов</text>
            <text x="390" y="467" fill="#8892a4" font-size="11" text-anchor="middle" font-family="system-ui">Аудит конфигурации</text>
            <text x="390" y="484" fill="#8892a4" font-size="11" text-anchor="middle" font-family="system-ui">Заголовки безопасности</text>
            <text x="390" y="508" fill="#ff9100" font-size="10" text-anchor="middle" font-family="monospace">Фоновый поток (30s)</text>
        </g>

        <!-- ═══ Code Signer ═══ -->
        <g class="arch-block" data-component="code_signer" style="cursor:pointer">
            <rect x="530" y="400" width="200" height="120" rx="10" fill="url(#grad-cyan)" stroke="#00d4ff" stroke-width="1.5"/>
            <text x="630" y="428" fill="#00d4ff" font-size="14" text-anchor="middle" font-weight="700" font-family="system-ui">✍️ Code Signer</text>
            <text x="630" y="450" fill="#8892a4" font-size="11" text-anchor="middle" font-family="system-ui">Подпись исходного кода</text>
            <text x="630" y="467" fill="#8892a4" font-size="11" text-anchor="middle" font-family="system-ui">Контроль целостности</text>
            <text x="630" y="484" fill="#8892a4" font-size="11" text-anchor="middle" font-family="system-ui">HMAC-SHA256 подписи</text>
            <text x="630" y="508" fill="#00d4ff" font-size="10" text-anchor="middle" font-family="monospace">sign.py / unsign.py</text>
        </g>

        <!-- ═══ Cluster ═══ -->
        <g class="arch-block" data-component="cluster" style="cursor:pointer">
            <rect x="760" y="400" width="220" height="120" rx="10" fill="url(#grad-green)" stroke="#00e676" stroke-width="1.5"/>
            <text x="870" y="428" fill="#00e676" font-size="14" text-anchor="middle" font-weight="700" font-family="system-ui">🌐 HA Cluster</text>
            <text x="870" y="450" fill="#8892a4" font-size="11" text-anchor="middle" font-family="system-ui">Master / Slave ноды</text>
            <text x="870" y="467" fill="#8892a4" font-size="11" text-anchor="middle" font-family="system-ui">Heartbeat мониторинг</text>
            <text x="870" y="484" fill="#8892a4" font-size="11" text-anchor="middle" font-family="system-ui">Автоматический Failover</text>
            <text x="870" y="508" fill="#00e676" font-size="10" text-anchor="middle" font-family="monospace">ClusterNode + LocalCluster</text>
        </g>

        <!-- ═══ Connection lines from main flow to background ═══ -->
        <!-- Dashed vertical connections -->
        <line x1="275" y1="250" x2="150" y2="400" stroke="#ffd600" stroke-width="1" stroke-dasharray="4,4" opacity="0.5"/>
        <line x1="550" y1="320" x2="390" y2="400" stroke="#ff9100" stroke-width="1" stroke-dasharray="4,4" opacity="0.5"/>
        <line x1="815" y1="245" x2="630" y2="400" stroke="#00d4ff" stroke-width="1" stroke-dasharray="4,4" opacity="0.5"/>
        <line x1="815" y1="245" x2="870" y2="400" stroke="#00e676" stroke-width="1" stroke-dasharray="4,4" opacity="0.5"/>

        <!-- Labels for flow -->
        <text x="550" y="355" fill="#5a6478" font-size="11" text-anchor="middle" font-family="system-ui">── Фоновые сервисы защиты ──</text>

        <!-- Data flow label -->
        <text x="550" y="75" fill="#00d4ff" font-size="11" text-anchor="middle" font-family="system-ui">──────────── Поток обработки запроса (Request Pipeline) ────────────</text>

        <!-- Animated data flow particles -->
        <circle r="4" fill="#00d4ff" opacity="0.8" filter="url(#glow)">
            <animateMotion dur="4s" repeatCount="indefinite" path="M 80,200 L 275,200 L 550,200 L 815,200 L 1010,200"/>
        </circle>
        <circle r="3" fill="#00e676" opacity="0.6" filter="url(#glow)">
            <animateMotion dur="4s" repeatCount="indefinite" begin="2s" path="M 80,200 L 275,200 L 550,200 L 815,200 L 1010,200"/>
        </circle>
    </svg>
    `;
}

// ─── Component Popups ─────────────────────────────────────────

const componentInfo = {
    request: {
        title: '🌐 Входящий запрос',
        description: 'HTTP-запрос от клиента (браузер, API, мобильное приложение). Проходит через все уровни защиты перед достижением обработчика приложения.',
        api: 'Flask request object — содержит URL, заголовки, параметры, тело запроса',
        code: `# Запрос автоматически проходит через:\n# 1. RateLimiter.before_request()\n# 2. IPS.before_request() → детекторы\n# 3. Обработчик маршрута\n# 4. DLP.after_request() → маскирование`
    },
    rate_limiter: {
        title: '🚦 Rate Limiter',
        description: 'Ограничитель частоты запросов по IP-адресу. Защищает от DDoS-атак и брутфорса. Использует скользящее окно (sliding window) для подсчёта запросов.',
        api: 'RateLimiter(app, max_requests=100, window=60)\nАвтоматически регистрирует before_request хук',
        code: `from sec.intrusions import RateLimiter\n\n# Макс 100 запросов в минуту с одного IP\nlimiter = RateLimiter(app, max_requests=100, window=60)\n\n# При превышении → HTTP 429 Too Many Requests`
    },
    ips_ids: {
        title: '🛡️ IPS / IDS (Intrusion Prevention/Detection System)',
        description: 'Система обнаружения и предотвращения вторжений. IDS логирует атаки, IPS блокирует их (abort 400). Содержит 6 детекторов: SQLi, XSS, LFI, RCE, Signatures, Rules.',
        api: 'IPS(app) — автоматически регистрирует все детекторы\nIDS(app) — только обнаружение, без блокировки\nips.add_detector(CustomDetector) — добавление своего детектора',
        code: `from sec.intrusions import IPS, IDS\n\n# IPS — блокирует атаки (abort 400)\nips = IPS(app)\n\n# IDS — только логирует\nids = IDS(app)\nids.add_detector(SQLiDetector)\n\n@ids.on_trigger\ndef on_attack():\n    print("Атака обнаружена!")`
    },
    application: {
        title: '⚙️ Application (AEngineApps)',
        description: 'Ядро приложения на базе AEngineApps — OOP-обёртка над Flask. Обрабатывает маршруты через Screen и API классы.',
        api: 'App(name) — создание приложения\nApp.add_screen(path, ScreenClass) — регистрация экрана\nApp.register_service(service) — регистрация сервиса',
        code: `from AEngineApps import App, API, Screen\n\napp = App("MyApp")\n\nclass UserAPI(API):\n    methods = ["GET", "POST"]\n    \n    def get(self):\n        return {"users": [...]}\n\napp.add_screen("/api/users", UserAPI)`
    },
    dlp: {
        title: '🔒 DLP (Data Loss Prevention)',
        description: 'Предотвращение утечек данных. Маскирует персональные данные (email, телефоны, паспорта) в исходящих ответах. Работает через after_request хук.',
        api: 'DLP(app, mode=DLPMode.Agressive)\ndlp.add_filter(MailFilter) — добавление фильтра\n$DLPSAFE{data} — обёртка для данных, которые НЕ нужно маскировать',
        code: `from sec.dlp import DLP, DLPMode, MailFilter,\n  PhoneFilter, PassportFilter\n\ndlp = DLP(app, mode=DLPMode.Agressive)\ndlp.add_filter(MailFilter)\ndlp.add_filter(PhoneFilter)\ndlp.add_filter(PassportFilter)\n\n# Email, телефоны и паспорта автоматически\n# маскируются в ВСЕХ ответах`
    },
    os_protection: {
        title: '🖥️ OS Protection',
        description: 'Модуль защиты операционной системы хоста. Контролирует потребление ресурсов (CPU, RAM) и проверяет привилегии (root/admin). Автоматически блокирует запросы при критической нагрузке (HTTP 503).',
        api: 'OSProtection(app, max_cpu_percent=90, max_ram_percent=90)\ncheck_resources() → {"cpu_percent": ..., "ram_percent": ...}\ncheck_privileges() → {"is_admin": bool}\nrun_health_check() → полный отчёт',
        code: `from sec.os_protect import OSProtection\n\nos_prot = OSProtection(app, max_cpu_percent=90)\n\n# Автоматическая проверка перед каждым запросом\n# При CPU > 90% или RAM > 90%:\n#   → HTTP 503 Service Unavailable\n\nhealth = os_prot.run_health_check()\nprint(health["resources"]["cpu_percent"])`
    },
    sys_protection: {
        title: '🔍 Advanced System Protection',
        description: 'Продвинутый модуль защиты. Фоновый сканер проверяет процессы на подозрительные имена (майнеры, reverse shell), аудит конфигурации (слабые ключи), мониторинг пользователей ОС.',
        api: 'AdvancedSystemProtection(app, scan_interval=30)\nscan() → полный отчёт\non_alert(callback) → колбэк при угрозе\nenable_cors(app) / enable_csp(app) → заголовки',
        code: `from sec.sys_protect import AdvancedSystemProtection,\n  enable_cors, enable_csp\n\nprot = AdvancedSystemProtection(app, scan_interval=30)\n\n@prot.on_alert\ndef handle_alert(report):\n    print(f"Угроза: {report['alerts']}")\n\nenable_cors(app)  # CORS заголовки\nenable_csp(app)   # CSP заголовки`
    },
    code_signer: {
        title: '✍️ Code Signer',
        description: 'Модуль контроля целостности исходного кода. Подписывает файлы с помощью HMAC-SHA256 и проверяет подписи при запуске. Защищает от несанкционированной модификации кода.',
        api: 'python sign.py — подписать все файлы проекта\npython unsign.py — удалить подписи\nАвтоматическая верификация при импорте',
        code: `# Подпись кода:\npython sec/sign.py\n\n# Верификация:\npython sec/code_signer.py\n\n# Каждый .py файл получает HMAC-SHA256\n# подпись в виде комментария.\n# При запуске проверяется целостность.`
    },
    cluster: {
        title: '🌐 HA Cluster',
        description: 'Модуль высокой доступности. Поддерживает Active-Passive кластеризацию с автоматическим Heartbeat и Failover. Master-нода обрабатывает запросы, Slave-ноды ожидают в горячем резерве.',
        api: 'ClusterNode(app, role, host, port)\nLocalCluster(app, workers=3) — локальный кластер\nHeartbeat: автоматический ping между нодами\nFailover: автоматическое переключение при сбое',
        code: `from sec.cluster import ClusterNode\nfrom sec.auto_cluster import LocalCluster\n\n# Локальный кластер на 3 воркерах:\ncluster = LocalCluster(app, workers=3)\ncluster.start()\n\n# Или ручная настройка нод:\nnode = ClusterNode(\n  app, role="master",\n  host="0.0.0.0", port=5000\n)`
    }
};

function showComponentPopup(id) {
    const info = componentInfo[id];
    if (!info) return;

    const html = `
        <div class="popup-title">${info.title}</div>

        <div class="popup-section">
            <h4>Описание</h4>
            <p>${info.description}</p>
        </div>

        <div class="popup-section">
            <h4>API</h4>
            <pre class="popup-code">${escapeHtml(info.api)}</pre>
        </div>

        <div class="popup-section">
            <h4>Пример использования</h4>
            <pre class="popup-code">${escapeHtml(info.code)}</pre>
        </div>
    `;

    showPopup(html);
}
