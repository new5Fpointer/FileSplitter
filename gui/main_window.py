import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter import font as tkfont
from .font_settings import FontSettingsDialog
from .widgets import LabelledEntry, LabelledCombobox, LogWidget
from .styles import StyleManager
from core.splitter import split_file

class FileSplitterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("文件分割工具")
        self.root.geometry("750x550")  # 增加宽度以适应新控件
        self.root.resizable(True, True)
        
        # 初始化样式管理器
        self.style_manager = StyleManager(root)
        
        # 创建主框架
        self.main_frame = ttk.Frame(root, padding="15")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建界面组件
        self.create_widgets()
        
        # 添加初始日志
        self.log_widget.log("欢迎使用文件分割工具")
        self.log_widget.log("请选择输入文件和输出目录")
        
    def create_widgets(self):
        # 标题
        title_label = ttk.Label(self.main_frame, text="文件分割工具", style="Title.TLabel")
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 15))
        
        # 输入文件选择
        self.input_entry = LabelledEntry(
            self.main_frame, "输入文件:", 
            browse_cmd=self.browse_input_file,
            entry_width=50
        )
        self.input_entry.grid(row=1, column=0, columnspan=3, sticky="ew", pady=5)
        
        # 输出目录选择
        self.output_entry = LabelledEntry(
            self.main_frame, "输出目录:", 
            browse_cmd=self.browse_output_dir,
            entry_width=50
        )
        self.output_entry.grid(row=2, column=0, columnspan=3, sticky="ew", pady=5)
        
        # 分割设置
        self.chars_entry = LabelledEntry(
            self.main_frame, "每个文件的字符数:", 
            default_value="1000",
            entry_width=15
        )
        self.chars_entry.grid(row=3, column=0, columnspan=3, sticky="w", pady=5)
        
        # 编码设置（输入）
        encoding_frame = ttk.Frame(self.main_frame)
        encoding_frame.grid(row=4, column=0, columnspan=3, sticky="ew", pady=5)
        
        ttk.Label(encoding_frame, text="编码设置:", style="Label.TLabel").pack(side=tk.LEFT, padx=(0, 10))
        
        self.encoding_combo = LabelledCombobox(
            encoding_frame, "输入编码:",
            values=["utf-8", "gbk", "gb2312", "big5", "latin1", "auto"],
            default_value="utf-8",
            width=10
        )
        self.encoding_combo.pack(side=tk.LEFT, padx=(0, 20))
        
        # 输出编码设置
        self.output_encoding_combo = LabelledCombobox(
            encoding_frame, "输出编码:",
            values=["同输入编码", "utf-8", "gbk", "gb2312", "latin1", "ansi"],
            default_value="同输入编码",
            width=10
        )
        self.output_encoding_combo.pack(side=tk.LEFT)
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(
            self.main_frame, variable=self.progress_var, 
            maximum=100, style="Progressbar.Horizontal.TProgressbar"
        )
        self.progress.grid(row=5, column=0, columnspan=3, sticky="ew", pady=15)
        
        # 状态标签
        self.status_var = tk.StringVar(value="准备就绪")
        status_label = ttk.Label(
            self.main_frame, textvariable=self.status_var, 
            style="Status.TLabel"
        )
        status_label.grid(row=6, column=0, columnspan=3, sticky="w")
        
        # 操作按钮
        btn_frame = ttk.Frame(self.main_frame)
        btn_frame.grid(row=7, column=0, columnspan=3, pady=15)
        
        start_btn = ttk.Button(
            btn_frame, text="开始分割", 
            command=self.start_split,
            style="Button.TButton"
        )
        start_btn.pack(side=tk.LEFT, padx=10)
        
        # 添加字体设置按钮
        font_btn = ttk.Button(
            btn_frame, text="字体设置", 
            command=self.open_font_settings,
            style="Button.TButton"
        )
        font_btn.pack(side=tk.LEFT, padx=10)
        
        quit_btn = ttk.Button(
            btn_frame, text="退出", 
            command=self.root.quit,
            style="Button.TButton"
        )
        quit_btn.pack(side=tk.RIGHT, padx=10)
        
        # 日志区域
        ttk.Label(self.main_frame, text="操作日志:", style="Label.TLabel").grid(
            row=8, column=0, sticky="w", pady=5)
        
        self.log_widget = LogWidget(self.main_frame)
        self.log_widget.grid(row=9, column=0, columnspan=3, sticky="nsew")
        
        # 配置网格权重
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(9, weight=1)
        
    def browse_input_file(self):
        """打开文件选择对话框"""
        file_path = filedialog.askopenfilename(
            title="选择要分割的文件",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        if file_path:
            self.input_entry.set_value(file_path)
            # 自动设置输出目录为输入文件所在目录
            if not self.output_entry.get_value():
                self.output_entry.set_value(os.path.dirname(file_path))
            self.log_widget.log(f"已选择输入文件: {file_path}")
    
    def browse_output_dir(self):
        """打开目录选择对话框"""
        dir_path = filedialog.askdirectory(title="选择输出目录")
        if dir_path:
            self.output_entry.set_value(dir_path)
            self.log_widget.log(f"已选择输出目录: {dir_path}")
    
    def open_font_settings(self):
        """打开字体设置对话框"""
        FontSettingsDialog(
            self.root, 
            self.style_manager, 
            self.log_widget.log,
            self.log_widget.update_font
        )
    
    def start_split(self):
        """开始分割文件"""
        # 获取输入值
        input_path = self.input_entry.get_value()
        output_dir = self.output_entry.get_value()
        
        # 验证输入
        if not input_path:
            messagebox.showerror("错误", "请选择输入文件")
            return
        
        if not output_dir:
            messagebox.showerror("错误", "请选择输出目录")
            return
        
        try:
            chars_per_file = int(self.chars_entry.get_value())
            if chars_per_file <= 0:
                raise ValueError("字符数必须为正整数")
        except ValueError:
            messagebox.showerror("错误", "请输入有效的字符数（正整数）")
            return
        
        # 获取输入和输出编码
        input_encoding = self.encoding_combo.get_value()
        output_encoding = self.output_encoding_combo.get_value()
        
        # 开始分割
        try:
            self.log_widget.log(f"开始分割文件: {input_path}")
            self.log_widget.log(f"每个分割文件将包含 {chars_per_file} 个字符")
            self.log_widget.log(f"输入编码: {input_encoding}, 输出编码: {output_encoding}")
            
            # 调用分割函数
            split_file(
                input_path=input_path,
                output_dir=output_dir,
                chars_per_file=chars_per_file,
                input_encoding=input_encoding,
                output_encoding=output_encoding,
                progress_callback=lambda p: self.progress_var.set(p),
                log_callback=self.log_widget.log
            )
            
            # 完成
            self.progress_var.set(100)
            messagebox.showinfo("完成", "文件分割完成！")
            self.log_widget.log("文件分割操作已完成")
            
        except Exception as e:
            messagebox.showerror("错误", f"处理文件时出错: {e}")
            self.log_widget.log(f"错误: {e}")