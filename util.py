def debug_print(message):
    filename, line_num, _, _ = traceback.extract_stack()[-2]
    print(f"[DEBUG] {filename}, line {line_num}: {message}")
