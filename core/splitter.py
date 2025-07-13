import os
import math
import chardet
import locale
from .file_utils import calculate_total_chars

def split_file(input_path, output_dir, chars_per_file, input_encoding, output_encoding,
              split_by_line=False, progress_callback=None, log_callback=None):
    """
    分割文件
    :param input_path: 输入文件路径
    :param output_dir: 输出目录
    :param chars_per_file: 每个分割文件的字符数
    :param input_encoding: 输入文件编码
    :param output_encoding: 输出文件编码
    :param split_by_line: 是否按行分割
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
    
    # 如果是自动检测输入编码
    if input_encoding == "auto":
        with open(input_path, "rb") as f:
            raw_data = f.read(4096)  # 读取前4KB检测
            result = chardet.detect(raw_data)
            input_encoding = result['encoding'] or 'utf-8'
        if log_callback:
            log_callback(f"自动检测到输入编码: {input_encoding}")
    
    # 确定输出编码
    if output_encoding == "同输入编码":
        output_encoding = input_encoding
        if log_callback:
            log_callback(f"输出编码使用输入编码: {input_encoding}")
    elif output_encoding == "ansi":
        # 获取系统ANSI编码
        output_encoding = locale.getpreferredencoding(do_setlocale=False)
        if log_callback:
            log_callback(f"系统ANSI编码: {output_encoding}")
    
    # 计算总字符数
    if log_callback:
        log_callback("正在计算文件总字符数...")
    
    total_chars = calculate_total_chars(input_path, input_encoding)
    
    if log_callback:
        log_callback(f"文件总字符数: {total_chars}")
    
    # 计算需要分割的文件数量
    num_files = math.ceil(total_chars / chars_per_file)
    
    if log_callback:
        log_callback(f"将分割为 {num_files} 个文件")
        log_callback("开始分割文件...")
        log_callback(f"输入编码: {input_encoding}, 输出编码: {output_encoding}")
        log_callback(f"分割方式: {'按行分割' if split_by_line else '按字符分割'}")
    
    # 实际分割文件
    with open(input_path, "r", encoding=input_encoding, errors="replace") as f:
        current_file = 1
        current_chars = 0
        current_chunk = []
        
        for line in f:
            line_length = len(line)
            
            if split_by_line:
                # 按行分割模式，每个文件只包含整行
                if current_chars + line_length > chars_per_file:
                    # 当前行会超出限制，先保存之前的块
                    if current_chunk:
                        chunk = ''.join(current_chunk)
                        output_path = os.path.join(
                            output_dir, 
                            f"{base_name}_part{current_file}{ext}"
                        )
                        
                        try:
                            with open(output_path, "w", encoding=output_encoding, errors="replace") as out_f:
                                out_f.write(chunk)
                            if log_callback:
                                log_callback(f"已创建分割文件: {os.path.basename(output_path)} ({len(chunk)} 字符)")
                        except Exception as e:
                            if log_callback:
                                log_callback(f"保存文件时出错: {str(e)}")
                        
                        # 更新进度
                        if progress_callback:
                            progress = (current_file / num_files) * 100
                            progress_callback(progress)
                        
                        # 重置当前块
                        current_file += 1
                        current_chars = 0
                        current_chunk = []
                
                # 添加当前行到块中
                current_chunk.append(line)
                current_chars += line_length
            
            else:
                # 按字符分割模式，当行内容可能被拆分
                if current_chars + line_length > chars_per_file:
                    # 找到可以拆分的位置
                    available_space = chars_per_file - current_chars
                    if available_space > 0:
                        # 添加部分字符到当前块
                        current_chunk.append(line[:available_space])
                        current_chars += available_space
                        
                        # 写入当前块到文件
                        chunk = ''.join(current_chunk)
                        output_path = os.path.join(
                            output_dir, 
                            f"{base_name}_part{current_file}{ext}"
                        )
                        
                        try:
                            with open(output_path, "w", encoding=output_encoding, errors="replace") as out_f:
                                out_f.write(chunk)
                            if log_callback:
                                log_callback(f"已创建分割文件: {os.path.basename(output_path)} ({len(chunk)} 字符)")
                        except Exception as e:
                            if log_callback:
                                log_callback(f"保存文件时出错: {str(e)}")
                        
                        # 更新进度
                        if progress_callback:
                            progress = (current_file / num_files) * 100
                            progress_callback(progress)
                        
                        # 重置当前块
                        current_file += 1
                        current_chars = 0
                        current_chunk = []
                        
                        # 剩余部分放到下一个块
                        current_chunk.append(line[available_space:])
                        current_chars += line_length - available_space
                    else:
                        # 当前行无法放入当前块，直接放到下一个块
                        if current_chunk:
                            chunk = ''.join(current_chunk)
                            output_path = os.path.join(
                                output_dir, 
                                f"{base_name}_part{current_file}{ext}"
                            )
                            
                            try:
                                with open(output_path, "w", encoding=output_encoding, errors="replace") as out_f:
                                    out_f.write(chunk)
                                if log_callback:
                                    log_callback(f"已创建分割文件: {os.path.basename(output_path)} ({len(chunk)} 字符)")
                            except Exception as e:
                                if log_callback:
                                    log_callback(f"保存文件时出错: {str(e)}")
                            
                            # 更新进度
                            if progress_callback:
                                progress = (current_file / num_files) * 100
                                progress_callback(progress)
                            
                            current_file += 1
                            current_chars = 0
                            current_chunk = []
                        
                        current_chunk.append(line)
                        current_chars += line_length
                else:
                    current_chunk.append(line)
                    current_chars += line_length
        
        # 写入最后一个块
        if current_chunk:
            chunk = ''.join(current_chunk)
            output_path = os.path.join(
                output_dir, 
                f"{base_name}_part{current_file}{ext}"
            )
            try:
                with open(output_path, "w", encoding=output_encoding, errors="replace") as out_f:
                    out_f.write(chunk)
                if log_callback:
                    log_callback(f"已创建分割文件: {os.path.basename(output_path)} ({len(chunk)} 字符)")
            except Exception as e:
                if log_callback:
                    log_callback(f"保存文件时出错: {str(e)}")
            
            # 更新进度
            if progress_callback:
                progress = (current_file / num_files) * 100
                progress_callback(progress)
    
    return current_file