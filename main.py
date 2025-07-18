from gui.main_window import FileSplitterApp
from tkinterdnd2 import Tk

if __name__ == "__main__":
    root = Tk()
    app = FileSplitterApp(root)
    root.mainloop()