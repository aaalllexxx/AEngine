"""
screens/pages.py — HTML-страница SPA и health-check.
"""

from AEngineApps import Screen


class IndexPage(Screen):
    """Единственная HTML-страница SPA-стенда."""

    route = "/"
    methods = ["GET"]

    def run(self):
        return self.render("index.html")


class HealthScreen(Screen):
    """Health-check для Docker / балансировщиков."""

    route = "/health"
    methods = ["GET"]

    def run(self):
        return self.json({"status": "healthy"})
