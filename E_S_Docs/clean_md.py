import os
import re

def clean_md_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # 语雀导出的常见垃圾标签
        content = re.sub(r'<font[^>]*>', '', content)
        content = re.sub(r'</font>', '', content)
        content = re.sub(r'<span[^>]*>', '', content)
        content = re.sub(r'</span>', '', content)
        content = re.sub(r'<div[^>]*>', '', content)
        content = re.sub(r'</div>', '', content)

        # 如果你发现还有其他多余的 HTML 标签, 可以取消下面这行的注释 (一键删所有标签)
        # content = re.sub(r'<[^>]+>', '', content)

        # 清理多余的空行 (把连续3个以上的换行符变成2个)
        content = re.sub(r'\n{3,}', '\n\n', content)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"✅ 已清理: {filepath}")
    except Exception as e:
        print(f"❌ 处理 {filepath} 时出错: {e}")

def main():
    target_dir = '.'  # 当前目录
    print(f"🔍 开始扫描目录: {os.path.abspath(target_dir)}")
    count = 0

    # 遍历目录
    for root, dirs, files in os.walk(target_dir):
        # 跳过隐藏文件夹 (如 .git, .venv)
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for file in files:
            if file.endswith('.md'):
                filepath = os.path.join(root, file)
                clean_md_file(filepath)
                count += 1

    print(f"🎉 清理完成! 共处理 {count} 个 Markdown 文件. ")

if __name__ == '__main__':
    main()