# utils/log.py
import logging
from config import LOG_FILE_PATH
from utils.io_tools import ensure_dir

def setup_logger():
    """配置日志记录器"""
    ensure_dir(LOG_FILE_PATH)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE_PATH, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

def log_error(message):
    """记录错误日志"""
    logging.error(message)

def log_info(message):
    """记录信息日志"""
    logging.info(message)

def log_missing_data(missing_info):
    """
    记录缺失字段：位置+原因+来源
    生成数据质量报告的一部分
    """
    log_info(f"数据缺失报告: {missing_info}")
    # 可以写入一个专门的报告文件
    pass 