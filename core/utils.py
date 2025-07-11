import os
import platform
import subprocess

class FileUtils:
    @staticmethod
    def open_directory(path):
        """打开指定目录"""
        if not os.path.isdir(path):
            return False
        
        try:
            system = platform.system()
            if system == "Windows":
                os.startfile(path)
            elif system == "Darwin":  # macOS
                subprocess.Popen(["open", path])
            else:  # Linux和其他系统
                subprocess.Popen(["xdg-open", path])
            return True
        except Exception:
            return False