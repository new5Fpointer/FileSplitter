import os
import configparser
import platform

class ConfigManager:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config_file = self._get_config_path()
        self._ensure_config_file()
        self.load_config()

    def _get_config_path(self):
        """获取配置文件路径"""
        system = platform.system()
        
        if system == "Windows":
            # Windows: 用户AppData目录
            appdata = os.getenv('APPDATA')
            if appdata:
                return os.path.join(appdata, "file_operations", "settings.ini")
            return "settings.ini"
        elif system == "Darwin":
            # macOS: 用户Library/Preferences目录
            home = os.path.expanduser("~")
            return os.path.join(home, "Library", "Preferences", "file_operations", "settings.ini")
        else:
            # Linux/Unix: 用户.config目录
            home = os.path.expanduser("~")
            return os.path.join(home, ".config", "file_operations", "settings.ini")

    def _ensure_config_file(self):
        """确保配置文件和目录存在"""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        
        if not os.path.exists(self.config_file):
            # 创建默认配置
            self.config['Settings'] = {
                'chars_per_file': '1000',
                'input_encoding': 'auto',
                'output_encoding': '同输入编码',
                'font_family': '微软雅黑',
                'font_size': '10',
                'font_weight': 'normal',
                'font_slant': 'roman',
                'split_by_line': 'False',
                'line_split_mode': 'strict'
            }
            self.save_config()

    def load_config(self):
        """加载配置文件"""
        self.config.read(self.config_file, encoding='utf-8')

    def save_config(self):
        """保存配置文件"""
        with open(self.config_file, 'w', encoding='utf-8') as configfile:
            self.config.write(configfile)

    def get_setting(self, section, key, default=None):
        """获取配置值"""
        try:
            return self.config.get(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return default

    def set_setting(self, section, key, value):
        """设置配置值"""
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, str(value))
        self.save_config()