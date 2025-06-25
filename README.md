# 高考数据采集与清洗系统

一个用于采集、清洗和整理高考相关数据的Python系统，支持从阳光高考平台、省级考试院等多个数据源获取数据。

## 功能特性

- **多源数据采集**: 支持阳光高考平台、省级考试院、第三方数据集
- **智能数据清洗**: 自动标准化院校/专业名称、处理缺失值、验证数据质量
- **灵活数据输出**: 支持JSON、CSV、Excel等多种格式
- **完整日志记录**: 详细的操作日志和错误追踪
- **数据质量报告**: 自动生成数据质量分析报告
- **模块化设计**: 清晰的代码结构，易于扩展和维护

## 项目结构

```
Gaokao-Data-Crawler/
├── main.py                 # 主调度程序
├── config.py              # 全局配置
├── requirements.txt       # 依赖包列表
├── test_crawler.py        # 测试脚本
├── start.sh              # 启动脚本
├── README.md             # 项目说明
├── crawlers/             # 爬虫模块
│   ├── __init__.py
│   ├── yangguang.py      # 阳光高考平台爬虫
│   └── provincial.py     # 省级考试院爬虫
├── data_processing/      # 数据处理模块
│   ├── __init__.py
│   ├── cleaner.py        # 数据清洗
│   └── converter.py      # 格式转换
├── utils/                # 工具包
│   ├── __init__.py
│   ├── io_tools.py       # 文件读写
│   └── log.py           # 日志管理
├── data/                 # 数据存储目录
│   ├── raw/             # 原始数据
│   ├── cleaned/         # 清洗后数据
│   └── final/           # 最终数据
├── logs/                # 日志文件
├── downloads/           # 下载文件
└── venv/               # Python虚拟环境
```

## 安装指南

### 方法一：使用启动脚本（推荐）

```bash
# 克隆项目
git clone https://github.com/your-username/Gaokao-Data-Crawler.git
cd Gaokao-Data-Crawler

# 运行启动脚本（会自动创建虚拟环境并安装依赖）
./start.sh
```

### 方法二：手动安装

#### 1. 克隆项目

```bash
git clone https://github.com/your-username/Gaokao-Data-Crawler.git
cd Gaokao-Data-Crawler
```

#### 2. 创建虚拟环境

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
# macOS/Linux:
source venv/bin/activate
# Windows:
# venv\Scripts\activate
```

#### 3. 安装依赖

```bash
pip install -r requirements.txt
```

#### 4. 创建必要目录

```bash
mkdir -p data/raw data/cleaned data/final logs downloads
```

## 使用方法

### 1. 激活虚拟环境

每次使用前都需要激活虚拟环境：

```bash
source venv/bin/activate  # macOS/Linux
# 或
# venv\Scripts\activate   # Windows
```

### 2. 运行测试

首先运行测试脚本验证系统是否正常工作：

```bash
python test_crawler.py
```

### 3. 配置参数

编辑 `config.py` 文件，根据需要调整以下参数：

- `PROVINCES`: 目标省份列表
- `YEARS`: 爬取年份范围
- `YANGGUANG_BASE_URL`: 阳光高考平台URL
- 数据存储路径和日志路径

### 4. 运行主程序

```bash
python main.py
```

程序将自动执行以下步骤：
1. 爬取阳光高考平台数据（院校、专业、分数线、招生章程）
2. 爬取省级考试院数据
3. 加载第三方数据集
4. 清洗和合并数据
5. 生成数据质量报告
6. 保存最终数据

## 数据输出格式

### 最终数据格式（JSON）

```json
[
  {
    "school": "清华大学",
    "major": "计算机类",
    "province": "北京",
    "year": 2023,
    "min_score": 698,
    "min_rank": 368,
    "plan_count": 15,
    "employment": "IT企业/科研机构",
    "missing_years": [2020],
    "data_source": ["阳光高考", "北京考试院"]
  }
]
```

### 数据质量报告

系统会自动生成包含以下内容的数据质量报告：
- 数据完整性统计
- 缺失值分析
- 重复数据检查
- 数值范围验证
- 数据源统计

## 模块说明

### 爬虫模块 (`crawlers/`)

- **yangguang.py**: 阳光高考平台爬虫
  - `crawl_schools()`: 爬取院校库
  - `crawl_majors()`: 爬取专业库
  - `crawl_scores()`: 爬取历年分数线
  - `crawl_admission_rules()`: 爬取招生章程

- **provincial.py**: 省级考试院爬虫
  - `crawl_provincial_scores()`: 爬取省级分数线
  - `load_github_dataset()`: 加载第三方数据集

### 数据处理模块 (`data_processing/`)

- **cleaner.py**: 数据清洗
  - `standardize_names()`: 标准化名称
  - `handle_missing_values()`: 处理缺失值
  - `merge_datasets()`: 合并数据集
  - `validate_data()`: 数据验证

- **converter.py**: 格式转换
  - `pdf_to_text()`: PDF转文本
  - `save_structured_data()`: 保存结构化数据
  - `generate_data_report()`: 生成数据报告

### 工具模块 (`utils/`)

- **io_tools.py**: 文件操作工具
- **log.py**: 日志管理

## 配置说明

### 主要配置项

```python
# 目标省份
PROVINCES = ["北京", "上海", "广东", "浙江", "江苏", "山东", "河南", "四川", "湖北", "湖南"]

# 爬取年份
YEARS = [2020, 2021, 2022, 2023]

# 数据存储路径
RAW_DATA_PATH = "data/raw"
CLEANED_DATA_PATH = "data/cleaned"
FINAL_DATA_PATH = "data/final"

# 日志文件路径
LOG_FILE_PATH = "logs/crawler.log"
```

## 常见问题解决

### 1. 依赖包安装失败

**问题**: `ModuleNotFoundError: No module named 'bs4'`

**解决方案**:
```bash
# 确保在虚拟环境中
source venv/bin/activate

# 重新安装依赖
pip install -r requirements.txt
```

### 2. 虚拟环境问题

**问题**: `externally-managed-environment` 错误

**解决方案**:
```bash
# 使用虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. 权限问题

**问题**: 无法执行启动脚本

**解决方案**:
```bash
chmod +x start.sh
./start.sh
```

## 注意事项

1. **反爬虫策略**: 系统已内置随机User-Agent、请求延迟等反爬虫措施
2. **数据准确性**: 建议在使用前验证爬取数据的准确性
3. **法律合规**: 请确保遵守相关网站的使用条款和法律法规
4. **资源消耗**: 大规模爬取可能消耗较多网络和存储资源
5. **虚拟环境**: 始终在虚拟环境中运行，避免依赖冲突

## 故障排除

### 常见问题

1. **网络连接失败**
   - 检查网络连接
   - 确认目标网站可访问
   - 调整请求超时时间

2. **数据解析错误**
   - 检查网站页面结构是否发生变化
   - 更新CSS选择器
   - 查看日志文件获取详细错误信息

3. **依赖包安装失败**
   - 使用虚拟环境
   - 更新pip版本
   - 检查Python版本兼容性

### 日志查看

查看详细日志信息：

```bash
tail -f logs/crawler.log
```

## 贡献指南

欢迎提交Issue和Pull Request来改进项目。

## 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 联系方式

如有问题或建议，请通过以下方式联系：
- 提交GitHub Issue
- 发送邮件至：[your-email@example.com]

---

**免责声明**: 本工具仅供学习和研究使用，使用者需自行承担使用风险，并确保遵守相关法律法规。
