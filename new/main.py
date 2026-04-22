import os
import time
from AEngineApps.app import App

class MyApp(App):
    def __init__(self):
        super().__init__(debug=True)
        self.load_config(self.project_root + "config.json")
    
if __name__ == "__main__":
    app = MyApp()
    app.run()