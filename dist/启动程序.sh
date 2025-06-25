#!/bin/bash
echo "高考数据采集系统启动中..."
echo ""
echo "正在检查环境..."
mkdir -p data/raw data/cleaned data/final logs downloads
echo "环境检查完成！"
echo ""
echo "启动程序..."
./高考数据采集系统
