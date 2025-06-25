#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高考数据采集系统 - EXE打包脚本
"""

import os
import sys
import subprocess
import shutil
import platform
from pathlib import Path

def check_dependencies():
    """检查打包依赖"""
    print("检查打包依赖...")
    
    try:
        import PyInstaller
        print(f"✓ PyInstaller 已安装: {PyInstaller.__version__}")
    except ImportError:
        print("✗ PyInstaller 未安装，正在安装...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # 在macOS上，tkinter通常不可用，但我们仍然可以打包
    system = platform.system()
    if system == "Darwin":  # macOS
        print("⚠️  在macOS上，将创建命令行版本")
        return True
    elif system == "Windows":
        try:
            import tkinter
            print("✓ tkinter 可用")
        except ImportError:
            print("✗ tkinter 不可用")
            return False
    else:  # Linux
        try:
            import tkinter
            print("✓ tkinter 可用")
        except ImportError:
            print("⚠️  tkinter 不可用，将创建命令行版本")
    
    return True

def clean_build_dirs():
    """清理构建目录"""
    print("清理构建目录...")
    
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"✓ 已删除 {dir_name}")
    
    # 清理spec文件
    for spec_file in Path('.').glob('*.spec'):
        if spec_file.name != 'build_exe.spec':
            spec_file.unlink()
            print(f"✓ 已删除 {spec_file.name}")

def create_directories():
    """创建必要的目录"""
    print("创建必要目录...")
    
    dirs_to_create = ['data/raw', 'data/cleaned', 'data/final', 'logs', 'downloads']
    for dir_path in dirs_to_create:
        os.makedirs(dir_path, exist_ok=True)
        print(f"✓ 已创建 {dir_path}")

def build_exe():
    """构建EXE文件"""
    print("开始构建可执行文件...")
    
    system = platform.system()
    
    if system == "Darwin":  # macOS
        # 在macOS上创建命令行版本
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "--onefile",
            "--name=高考数据采集系统",
            "--add-data=config.py:.",
            "--add-data=crawlers:crawlers",
            "--add-data=data_processing:data_processing", 
            "--add-data=utils:utils",
            "--add-data=test_crawler.py:.",
            "--add-data=main.py:.",
            "main.py"  # 使用main.py而不是gui_main.py
        ]
    else:
        # Windows/Linux使用spec文件
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "build_exe.spec"
        ]
    
    print(f"执行命令: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✓ 可执行文件构建成功！")
        return True
    else:
        print("✗ 可执行文件构建失败")
        print("错误输出:")
        print(result.stderr)
        return False

def copy_additional_files():
    """复制额外文件到dist目录"""
    print("复制额外文件...")
    
    dist_dir = Path("dist")
    if not dist_dir.exists():
        print("✗ dist目录不存在")
        return False
    
    # 复制README文件
    if os.path.exists("README.md"):
        shutil.copy2("README.md", dist_dir / "README.md")
        print("✓ 已复制 README.md")
    
    # 复制requirements文件
    if os.path.exists("requirements.txt"):
        shutil.copy2("requirements.txt", dist_dir / "requirements.txt")
        print("✓ 已复制 requirements.txt")
    
    return True

def create_launcher_script():
    """创建启动脚本"""
    print("创建启动脚本...")
    
    dist_dir = Path("dist")
    system = platform.system()
    
    if system == "Windows":
        launcher_content = '''@echo off
echo 高考数据采集系统启动中...
echo.
echo 正在检查环境...
if not exist "data" mkdir data
if not exist "data\\raw" mkdir data\\raw
if not exist "data\\cleaned" mkdir data\\cleaned
if not exist "data\\final" mkdir data\\final
if not exist "logs" mkdir logs
if not exist "downloads" mkdir downloads
echo 环境检查完成！
echo.
echo 启动程序...
"高考数据采集系统.exe"
pause
'''
        launcher_path = dist_dir / "启动程序.bat"
        with open(launcher_path, 'w', encoding='gbk') as f:
            f.write(launcher_content)
        print("✓ 已创建启动脚本: 启动程序.bat")
        
    elif system == "Darwin":  # macOS
        launcher_content = '''#!/bin/bash
echo "高考数据采集系统启动中..."
echo ""
echo "正在检查环境..."
mkdir -p data/raw data/cleaned data/final logs downloads
echo "环境检查完成！"
echo ""
echo "启动程序..."
./高考数据采集系统
'''
        launcher_path = dist_dir / "启动程序.sh"
        with open(launcher_path, 'w', encoding='utf-8') as f:
            f.write(launcher_content)
        os.chmod(launcher_path, 0o755)  # 添加执行权限
        print("✓ 已创建启动脚本: 启动程序.sh")
        
    else:  # Linux
        launcher_content = '''#!/bin/bash
echo "高考数据采集系统启动中..."
echo ""
echo "正在检查环境..."
mkdir -p data/raw data/cleaned data/final logs downloads
echo "环境检查完成！"
echo ""
echo "启动程序..."
./高考数据采集系统
'''
        launcher_path = dist_dir / "启动程序.sh"
        with open(launcher_path, 'w', encoding='utf-8') as f:
            f.write(launcher_content)
        os.chmod(launcher_path, 0o755)  # 添加执行权限
        print("✓ 已创建启动脚本: 启动程序.sh")

def main():
    """主函数"""
    print("=" * 50)
    print("高考数据采集系统 - 可执行文件打包工具")
    print("=" * 50)
    print(f"操作系统: {platform.system()}")
    print(f"Python版本: {sys.version}")
    
    # 检查依赖
    if not check_dependencies():
        print("依赖检查失败，退出打包")
        return False
    
    # 清理构建目录
    clean_build_dirs()
    
    # 创建必要目录
    create_directories()
    
    # 构建可执行文件
    if not build_exe():
        return False
    
    # 复制额外文件
    copy_additional_files()
    
    # 创建启动脚本
    create_launcher_script()
    
    print("\n" + "=" * 50)
    print("打包完成！")
    print("=" * 50)
    
    system = platform.system()
    if system == "Windows":
        print("可执行文件位置: dist/高考数据采集系统.exe")
        print("启动脚本: dist/启动程序.bat")
    else:
        print("可执行文件位置: dist/高考数据采集系统")
        print("启动脚本: dist/启动程序.sh")
    
    print("\n使用说明:")
    print("1. 将整个dist文件夹复制到目标机器")
    if system == "Windows":
        print("2. 双击'启动程序.bat'或直接运行exe文件")
    else:
        print("2. 运行'./启动程序.sh'或直接运行可执行文件")
    print("3. 程序会自动创建必要的目录结构")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1) 