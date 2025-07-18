from gui.main_window import FileSplitterApp
from tkinterdnd2 import Tk
import os
import sys
import base64
from icon_data import icon_data

if __name__ == "__main__":
    root = Tk()
        # 动态获取图标路径
    if getattr(sys, 'frozen', False):
        # 打包后运行时
        icon_path = os.path.join(sys._MEIPASS, "icon.ico")
    else:
        # 源码运行时
        icon_path = os.path.join(os.path.dirname(__file__), "icon.ico")
    icon_data = base64.b64decode(icon_data.encode("utf-8"))
    root.iconbitmap(icon_path)
    app = FileSplitterApp(root)
    root.mainloop()
