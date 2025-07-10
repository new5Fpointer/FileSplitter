import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import platform
import subprocess
import threading
from .font_settings import FontSettingsDialog
from .widgets import LabelledEntry, LabelledCombobox, LogWidget
from .styles import StyleManager
from core.splitter import split_file

class FileSplitterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("文件分割工具")
        self.root.geometry("750x550")
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
    
    def open_output_directory(self):
        """打开输出目录"""
        output_dir = self.output_entry.get_value()
        if output_dir and os.path.isdir(output_dir):
            try:
                # 根据操作系统使用不同的方法打开目录
                system = platform.system()
                if system == "Windows":
                    os.startfile(output_dir)
                elif system == "Darwin":  # macOS
                    subprocess.Popen(["open", output_dir])
                else:  # Linux和其他系统
                    subprocess.Popen(["xdg-open", output_dir])
                self.log_widget.log(f"已打开输出目录: {output_dir}")
            except Exception as e:
                messagebox.showerror("错误", f"无法打开目录: {e}")
                self.log_widget.log(f"打开目录错误: {e}")
        else:
            messagebox.showwarning("警告", "输出目录无效或不存在")
            self.log_widget.log("无法打开无效的输出目录")
    
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
            default_value="auto",
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
        self.status_var = tk.StringVar(value="分割进度")
        status_label = ttk.Label(
            self.main_frame, textvariable=self.status_var, 
            style="Status.TLabel"
        )
        status_label.grid(row=6, column=0, columnspan=3, sticky="w")
        
        # 操作按钮
        btn_frame = ttk.Frame(self.main_frame)
        btn_frame.grid(row=7, column=0, columnspan=3, pady=15)
        
        # 保存开始按钮的引用
        self.start_btn = ttk.Button(
            btn_frame, text="开始分割", 
            command=self.start_split,
            style="Button.TButton"
        )
        self.start_btn.pack(side=tk.LEFT, padx=10)
        
        # 添加字体设置按钮
        font_btn = ttk.Button(
            btn_frame, text="字体设置", 
            command=self.open_font_settings,
            style="Button.TButton"
        )
        font_btn.pack(side=tk.LEFT, padx=10)
        
        # 打开输出目录按钮（初始禁用）
        self.open_output_btn = ttk.Button(
            btn_frame, text="打开输出目录", 
            command=self.open_output_directory,
            state=tk.DISABLED,
            style="Button.TButton"
        )
        self.open_output_btn.pack(side=tk.LEFT, padx=10)
        
        quit_btn = ttk.Button(
            btn_frame, text="退出", 
            command=self.root.quit,
            style="Button.TButton"
        )
        quit_btn.pack(side=tk.RIGHT, padx=10)
        
        #日志区域
        self.log_widget = LogWidget(self.main_frame)
        self.log_widget.grid(row=9, column=0, columnspan=3, sticky="nsew")
        
        # 配置网格权重
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(9, weight=1)
    
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
        
        # 禁用打开输出目录按钮和开始按钮（防止在分割过程中点击）
        self.open_output_btn.config(state=tk.DISABLED)
        self.start_btn.config(state=tk.DISABLED)
        
        # 重置进度条和状态
        self.progress_var.set(0)
        self.status_var.set("开始分割...")
        
        # 记录日志
        self.log_widget.log(f"开始分割文件: {input_path}")
        self.log_widget.log(f"每个分割文件将包含 {chars_per_file} 个字符")
        self.log_widget.log(f"输入编码: {input_encoding}, 输出编码: {output_encoding}")
        
        # 使用线程执行分割操作
        threading.Thread(
            target=self.run_split_in_thread,
            args=(input_path, output_dir, chars_per_file, input_encoding, output_encoding),
            daemon=True
        ).start()
    
    def run_split_in_thread(self, input_path, output_dir, chars_per_file, input_encoding, output_encoding):
        """在单独的线程中执行分割操作"""
        try:
            # 调用分割函数
            split_file(
                input_path=input_path,
                output_dir=output_dir,
                chars_per_file=chars_per_file,
                input_encoding=input_encoding,
                output_encoding=output_encoding,
                progress_callback=self.update_progress,
                log_callback=self.log_in_ui_thread
            )
            
            # 完成后的操作需要在主线程执行
            self.root.after(0, self.on_split_completed)
            
        except Exception as e:
            # 错误处理也需要在主线程执行
            self.root.after(0, self.on_split_error, e)
    
    def update_progress(self, progress):
        """UI线程安全的进度更新方法"""
        # 使用after方法在UI线程更新进度
        self.root.after(0, self._update_progress_ui, progress)
    
    def _update_progress_ui(self, progress):
        """在UI线程中更新进度条"""
        self.progress_var.set(progress)
        self.status_var.set(f"处理中: {int(progress)}%")
    
    def log_in_ui_thread(self, message):
        """UI线程安全的日志记录方法"""
        self.root.after(0, self._log_in_ui, message)
    
    def _log_in_ui(self, message):
        """在UI线程中记录日志"""
        self.log_widget.log(message)
    
    def on_split_completed(self):
        """分割完成后的处理"""
        self.progress_var.set(100)
        self.status_var.set("分割完成")
        messagebox.showinfo("完成", "文件分割完成！")
        self.log_widget.log("文件分割操作已完成")
        
        # 启用打开输出目录按钮和开始按钮
        self.open_output_btn.config(state=tk.NORMAL)
        self.start_btn.config(state=tk.NORMAL)
        self.log_widget.log("点击'打开输出目录'按钮查看分割后的文件")
    
    def on_split_error(self, error):
        """分割出错时的处理"""
        self.progress_var.set(0)
        self.status_var.set("处理出错")
        messagebox.showerror("错误", f"处理文件时出错: {error}")
        self.log_widget.log(f"错误: {error}")
        
        # 启用开始按钮
        self.start_btn.config(state=tk.NORMAL)