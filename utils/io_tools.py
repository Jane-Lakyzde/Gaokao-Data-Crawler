# utils/io_tools.py
import os

def ensure_dir(path):
    """确保目录存在"""
    os.makedirs(os.path.dirname(path), exist_ok=True)

def read_html(html_path):
    """
    缓存HTML避免重复爬取
    """
    if os.path.exists(html_path):
        with open(html_path, 'r', encoding='utf-8') as f:
            return f.read()
    return None

def save_html(html_content, html_path):
    """
    保存HTML内容
    """
    ensure_dir(html_path)
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

def save_interim_data(data, path):
    """
    保存中间结果（阶段：raw/cleaned）
    """
    ensure_dir(path)
    # 假设data是DataFrame
    # data.to_csv(path, index=False)
    print(f"中间数据已保存到: {path}")
    pass 