def calculate_total_chars(file_path, encoding):
    total_chars = 0
    with open(file_path, "r", encoding=encoding, errors="replace") as f:
        while True:
            chunk = f.read(4096)  # 4KB块
            if not chunk:
                break
            total_chars += len(chunk)
    return total_chars