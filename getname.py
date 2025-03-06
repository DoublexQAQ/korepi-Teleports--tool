import os
import re
from tkinter import Tk
from tkinter.filedialog import askdirectory, askopenfilename

def natural_sort_key(s):
    """自然排序键函数：数字优先，字母次之"""
    return [int(text) if text.isdigit() else text.lower() 
            for text in re.split(r'(\d+)', s)]

def write_folder_structure(root_dir, output_file):
    """为单个文件夹生成结构文件"""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            root_name = os.path.basename(os.path.normpath(root_dir)) or root_dir
            f.write(f"{root_name}\n")
            
            dirs = sorted(
                [d for d in os.listdir(root_dir) 
                 if os.path.isdir(os.path.join(root_dir, d))],
                key=natural_sort_key
            )
            
            for i, dir_name in enumerate(dirs):
                is_last = i == len(dirs) - 1
                _write_tree(f, 
                           os.path.join(root_dir, dir_name),
                           "", 
                           is_last)
    except Exception as e:
        print(f"生成 {output_file} 失败: {str(e)}")

def _write_tree(f, current_dir, prefix, is_last):
    """生成带数字前缀的原始结构"""
    dir_name = os.path.basename(current_dir)
    
    # 自动添加数字前缀
    if not re.match(r'^\d+', dir_name):
        parent_dirs = len(prefix.split('│   ')) - 1
        dir_name = f"{parent_dirs + 1} - {dir_name}"
    
    connector = "└── " if is_last else "├── "
    f.write(f"{prefix}{connector}{dir_name}\n")
    
    new_prefix = prefix + ("    " if is_last else "│   ")
    
    try:
        dirs = sorted(
            [d for d in os.listdir(current_dir) 
             if os.path.isdir(os.path.join(current_dir, d))],
            key=natural_sort_key
        )
    except PermissionError:
        return
    
    for i, sub_dir in enumerate(dirs):
        is_sub_last = i == len(dirs) - 1
        _write_tree(f, 
                  os.path.join(current_dir, sub_dir),
                  new_prefix, 
                  is_sub_last)

def convert_structure_to_path(txt_file, root_path):
    """将结构文件转换为实际路径"""
    try:
        with open(txt_file, 'r', encoding='utf-8') as f:
            lines = f.read().splitlines()
        
        if not lines:
            print(f"文件 {txt_file} 是空的")
            return

        # 创建根目录（如果不存在）
        base_dir = os.path.join(root_path, lines[0].strip())  # 添加根目录名称
        if not os.path.exists(base_dir):
            choice = input(f"根路径 {base_dir} 不存在，要创建吗？(y/n): ").lower()
            if choice == 'y':
                os.makedirs(base_dir)
            else:
                print("已取消操作")
                return

        # 解析树状结构
        stack = [(base_dir, -1)]  # (当前路径, 层级)

        for line in lines[1:]:  # 跳过第一行根目录名称
            line = line.rstrip()
            if not line:
                continue

            # 计算缩进层级（每4个空格代表一级）
            indent = len(line) - len(line.lstrip())
            level = indent // 4

            # 获取完整目录名称（保留数字前缀）
            dir_name = line.lstrip("├──└│ ").strip()
            
            # 更新路径栈
            while level <= stack[-1][1]:
                stack.pop()
            
            parent_path = stack[-1][0]
            new_path = os.path.join(parent_path, dir_name)
            
            # 创建目录
            if not os.path.exists(new_path):
                os.makedirs(new_path)
                print(f"已创建：{new_path}")
            else:
                print(f"已存在：{new_path}")

            stack.append((new_path, level))

    except Exception as e:
        print(f"转换失败: {str(e)}")

if __name__ == '__main__':
    root = Tk()
    root.withdraw()

    # 新增功能选择
    choice = input("请选择操作：\n1. 生成结构文件\n2. 转换结构文件\n请输入数字: ").strip()

    if choice == '1':
        # 支持连续多选（取消选择即结束）
        selected_dirs = []
        while True:
            dir_path = askdirectory(title='选择文件夹（取消选择以结束）')
            if not dir_path:
                break
            selected_dirs.append(dir_path)
        
        if not selected_dirs:
            print("未选择任何文件夹，程序退出")
            exit()
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 为每个选中的文件夹生成独立文件
        for idx, folder_path in enumerate(selected_dirs, 1):
            # 生成安全文件名
            folder_name = os.path.basename(os.path.normpath(folder_path)) or f"未命名文件夹_{idx}"
            safe_name = re.sub(r'[\\/*?:"<>|]', '_', folder_name)  # 替换非法字符
            output_path = os.path.join(script_dir, f"{safe_name}_结构树.txt")
            
            # 避免覆盖已有文件
            counter = 1
            while os.path.exists(output_path):
                output_path = os.path.join(script_dir, f"{safe_name}_结构树({counter}).txt")
                counter += 1
            
            write_folder_structure(folder_path, output_path)
            print(f"已生成：{output_path}")

        print("所有结构文件生成完成！")
    elif choice == '2':
        # 选择要转换的txt文件
        txt_files = []
        while True:
            file_path = askopenfilename(
                title='选择结构文件（取消选择以结束）',
                filetypes=[("文本文件", "*.txt")]
            )
            if not file_path:
                break
            txt_files.append(file_path)
        
        if not txt_files:
            print("未选择任何文件，程序退出")
            exit()

        # 选择根目录
        root_path = askdirectory(title='选择根目录（例如D盘下的某个目录）')
        if not root_path:
            print("未选择根目录，程序退出")
            exit()

        # 批量转换
        for txt_file in txt_files:
            print(f"\n正在转换：{os.path.basename(txt_file)}")
            convert_structure_to_path(txt_file, root_path)
        
        print("\n所有转换完成！")
    else:
        print("无效选择，程序退出")