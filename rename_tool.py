import os
import re
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
from datetime import datetime

class RenameApp:
    def __init__(self, master):
        self.master = master
        master.title("文件夹批量重命名工具")
        master.geometry("800x600")
        
        # 创建UI组件
        self.create_widgets()
        
        # 初始化变量
        self.old_file = ""
        self.new_file = ""
        self.root_dir = ""

    def create_widgets(self):
        # 文件选择区域
        file_frame = ttk.LabelFrame(self.master, text="文件选择")
        file_frame.pack(pady=10, padx=10, fill="x")

        # 旧路径文件选择
        ttk.Label(file_frame, text="原始路径文件:").grid(row=0, column=0, padx=5, sticky="w")
        self.old_entry = ttk.Entry(file_frame, width=50)
        self.old_entry.grid(row=0, column=1, padx=5)
        ttk.Button(file_frame, text="浏览...", command=self.select_old_file).grid(row=0, column=2)

        # 新路径文件选择
        ttk.Label(file_frame, text="翻译路径文件:").grid(row=1, column=0, padx=5, sticky="w")
        self.new_entry = ttk.Entry(file_frame, width=50)
        self.new_entry.grid(row=1, column=1, padx=5)
        ttk.Button(file_frame, text="浏览...", command=self.select_new_file).grid(row=1, column=2)

        # 根目录选择
        ttk.Label(file_frame, text="处理根目录:").grid(row=2, column=0, padx=5, sticky="w")
        self.dir_entry = ttk.Entry(file_frame, width=50)
        self.dir_entry.grid(row=2, column=1, padx=5)
        ttk.Button(file_frame, text="浏览...", command=self.select_root_dir).grid(row=2, column=2)

        # 处理按钮
        self.start_btn = ttk.Button(self.master, text="开始处理", command=self.start_processing)
        self.start_btn.pack(pady=10)

        # 日志显示区域
        log_frame = ttk.LabelFrame(self.master, text="处理日志")
        log_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        self.log_area = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD)
        self.log_area.pack(fill="both", expand=True)

        # 进度条
        self.progress = ttk.Progressbar(self.master, orient="horizontal", mode="determinate")
        self.progress.pack(fill="x", padx=10, pady=5)

    def select_old_file(self):
        file_path = filedialog.askopenfilename(
            title="选择原始路径文件",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            self.old_file = file_path
            self.old_entry.delete(0, tk.END)
            self.old_entry.insert(0, file_path)

    def select_new_file(self):
        file_path = filedialog.askopenfilename(
            title="选择翻译路径文件",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            self.new_file = file_path
            self.new_entry.delete(0, tk.END)
            self.new_entry.insert(0, file_path)

    def select_root_dir(self):
        dir_path = filedialog.askdirectory(title="选择处理根目录")
        if dir_path:
            self.root_dir = dir_path
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, dir_path)

    def log_message(self, message):
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)
        self.master.update()

    def start_processing(self):
        # 禁用按钮防止重复点击
        self.start_btn.config(state="disabled")
        self.progress["value"] = 0
        
        try:
            # 读取文件内容
            with open(self.old_file, 'r', encoding='utf-8') as f:
                old_paths = f.readlines()
            with open(self.new_file, 'r', encoding='utf-8') as f:
                new_paths = f.readlines()

            # 验证文件
            if len(old_paths) != len(new_paths):
                self.log_message("错误：两个文件的行数不一致！")
                return

            # 创建翻译映射
            translation_map = {}
            for old_line, new_line in zip(old_paths, new_paths):
                old_parts = old_line.strip().split('\\')
                new_parts = new_line.strip().split('\\')
                for o_part, n_part in zip(old_parts, new_parts):
                    translation_map[o_part] = n_part

            # 执行重命名
            total = 0
            success = 0
            for root, dirs, files in os.walk(self.root_dir):
                total += len(dirs)

            self.progress["maximum"] = total
            current = 0

            for root, dirs, files in os.walk(self.root_dir, topdown=False):
                for name in dirs:
                    current += 1
                    old_path = os.path.join(root, name)
                    try:
                        # 转换路径逻辑
                        relative_path = os.path.relpath(old_path, self.root_dir)
                        new_parts = [translation_map.get(p, p) for p in relative_path.split(os.sep)]
                        new_path = os.path.join(self.root_dir, *new_parts)
                        
                        if not os.path.exists(new_path):
                            os.rename(old_path, new_path)
                            self.log_message(f"成功：{old_path} → {new_path}")
                            success += 1
                        else:
                            self.log_message(f"跳过：{new_path} 已存在")
                        
                        # 更新进度条
                        self.progress["value"] = current
                        self.master.update()
                    except Exception as e:
                        self.log_message(f"失败：{old_path} → {str(e)}")

            # 显示最终结果
            self.log_message("\n处理完成！")
            self.log_message(f"总项目：{total}  成功：{success}  失败：{total-success}")

        except Exception as e:
            self.log_message(f"发生错误：{str(e)}")
        finally:
            self.start_btn.config(state="normal")

if __name__ == "__main__":
    root = tk.Tk()
    app = RenameApp(root)
    root.mainloop()