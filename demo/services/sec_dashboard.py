"""Авто-подключение дашборда безопасности sec (auto-discovered AEngine).

AEngine находит экземпляры Service в каталоге services/ (config.json: "services": "auto")
и регистрирует их автоматически.
"""
from AEngineApps.dashboard import SecDashboardService

# Дашборд безопасности доступен по адресу /sec-admin
sec_dashboard_service = SecDashboardService(prefix="/sec-admin")
