# data_processing/converter.py
import json
import csv
import pandas as pd
from pdfplumber import open as load_pdf
from utils.log import log_info, log_error
from utils.io_tools import ensure_dir
# from pdfminer.high_level import extract_text

def pdf_to_text(pdf_path):
    """
    招生章程PDF → 结构化文本
    提取关键字段：体检要求/单科成绩要求/加分政策
    """
    log_info(f"转换PDF文件: {pdf_path}")
    
    try:
        rules = {
            "body_check": "",
            "subject_scores": "",
            "bonus_policies": "",
            "admission_rules": "",
            "special_requirements": ""
        }
        
        with load_pdf(pdf_path) as pdf:
            full_text = ""
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n"
            
            # 提取关键信息（使用关键词匹配）
            if "体检" in full_text or "身体" in full_text:
                # 提取体检要求
                body_section = extract_section(full_text, ["体检", "身体", "健康"])
                rules["body_check"] = body_section
            
            if "单科" in full_text or "科目" in full_text:
                # 提取单科成绩要求
                subject_section = extract_section(full_text, ["单科", "科目", "数学", "英语"])
                rules["subject_scores"] = subject_section
            
            if "加分" in full_text or "政策" in full_text:
                # 提取加分政策
                bonus_section = extract_section(full_text, ["加分", "政策", "优惠"])
                rules["bonus_policies"] = bonus_section
            
            # 提取录取规则
            admission_section = extract_section(full_text, ["录取", "招生", "投档"])
            rules["admission_rules"] = admission_section
            
            # 提取特殊要求
            special_section = extract_section(full_text, ["特殊", "要求", "限制"])
            rules["special_requirements"] = special_section
        
        log_info(f"PDF转换完成，提取了 {len([v for v in rules.values() if v])} 个关键信息段")
        return rules
        
    except Exception as e:
        log_error(f"PDF转换失败: {e}")
        return {}

def extract_section(text, keywords, context_lines=3):
    """
    根据关键词提取相关段落
    """
    lines = text.split('\n')
    relevant_lines = []
    
    for i, line in enumerate(lines):
        if any(keyword in line for keyword in keywords):
            # 提取关键词行及其前后几行
            start = max(0, i - context_lines)
            end = min(len(lines), i + context_lines + 1)
            relevant_lines.extend(lines[start:end])
    
    return '\n'.join(relevant_lines) if relevant_lines else ""

def save_structured_data(data, path, format="json"):
    """
    统一输出格式（JSON/CSV）
    """
    log_info(f"以 {format} 格式保存结构化数据到 {path}")
    
    try:
        ensure_dir(path)
        
        if format == "json":
            with open(path, 'w', encoding='utf-8') as f:
                if isinstance(data, pd.DataFrame):
                    data.to_json(f, orient='records', indent=4, force_ascii=False)
                else:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                    
        elif format == "csv":
            if isinstance(data, pd.DataFrame):
                data.to_csv(path, index=False, encoding='utf-8-sig')
            else:
                # 如果是字典列表，转换为CSV
                if data and isinstance(data[0], dict):
                    fieldnames = list(data[0].keys())
                    with open(path, 'w', newline='', encoding='utf-8-sig') as f:
                        writer = csv.DictWriter(f, fieldnames=fieldnames)
                        writer.writeheader()
                        writer.writerows(data)
                        
        elif format == "excel":
            if isinstance(data, pd.DataFrame):
                data.to_excel(path, index=False, engine='openpyxl')
            else:
                log_error("Excel格式仅支持DataFrame数据")
                return
                
        else:
            log_error(f"不支持的格式: {format}")
            return
            
        log_info(f"数据已成功保存到: {path}")
        
    except Exception as e:
        log_error(f"保存数据时出错: {e}")

def generate_data_report(data, output_path="reports/data_quality_report.json"):
    """
    生成数据质量报告
    """
    log_info("生成数据质量报告...")
    
    try:
        ensure_dir(output_path)
        
        if isinstance(data, pd.DataFrame):
            report = {
                "summary": {
                    "total_records": len(data),
                    "total_columns": len(data.columns),
                    "data_types": data.dtypes.to_dict()
                },
                "missing_values": data.isnull().sum().to_dict(),
                "duplicates": {
                    "total_duplicates": data.duplicated().sum(),
                    "duplicate_pairs": data.duplicated(subset=["school", "major", "province", "year"]).sum()
                },
                "data_quality": {
                    "completeness": (1 - data.isnull().sum().sum() / (len(data) * len(data.columns))) * 100,
                    "uniqueness": (1 - data.duplicated().sum() / len(data)) * 100
                }
            }
            
            # 数值型数据的统计信息
            numeric_columns = data.select_dtypes(include=['number']).columns
            if len(numeric_columns) > 0:
                report["numeric_stats"] = data[numeric_columns].describe().to_dict()
            
            # 分类型数据的统计信息
            categorical_columns = data.select_dtypes(include=['object']).columns
            if len(categorical_columns) > 0:
                report["categorical_stats"] = {}
                for col in categorical_columns:
                    report["categorical_stats"][col] = data[col].value_counts().to_dict()
            
        else:
            report = {
                "data_type": type(data).__name__,
                "data_length": len(data) if hasattr(data, '__len__') else "Unknown",
                "message": "非DataFrame数据，无法生成详细报告"
            }
        
        # 保存报告
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=4)
        
        log_info(f"数据质量报告已生成: {output_path}")
        return report
        
    except Exception as e:
        log_error(f"生成数据质量报告时出错: {e}")
        return {}

def convert_to_standard_format(data):
    """
    转换为标准输出格式
    """
    log_info("转换为标准输出格式...")
    
    try:
        if isinstance(data, pd.DataFrame):
            # 转换为字典列表格式
            standard_data = []
            for _, row in data.iterrows():
                record = {
                    "school": row.get("school", ""),
                    "major": row.get("major", ""),
                    "province": row.get("province", ""),
                    "year": row.get("year", ""),
                    "min_score": row.get("min_score", ""),
                    "min_rank": row.get("min_rank", ""),
                    "plan_count": row.get("plan_count", ""),
                    "employment": row.get("employment", ""),
                    "missing_years": row.get("missing_years", []),
                    "data_source": row.get("data_source", [])
                }
                standard_data.append(record)
            return standard_data
        else:
            return data
            
    except Exception as e:
        log_error(f"转换标准格式时出错: {e}")
        return data

def create_summary_statistics(data):
    """
    创建数据摘要统计
    """
    log_info("创建数据摘要统计...")
    
    try:
        if not isinstance(data, pd.DataFrame):
            return {}
        
        summary = {
            "total_schools": data["school"].nunique() if "school" in data.columns else 0,
            "total_majors": data["major"].nunique() if "major" in data.columns else 0,
            "total_provinces": data["province"].nunique() if "province" in data.columns else 0,
            "year_range": {
                "min": data["year"].min() if "year" in data.columns else None,
                "max": data["year"].max() if "year" in data.columns else None
            },
            "score_statistics": {}
        }
        
        # 分数统计
        if "min_score" in data.columns:
            numeric_scores = pd.to_numeric(data["min_score"], errors='coerce')
            summary["score_statistics"] = {
                "mean": numeric_scores.mean(),
                "median": numeric_scores.median(),
                "min": numeric_scores.min(),
                "max": numeric_scores.max(),
                "std": numeric_scores.std()
            }
        
        log_info("数据摘要统计创建完成")
        return summary
        
    except Exception as e:
        log_error(f"创建摘要统计时出错: {e}")
        return {} 