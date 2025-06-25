# 全局配置
# =================================

# 目标省份
PROVINCES = ["北京", "上海", "广东", "江苏", "浙江", "山东", "河南", "四川", "湖北", "湖南"]

# 爬取年份
YEARS = [2020, 2021, 2022, 2023]

# 阳光高考平台URL
YANGGUANG_BASE_URL = "https://gaokao.chsi.com.cn"

# 数据存储路径
RAW_DATA_PATH = "data/raw"
CLEANED_DATA_PATH = "data/cleaned"
FINAL_DATA_PATH = "data/final"

# 日志文件路径
LOG_FILE_PATH = "logs/crawler.log"

# 字段映射 (示例)
FIELD_MAPPING = {
    "院校名称": "school_name",
    "专业名称": "major_name",
    "最低分": "min_score",
    "最低位次": "min_rank",
}

# 请求头
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# IP代理池 (如果需要)
PROXY_POOL = [
    # "http://user:pass@host:port",
] 