import re
import os
from tkinter import filedialog
from tkinter import Tk

def parse_tree(tree_text):
    lines = [l.rstrip() for l in tree_text.split('\n') if l.strip()]
    if not lines:
        return []
    
    # 基础路径配置
    base_path = r"D:\桌面\Teleport-pack-zh-main\Teleport-pack-zh-main\zh"
    
    # 初始化根目录（保留完整名称）
    root_line = lines[0].strip()
    # 仅去除行首的格式符号，保留完整内容
    root_name = re.sub(r'^[├─└│\s]*', '', root_line).strip()  # 修改点1
    current_path = os.path.join(base_path, root_name)
    result = [current_path]
    
    # 使用栈记录路径层级
    path_stack = [current_path]
    level_stack = [0]

    for line in lines[1:]:
        try:
            # 计算缩进层级
            indent = len(re.match(r'^[\s│]*', line).group())
            # 完整保留带[]的目录名（仅去除缩进符号）
            line_content = re.sub(r'^[├─└│\s]*', '', line).strip()  # 修改点2

            # 安全弹出逻辑
            while len(level_stack) > 1 and indent <= level_stack[-1]:
                path_stack.pop()
                level_stack.pop()

            # 构建新路径
            new_path = os.path.join(path_stack[-1], line_content)
            result.append(new_path)
            
            # 更新栈状态
            path_stack.append(new_path)
            level_stack.append(indent)
        except Exception as e:
            print(f"解析行失败: {line} | 错误: {str(e)}")
            continue

    return result
def process_single_file(input_file, output_folder):
    """处理单个文件"""
    with open(input_file, 'r', encoding='utf-8') as f:
        structure_text = f.read()
    
    # 生成路径列表
    path_pairs = parse_tree(structure_text)
    
    # 生成输出文件名
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    output_file = os.path.join(output_folder, f"{base_name}_paths.txt")
    
    # 避免覆盖已有文件
    counter = 1
    while os.path.exists(output_file):
        output_file = os.path.join(output_folder, f"{base_name}_paths({counter}).txt")
        counter += 1
    
    # 写入结果文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(path_pairs))
    
    return output_file

def main():
    root = Tk()
    root.withdraw()
    
    # 批量选择输入文件
    input_files = filedialog.askopenfilenames(
        title="选择结构树文件（可多选）",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )
    if not input_files:
        print("未选择文件")
        return
    
    # 选择输出目录
    output_folder = filedialog.askdirectory(title="选择保存目录")
    if not output_folder:
        print("未选择保存目录")
        return
    
    # 处理所有文件
    success_count = 0
    for input_file in input_files:
        try:
            output_file = process_single_file(input_file, output_folder)
            print(f"已生成：{output_file}")
            success_count += 1
        except Exception as e:
            print(f"处理 {os.path.basename(input_file)} 失败：{str(e)}")
    
    print(f"\n处理完成！成功 {success_count}/{len(input_files)} 个文件")

if __name__ == "__main__":
    main()
