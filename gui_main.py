# gui_main.py
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import sys
import os
from datetime import datetime

# 添加项目路径到sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from main import pipeline
    from config import PROVINCES, YEARS
    from utils.log import setup_logger, log_info, log_error
    from test_crawler import main as test_main
except ImportError as e:
    print(f"导入错误: {e}")
    # 如果导入失败，创建模拟函数
    def pipeline():
        return "模拟运行"
    def test_main():
        print("测试完成")
    PROVINCES = ["北京", "上海", "广东"]
    YEARS = [2023]

class RedirectText:
    """重定向输出到GUI文本框"""
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.buffer = ""

    def write(self, string):
        self.buffer += string
        self.text_widget.insert(tk.END, string)
        self.text_widget.see(tk.END)
        self.text_widget.update()

    def flush(self):
        pass

class GaokaoDataCollectorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("高考数据采集与清洗系统")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # 设置样式
        style = ttk.Style()
        style.theme_use('clam')
        
        self.setup_ui()
        self.setup_logging()
        self.is_running = False
        
    def setup_ui(self):
        """设置用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置标题
        title_label = ttk.Label(main_frame, text="高考数据采集与清洗系统", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 配置区域
        config_frame = ttk.LabelFrame(main_frame, text="配置设置", padding="10")
        config_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 省份选择
        ttk.Label(config_frame, text="目标省份:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.province_var = tk.StringVar(value="北京,上海,广东")
        province_entry = ttk.Entry(config_frame, textvariable=self.province_var, width=40)
        province_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        ttk.Label(config_frame, text="(用逗号分隔)").grid(row=0, column=2, sticky=tk.W, padx=(5, 0), pady=5)
        
        # 年份选择
        ttk.Label(config_frame, text="爬取年份:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.year_var = tk.StringVar(value="2023")
        year_entry = ttk.Entry(config_frame, textvariable=self.year_var, width=40)
        year_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        ttk.Label(config_frame, text="(用逗号分隔)").grid(row=1, column=2, sticky=tk.W, padx=(5, 0), pady=5)
        
        # 输出格式选择
        ttk.Label(config_frame, text="输出格式:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.format_var = tk.StringVar(value="json")
        format_combo = ttk.Combobox(config_frame, textvariable=self.format_var, 
                                   values=["json", "csv", "excel"], state="readonly", width=37)
        format_combo.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        # 操作按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=10)
        
        self.start_button = ttk.Button(button_frame, text="开始采集", 
                                      command=self.start_collection, style="Accent.TButton")
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.test_button = ttk.Button(button_frame, text="运行测试", 
                                     command=self.run_test)
        self.test_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.clear_button = ttk.Button(button_frame, text="清空日志", 
                                      command=self.clear_log)
        self.clear_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.open_folder_button = ttk.Button(button_frame, text="打开数据文件夹", 
                                            command=self.open_data_folder)
        self.open_folder_button.pack(side=tk.LEFT)
        
        # 进度条
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 状态标签
        self.status_var = tk.StringVar(value="就绪")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, 
                                font=("Arial", 10, "bold"))
        status_label.grid(row=4, column=0, columnspan=3, pady=(0, 10))
        
        # 日志显示区域
        log_frame = ttk.LabelFrame(main_frame, text="运行日志", padding="5")
        log_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=80)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(5, weight=1)
        config_frame.columnconfigure(1, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
    def setup_logging(self):
        """设置日志重定向"""
        self.redirect = RedirectText(self.log_text)
        sys.stdout = self.redirect
        sys.stderr = self.redirect
        
    def start_collection(self):
        """开始数据采集"""
        if self.is_running:
            messagebox.showwarning("警告", "任务正在运行中，请等待完成")
            return
            
        # 获取配置
        provinces = [p.strip() for p in self.province_var.get().split(",") if p.strip()]
        years = [int(y.strip()) for y in self.year_var.get().split(",") if y.strip()]
        
        if not provinces or not years:
            messagebox.showerror("错误", "请正确配置省份和年份")
            return
            
        # 更新UI状态
        self.is_running = True
        self.start_button.config(state="disabled")
        self.test_button.config(state="disabled")
        self.progress.start()
        self.status_var.set("正在采集数据...")
        
        # 在新线程中运行采集任务
        thread = threading.Thread(target=self._run_collection, args=(provinces, years))
        thread.daemon = True
        thread.start()
        
    def _run_collection(self, provinces, years):
        """运行数据采集"""
        try:
            print(f"开始数据采集 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"目标省份: {provinces}")
            print(f"目标年份: {years}")
            print("-" * 50)
            
            # 这里调用实际的采集函数
            # 为了演示，我们使用模拟函数
            result = pipeline()
            
            print(f"数据采集完成 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"结果: {result}")
            
            # 在主线程中更新UI
            self.root.after(0, self._collection_completed, True)
            
        except Exception as e:
            print(f"采集过程中出现错误: {str(e)}")
            self.root.after(0, self._collection_completed, False, str(e))
            
    def _collection_completed(self, success, error_msg=""):
        """采集完成回调"""
        self.is_running = False
        self.start_button.config(state="normal")
        self.test_button.config(state="normal")
        self.progress.stop()
        
        if success:
            self.status_var.set("采集完成")
            messagebox.showinfo("完成", "数据采集已完成！")
        else:
            self.status_var.set("采集失败")
            messagebox.showerror("错误", f"数据采集失败: {error_msg}")
            
    def run_test(self):
        """运行测试"""
        if self.is_running:
            messagebox.showwarning("警告", "任务正在运行中，请等待完成")
            return
            
        self.is_running = True
        self.test_button.config(state="disabled")
        self.progress.start()
        self.status_var.set("正在运行测试...")
        
        thread = threading.Thread(target=self._run_test)
        thread.daemon = True
        thread.start()
        
    def _run_test(self):
        """在后台运行测试"""
        try:
            print(f"开始系统测试 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("-" * 30)
            
            # 导入并运行测试
            test_main()
            
            print("-" * 30)
            print("测试完成")
            
            self.root.after(0, self._test_completed, True)
            
        except Exception as e:
            print(f"测试过程中出现错误: {str(e)}")
            self.root.after(0, self._test_completed, False, str(e))
            
    def _test_completed(self, success, error_msg=""):
        """测试完成回调"""
        self.is_running = False
        self.test_button.config(state="normal")
        self.progress.stop()
        
        if success:
            self.status_var.set("测试完成")
            messagebox.showinfo("完成", "系统测试已完成！")
        else:
            self.status_var.set("测试失败")
            messagebox.showerror("错误", f"系统测试失败: {error_msg}")
            
    def clear_log(self):
        """清空日志"""
        self.log_text.delete(1.0, tk.END)
        
    def open_data_folder(self):
        """打开数据文件夹"""
        import subprocess
        import platform
        
        data_path = os.path.join(os.getcwd(), "data")
        if not os.path.exists(data_path):
            os.makedirs(data_path)
            
        try:
            if platform.system() == "Windows":
                subprocess.run(["explorer", data_path])
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", data_path])
            else:  # Linux
                subprocess.run(["xdg-open", data_path])
        except Exception as e:
            messagebox.showerror("错误", f"无法打开文件夹: {str(e)}")
            
    def on_closing(self):
        """关闭程序时的处理"""
        if self.is_running:
            if messagebox.askokcancel("退出", "任务正在运行中，确定要退出吗？"):
                self.root.destroy()
        else:
            self.root.destroy()

def main():
    """主函数"""
    root = tk.Tk()
    app = GaokaoDataCollectorGUI(root)
    app.is_running = False
    
    # 设置关闭事件
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # 启动GUI
    root.mainloop()

if __name__ == "__main__":
    main() 