# EPUB English to Chinese Translator

一个自动将英文 EPUB 电子书翻译成中文的工具。

## 功能特点

- 📚 完整保留 EPUB 原书结构（目录、章节顺序等）
- 🌐 使用 Google 翻译进行高质量翻译
- 🔍 智能识别可翻译的文本内容
- 💾 保留图片、样式表等非文本资源
- ⚡ 支持翻译缓存，提高效率

## 安装依赖

```bash
pip install ebooklib googletrans==4.0.0-rc1 beautifulsoup4 lxml
```

## 使用方法

### 命令行使用

```bash
# 基本用法（输出文件名为：原文件名_chinese.epub）
python epub_translator.py book.epub

# 指定输出文件名
python epub_translator.py book.epub output_book.epub
```

### Python 代码调用

```python
from epub_translator import EPUBTranslator

# 创建翻译器实例
translator = EPUBTranslator(src_lang='en', dest_lang='zh-cn')

# 翻译 EPUB 文件
translator.translate_epub('input.epub', 'output.epub')
```

### 带进度回调的使用

```python
from epub_translator import EPUBTranslator

def show_progress(current, total):
    print(f"Progress: {current}/{total} ({current/total*100:.1f}%)")

translator = EPUBTranslator()
translator.translate_epub('book.epub', progress_callback=show_progress)
```

## 支持的翻译语言

默认配置：
- 源语言：英语 (`en`)
- 目标语言：简体中文 (`zh-cn`)

可以通过修改 `EPUBTranslator` 初始化参数来支持其他语言组合：

```python
# 例如：英语到日语
translator = EPUBTranslator(src_lang='en', dest_lang='ja')

# 例如：法语到中文
translator = EPUBTranslator(src_lang='fr', dest_lang='zh-cn')
```

## 注意事项

1. **网络连接**：需要联网才能使用 Google 翻译服务
2. **翻译速率限制**：Google 翻译有请求频率限制，大文件可能需要较长时间
3. **文件格式**：仅支持标准 EPUB 格式
4. **文本检测**：工具会智能检测英文文本，避免翻译非英文内容

## 故障排除

### 常见问题

**问题**: `googletrans` 连接失败
- **解决**: 可能是网络问题或 API 限制，尝试使用代理或稍后重试

**问题**: 翻译结果不理想
- **解决**: 可以尝试更换翻译引擎，如接入 DeepL、百度翻译等 API

**问题**: EPUB 文件损坏
- **解决**: 确保输入文件是有效的 EPUB 格式，可以用其他阅读器验证

## 扩展开发

如需接入其他翻译服务（如 DeepL、有道、百度翻译等），可以继承 `EPUBTranslator` 类并重写 `translate_text` 方法：

```python
class CustomTranslator(EPUBTranslator):
    def translate_text(self, text):
        # 实现自定义翻译逻辑
        pass
```

## License

MIT License