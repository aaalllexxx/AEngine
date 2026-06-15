"""
Намеренно уязвимые эндпоинты демостенда AEngine.

ВНИМАНИЕ: код ниже СПЕЦИАЛЬНО написан небезопасно (SQLi, XSS, RCE, LFI),
чтобы продемонстрировать работу модуля защиты sec (IDS/IPS).
НЕ используйте эти паттерны в реальных приложениях.

При включённом модуле intrusion (вкладка «Модули» в /sec-admin) IPS блокирует
вредоносные запросы (HTTP 400) ещё до того, как они дойдут до этих обработчиков.
"""

import os
import sqlite3

from AEngineApps.screen import Screen
from AEngineApps.api import API


class HomeScreen(Screen):
    """Главная страница со списком уязвимых форм."""
    route = "/"
    methods = ["GET"]

    def run(self, *args, **kwargs):
        return self.render("index.html", title="AEngine Security Demo")


class LoginAPI(API):
    """SQL-инъекция: логин/пароль подставляются в SQL-строку конкатенацией."""
    route = "/api/login"
    methods = ["POST"]

    def post(self, *args, **kwargs):
        login = self.request.form.get("login", "")
        password = self.request.form.get("password", "")

        con = sqlite3.connect(":memory:")
        cur = con.cursor()
        cur.execute("CREATE TABLE users(id INTEGER, name TEXT, pass TEXT, secret TEXT)")
        cur.executemany(
            "INSERT INTO users VALUES (?,?,?,?)",
            [(1, "admin", "s3cr3t", "FLAG{sql_injection_demo}"),
             (2, "alice", "wonderland", "user-data-alice")],
        )
        # УЯЗВИМО: пользовательский ввод напрямую в запросе.
        query = f"SELECT name, secret FROM users WHERE name='{login}' AND pass='{password}'"
        try:
            rows = cur.execute(query).fetchall()
        except Exception as e:
            return {"error": str(e), "query": query}, 400
        finally:
            con.close()

        if rows:
            return {"status": "ok", "query": query, "rows": rows}
        return {"status": "denied", "query": query}, 401


class SearchAPI(API):
    """Отражённый XSS: параметр q возвращается в HTML без экранирования."""
    route = "/api/search"
    methods = ["GET"]

    def get(self, *args, **kwargs):
        q = self.request.args.get("q", "")
        # УЯЗВИМО: ввод вставляется в HTML как есть.
        return f"<h2>Результаты поиска: {q}</h2><p>Ничего не найдено.</p>"


class ExecAPI(API):
    """RCE (command injection): ввод попадает в shell-команду."""
    route = "/api/exec"
    methods = ["GET"]

    def get(self, *args, **kwargs):
        host = self.request.args.get("host", "127.0.0.1")
        # УЯЗВИМО: ввод склеивается в команду оболочки.
        command = f"ping -n 1 {host}"
        # В НАСТОЯЩЕМ уязвимом приложении здесь был бы вызов:
        #   subprocess.check_output(command, shell=True, text=True)
        # В демостенде команда НЕ выполняется (безопасность): возвращаем точку инъекции.
        # Детектор RCE анализирует payload запроса, а не результат выполнения.
        return {"would_execute": command, "note": "shell-команда НЕ выполнена (демо)"}


class ReadFileAPI(API):
    """LFI / Path Traversal: файл читается по пути из параметра без проверки."""
    route = "/api/readfile"
    methods = ["GET"]

    def get(self, *args, **kwargs):
        rel_path = self.request.args.get("path", "readme.txt")
        # УЯЗВИМО: нет проверки выхода за пределы каталога проекта.
        target = os.path.join(self._app.project_root, rel_path)
        try:
            with open(target, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()[:2000]
            return {"path": rel_path, "content": content}
        except Exception as e:
            return {"error": str(e), "path": rel_path}, 404
