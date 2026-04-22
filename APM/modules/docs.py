__help__ = "Открыть документацию AEngineApps"
__module_type__ = "ПРОЧЕЕ"
import webbrowser

def run(*args, **kwargs):
    arg = kwargs["args"]
    if "-h" in arg:
        print("Usage: apm docs")
        return
    webbrowser.open("https://github.com/aaalllexxx/AEngineApps")