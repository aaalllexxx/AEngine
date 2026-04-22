import os
import subprocess
import tempfile
    
class System:
    """Кроссплатформенная абстракция для Windows/Linux операций."""
    name = "windows" if os.name == "nt" else "linux"
    
    @classmethod
    def get_config_dir(cls):
        """Get platform-specific config directory"""
        if cls.name == "windows":
            appdata = os.getenv('APPDATA')
            if not appdata:
                # Fallback if APPDATA is not set
                appdata = os.path.expanduser('~/AppData/Roaming')
            return os.path.join(appdata, 'apm')
        else:
            return os.path.expanduser('~/.config/apm')
    
    @classmethod
    def get_temp_file(cls, filename="apm_goto.tmp"):
        """Get platform-specific temporary file path"""
        return os.path.join(tempfile.gettempdir(), filename)

    @classmethod
    def clear(cls):
        """Очистка консоли."""
        if cls.name == "windows":
            os.system("cls")
        else:
            os.system("clear")
    
    @classmethod
    def run(cls, win_command, lin_command, env=None):
        """Запускает платформо-специфичную команду. Возвращает код возврата."""
        command = win_command if cls.name == "windows" else lin_command
        try:
            result = subprocess.run(command, shell=True, env=env)
            return result.returncode
        except FileNotFoundError:
            # Fallback: попробовать через subprocess.call
            try:
                return subprocess.call(command, shell=True, env=env)
            except Exception:
                return 1

    