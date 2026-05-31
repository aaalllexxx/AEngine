"""
test_security.py — Тесты для модуля безопасности sec/.

Тестирует: BasicFilter, DLPMode, ClusterNode (создание),
детекторы IDS (SQLi, XSS, LFI, RCE паттерны).
"""

import pytest

from sec.dlp import BasicFilter, DLPMode, MailFilter, PhoneFilter, PassportFilter
from sec.cluster import ClusterNode
from sec.intrusions import (
    BaseDetector,
    SQLiDetector,
    XSSDetector,
    LFIDetector,
    RCEDetector,
)


# ═══════════════════════════════════════════════════════════════
# DLP — BasicFilter и подклассы
# ═══════════════════════════════════════════════════════════════


class TestDLPFilters:
    """Тесты DLP-фильтров (BasicFilter и подклассы)."""

    def test_dlp_mode_values(self):
        """DLPMode имеет Agressive и Passive."""
        assert DLPMode.Agressive.value == 0
        assert DLPMode.Passive.value == 1

    def test_mail_filter_detects_email(self):
        """MailFilter обнаруживает email-адреса."""
        text = "Send to admin@example.com for info"
        assert MailFilter.check(text) is not False

    def test_mail_filter_no_email(self):
        """MailFilter не срабатывает без email."""
        text = "No email addresses here"
        assert MailFilter.check(text) is False

    def test_mail_filter_hide(self):
        """MailFilter.hide() удаляет email из текста."""
        text = "Contact: user@test.com"
        result = MailFilter.hide(text)
        assert "user@test.com" not in result

    def test_mail_filter_hide_clean_text(self):
        """MailFilter.hide() не модифицирует текст без email."""
        clean_text = "No sensitive data here"
        assert MailFilter.hide(clean_text) == clean_text

    def test_phone_filter_detects_phone(self):
        """PhoneFilter обнаруживает телефонные номера."""
        text = "Call +79991234567 now"
        assert PhoneFilter.check(text) is not False

    def test_phone_filter_no_phone(self):
        """PhoneFilter не срабатывает без телефона."""
        text = "No phone number"
        assert PhoneFilter.check(text) is False

    def test_passport_filter_detects_passport(self):
        """PassportFilter обнаруживает паспортные данные."""
        text = "Паспорт: 1234 567890"
        assert PassportFilter.check(text) is not False

    def test_passport_filter_no_passport(self):
        """PassportFilter не срабатывает без паспортных данных."""
        text = "Просто текст без номеров"
        assert PassportFilter.check(text) is False

    def test_basic_filter_max_length(self):
        """BasicFilter не проверяет текст длиннее 1МБ."""
        long_text = "a" * 1_100_000
        assert BasicFilter.check(long_text) is False

    def test_phone_filter_hide(self):
        """PhoneFilter.hide() удаляет телефон из текста."""
        text = "Call +79991234567 now"
        result = PhoneFilter.hide(text)
        assert "+79991234567" not in result


# ═══════════════════════════════════════════════════════════════
# IDS — Детекторы (проверка паттернов без Flask request)
# ═══════════════════════════════════════════════════════════════


class TestDetectorPatterns:
    """Тесты паттернов детекторов (без активного Flask-запроса)."""

    def test_sqli_dangerous_keywords(self):
        """SQLiDetector содержит набор опасных ключевых слов."""
        assert "SELECT" in SQLiDetector.dangerous
        assert "UNION" in SQLiDetector.dangerous
        assert "DROP" in SQLiDetector.dangerous
        assert "INSERT" in SQLiDetector.dangerous

    def test_sqli_special_chars(self):
        """SQLiDetector содержит спецсимволы SQL-инъекций."""
        assert "--" in SQLiDetector.special
        assert "/*" in SQLiDetector.special
        assert ";" in SQLiDetector.special

    def test_xss_detector_has_patterns(self):
        """XSSDetector имеет critical_patterns и suspicious_patterns."""
        assert hasattr(XSSDetector, "critical_patterns")
        assert hasattr(XSSDetector, "suspicious_patterns")
        assert "<script" in XSSDetector.critical_patterns
        assert "javascript:" in XSSDetector.critical_patterns
        assert "<" in XSSDetector.suspicious_patterns

    def test_lfi_detector_patterns(self):
        """LFIDetector обнаруживает path traversal паттерны."""
        pattern = LFIDetector.patterns
        assert pattern.search("../../etc/passwd") is not None
        assert pattern.search("%2e%2e/secret") is not None
        assert pattern.search("/etc/shadow") is not None
        assert pattern.search("normal/path") is None

    def test_rce_detector_dangerous_commands(self):
        """RCEDetector содержит список опасных команд."""
        assert "eval" in RCEDetector.dangerous
        assert "exec" in RCEDetector.dangerous
        assert "system" in RCEDetector.dangerous
        assert "subprocess" in RCEDetector.dangerous

    def test_base_detector_is_abstract(self):
        """BaseDetector — абстрактный класс, нельзя напрямую использовать."""
        assert hasattr(BaseDetector, "run")
        assert hasattr(BaseDetector, "log")
        assert hasattr(BaseDetector, "trigger_response")


# ═══════════════════════════════════════════════════════════════
# ClusterNode
# ═══════════════════════════════════════════════════════════════


class TestClusterNode:
    """Тесты для ClusterNode (создание, конфигурация)."""

    def test_cluster_node_creation(self):
        """ClusterNode создаётся с корректными параметрами."""
        node = ClusterNode(
            node_id="node-1",
            role="master",
            master_ip="127.0.0.1",
            master_port=9000,
        )
        assert node.node_id == "node-1"
        assert node.role == "master"
        assert node.master_ip == "127.0.0.1"
        assert node.master_port == 9000
        assert node.running is False

    def test_cluster_node_slave(self):
        """ClusterNode в роли slave нормализует роль в lowercase."""
        node = ClusterNode(
            node_id="node-2",
            role="SLAVE",
            master_ip="10.0.0.1",
            master_port=9000,
        )
        assert node.role == "slave"

    def test_cluster_node_default_params(self):
        """ClusterNode имеет дефолтные параметры heartbeat."""
        node = ClusterNode(
            node_id="node-3",
            role="master",
            master_ip="127.0.0.1",
            master_port=9000,
        )
        assert node.heartbeat_interval == 2
        assert node.timeout == 6
        assert node.sync_dir == "."

    def test_cluster_node_custom_params(self):
        """ClusterNode принимает кастомные параметры."""
        node = ClusterNode(
            node_id="node-4",
            role="master",
            master_ip="127.0.0.1",
            master_port=9000,
            sync_dir="/tmp/sync",
            heartbeat_interval=5,
            timeout=15,
        )
        assert node.heartbeat_interval == 5
        assert node.timeout == 15
        assert node.sync_dir == "/tmp/sync"

    def test_cluster_node_stop(self):
        """ClusterNode.stop() устанавливает running=False."""
        node = ClusterNode(
            node_id="node-5",
            role="master",
            master_ip="127.0.0.1",
            master_port=9000,
        )
        node.running = True
        node.stop()
        assert node.running is False

    def test_cluster_node_on_failover_default(self):
        """on_failover по умолчанию None."""
        node = ClusterNode(
            node_id="node-6",
            role="slave",
            master_ip="127.0.0.1",
            master_port=9000,
        )
        assert node.on_failover is None

    def test_is_safe_tar_member_blocks_traversal(self, tmp_path):
        """_is_safe_tar_member блокирует path traversal."""
        import tarfile

        # Создаём фиктивный TarInfo с опасным путём
        bad_member = tarfile.TarInfo(name="../../etc/passwd")
        assert ClusterNode._is_safe_tar_member(bad_member, str(tmp_path)) is False

    def test_is_safe_tar_member_allows_normal(self, tmp_path):
        """_is_safe_tar_member разрешает нормальные пути."""
        import tarfile

        good_member = tarfile.TarInfo(name="src/main.py")
        assert ClusterNode._is_safe_tar_member(good_member, str(tmp_path)) is True


# ═══════════════════════════════════════════════════════════════
# __init__.py экспорт
# ═══════════════════════════════════════════════════════════════


class TestSecExports:
    """Тест экспортируемых имён из sec/__init__.py."""

    def test_all_exports(self):
        """sec.__all__ содержит все ключевые классы."""
        import sec

        expected = [
            "IDS", "IPS", "BaseDetector",
            "DLP", "DLPMode", "BasicFilter",
            "ClusterNode", "Logger",
        ]
        for name in expected:
            assert name in sec.__all__, f"{name} не найден в sec.__all__"
            assert hasattr(sec, name), f"sec.{name} не доступен"
