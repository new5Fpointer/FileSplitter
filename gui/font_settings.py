import tkinter as tk
from tkinter import ttk, font as tkfont

class FontSettingsDialog(tk.Toplevel):
    """字体设置对话框"""
    def __init__(self, parent, style_manager, log_callback, update_log_font):
        super().__init__(parent)
        self.title("字体设置")
        self.geometry("500x525")
        self.resizable(True, True)
        self.transient(parent)  # 设置为父窗口的临时窗口
        self.grab_set()  # 设置为模态对话框
        
        self.style_manager = style_manager
        self.log_callback = log_callback
        self.update_log_font = update_log_font
        self.current_font = style_manager.current_font
        self.current_size = style_manager.current_size
        self.current_weight = style_manager.current_weight
        self.current_slant = style_manager.current_slant
        
        # 创建主框架
        main_frame = ttk.Frame(self, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建控件
        self.create_widgets(main_frame)
        
        # 更新预览
        self.update_preview()
    
    def create_widgets(self, parent):
        """创建对话框控件"""
        # 字体家族
        font_frame = ttk.LabelFrame(parent, text="字体家族")
        font_frame.pack(fill=tk.X, pady=5)
        
        self.font_var = tk.StringVar(value=self.current_font)
        fonts = sorted(tkfont.families())
        font_combo = ttk.Combobox(
            font_frame, textvariable=self.font_var, 
            values=fonts, width=40
        )
        font_combo.pack(fill=tk.X, padx=5, pady=5)
        font_combo.bind("<<ComboboxSelected>>", self.on_font_change)
        
        # 字体大小
        size_frame = ttk.LabelFrame(parent, text="字体大小")
        size_frame.pack(fill=tk.X, pady=5)
        
        self.size_var = tk.StringVar(value=str(self.current_size))
        size_combo = ttk.Combobox(
            size_frame, textvariable=self.size_var, 
            values=["8", "9", "10", "11", "12", "14", "16", "18", "20", "24"],
            width=10
        )
        size_combo.pack(side=tk.LEFT, padx=5, pady=5)
        size_combo.bind("<<ComboboxSelected>>", self.on_size_change)
        
        # 字体样式
        style_frame = ttk.LabelFrame(parent, text="字体样式")
        style_frame.pack(fill=tk.X, pady=5)
        
        # 加粗
        self.bold_var = tk.BooleanVar(value=(self.current_weight == "bold"))
        bold_check = ttk.Checkbutton(
            style_frame, text="加粗", 
            variable=self.bold_var,
            command=self.on_style_change
        )
        bold_check.pack(side=tk.LEFT, padx=5)
        
        # 斜体
        self.italic_var = tk.BooleanVar(value=(self.current_slant == "italic"))
        italic_check = ttk.Checkbutton(
            style_frame, text="斜体", 
            variable=self.italic_var,
            command=self.on_style_change
        )
        italic_check.pack(side=tk.LEFT, padx=5)
        
        # 预览区域
        preview_frame = ttk.LabelFrame(parent, text="预览")
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.preview_text = tk.Text(
            preview_frame, height=8, wrap=tk.WORD,
            font=(self.current_font, self.current_size, self.current_weight, self.current_slant)
        )
        self.preview_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.preview_text.insert(tk.END, 
            "这是一个字体预览示例\n"
            "The quick brown fox jumps over the lazy dog\n"
            "0123456789 !@#$%^&*()\n"
            "字体设置窗口可以让您更直观地选择喜欢的字体样式。"
        )
        self.preview_text.config(state="disabled")  # 设置为只读
        
        # 按钮区域
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, pady=10)
        
        apply_btn = ttk.Button(
            btn_frame, text="取消", 
            command=self.destroy,
            width=10
        )
        apply_btn.pack(side=tk.RIGHT, padx=5)
        
        cancel_btn = ttk.Button(
            btn_frame, text="确定", 
            command=self.apply_font,
            width=10
        )
        cancel_btn.pack(side=tk.RIGHT, padx=5)
    
    def on_font_change(self, event=None):
        """字体家族改变事件"""
        self.current_font = self.font_var.get()
        self.update_preview()
    
    def on_size_change(self, event=None):
        """字体大小改变事件"""
        try:
            self.current_size = int(self.size_var.get())
            self.update_preview()
        except ValueError:
            pass
    
    def on_style_change(self):
        """字体样式改变事件"""
        self.current_weight = "bold" if self.bold_var.get() else "normal"
        self.current_slant = "italic" if self.italic_var.get() else "roman"
        self.update_preview()
    
    def update_preview(self):
        """更新预览文本"""
        font_tuple = (
            self.current_font, 
            self.current_size, 
            self.current_weight, 
            self.current_slant
        )
        # 临时启用文本框进行更新
        self.preview_text.config(state="normal")
        self.preview_text.configure(font=font_tuple)
        self.preview_text.config(state="disabled")
    
    def apply_font(self):
        """应用字体设置"""
        # 更新样式管理器
        self.style_manager.update_font(
            self.current_font, 
            self.current_size,
            self.current_weight,
            self.current_slant
        )
        
        # 更新日志字体
        self.update_log_font(
            self.current_font, 
            self.current_size,
            self.current_weight,
            self.current_slant
        )
        
        # 记录日志
        weight_text = "加粗" if self.current_weight == "bold" else "常规"
        slant_text = "斜体" if self.current_slant == "italic" else "正体"
        font_info = f"{self.current_font}, {self.current_size}pt, {weight_text}{slant_text}"
        
        self.log_callback(f"已应用新字体: {font_info}")
        self.destroy()