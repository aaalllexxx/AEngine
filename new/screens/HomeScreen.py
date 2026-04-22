"""
Примеры экранов. Несколько экранов в одном файле.
"""

from AEngineApps.screen import Screen


class HomeScreen(Screen):
    """Главный экран."""
    route = "/"
    methods = ["GET"]
    
    def run(self, *args, **kwargs):
        return self.render("index.html")