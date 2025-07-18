import tkinter as tk
from tkinter import ttk
import os
from tkinterdnd2 import DND_FILES

class ImmediateCombobox(ttk.Combobox):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.bind("<<ComboboxSelected>>", self.on_select)
        self.bind("<FocusOut>", self.on_focus_out)
        self._last_value = self.get()
    
    def on_select(self, event):
        """当选择项时立即处理"""
        current_value = self.get()
        if current_value != self._last_value:
            self._last_value = current_value
            self.event_generate("<<ImmediateSelect>>")
    
    def on_focus_out(self, event):
        """当失去焦点时检查值是否改变"""
        current_value = self.get()
        if current_value != self._last_value:
            self._last_value = current_value
            self.event_generate("<<ImmediateSelect>>")

class LabelledEntry(ttk.Frame):
    def __init__(self, parent, label_text, default_value="", browse_cmd=None, entry_width=30, **kwargs):
        super().__init__(parent, **kwargs)

        self.label = ttk.Label(self, text=label_text)
        self.label.pack(side="left", padx=(0, 5))

        self.entry_var = tk.StringVar(value=default_value)
        self.entry = ttk.Entry(self, textvariable=self.entry_var, width=entry_width)
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 5))

        if browse_cmd:
            self.browse_btn = ttk.Button(self, text="浏览...", command=browse_cmd, width=8)
            self.browse_btn.pack(side="right")

        # 拖拽支持
        self.entry.drop_target_register(DND_FILES)
        self.entry.dnd_bind('<<Drop>>', self.on_drop)

    def on_drop(self, event):
        path = event.data.strip('{}').replace('/', os.sep)
        if os.path.isfile(path) or os.path.isdir(path):
            self.entry_var.set(path)
    
    def get_value(self):
        """获取输入框的值"""
        return self.entry_var.get().strip()
    
    def set_value(self, value):
        """设置输入框的值"""
        self.entry_var.set(value)
    
    def set_label_text(self, text):
        """动态修改左侧标签文字"""
        self.label.config(text=text)

    def on_drop(self, event):
        path = event.data
        # 处理 Windows 路径可能带花括号的问题
        path = path.strip('{}').replace('/', os.sep)
        if os.path.isfile(path) or os.path.isdir(path):
            self.entry_var.set(path)

class LabelledCombobox(ttk.Frame):
    def __init__(self, parent, label_text, values, default_value="", width=None, combobox_class=None, **kwargs):
        super().__init__(parent, **kwargs)
        
        # 创建标签
        self.label = ttk.Label(self, text=label_text, style="Label.TLabel")
        self.label.pack(side=tk.LEFT, padx=(0, 5))
        
        # 创建下拉框
        self.combo_var = tk.StringVar(value=default_value)
        combo_options = {"textvariable": self.combo_var, "values": values}
        if width: combo_options["width"] = width
            
        # 使用自定义类或默认类
        combo_class = combobox_class or ttk.Combobox
        self.combo = combo_class(self, **combo_options)
        self.combo.pack(side=tk.LEFT)
    
    def get_value(self):
        """获取下拉框的值"""
        return self.combo_var.get().strip()
    
    def set_value(self, value):
        """设置下拉框的值"""
        self.combo_var.set(value)

class LogWidget(tk.Frame):
    """日志显示组件 - 只读"""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        # 日志标签
        self.log_label = ttk.Label(self, text="操作日志:", style="Label.TLabel")
        self.log_label.pack(anchor="w", pady=(0, 5))

        # 日志文本框
        self.log_font = tk.font.Font(family="微软雅黑", size=9)
        self.log_text = tk.Text(
            self,
            wrap=tk.WORD,
            font=self.log_font,
            state="disabled",          # ← 设为只读
            cursor="arrow"             # ← 禁用编辑光标
        )
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 滚动条
        self.scrollbar = ttk.Scrollbar(self, command=self.log_text.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=self.scrollbar.set)

    def log(self, message):
        """追加日志（自动滚动到底部）"""
        self.log_text.config(state="normal")      # 临时可写
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")    # 恢复只读

    def update_font(self, family, size, weight="normal", slant="roman"):
        """更新日志字体"""
        self.log_font.configure(
            family=family, size=size-1, weight=weight, slant=slant
        )