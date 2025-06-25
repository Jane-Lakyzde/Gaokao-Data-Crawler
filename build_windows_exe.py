#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高考数据采集系统 - Windows EXE打包脚本
专门用于Windows系统，包含GUI界面支持
"""

import os
import sys
import subprocess
import shutil
import platform
from pathlib import Path

def check_windows():
    """检查是否为Windows系统"""
    if platform.system() != "Windows":
        print("错误：此脚本只能在Windows系统上运行")
        return False
    return True

def check_dependencies():
    """检查打包依赖"""
    print("检查打包依赖...")
    
    try:
        import PyInstaller
        print(f"✓ PyInstaller 已安装: {PyInstaller.__version__}")
    except ImportError:
        print("✗ PyInstaller 未安装，正在安装...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    try:
        import tkinter
        print("✓ tkinter 可用")
    except ImportError:
        print("✗ tkinter 不可用，将创建命令行版本")
    
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

def build_gui_exe():
    """构建带GUI的可执行文件"""
    print("开始构建GUI版本...")
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--clean",
        "--onefile",
        "--windowed",  # 隐藏控制台窗口
        "--name=高考数据采集系统_GUI",
        "--add-data=config.py;.",
        "--add-data=crawlers;crawlers",
        "--add-data=data_processing;data_processing", 
        "--add-data=utils;utils",
        "--add-data=test_crawler.py;.",
        "--add-data=main.py;.",
        "--hidden-import=tkinter",
        "--hidden-import=tkinter.ttk",
        "--hidden-import=tkinter.scrolledtext",
        "--hidden-import=tkinter.messagebox",
        "gui_main.py"
    ]
    
    print(f"执行命令: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✓ GUI版本构建成功！")
        return True
    else:
        print("✗ GUI版本构建失败")
        print("错误输出:")
        print(result.stderr)
        return False

def build_cli_exe():
    """构建命令行版本的可执行文件"""
    print("开始构建命令行版本...")
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--clean",
        "--onefile",
        "--name=高考数据采集系统_CLI",
        "--add-data=config.py;.",
        "--add-data=crawlers;crawlers",
        "--add-data=data_processing;data_processing", 
        "--add-data=utils;utils",
        "--add-data=test_crawler.py;.",
        "--add-data=main.py;.",
        "main.py"
    ]
    
    print(f"执行命令: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✓ 命令行版本构建成功！")
        return True
    else:
        print("✗ 命令行版本构建失败")
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

def create_launcher_scripts():
    """创建启动脚本"""
    print("创建启动脚本...")
    
    dist_dir = Path("dist")
    
    # GUI版本启动脚本
    gui_launcher_content = '''@echo off
echo 高考数据采集系统(GUI版本)启动中...
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
echo 启动GUI程序...
"高考数据采集系统_GUI.exe"
'''
    
    gui_launcher_path = dist_dir / "启动GUI版本.bat"
    with open(gui_launcher_path, 'w', encoding='gbk') as f:
        f.write(gui_launcher_content)
    print("✓ 已创建启动脚本: 启动GUI版本.bat")
    
    # CLI版本启动脚本
    cli_launcher_content = '''@echo off
echo 高考数据采集系统(命令行版本)启动中...
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
echo 启动命令行程序...
"高考数据采集系统_CLI.exe"
pause
'''
    
    cli_launcher_path = dist_dir / "启动命令行版本.bat"
    with open(cli_launcher_path, 'w', encoding='gbk') as f:
        f.write(cli_launcher_content)
    print("✓ 已创建启动脚本: 启动命令行版本.bat")

def create_installer_script():
    """创建安装脚本"""
    print("创建安装脚本...")
    
    dist_dir = Path("dist")
    
    installer_content = '''@echo off
echo ========================================
echo 高考数据采集系统 - 安装程序
echo ========================================
echo.
echo 正在创建程序目录...
if not exist "C:\\Program Files\\高考数据采集系统" mkdir "C:\\Program Files\\高考数据采集系统"
echo.
echo 正在复制文件...
copy "高考数据采集系统_GUI.exe" "C:\\Program Files\\高考数据采集系统\\"
copy "高考数据采集系统_CLI.exe" "C:\\Program Files\\高考数据采集系统\\"
copy "README.md" "C:\\Program Files\\高考数据采集系统\\"
copy "requirements.txt" "C:\\Program Files\\高考数据采集系统\\"
echo.
echo 正在创建桌面快捷方式...
echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateShortcut.vbs
echo sLinkFile = "%USERPROFILE%\\Desktop\\高考数据采集系统.lnk" >> CreateShortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateShortcut.vbs
echo oLink.TargetPath = "C:\\Program Files\\高考数据采集系统\\高考数据采集系统_GUI.exe" >> CreateShortcut.vbs
echo oLink.WorkingDirectory = "C:\\Program Files\\高考数据采集系统" >> CreateShortcut.vbs
echo oLink.Description = "高考数据采集系统" >> CreateShortcut.vbs
echo oLink.Save >> CreateShortcut.vbs
cscript //nologo CreateShortcut.vbs
del CreateShortcut.vbs
echo.
echo 安装完成！
echo 桌面快捷方式已创建。
echo.
pause
'''
    
    installer_path = dist_dir / "安装程序.bat"
    with open(installer_path, 'w', encoding='gbk') as f:
        f.write(installer_content)
    print("✓ 已创建安装脚本: 安装程序.bat")

def main():
    """主函数"""
    print("=" * 50)
    print("高考数据采集系统 - Windows EXE打包工具")
    print("=" * 50)
    print(f"操作系统: {platform.system()}")
    print(f"Python版本: {sys.version}")
    
    # 检查系统
    if not check_windows():
        return False
    
    # 检查依赖
    if not check_dependencies():
        print("依赖检查失败，退出打包")
        return False
    
    # 清理构建目录
    clean_build_dirs()
    
    # 创建必要目录
    create_directories()
    
    # 构建GUI版本
    gui_success = build_gui_exe()
    
    # 构建CLI版本
    cli_success = build_cli_exe()
    
    if not gui_success and not cli_success:
        print("所有版本构建都失败了")
        return False
    
    # 复制额外文件
    copy_additional_files()
    
    # 创建启动脚本
    create_launcher_scripts()
    
    # 创建安装脚本
    create_installer_script()
    
    print("\n" + "=" * 50)
    print("打包完成！")
    print("=" * 50)
    
    if gui_success:
        print("GUI版本: dist/高考数据采集系统_GUI.exe")
        print("启动脚本: dist/启动GUI版本.bat")
    
    if cli_success:
        print("CLI版本: dist/高考数据采集系统_CLI.exe")
        print("启动脚本: dist/启动命令行版本.bat")
    
    print("安装脚本: dist/安装程序.bat")
    
    print("\n使用说明:")
    print("1. 将整个dist文件夹复制到目标Windows机器")
    print("2. 运行'安装程序.bat'进行安装")
    print("3. 或直接运行对应的启动脚本")
    print("4. 程序会自动创建必要的目录结构")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1) 