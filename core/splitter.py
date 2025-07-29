import os
import re
import math
import chardet
import locale
from .file_utils import calculate_total_chars

def split_file(input_path, output_dir, chars_per_file, input_encoding, output_encoding,
              split_by_line=False, line_split_mode="strict", progress_callback=None, log_callback=None):
    """
    分割文件
    :param input_path: 输入文件路径
    :param output_dir: 输出目录
    :param chars_per_file: 每个分割文件的字符数
    :param input_encoding: 输入文件编码
    :param output_encoding: 输出文件编码
    :param split_by_line: 是否按行分割
    :param line_split_mode: 行分割模式 ("strict" 或 "flexible")
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
        if split_by_line:
            log_callback(f"行分割模式: {'严格行分割' if line_split_mode == 'strict' else '灵活行分割'}")
    
    # 实际分割文件
    with open(input_path, "r", encoding=input_encoding, errors="replace") as f:
        current_file = 1
        current_chars = 0
        current_chunk = []
        
        for line in f:
            line_length = len(line)
            
            if split_by_line:
                if line_split_mode == "flexible":
                    # 灵活行分割模式 - 优先保证行完整
                    if current_chars + line_length > chars_per_file:
                        # 即使超出限制也加入当前行
                        current_chunk.append(line)
                        current_chars += line_length
                        
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
                    else:
                        # 当前行加入不会超出限制，正常添加
                        current_chunk.append(line)
                        current_chars += line_length
                
                else:  # 严格行分割模式
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
                        
                        # 将当前行放入新块
                        current_chunk.append(line)
                        current_chars = line_length
                    else:
                        # 当前行加入不会超出限制，正常添加
                        current_chunk.append(line)
                        current_chars += line_length
            
            else:
                # 按字符分割模式
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

def split_file_by_lines(input_path, output_dir, lines_per_file,
                        input_encoding, output_encoding,
                        progress_callback=None, log_callback=None):
    """纯粹按行数切分"""
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"文件不存在: {input_path}")

    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.basename(input_path)
    base_name, ext = os.path.splitext(filename)

    # 编码
    if input_encoding == "auto":
        with open(input_path, "rb") as f:
            raw = f.read(4096)
            input_encoding = chardet.detect(raw)['encoding'] or 'utf-8'
        if log_callback:
            log_callback(f"自动检测到输入编码: {input_encoding}")

    if output_encoding == "同输入编码":
        output_encoding = input_encoding
    elif output_encoding == "ansi":
        output_encoding = locale.getpreferredencoding(do_setlocale=False)

    # 总行数
    with open(input_path, 'r', encoding=input_encoding, errors='replace') as f:
        total_lines = sum(1 for _ in f)
    if log_callback:
        log_callback(f"文件总行数: {total_lines}")

    total_files = (total_lines + lines_per_file - 1) // lines_per_file
    if log_callback:
        log_callback(f"将分割为 {total_files} 个文件")

    with open(input_path, 'r', encoding=input_encoding, errors='replace') as in_f:
        file_no = 1
        written_lines = 0
        out_f = None
        for line_no, line in enumerate(in_f, 1):
            if written_lines % lines_per_file == 0:
                if out_f:
                    out_f.close()
                out_path = os.path.join(output_dir, f"{base_name}_part{file_no}{ext}")
                out_f = open(out_path, 'w', encoding=output_encoding, errors='replace')
                file_no += 1
                if log_callback:
                    log_callback(f"创建: {os.path.basename(out_path)}")

            out_f.write(line)
            written_lines += 1

            if progress_callback:
                progress = min(100, int(line_no * 100 / total_lines))
                progress_callback(progress)

        if out_f:
            out_f.close()
    return file_no - 1

def split_file_by_parts(input_path, output_dir, total_parts,
                        input_encoding, output_encoding,
                        progress_callback=None, log_callback=None):
    """
    按指定份数 **严格按字符数** 均分文件（行可能被截断）
    """
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"文件不存在: {input_path}")
    if total_parts <= 0:
        raise ValueError("份数必须大于 0")

    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.basename(input_path)
    base_name, ext = os.path.splitext(filename)

    # 编码处理
    if input_encoding == "auto":
        with open(input_path, "rb") as f:
            raw = f.read(4096)
            input_encoding = chardet.detect(raw)['encoding'] or 'utf-8'
        if log_callback:
            log_callback(f"自动检测到输入编码: {input_encoding}")

    if output_encoding == "同输入编码":
        output_encoding = input_encoding
    elif output_encoding == "ansi":
        output_encoding = locale.getpreferredencoding(do_setlocale=False)

    # 总字符数 & 每份字符数
    total_chars = calculate_total_chars(input_path, input_encoding)
    chars_per_part = total_chars // total_parts
    base_size = (total_chars + total_parts - 1) // total_parts
    if log_callback:
        log_callback(f"文件总字符数: {total_chars}")
        log_callback(f"将按 {total_parts} 份分割")

    # 开始切块
    with open(input_path, "r", encoding=input_encoding, errors="replace") as f:
        for part_no in range(1, total_parts + 1):
            # 计算当前份大小
            if part_no < total_parts:
                current_chunk_size = base_size
            else:
                current_chunk_size = total_chars - (total_parts - 1) * base_size
            chunk = f.read(current_chunk_size)
            if not chunk:
                break
            out_path = os.path.join(output_dir, f"{base_name}_part{part_no}{ext}")
            with open(out_path, "w", encoding=output_encoding, errors="replace") as out_f:
                out_f.write(chunk)
            if log_callback:
                log_callback(f"已创建: {os.path.basename(out_path)} ({len(chunk)} 字符)")
            if progress_callback:
                progress = (part_no / total_parts) * 100
                progress_callback(progress)

    return total_parts

def split_file_by_regex(input_path, output_dir, regex_pattern, 
                        input_encoding, output_encoding,
                        include_delimiter=False,  # 是否包含分隔符在结果中
                        progress_callback=None, log_callback=None):
    """
    按正则表达式分割文件
    :param input_path: 输入文件路径
    :param output_dir: 输出目录
    :param regex_pattern: 正则表达式模式
    :param input_encoding: 输入编码
    :param output_encoding: 输出编码
    :param include_delimiter: 是否在分割结果中包含分隔符
    :param progress_callback: 进度回调函数
    :param log_callback: 日志回调函数
    :return: 创建的文件数量
    """
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"文件不存在: {input_path}")
    
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.basename(input_path)
    base_name, ext = os.path.splitext(filename)
    
    # 编码处理
    if input_encoding == "auto":
        with open(input_path, "rb") as f:
            raw = f.read(4096)
            input_encoding = chardet.detect(raw)['encoding'] or 'utf-8'
        if log_callback:
            log_callback(f"自动检测到输入编码: {input_encoding}")
    
    if output_encoding == "同输入编码":
        output_encoding = input_encoding
    elif output_encoding == "ansi":
        output_encoding = locale.getpreferredencoding(do_setlocale=False)
    
    # 编译正则表达式
    try:
        pattern = re.compile(regex_pattern)
    except re.error as e:
        raise ValueError(f"无效的正则表达式: {e}")
    
    file_count = 1
    current_chunk = []
    
    with open(input_path, "r", encoding=input_encoding, errors="replace") as f:
        if log_callback:
            log_callback(f"开始按正则表达式分割: {regex_pattern}")
        
        for line in f:
            # 在当前行中查找所有匹配
            matches = list(pattern.finditer(line))
            
            if not matches:
                current_chunk.append(line)
                continue
            
            last_index = 0
            for match in matches:
                start, end = match.span()
                
                # 添加匹配前的部分
                if start > last_index:
                    current_chunk.append(line[last_index:start])
                
                # 处理匹配部分
                matched_text = line[start:end]
                
                # 如果当前块有内容，写入文件
                if current_chunk:
                    out_path = os.path.join(output_dir, f"{base_name}_part{file_count}{ext}")
                    with open(out_path, "w", encoding=output_encoding, errors="replace") as out_f:
                        out_f.write(''.join(current_chunk))
                    if log_callback:
                        log_callback(f"已创建: {os.path.basename(out_path)}")
                    file_count += 1
                    current_chunk = []
                
                # 是否包含分隔符在结果中
                if include_delimiter:
                    current_chunk.append(matched_text)
                
                last_index = end
            
            # 添加匹配后的剩余部分
            if last_index < len(line):
                current_chunk.append(line[last_index:])
    
    # 写入最后一块
    if current_chunk:
        out_path = os.path.join(output_dir, f"{base_name}_part{file_count}{ext}")
        with open(out_path, "w", encoding=output_encoding, errors="replace") as out_f:
            out_f.write(''.join(current_chunk))
        if log_callback:
            log_callback(f"已创建: {os.path.basename(out_path)}")
        file_count += 1
    
    return file_count - 1