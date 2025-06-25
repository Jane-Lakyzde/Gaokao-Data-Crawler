# main.py
import config
from utils.log import setup_logger, log_info, log_error
from crawlers.yangguang import crawl_schools, crawl_majors, crawl_scores, crawl_admission_rules
from crawlers.provincial import crawl_provincial_scores, load_github_dataset
from data_processing.cleaner import (
    standardize_names, 
    handle_missing_values, 
    merge_datasets, 
    validate_data,
    clean_province_names
)
from data_processing.converter import (
    save_structured_data, 
    generate_data_report, 
    convert_to_standard_format,
    create_summary_statistics
)
import pandas as pd
import os

def crawl_yangguang(years, provinces):
    """主函数：爬取阳光高考平台数据"""
    log_info("启动阳光高考平台数据爬取...")
    
    all_data = {
        "schools": [],
        "majors": [],
        "scores": [],
        "admission_rules": []
    }
    
    try:
        # 爬取院校库
        log_info("开始爬取院校库...")
        schools = crawl_schools()
        all_data["schools"] = schools
        
        # 爬取专业库
        log_info("开始爬取专业库...")
        majors = crawl_majors()
        all_data["majors"] = majors
        
        # 爬取历年分数线
        log_info("开始爬取历年分数线...")
        for year in years:
            for province in provinces:
                scores = crawl_scores(year, province)
                all_data["scores"].extend(scores)
        
        # 爬取部分院校的招生章程（示例：前10所院校）
        log_info("开始爬取招生章程...")
        school_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]  # 示例院校ID
        for school_id in school_ids:
            rules = crawl_admission_rules(school_id)
            if rules:
                all_data["admission_rules"].append({
                    "school_id": school_id,
                    "rules": rules
                })
        
        log_info("阳光高考平台数据爬取完成。")
        return all_data
        
    except Exception as e:
        log_error(f"阳光高考平台数据爬取失败: {str(e)}")
        return all_data

def crawl_provincial(provinces):
    """主函数：爬取省级考试院数据"""
    log_info("启动省级考试院数据爬取...")
    
    provincial_data = []
    
    try:
        # 省级考试院URL映射（需要根据实际情况调整）
        province_urls = {
            "北京": "http://www.bjeea.cn/html/gkgz/tzgg/",
            "上海": "http://www.shmeea.edu.cn/page/24300/",
            "广东": "http://eea.gd.gov.cn/",
            "浙江": "http://www.zjzs.net/",
            "江苏": "http://www.jseea.cn/",
            "山东": "http://www.sdzk.cn/",
            "河南": "http://www.heao.gov.cn/",
            "四川": "http://www.sceea.cn/",
            "湖北": "http://www.hbea.edu.cn/",
            "湖南": "http://www.hneao.edu.cn/"
        }
        
        for province in provinces:
            if province in province_urls:
                data = crawl_provincial_scores(province_urls[province])
                if data:
                    provincial_data.extend(data)
        
        log_info("省级考试院数据爬取完成。")
        return provincial_data
        
    except Exception as e:
        log_error(f"省级考试院数据爬取失败: {str(e)}")
        return provincial_data

def load_third_party_data():
    """加载第三方数据集"""
    log_info("加载第三方数据集...")
    
    try:
        # 示例GitHub数据集URL（需要替换为实际URL）
        github_urls = [
            "https://raw.githubusercontent.com/example/gaokao-data/main/scores.csv",
            "https://raw.githubusercontent.com/example/gaokao-data/main/schools.json"
        ]
        
        third_party_data = []
        for url in github_urls:
            data = load_github_dataset(url)
            if data:
                third_party_data.append(data)
        
        log_info("第三方数据集加载完成。")
        return third_party_data
        
    except Exception as e:
        log_error(f"第三方数据集加载失败: {str(e)}")
        return []

def clean_and_merge(yangguang_data, provincial_data, third_party_data):
    """清洗与合并数据"""
    log_info("开始数据清洗与合并...")
    
    try:
        # 转换数据为DataFrame格式
        yangguang_scores_df = pd.DataFrame(yangguang_data.get("scores", []))
        provincial_df = pd.DataFrame(provincial_data)
        
        # 处理第三方数据
        third_party_df = None
        if third_party_data:
            third_party_df = pd.concat([pd.DataFrame(data) for data in third_party_data], ignore_index=True)
        
        # 数据清洗
        if not yangguang_scores_df.empty:
            yangguang_scores_df = clean_province_names(yangguang_scores_df)
            yangguang_scores_df = standardize_names(yangguang_scores_df, "school")
            yangguang_scores_df = standardize_names(yangguang_scores_df, "major")
            yangguang_scores_df = handle_missing_values(yangguang_scores_df, strategy="mark_na")
        
        if not provincial_df.empty:
            provincial_df = clean_province_names(provincial_df)
            provincial_df = standardize_names(provincial_df, "school")
            provincial_df = standardize_names(provincial_df, "major")
            provincial_df = handle_missing_values(provincial_df, strategy="mark_na")
        
        if third_party_df is not None and not third_party_df.empty:
            third_party_df = clean_province_names(third_party_df)
            third_party_df = standardize_names(third_party_df, "school")
            third_party_df = standardize_names(third_party_df, "major")
            third_party_df = handle_missing_values(third_party_df, strategy="mark_na")
        
        # 合并数据集
        cleaned_data = merge_datasets(yangguang_scores_df, provincial_df, third_party_df)
        
        # 数据验证
        validation_results = validate_data(cleaned_data)
        log_info(f"数据验证结果: {validation_results}")
        
        log_info("数据清洗与合并完成。")
        return cleaned_data
        
    except Exception as e:
        log_error(f"数据清洗与合并失败: {str(e)}")
        return pd.DataFrame()

def pipeline():
    """数据处理主流程"""
    # 初始化日志
    setup_logger()
    log_info("="*50)
    log_info("高考数据采集与清洗流程启动")
    log_info("="*50)

    try:
        # 阶段1：爬取原始数据
        log_info("【阶段1】开始爬取原始数据...")
        yangguang_data = crawl_yangguang(config.YEARS, config.PROVINCES)
        provincial_data = crawl_provincial(config.PROVINCES)
        third_party_data = load_third_party_data()
        log_info("【阶段1】原始数据爬取完成。")

        # 阶段2：清洗与合并
        log_info("【阶段2】开始清洗与合并数据...")
        cleaned_data = clean_and_merge(
            yangguang_data,
            provincial_data,
            third_party_data
        )
        log_info("【阶段2】数据清洗与合并完成。")

        # 阶段3：结构化存储
        log_info("【阶段3】开始结构化存储数据...")
        
        # 保存清洗后的数据
        if not cleaned_data.empty:
            # 保存为JSON格式
            json_output_path = f"{config.FINAL_DATA_PATH}/gaokao_data.json"
            save_structured_data(cleaned_data, json_output_path, format="json")
            
            # 保存为CSV格式
            csv_output_path = f"{config.FINAL_DATA_PATH}/gaokao_data.csv"
            save_structured_data(cleaned_data, csv_output_path, format="csv")
            
            # 生成数据质量报告
            report_path = f"{config.FINAL_DATA_PATH}/data_quality_report.json"
            generate_data_report(cleaned_data, report_path)
            
            # 生成摘要统计
            summary = create_summary_statistics(cleaned_data)
            summary_path = f"{config.FINAL_DATA_PATH}/summary_statistics.json"
            save_structured_data(summary, summary_path, format="json")
            
            log_info(f"【阶段3】结构化存储完成，数据已保存至 {config.FINAL_DATA_PATH}")
        else:
            log_error("【阶段3】没有数据可保存")

        # 保存原始数据（院校、专业信息）
        if yangguang_data.get("schools"):
            schools_path = f"{config.RAW_DATA_PATH}/schools.json"
            save_structured_data(yangguang_data["schools"], schools_path, format="json")
        
        if yangguang_data.get("majors"):
            majors_path = f"{config.RAW_DATA_PATH}/majors.json"
            save_structured_data(yangguang_data["majors"], majors_path, format="json")
        
        if yangguang_data.get("admission_rules"):
            rules_path = f"{config.RAW_DATA_PATH}/admission_rules.json"
            save_structured_data(yangguang_data["admission_rules"], rules_path, format="json")

        log_info("="*50)
        log_info("所有任务执行完毕")
        log_info("="*50)
        
    except Exception as e:
        log_error(f"数据处理流程执行失败: {str(e)}")
        raise

if __name__ == '__main__':
    pipeline() 