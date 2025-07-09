import os
import math
import chardet
from .file_utils import calculate_total_chars

def split_file(input_path, output_dir, chars_per_file, encoding, 
              progress_callback=None, log_callback=None):
    """
    分割文件
    :param input_path: 输入文件路径
    :param output_dir: 输出目录
    :param chars_per_file: 每个分割文件的字符数
    :param encoding: 文件编码
    :param progress_callback: 进度回调函数
    :param log_callback: 日志回调函数
    """
    # 验证文件是否存在
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"文件不存在: {input_path}")
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 获取文件信息
    filename = os.path.basename(input_path)
    base_name, ext = os.path.splitext(filename)
    
    # 如果是自动检测编码
    if encoding == "auto":
        with open(input_path, "rb") as f:
            raw_data = f.read(4096)  # 读取前4KB检测
            result = chardet.detect(raw_data)
            encoding = result['encoding'] or 'utf-8'
        if log_callback:
            log_callback(f"自动检测到编码: {encoding}")
    
    # 计算总字符数
    if log_callback:
        log_callback("正在计算文件总字符数...")
    
    total_chars = calculate_total_chars(input_path, encoding)
    
    if log_callback:
        log_callback(f"文件总字符数: {total_chars}")
    
    # 计算需要分割的文件数量
    num_files = math.ceil(total_chars / chars_per_file)
    
    if log_callback:
        log_callback(f"将分割为 {num_files} 个文件")
        log_callback("开始分割文件...")
    
    # 实际分割文件
    with open(input_path, "r", encoding=encoding, errors="replace") as f:
        for i in range(num_files):
            # 更新进度
            if progress_callback:
                progress = (i + 1) / num_files * 100
                progress_callback(progress)
            
            # 创建输出文件名
            output_path = os.path.join(
                output_dir, 
                f"{base_name}_part{i+1}{ext}"
            )
            
            # 读取指定数量的字符
            chunk = ""
            chars_read = 0
            
            while chars_read < chars_per_file:
                remaining = chars_per_file - chars_read
                data = f.read(min(4096, remaining))
                if not data:
                    break
                chunk += data
                chars_read += len(data)
            
            # 写入分割文件
            with open(output_path, "w", encoding=encoding) as out_f:
                out_f.write(chunk)
            
            if log_callback:
                log_callback(f"已创建分割文件: {os.path.basename(output_path)} ({len(chunk)} 字符)")
    
    return num_files