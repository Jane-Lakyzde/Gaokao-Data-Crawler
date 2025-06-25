# data_processing/cleaner.py
import pandas as pd
import re
from utils.log import log_info, log_error, log_missing_data

def standardize_names(data, field):
    """
    统一院校/专业名称（去除括号备注/缩写）
    例：北京大学(医学部) → 北京大学
    """
    log_info(f"开始标准化字段: {field}")
    
    try:
        if isinstance(data, pd.DataFrame):
            # 去除括号内容
            data[field] = data[field].astype(str).str.replace(r"\([^)]*\)", "", regex=True)
            # 去除多余空格
            data[field] = data[field].str.strip()
            # 统一常见缩写
            name_mapping = {
                "北大": "北京大学",
                "清华": "清华大学",
                "复旦": "复旦大学",
                "上交": "上海交通大学",
                "浙大": "浙江大学",
                "南大": "南京大学",
                "中大": "中山大学",
                "华科": "华中科技大学",
                "武大": "武汉大学",
                "川大": "四川大学"
            }
            data[field] = data[field].replace(name_mapping)
            
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and field in item:
                    item[field] = re.sub(r"\([^)]*\)", "", str(item[field])).strip()
        
        log_info(f"字段 {field} 标准化完成")
        return data
        
    except Exception as e:
        log_error(f"标准化字段 {field} 时出错: {str(e)}")
        return data

def handle_missing_values(df, strategy="mark_na"):
    """
    缺失值处理：
    - 连续缺失：线性插值
    - 单点缺失：标记N/A并记录来源
    """
    log_info(f"开始处理缺失值，策略: {strategy}")
    
    try:
        if strategy == "mark_na":
            # 标记缺失值
            df = df.fillna("N/A")
            missing_count = df.isnull().sum().sum()
            if missing_count > 0:
                log_missing_data(f"标记了 {missing_count} 个缺失值")
                
        elif strategy == "interpolate":
            # 线性插值（仅适用于数值型数据）
            numeric_columns = df.select_dtypes(include=['number']).columns
            for col in numeric_columns:
                if df[col].isnull().sum() > 0:
                    df[col] = df[col].interpolate(method='linear')
                    log_info(f"对列 {col} 进行了线性插值")
                    
        elif strategy == "drop":
            # 删除包含缺失值的行
            original_count = len(df)
            df = df.dropna()
            dropped_count = original_count - len(df)
            log_info(f"删除了 {dropped_count} 行包含缺失值的数据")
            
        elif strategy == "forward_fill":
            # 前向填充
            df = df.fillna(method='ffill')
            log_info("使用前向填充处理缺失值")
            
        return df
        
    except Exception as e:
        log_error(f"处理缺失值时出错: {str(e)}")
        return df

def merge_datasets(yangguang_df, provincial_df, third_party_df=None):
    """
    合并阳光高考与省级数据：
    - 按年份+省份+院校名称匹配
    - 冲突时优先省级数据
    """
    log_info("开始合并数据集...")
    
    try:
        # 确保数据为DataFrame格式
        if not isinstance(yangguang_df, pd.DataFrame):
            yangguang_df = pd.DataFrame(yangguang_df)
        if not isinstance(provincial_df, pd.DataFrame):
            provincial_df = pd.DataFrame(provincial_df)
        if third_party_df is not None and not isinstance(third_party_df, pd.DataFrame):
            third_party_df = pd.DataFrame(third_party_df)
        
        # 标准化关键字段
        yangguang_df = standardize_names(yangguang_df, "school")
        provincial_df = standardize_names(provincial_df, "school")
        if third_party_df is not None:
            third_party_df = standardize_names(third_party_df, "school")
        
        # 添加数据源标识
        yangguang_df['data_source'] = '阳光高考'
        provincial_df['data_source'] = '省级考试院'
        if third_party_df is not None:
            third_party_df['data_source'] = '第三方数据'
        
        # 合并数据集
        merged_df = pd.concat([yangguang_df, provincial_df], ignore_index=True)
        if third_party_df is not None:
            merged_df = pd.concat([merged_df, third_party_df], ignore_index=True)
        
        # 去重处理，优先保留省级数据
        merged_df = merged_df.drop_duplicates(
            subset=["school", "major", "province", "year"], 
            keep="last"
        )
        
        # 处理冲突数据
        conflict_columns = ["min_score", "min_rank", "plan_count"]
        for col in conflict_columns:
            if col in merged_df.columns:
                # 对于数值型数据，优先使用省级数据
                merged_df[f"{col}_source"] = merged_df['data_source']
        
        log_info(f"数据集合并完成，最终数据量: {len(merged_df)} 条记录")
        return merged_df
        
    except Exception as e:
        log_error(f"合并数据集时出错: {str(e)}")
        return pd.DataFrame()

def validate_data(df):
    """
    数据验证：检查数据质量和一致性
    """
    log_info("开始数据验证...")
    
    validation_results = {
        "total_records": len(df),
        "missing_values": {},
        "invalid_scores": 0,
        "invalid_years": 0,
        "duplicates": 0
    }
    
    try:
        # 检查缺失值
        for col in df.columns:
            missing_count = df[col].isnull().sum()
            if missing_count > 0:
                validation_results["missing_values"][col] = missing_count
        
        # 验证分数范围
        if "min_score" in df.columns:
            invalid_scores = df[
                (df["min_score"] != "N/A") & 
                ((df["min_score"] < 0) | (df["min_score"] > 750))
            ]
            validation_results["invalid_scores"] = len(invalid_scores)
        
        # 验证年份范围
        if "year" in df.columns:
            invalid_years = df[
                (df["year"] < 2010) | (df["year"] > 2024)
            ]
            validation_results["invalid_years"] = len(invalid_years)
        
        # 检查重复记录
        duplicates = df.duplicated(subset=["school", "major", "province", "year"]).sum()
        validation_results["duplicates"] = duplicates
        
        log_info(f"数据验证完成: {validation_results}")
        return validation_results
        
    except Exception as e:
        log_error(f"数据验证时出错: {str(e)}")
        return validation_results

def clean_province_names(df):
    """
    清理省份名称，统一格式
    """
    log_info("开始清理省份名称...")
    
    province_mapping = {
        "北京市": "北京",
        "上海市": "上海", 
        "广东省": "广东",
        "浙江省": "浙江",
        "江苏省": "江苏",
        "山东省": "山东",
        "河南省": "河南",
        "四川省": "四川",
        "湖北省": "湖北",
        "湖南省": "湖南"
    }
    
    try:
        if "province" in df.columns:
            df["province"] = df["province"].replace(province_mapping)
        log_info("省份名称清理完成")
        return df
    except Exception as e:
        log_error(f"清理省份名称时出错: {str(e)}")
        return df 