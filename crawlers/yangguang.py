# crawlers/yangguang.py
import requests
from bs4 import BeautifulSoup
import time
import random
from fake_useragent import UserAgent
from utils.log import log_error, log_info
from config import YANGGUANG_BASE_URL, HEADERS, PROXY_POOL

def get_random_ua():
    """随机生成User-Agent"""
    try:
        ua = UserAgent()
        return ua.random
    except:
        return HEADERS['User-Agent']

def crawl_schools():
    """
    院校库爬取：院校名称、详情页URL、所在地、主管部门、院校类型、学历层次、满意度
    分页爬取 https://gaokao.chsi.com.cn/sch/search.do?searchType=1&start=0
    """
    log_info("开始爬取阳光高考院校库...")
    base_url = f"{YANGGUANG_BASE_URL}/sch/search.do"
    schools = []
    start = 0
    while True:
        params = {"searchType": 1, "start": start}
        headers = {"User-Agent": get_random_ua()}
        try:
            log_info(f"正在爬取第 {start//20+1} 页院校数据...")
            resp = requests.get(base_url, params=params, headers=headers, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            table = soup.find("table", class_="ch-table")
            if not table:
                log_info(f"第 {start//20+1} 页未找到院校数据，可能已到达最后一页")
                break
            rows = table.find_all("tr")[1:]  # 跳过表头
            if not rows:
                log_info(f"第 {start//20+1} 页无数据，结束爬取")
                break
            for row in rows:
                cols = row.find_all("td")
                if len(cols) < 7:
                    continue
                name_tag = cols[0].find("a")
                school_name = name_tag.text.strip() if name_tag else ""
                detail_url = f"https://gaokao.chsi.com.cn" + name_tag["href"] if name_tag else ""
                location = cols[1].text.strip()
                department = cols[2].text.strip()
                school_type = cols[3].text.strip()
                level = cols[4].text.strip()
                satisfaction = cols[5].text.strip()
                schools.append({
                    "院校名称": school_name,
                    "详情页": detail_url,
                    "所在地": location,
                    "主管部门": department,
                    "院校类型": school_type,
                    "学历层次": level,
                    "满意度": satisfaction
                })
            start += 20
            time.sleep(random.uniform(1, 2))
        except Exception as e:
            log_error(f"爬取第 {start//20+1} 页院校数据时出错: {str(e)}")
            break
    log_info(f"院校库爬取完成，共获取 {len(schools)} 所院校信息")
    return schools

def crawl_majors():
    """
    专业库爬取：专业名称/代码/类别/简介/就业方向
    遍历专业分类页 https://gaokao.chsi.com.cn/zyk/
    """
    log_info("开始爬取阳光高考专业库...")
    url = f"{YANGGUANG_BASE_URL}/zyk/"
    majors = []
    
    # 专业分类代码
    categories = {
        "gx": "工学",
        "ls": "理学", 
        "wy": "文学",
        "kj": "经济学",
        "yy": "医学",
        "qt": "其他"
    }
    
    try:
        for category_code, category_name in categories.items():
            log_info(f"正在爬取 {category_name} 类专业...")
            category_url = f"{url}?zyfx={category_code}"
            headers = {"User-Agent": get_random_ua()}
            
            resp = requests.get(category_url, headers=headers, timeout=10)
            resp.raise_for_status()
            
            soup = BeautifulSoup(resp.text, "html.parser")
            major_items = soup.select(".major-info-item")
            
            for item in major_items:
                try:
                    major = {
                        "name": item.select_one(".major-name").text.strip() if item.select_one(".major-name") else "",
                        "code": item.get("id", ""),
                        "category": category_name,
                        "intro": item.select_one(".major-desc").text.strip() if item.select_one(".major-desc") else "",
                        "career": item.select_one(".major-career").text.strip() if item.select_one(".major-career") else ""
                    }
                    majors.append(major)
                except Exception as e:
                    log_error(f"解析专业数据时出错: {str(e)}")
                    continue
            
            time.sleep(random.randint(3, 5))
            
        log_info(f"专业库爬取完成，共获取 {len(majors)} 个专业信息")
        return majors
        
    except Exception as e:
        log_error(f"爬取专业库时发生错误: {str(e)}")
        return []

def crawl_scores(year, province):
    """
    历年分数线：院校/专业/分数/位次/招生计划
    动态构建查询URL：https://gaokao.chsi.com.cn/lqfs/search.do?&year={year}&ssdm={province_code}
    处理AJAX请求（可能需要Selenium模拟点击）
    """
    log_info(f"开始爬取 {year} 年 {province} 的历年分数线...")
    
    try:
        # 省份代码映射（需要根据实际情况调整）
        province_codes = {
            "北京": "11", "上海": "31", "广东": "44", "浙江": "33",
            "江苏": "32", "山东": "37", "河南": "41", "四川": "51",
            "湖北": "42", "湖南": "43"
        }
        
        province_code = province_codes.get(province, province)
        url = f"{YANGGUANG_BASE_URL}/lqfs/search.do"
        params = {
            "year": year,
            "ssdm": province_code
        }
        headers = {"User-Agent": get_random_ua()}
        
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        resp.raise_for_status()
        
        # 解析分数线数据
        scores = []
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # 根据实际页面结构解析数据
        score_items = soup.select(".score-item")  # 需要根据实际CSS选择器调整
        
        for item in score_items:
            try:
                score_data = {
                    "school": item.select_one(".school-name").text.strip() if item.select_one(".school-name") else "",
                    "major": item.select_one(".major-name").text.strip() if item.select_one(".major-name") else "",
                    "min_score": item.select_one(".min-score").text.strip() if item.select_one(".min-score") else "",
                    "min_rank": item.select_one(".min-rank").text.strip() if item.select_one(".min-rank") else "",
                    "plan_count": item.select_one(".plan-count").text.strip() if item.select_one(".plan-count") else "",
                    "year": year,
                    "province": province
                }
                scores.append(score_data)
            except Exception as e:
                log_error(f"解析分数线数据时出错: {str(e)}")
                continue
        
        log_info(f"{year}年{province}分数线爬取完成，共获取 {len(scores)} 条记录")
        return scores
        
    except Exception as e:
        log_error(f"{province}-{year} 分数线爬取失败: {str(e)}")
        return []

def crawl_admission_rules(school_id):
    """
    招生章程：提取录取规则/特殊要求
    解析 https://gaokao.chsi.com.cn/zsgs/zhangcheng/list.do?schoolid={school_id}
    处理PDF文本（pdfminer / PyPDF2）
    """
    log_info(f"开始爬取院校ID {school_id} 的招生章程...")
    
    try:
        url = f"{YANGGUANG_BASE_URL}/zsgs/zhangcheng/list.do"
        params = {"schoolid": school_id}
        headers = {"User-Agent": get_random_ua()}
        
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        resp.raise_for_status()
        
        # 检查是否为PDF内容
        if resp.text.startswith("<PDF>"):
            pdf_url = resp.text.split(">")[1].split("<")[0]
            pdf_path = download_pdf(pdf_url)
            rules = pdf_to_text(pdf_path)
        else:
            rules = parse_html_rules(resp.text)
        
        log_info(f"院校ID {school_id} 招生章程爬取完成")
        return rules
        
    except Exception as e:
        log_error(f"爬取院校ID {school_id} 招生章程时出错: {str(e)}")
        return {}

def download_pdf(url):
    """下载PDF文件"""
    try:
        headers = {"User-Agent": get_random_ua()}
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        
        # 保存PDF文件
        filename = f"downloads/admission_rules_{int(time.time())}.pdf"
        with open(filename, 'wb') as f:
            f.write(resp.content)
        
        return filename
    except Exception as e:
        log_error(f"下载PDF文件失败: {str(e)}")
        return None

def parse_html_rules(html_content):
    """解析HTML格式的招生章程"""
    try:
        soup = BeautifulSoup(html_content, "html.parser")
        rules = {
            "body_check": "",
            "subject_scores": "",
            "bonus_policies": ""
        }
        
        # 根据实际页面结构提取规则信息
        # 这里需要根据具体的HTML结构进行调整
        
        return rules
    except Exception as e:
        log_error(f"解析HTML招生章程时出错: {str(e)}")
        return {} 