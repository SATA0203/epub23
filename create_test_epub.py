# 创建一个简单的测试用 EPUB 文件
from ebooklib import epub

book = epub.EpubBook()
book.set_identifier('test-book-001')
book.set_title('Test English Book')
book.set_language('en')
book.add_author('Test Author')

# 创建章节
chapter1 = epub.EpubHtml(title='Chapter 1', file_name='chap_01.xhtml', lang='en')
chapter1.content = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head><title>Chapter 1</title></head>
<body>
<h1>Chapter 1: Introduction</h1>
<p>This is a test paragraph in English. It contains some sample text for translation.</p>
<p>The quick brown fox jumps over the lazy dog. This sentence contains every letter of the alphabet.</p>
<p>Technology is advancing rapidly in the modern world. Artificial intelligence and machine learning are transforming industries.</p>
</body>
</html>'''

book.add_item(chapter1)

# 设置 spine - 不设置 toc
book.spine = ['chap_01']

# 保存
epub.write_epub('/workspace/test_input.epub', book, {})
print("✓ 测试用英文 EPUB 文件已创建：test_input.epub")

# 验证可以读取
book2 = epub.read_epub('/workspace/test_input.epub')
print("✓ 验证成功：文件可以正常读取")
print(f"  章节数：{len(list(book2.get_items()))}")
for item in book2.get_items():
    print(f"  - {item.file_name} (id={item.get_id()}): {type(item).__name__}")
