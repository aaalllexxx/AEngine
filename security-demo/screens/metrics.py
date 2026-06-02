"""
screens/metrics.py — вкладка «Метрики».

Сводка/журнал берутся из GlobalStorage (см. ``state.py``), системные метрики — из
реального ``psutil``. Нагрузочный тест (`stress-test`) — это сравнительная
ВИЗУАЛИЗАЦИЯ (синтетические кривые), а не работа ``sec``; используется только для
наглядного сравнения «с rate limiter / без».
"""

import os

from AEngineApps import API

from state import get_metrics, get_logs, reset_metrics


class MetricsSummaryAPI(API):
    route = "/api/metrics/summary"
    methods = ["GET"]

    def get(self):
        m = get_metrics()
        return {
            "total_attacks": m["total_attacks"],
            "blocked": m["blocked"],
            "passed": m["passed"],
            "by_type": m["by_type"],
            "block_rate": round(m["blocked"] / max(m["total_attacks"], 1) * 100, 1),
        }


class MetricsSystemAPI(API):
    route = "/api/metrics/system"
    methods = ["GET"]

    def get(self):
        try:
            import psutil
            cpu = psutil.cpu_percent(interval=0.1)
            ram = psutil.virtual_memory().percent
            connections = len(psutil.net_connections(kind="inet"))
            disk = psutil.disk_usage("/").percent if os.name != "nt" else psutil.disk_usage("C:\\").percent
        except Exception:
            cpu = ram = connections = disk = 0

        return {
            "cpu_percent": cpu,
            "ram_percent": ram,
            "connections": connections,
            "disk_percent": disk,
            "platform": os.name,
        }


class MetricsLogsAPI(API):
    route = "/api/metrics/logs"
    methods = ["GET"]

    def get(self):
        limit = self.get_arg("limit", int, 100)
        return get_logs(limit)


class StressTestAPI(API):
    route = "/api/metrics/stress-test"
    methods = ["POST"]

    def post(self):
        data = self.request.get_json(silent=True) or {}
        with_rate_limiter = data.get("with_rate_limiter", True)
        num_requests = min(int(data.get("requests", 200)), 500)

        try:
            import psutil
            base_cpu = psutil.cpu_percent(interval=0.1)
            base_ram = psutil.virtual_memory().percent
        except Exception:
            base_cpu = 15.0
            base_ram = 40.0

        max_rps = 100  # Порог rate limiter
        data_points = []
        for i in range(0, num_requests, 10):
            progress = i / num_requests
            if with_rate_limiter:
                cpu = base_cpu + (progress * 5) + (i % 3)
                ram = base_ram + (progress * 2)
                active_requests = min(i, max_rps)
            else:
                cpu = base_cpu + (progress * 45) + (i % 5)
                ram = base_ram + (progress * 20)
                active_requests = i

            data_points.append({
                "request_num": i,
                "cpu": round(min(cpu, 99), 1),
                "ram": round(min(ram, 99), 1),
                "active_requests": active_requests,
                "rps": min(i, max_rps) if with_rate_limiter else i,
            })

        return {
            "with_rate_limiter": with_rate_limiter,
            "total_requests": num_requests,
            "data_points": data_points,
        }


class MetricsResetAPI(API):
    route = "/api/metrics/reset"
    methods = ["POST"]

    def post(self):
        reset_metrics()
        return {"status": "ok", "message": "Metrics reset"}
