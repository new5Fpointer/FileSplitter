import os
import math
import chardet
import locale
import re

def calculate_total_chars(file_path, encoding):
    total_chars = 0
    with open(file_path, "r", encoding=encoding, errors="replace") as f:
        while True:
            chunk = f.read(4096)
            if not chunk:
                break
            total_chars += len(chunk)
    return total_chars


def split_file(input_path, output_dir, chars_per_file, input_encoding, output_encoding,
               split_by_line=False, line_split_mode="strict",
               progress_callback=None, log_callback=None):
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"文件不存在: {input_path}")

    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.basename(input_path)
    base_name, ext = os.path.splitext(filename)

    # 编码检测
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

    total_chars = calculate_total_chars(input_path, input_encoding)
    num_files = math.ceil(total_chars / chars_per_file)

    if log_callback:
        log_callback(f"文件总字符数: {total_chars}")
        log_callback(f"将分割为 {num_files} 个文件")

    with open(input_path, "r", encoding=input_encoding, errors="replace") as f:
        current_file = 1
        current_chars = 0
        current_chunk = []

        for line in f:
            line_length = len(line)

            if split_by_line:
                if line_split_mode == "flexible":
                    if current_chars + line_length > chars_per_file:
                        # 如果当前块非空，先写入
                        if current_chunk:
                            chunk = ''.join(current_chunk)
                            out_path = os.path.join(output_dir, f"{base_name}_part{current_file}{ext}")
                            with open(out_path, "w", encoding=output_encoding, errors="replace") as out_f:
                                out_f.write(chunk)
                            if log_callback:
                                log_callback(f"已创建: {os.path.basename(out_path)} ({len(chunk)} 字符)")
                            if progress_callback:
                                progress = (current_file / num_files) * 100
                                progress_callback(progress)
                            current_file += 1

                        # 保留当前行作为下一份文件的起始
                        current_chunk = [line]
                        current_chars = line_length
                    else:
                        current_chunk.append(line)
                        current_chars += line_length
                else:  # strict
                    if current_chars + line_length > chars_per_file:
                        if current_chunk:
                            chunk = ''.join(current_chunk)
                            out_path = os.path.join(output_dir, f"{base_name}_part{current_file}{ext}")
                            with open(out_path, "w", encoding=output_encoding, errors="replace") as out_f:
                                out_f.write(chunk)
                            if log_callback:
                                log_callback(f"已创建: {os.path.basename(out_path)} ({len(chunk)} 字符)")
                            if progress_callback:
                                progress = (current_file / num_files) * 100
                                progress_callback(progress)
                            current_file += 1
                        current_chunk = [line]
                        current_chars = line_length
                    else:
                        current_chunk.append(line)
                        current_chars += line_length
            else:
                # 按字符分割
                if current_chars + line_length > chars_per_file:
                    available = chars_per_file - current_chars
                    if available > 0:
                        current_chunk.append(line[:available])
                    chunk = ''.join(current_chunk)
                    out_path = os.path.join(output_dir, f"{base_name}_part{current_file}{ext}")
                    with open(out_path, "w", encoding=output_encoding, errors="replace") as out_f:
                        out_f.write(chunk)
                    if log_callback:
                        log_callback(f"已创建: {os.path.basename(out_path)} ({len(chunk)} 字符)")
                    if progress_callback:
                        progress = (current_file / num_files) * 100
                        progress_callback(progress)
                    current_file += 1
                    current_chunk = [line[available:]] if available < line_length else []
                    current_chars = len(current_chunk[0]) if current_chunk else 0
                else:
                    current_chunk.append(line)
                    current_chars += line_length

        if current_chunk:
            chunk = ''.join(current_chunk)
            out_path = os.path.join(output_dir, f"{base_name}_part{current_file}{ext}")
            with open(out_path, "w", encoding=output_encoding, errors="replace") as out_f:
                out_f.write(chunk)
            if log_callback:
                log_callback(f"已创建: {os.path.basename(out_path)} ({len(chunk)} 字符)")
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
    remainder = total_chars % total_parts        # 余数，前 remainder 份多 1 字符
    if log_callback:
        log_callback(f"文件总字符数: {total_chars}")
        log_callback(f"将按 {total_parts} 份分割，"
                     f"前 {remainder} 份每份 {chars_per_part + 1} 字符，"
                     f"最后一份 {chars_per_part} 字符")

    # 开始切块
    with open(input_path, "r", encoding=input_encoding, errors="replace") as f:
        for part_no in range(1, total_parts + 1):
            # 计算当前份大小
            current_chunk_size = chars_per_part + (1 if part_no <= remainder else 0)
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