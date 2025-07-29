import chardet
import locale
import os

def determine_encodings(input_path, input_encoding, output_encoding, log_callback=None):
    """
    判断并返回最终的输入编码和输出编码
    :param input_path: 输入文件路径
    :param input_encoding: 输入文件编码（可为'auto'）
    :param output_encoding: 输出文件编码（可为'同输入编码'或'ansi'）
    :param log_callback: 日志回调函数
    :return: (input_encoding, output_encoding)
    """
    # 输入编码判断
    if input_encoding == "auto":
        with open(input_path, "rb") as f:
            raw_data = f.read(4096)
            result = chardet.detect(raw_data)
            input_encoding = result['encoding'] or 'utf-8'
        if log_callback:
            log_callback(f"自动检测到输入编码: {input_encoding}")

    # 输出编码判断
    if output_encoding == "同输入编码":
        output_encoding = input_encoding
        if log_callback:
            log_callback(f"输出编码使用输入编码: {input_encoding}")
    elif output_encoding == "ansi":
        output_encoding = locale.getpreferredencoding(do_setlocale=False)
        if log_callback:
            log_callback(f"系统ANSI编码: {output_encoding}")
    return input_encoding, output_encoding

def calculate_total_chars(file_path, encoding):
    total_chars = 0
    with open(file_path, "r", encoding=encoding, errors="replace") as f:
        while True:
            chunk = f.read(4096)  # 4KB块
            if not chunk:
                break
            total_chars += len(chunk)
    return total_chars