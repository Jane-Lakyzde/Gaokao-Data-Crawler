#!/bin/bash

# 高考数据采集系统启动脚本

echo "=== 高考数据采集与清洗系统 ==="
echo "正在启动..."

# 检查虚拟环境是否存在
if [ ! -d "venv" ]; then
    echo "虚拟环境不存在，正在创建..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 检查依赖是否安装
echo "检查依赖包..."
python -c "import bs4, requests, pandas" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "依赖包未安装，正在安装..."
    pip install -r requirements.txt
fi

# 运行测试
echo "运行系统测试..."
python test_crawler.py

echo ""
echo "系统准备就绪！"
echo "运行以下命令开始数据采集："
echo "  python main.py"
echo ""
echo "或者运行测试："
echo "  python test_crawler.py" 