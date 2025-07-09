from tkinter import ttk

class StyleManager:
    """管理应用样式"""
    def __init__(self, root):
        self.root = root
        self.style = ttk.Style()
        
        # 初始字体设置
        self.current_font = "微软雅黑"
        self.current_size = 10
        self.current_weight = "normal"
        self.current_slant = "roman"
        
        # 配置初始样式
        self.configure_styles()
    
    def configure_styles(self):
        """配置所有组件的样式"""
        # 基本字体设置
        base_font = (self.current_font, self.current_size, self.current_weight, self.current_slant)
        title_font = (self.current_font, self.current_size + 4, "bold", self.current_slant)
        status_font = (self.current_font, self.current_size - 1, self.current_weight, self.current_slant)
        
        # 配置各种组件的样式
        self.style.configure("Title.TLabel", font=title_font, foreground="#333333")
        self.style.configure("Label.TLabel", font=base_font, foreground="#333333")
        self.style.configure("Button.TButton", font=base_font, padding=5)
        self.style.configure("Entry.TEntry", font=base_font)
        self.style.configure("Combobox.TCombobox", font=base_font)
        self.style.configure("Status.TLabel", font=status_font, foreground="#666666")
        self.style.configure("Progressbar.Horizontal.TProgressbar", thickness=15)
        self.style.configure("TFrame", background="#ffffff")
        self.style.configure("TLabelframe", font=base_font)
        self.style.configure("TLabelframe.Label", font=base_font)
    
    def update_font(self, new_font, new_size, weight="normal", slant="roman"):
        """更新字体设置"""
        self.current_font = new_font
        self.current_size = new_size
        self.current_weight = weight
        self.current_slant = slant
        self.configure_styles()