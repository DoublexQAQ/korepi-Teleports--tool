import os
import re
from tkinter import Tk
from tkinter.filedialog import askdirectory

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
    """递归生成树状结构"""
    dir_name = os.path.basename(current_dir)
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

if __name__ == '__main__':
    root = Tk()
    root.withdraw()
    
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