def calculate_total_chars(file_path, encoding):
    """
    计算文件的总字符数
    :param file_path: 文件路径
    :param encoding: 文件编码
    :return: 总字符数
    """
    total_chars = 0
    with open(file_path, "r", encoding=encoding, errors="replace") as f:
        while True:
            chunk = f.read(4096)  # 4KB块
            if not chunk:
                break
            total_chars += len(chunk)
    return total_chars