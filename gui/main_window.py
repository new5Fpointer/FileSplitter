import os,sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import platform
import subprocess
import threading
from .font_settings import FontSettingsDialog
from .widgets import LabelledEntry, LabelledCombobox, LogWidget
from .styles import StyleManager
from core.splitter import split_file
from core.config_manager import ConfigManager


class FileSplitterApp:

    def __init__(self, root):
        self.root = root
        self.root.title("文件分割工具")
        self.root.geometry("750x600")
        self.root.resizable(True, True)

        # 替换Tkinter默认窗口图标
        if getattr(sys, 'frozen', False):
            # 打包后 exe 运行时
            icon_path = os.path.join(sys._MEIPASS, "icon.ico")
        else:
            # 源码运行时
            icon_path = os.path.join(os.path.dirname(__file__), "..", "icon.ico")
        self.root.iconbitmap(icon_path)

        self.config = ConfigManager()
        self.style_manager = StyleManager(root)

        self.main_frame = ttk.Frame(root, padding="15")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.create_widgets()
        self.apply_saved_settings()          # 1. 先恢复下拉框和数值
        self.apply_saved_font_settings()     # 2. 再恢复字体
        self.log_widget.log("欢迎使用文件分割工具")
        self.log_widget.log("请选择输入文件和输出目录")

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)  # 关闭窗口时保存配置

    # ---------- 事件绑定 ----------
    def bind_setting_changes(self):
        self.chars_entry.entry.bind("<FocusOut>", self.save_settings)
        self.encoding_combo.combo.bind("<<ComboboxSelected>>", self.save_settings)
        self.output_encoding_combo.combo.bind("<<ComboboxSelected>>", self.save_settings)
        self.line_mode_combo.combo.bind("<<ComboboxSelected>>", self.save_settings)

    def on_closing(self):
        """窗口关闭时保存设置再退出"""
        self.save_settings()          # 把当前输入写进配置文件
        self.root.destroy()           # 真正关闭窗口

    # ---------- 应用保存的设置 ----------
    def apply_saved_font_settings(self):
        font_family = self.config.get_setting('Settings', 'font_family', '微软雅黑')
        font_size = int(self.config.get_setting('Settings', 'font_size', 10))
        font_weight = self.config.get_setting('Settings', 'font_weight', 'normal')
        font_slant = self.config.get_setting('Settings', 'font_slant', 'roman')
        self.style_manager.update_font(font_family, font_size, font_weight, font_slant)
        self.log_widget.update_font(font_family, font_size, font_weight, font_slant)

    def apply_saved_settings(self):
        # 1. 恢复分割模式下拉框
        mode = self.config.get_setting('Settings', 'split_mode', '按字符分割')
        self.line_mode_combo.set_value(mode)
        
        # 2. 立即更新界面状态
        self.update_ui_for_mode(mode)
        
        # 3. 根据模式恢复数值
        if mode == "按行分割":
            val = self.config.get_setting('Settings', 'lines_per_file', '1000')
            self.chars_entry.set_value(val)
            self.chars_entry.set_label_text("每份文件的字符数/行数/份数:")
        elif mode == "份数分割":
            val = self.config.get_setting('Settings', 'parts_per_file', '4')
            self.chars_entry.set_value(val)
            self.chars_entry.set_label_text("每份文件的字符数/行数/份数:")
        else:   # 按字符 / 严格行 / 灵活行 / 正则表达式
            val = self.config.get_setting('Settings', 'chars_per_file', '1000')
            self.chars_entry.set_value(val)
            self.chars_entry.set_label_text("每份文件的字符数/行数/份数:")

        # 4. 恢复编码下拉框
        in_enc  = self.config.get_setting('Settings', 'input_encoding',  'auto')
        out_enc = self.config.get_setting('Settings', 'output_encoding', '同输入编码')
        self.encoding_combo.set_value(in_enc)
        self.output_encoding_combo.set_value(out_enc)
        
        # 5. 恢复正则表达式设置
        regex_val = self.config.get_setting('Settings', 'regex_pattern', '')
        self.regex_entry.delete(0, tk.END)
        self.regex_entry.insert(0, regex_val)
        
        include_delim = self.config.get_setting('Settings', 'include_delimiter', 'False') == 'True'
        self.include_delim_var.set(include_delim)
    
    def update_ui_for_mode(self, mode):
        """根据分割模式更新界面状态"""
        if mode == "按正则分割":
            self.regex_frame.grid()  # 显示正则表达式框架
            self.chars_entry.grid_remove()  # 隐藏字符数输入框
        else:
            self.regex_frame.grid_remove()  # 隐藏正则表达式框架
            self.chars_entry.grid()  # 显示字符数输入框
    # ---------- 保存设置 ----------
    def save_settings(self, event=None):
        mode = self.line_mode_combo.get_value()
        self.config.set_setting('Settings', 'split_mode', mode)

        if mode == "按行分割":
            self.config.set_setting('Settings', 'lines_per_file', self.chars_entry.get_value())
        elif mode == "份数分割":
            self.config.set_setting('Settings', 'parts_per_file', self.chars_entry.get_value())
        else:
            self.config.set_setting('Settings', 'chars_per_file', self.chars_entry.get_value())

        # 补上下面两行
        self.config.set_setting('Settings', 'input_encoding',  self.encoding_combo.get_value())
        self.config.set_setting('Settings', 'output_encoding', self.output_encoding_combo.get_value())
        
        # 保存正则表达式设置
        self.config.set_setting('Settings', 'regex_pattern', self.regex_entry.get())
        self.config.set_setting('Settings', 'include_delimiter', str(self.include_delim_var.get()))

        self.log_widget.log("设置已自动保存")

    # ---------- 浏览/打开 ----------
    def browse_input_file(self):
        path = filedialog.askopenfilename(
            title="选择要分割的文件",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")])
        if path:
            self.input_entry.set_value(path)
            if not self.output_entry.get_value():
                self.output_entry.set_value(os.path.dirname(path))
            self.log_widget.log(f"已选择输入文件: {path}")

    def browse_output_dir(self):
        dir_path = filedialog.askdirectory(title="选择输出目录")
        if dir_path:
            self.output_entry.set_value(dir_path)
            self.log_widget.log(f"已选择输出目录: {dir_path}")

    def open_output_directory(self):
        path = self.output_entry.get_value()
        if os.path.isdir(path):
            try:
                syst = platform.system()
                if syst == "Windows":
                    os.startfile(path)
                elif syst == "Darwin":
                    subprocess.Popen(["open", path])
                else:
                    subprocess.Popen(["xdg-open", path])
                self.log_widget.log(f"已打开输出目录: {path}")
            except Exception as e:
                messagebox.showerror("错误", f"无法打开目录: {e}")
                self.log_widget.log(f"打开目录错误: {e}")
        else:
            messagebox.showwarning("警告", "输出目录无效或不存在")

    # ---------- 创建界面 ----------
    def create_widgets(self):
        # 标题
        ttk.Label(self.main_frame, text="文件分割工具", style="Title.TLabel") \
            .grid(row=0, column=0, columnspan=3, pady=(0, 15))

        # 输入文件
        self.input_entry = LabelledEntry(
            self.main_frame, "输入文件:",
            browse_cmd=self.browse_input_file, entry_width=50)
        self.input_entry.grid(row=1, column=0, columnspan=3, sticky="ew", pady=5)

        # 输出目录
        self.output_entry = LabelledEntry(
            self.main_frame, "输出目录:",
            browse_cmd=self.browse_output_dir, entry_width=50)
        self.output_entry.grid(row=2, column=0, columnspan=3, sticky="ew", pady=5)

        # 字符数/行数输入框
        self.chars_entry = LabelledEntry(
            self.main_frame, "每个文件的字符数/行数/份数:",
            default_value="1000", entry_width=15)
        self.chars_entry.grid(row=3, column=0, columnspan=3, sticky="w", pady=5)

        # 分割方式
        split_frame = ttk.Frame(self.main_frame)
        split_frame.grid(row=4, column=0, columnspan=3, sticky="ew", pady=5)
        ttk.Label(split_frame, text="分割方式:", style="Label.TLabel").pack(side=tk.LEFT, padx=(0, 10))
        self.line_mode_combo = LabelledCombobox(
            split_frame, "", 
            values=["按字符分割", "按行分割", "严格行分割", "灵活行分割", "份数分割", "按正则分割"],
            default_value="按字符分割", width=15)
        self.line_mode_combo.pack(side=tk.LEFT)
        
        # 绑定分割模式改变事件 - 确保选择后立即触发
        self.line_mode_combo.combo.bind("<ButtonRelease-1>", self.on_combo_click)
        self.line_mode_combo.combo.bind("<FocusOut>", self.on_split_mode_change)

        # 编码设置
        self.enc_frame = ttk.Frame(self.main_frame)
        self.enc_frame.grid(row=5, column=0, columnspan=3, sticky="ew", pady=5)
        ttk.Label(self.enc_frame, text="编码设置:", style="Label.TLabel") \
            .pack(side=tk.LEFT, padx=(0, 10))
        self.encoding_combo = LabelledCombobox(
            self.enc_frame, "输入编码:",
            values=["utf-8", "gbk", "gb2312", "big5", "latin1", "auto"],
            default_value="auto", width=10)
        self.encoding_combo.pack(side=tk.LEFT, padx=(0, 20))
        self.output_encoding_combo = LabelledCombobox(
            self.enc_frame, "输出编码:",
            values=["同输入编码", "utf-8", "gbk", "gb2312", "latin1", "ansi"],
            default_value="同输入编码", width=10)
        self.output_encoding_combo.pack(side=tk.LEFT)

        # 正则表达式设置 (初始隐藏)
        self.regex_frame = ttk.Frame(self.main_frame)
        self.regex_frame.grid(row=6, column=0, columnspan=3, sticky="ew", pady=5)
        self.regex_frame.grid_remove()  # 初始隐藏
        
        ttk.Label(self.regex_frame, text="正则表达式:", style="Label.TLabel") \
            .pack(side=tk.LEFT, padx=(0, 5))
        
        self.regex_entry = ttk.Entry(self.regex_frame, width=40)
        self.regex_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        self.include_delim_var = tk.BooleanVar(value=False)
        self.include_delim_check = ttk.Checkbutton(
            self.regex_frame, text="包含分隔符", 
            variable=self.include_delim_var)
        self.include_delim_check.pack(side=tk.LEFT)

        # 进度条
        self.progress_var = tk.DoubleVar()
        ttk.Progressbar(self.main_frame, variable=self.progress_var, maximum=100,
                       style="Progressbar.Horizontal.TProgressbar") \
            .grid(row=7, column=0, columnspan=3, sticky="ew", pady=15)

        # 状态标签
        self.status_var = tk.StringVar(value="准备就绪")
        ttk.Label(self.main_frame, textvariable=self.status_var, style="Status.TLabel") \
            .grid(row=8, column=0, columnspan=3, sticky="w")

        # 按钮区域
        btn_frame = ttk.Frame(self.main_frame)
        btn_frame.grid(row=9, column=0, columnspan=3, pady=15)
        self.start_btn = ttk.Button(btn_frame, text="开始分割", command=self.start_split)
        self.start_btn.pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="字体设置", command=self.open_font_settings).pack(side=tk.LEFT, padx=10)
        self.open_output_btn = ttk.Button(btn_frame, text="打开输出目录", state=tk.DISABLED,
                                        command=self.open_output_directory)
        self.open_output_btn.pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="退出", command=self.root.quit).pack(side=tk.RIGHT, padx=10)

        # 日志区域
        self.log_widget = LogWidget(self.main_frame)
        self.log_widget.grid(row=10, column=0, columnspan=3, sticky="nsew")
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(10, weight=1)
        
        # 绑定设置变更事件
        self.bind_setting_changes()

    # ---------- 事件处理 ----------
    def on_combo_click(self, event):
        """当点击组合框时处理下拉列表选择"""
        # 获取当前下拉列表是否打开
        is_open = self.line_mode_combo.combo.cget("state") == "readonly"
        
        # 使用 after 延迟处理，确保在下拉列表关闭后执行
        self.root.after(100, lambda: self.check_combo_selection(is_open))

    def check_combo_selection(self, was_open):
        """检查组合框是否已选择新值"""
        # 获取当前状态
        is_open = self.line_mode_combo.combo.cget("state") == "readonly"
        
        # 如果之前是打开状态而现在关闭了，说明用户做了选择
        if was_open and not is_open:
            self.on_split_mode_change()

    def on_split_mode_change(self, event=None):
        """当分割模式改变时更新界面状态并保存设置"""
        mode = self.line_mode_combo.get_value()
        self.update_ui_for_mode(mode)
        self.save_settings()
        self.root.update_idletasks()  # 强制刷新界面

    # ---------- 字体设置 ----------
    def open_font_settings(self):
        FontSettingsDialog(
            self.root, self.style_manager, self.log_widget.log,
            self.log_widget.update_font, on_font_applied=self.save_font_settings)

    def save_font_settings(self, font_family, font_size, font_weight, font_slant):
        self.config.set_setting('Settings', 'font_family', font_family)
        self.config.set_setting('Settings', 'font_size', str(font_size))
        self.config.set_setting('Settings', 'font_weight', font_weight)
        self.config.set_setting('Settings', 'font_slant', font_slant)
        self.log_widget.log(f"字体设置已保存: {font_family}, {font_size}pt")

    # ---------- 开始分割 ----------
    def start_split(self):
        self.save_settings()
        input_path = self.input_entry.get_value()
        output_dir = self.output_entry.get_value()
        if not input_path or not output_dir:
            messagebox.showerror("错误", "请选择输入文件和输出目录")
            return

        mode = self.line_mode_combo.get_value()
        in_enc  = self.encoding_combo.get_value()
        out_enc = self.output_encoding_combo.get_value()

        if mode == "按行分割":
            try:
                lines = int(self.chars_entry.get_value())
                if lines <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("错误", "请输入有效的行数")
                return

            self.open_output_btn.config(state=tk.DISABLED)
            self.start_btn.config(state=tk.DISABLED)
            self.progress_var.set(0)
            self.status_var.set("开始按行分割...")

            threading.Thread(
                target=self.run_split_by_lines,
                args=(input_path, output_dir, lines, in_enc, out_enc),
                daemon=True).start()
        elif mode == "份数分割":
            try:
                parts = int(self.chars_entry.get_value())
                if parts <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("错误", "请输入有效的份数")
                return

            self.open_output_btn.config(state=tk.DISABLED)
            self.start_btn.config(state=tk.DISABLED)
            self.progress_var.set(0)
            self.status_var.set("开始按份数分割...")

            threading.Thread(
                target=self.run_split_by_parts,
                args=(input_path, output_dir, parts, in_enc, out_enc),
                daemon=True).start()
        elif mode == "按正则分割":
            regex_pattern = self.regex_entry.get().strip()
            if not regex_pattern:
                messagebox.showerror("错误", "请输入有效的正则表达式")
                return
                
            include_delim = self.include_delim_var.get()
            
            self.open_output_btn.config(state=tk.DISABLED)
            self.start_btn.config(state=tk.DISABLED)
            self.progress_var.set(0)
            self.status_var.set("开始按正则表达式分割...")
            
            threading.Thread(
                target=self.run_split_by_regex,
                args=(input_path, output_dir, regex_pattern, in_enc, out_enc, include_delim),
                daemon=True).start()
        else:
            try:
                chars = int(self.chars_entry.get_value())
                if chars <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("错误", "请输入有效的字符数")
                return

            split_by_line = (mode != "按字符分割")
            line_mode = 'strict' if mode == "严格行分割" else 'flexible'

            self.open_output_btn.config(state=tk.DISABLED)
            self.start_btn.config(state=tk.DISABLED)
            self.progress_var.set(0)
            self.status_var.set("开始分割...")

            threading.Thread(
                target=self.run_split_in_thread,
                args=(input_path, output_dir, chars, in_enc, out_enc,
                      split_by_line, line_mode),
                daemon=True).start()

    def run_split_in_thread(self, *args):
        try:
            num = split_file(*args, progress_callback=self.update_progress,
                             log_callback=self.log_in_ui_thread)
            self.root.after(0, self.on_split_completed, num)
        except Exception as e:
            self.root.after(0, self.on_split_error, e)
            
    def run_split_by_regex(self, *args):
        try:
            from core.splitter import split_file_by_regex
            num = split_file_by_regex(
                *args,
                progress_callback=self.update_progress,
                log_callback=self.log_in_ui_thread)
            self.root.after(0, self.on_split_completed, num)
        except Exception as e:
            self.root.after(0, self.on_split_error, e)

    def run_split_by_lines(self, *args):
        try:
            from core.splitter import split_file_by_lines
            num = split_file_by_lines(
                *args,
                progress_callback=self.update_progress,
                log_callback=self.log_in_ui_thread)
            self.root.after(0, self.on_split_completed, num)
        except Exception as e:
            self.root.after(0, self.on_split_error, e)

    def update_progress(self, p):
        self.root.after(0, lambda: (self.progress_var.set(p),
                                    self.status_var.set(f"处理中: {int(p)}%")))

    def log_in_ui_thread(self, msg):
        self.root.after(0, lambda: self.log_widget.log(msg))

    def on_split_completed(self, n):
        self.progress_var.set(100)
        self.status_var.set("分割完成")
        messagebox.showinfo("完成", f"共创建 {n} 个文件")
        self.start_btn.config(state=tk.NORMAL)
        self.open_output_btn.config(state=tk.NORMAL)

    def on_split_error(self, e):
        self.progress_var.set(0)
        self.status_var.set("处理出错")
        messagebox.showerror("错误", str(e))
        self.start_btn.config(state=tk.NORMAL)

    def run_split_by_parts(self, *args):
        try:
            from core.splitter import split_file_by_parts
            num = split_file_by_parts(
                *args,
                progress_callback=self.update_progress,
                log_callback=self.log_in_ui_thread)
            self.root.after(0, self.on_split_completed, num)
        except Exception as e:
            self.root.after(0, self.on_split_error, e)