# test_crawler.py
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.log import setup_logger, log_info
from crawlers.yangguang import get_random_ua
from data_processing.cleaner import standardize_names, clean_province_names
from data_processing.converter import convert_to_standard_format
import pandas as pd

def test_user_agent():
    """测试User-Agent生成"""
    log_info("测试User-Agent生成...")
    try:
        ua = get_random_ua()
        log_info(f"生成的User-Agent: {ua}")
        return True
    except Exception as e:
        log_info(f"User-Agent生成失败: {e}")
        return False

def test_data_cleaning():
    """测试数据清洗功能"""
    log_info("测试数据清洗功能...")
    
    # 创建测试数据
    test_data = pd.DataFrame({
        "school": ["北京大学(医学部)", "清华大学", "复旦(上海医学院)", "北大"],
        "major": ["计算机科学与技术", "软件工程", "人工智能", "数据科学"],
        "province": ["北京市", "上海", "广东省", "浙江省"],
        "year": [2023, 2023, 2023, 2023],
        "min_score": [680, 675, 670, 665]
    })
    
    try:
        # 测试名称标准化
        cleaned_data = standardize_names(test_data.copy(), "school")
        log_info(f"名称标准化结果: {cleaned_data['school'].tolist()}")
        
        # 测试省份名称清理
        cleaned_data = clean_province_names(cleaned_data)
        log_info(f"省份名称清理结果: {cleaned_data['province'].tolist()}")
        
        return True
    except Exception as e:
        log_info(f"数据清洗测试失败: {e}")
        return False

def test_data_conversion():
    """测试数据转换功能"""
    log_info("测试数据转换功能...")
    
    # 创建测试数据
    test_data = pd.DataFrame({
        "school": ["北京大学", "清华大学"],
        "major": ["计算机", "软件工程"],
        "province": ["北京", "北京"],
        "year": [2023, 2023],
        "min_score": [680, 675]
    })
    
    try:
        # 测试标准格式转换
        standard_data = convert_to_standard_format(test_data)
        log_info(f"标准格式转换结果: {len(standard_data)} 条记录")
        return True
    except Exception as e:
        log_info(f"数据转换测试失败: {e}")
        return False

def test_config():
    """测试配置加载"""
    log_info("测试配置加载...")
    
    try:
        from config import PROVINCES, YEARS, YANGGUANG_BASE_URL
        log_info(f"目标省份: {PROVINCES}")
        log_info(f"目标年份: {YEARS}")
        log_info(f"阳光高考URL: {YANGGUANG_BASE_URL}")
        return True
    except Exception as e:
        log_info(f"配置加载失败: {e}")
        return False

def main():
    """运行所有测试"""
    setup_logger()
    log_info("开始运行测试...")
    
    tests = [
        ("配置加载", test_config),
        ("User-Agent生成", test_user_agent),
        ("数据清洗", test_data_cleaning),
        ("数据转换", test_data_conversion)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        log_info(f"运行测试: {test_name}")
        if test_func():
            log_info(f"✓ {test_name} 测试通过")
            passed += 1
        else:
            log_info(f"✗ {test_name} 测试失败")
    
    log_info(f"测试完成: {passed}/{total} 通过")
    
    if passed == total:
        log_info("所有测试通过！系统准备就绪。")
    else:
        log_info("部分测试失败，请检查相关模块。")

if __name__ == "__main__":
    main() 