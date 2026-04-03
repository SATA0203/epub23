#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EPUB English to Chinese Translator

This tool automatically translates EPUB books from English to Chinese.
It preserves the original EPUB structure while translating text content.

Requirements:
    pip install ebooklib googletrans==4.0.0-rc1 beautifulsoup4 lxml

Usage:
    python epub_translator.py input.epub [output.epub]
"""

import sys
import os
import re
from pathlib import Path
from ebooklib import epub
from bs4 import BeautifulSoup
from googletrans import Translator
import time


class EPUBTranslator:
    """Translate EPUB files from English to Chinese."""
    
    def __init__(self, src_lang='en', dest_lang='zh-cn'):
        """
        Initialize the translator.
        
        Args:
            src_lang: Source language code (default: 'en' for English)
            dest_lang: Destination language code (default: 'zh-cn' for Chinese Simplified)
        """
        self.src_lang = src_lang
        self.dest_lang = dest_lang
        self.translator = Translator()
        self.translation_cache = {}
        
    def translate_text(self, text):
        """
        Translate a single text string.
        
        Args:
            text: Text to translate
            
        Returns:
            Translated text
        """
        if not text or not text.strip():
            return text
            
        # Check cache first
        if text in self.translation_cache:
            return self.translation_cache[text]
            
        try:
            # Skip translation for very short strings that might be formatting
            if len(text.strip()) < 2:
                return text
                
            result = self.translator.translate(
                text, 
                src=self.src_lang, 
                dest=self.dest_lang
            )
            translated = result.text
            
            # Cache the result
            self.translation_cache[text] = translated
            return translated
            
        except Exception as e:
            print(f"Warning: Translation failed for text: {text[:50]}... Error: {e}")
            return text
    
    def translate_html_content(self, html_content):
        """
        Translate HTML content while preserving tags and structure.
        
        Args:
            html_content: HTML string to translate
            
        Returns:
            Translated HTML string
        """
        soup = BeautifulSoup(html_content, 'lxml')
        
        # List of tags that typically contain translatable text
        text_tags = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 
                     'li', 'span', 'div', 'td', 'th', 'blockquote',
                     'caption', 'figcaption', 'label', 'legend']
        
        # Translate text in each tag
        for tag_name in text_tags:
            for tag in soup.find_all(tag_name):
                if tag.string and tag.string.strip():
                    original_text = tag.string
                    translated_text = self.translate_text(original_text)
                    if translated_text != original_text:
                        tag.string.replace_with(translated_text)
        
        # Also handle text nodes that are direct children
        for element in soup.find_all(True):
            if element.contents:
                new_contents = []
                for content in element.contents:
                    if isinstance(content, str) and content.strip():
                        # Only translate if it's mostly alphabetic (likely English text)
                        if re.search(r'[a-zA-Z]', content) and len(re.findall(r'[a-zA-Z]', content)) > len(content) * 0.5:
                            translated = self.translate_text(content)
                            new_contents.append(translated)
                        else:
                            new_contents.append(content)
                    else:
                        new_contents.append(content)
                if new_contents != list(element.contents):
                    element.clear()
                    element.extend(new_contents)
        
        return str(soup)
    
    def translate_epub(self, input_path, output_path=None, progress_callback=None):
        """
        Translate an entire EPUB file.
        
        Args:
            input_path: Path to input EPUB file
            output_path: Path for output EPUB file (default: input_chinese.epub)
            progress_callback: Optional callback function for progress updates
            
        Returns:
            Path to the translated EPUB file
        """
        input_path = Path(input_path)
        
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")
            
        if output_path is None:
            output_path = input_path.parent / f"{input_path.stem}_chinese{input_path.suffix}"
        else:
            output_path = Path(output_path)
            
        print(f"Reading EPUB: {input_path}")
        book = epub.read_epub(input_path)
        
        # Create a new book with translated content
        new_book = epub.EpubBook()
        
        # Copy metadata
        new_book.set_identifier(book.get_metadata('DC', 'identifier')[0][0] if book.get_metadata('DC', 'identifier') else 'translated-book')
        new_book.set_title(book.get_metadata('DC', 'title')[0][0] + ' (Chinese Translation)' if book.get_metadata('DC', 'title') else 'Translated Book')
        new_book.set_language('zh-cn')
        
        # Copy other metadata
        for meta_name in ['creator', 'contributor', 'publisher', 'date', 'description', 'subject']:
            meta_value = book.get_metadata('DC', meta_name)
            if meta_value:
                for value in meta_value:
                    new_book.add_metadata('DC', meta_name, value[0])
        
        # Process items (chapters, images, etc.)
        translated_items = []
        total_items = sum(1 for item in book.items if hasattr(item, 'content') and item.media_type == 'application/xhtml+xml')
        processed_items = 0
        
        print(f"Found {total_items} translatable chapters")
        
        for item in book.items:
            # Check if this is an XHTML content file (chapter)
            if hasattr(item, 'content') and item.media_type == 'application/xhtml+xml':
                processed_items += 1
                if progress_callback:
                    progress_callback(processed_items, total_items)
                    
                print(f"Translating chapter {processed_items}/{total_items}: {item.get_name()}")
                
                try:
                    # Decode content if it's bytes
                    if isinstance(item.content, bytes):
                        content_str = item.content.decode('utf-8')
                    else:
                        content_str = item.content
                    
                    # Translate the HTML content
                    translated_content = self.translate_html_content(content_str)
                    
                    # Create new item with translated content
                    new_item = epub.EpubHtml(
                        title=item.title,
                        file_name=item.file_name,
                        lang='zh-cn'
                    )
                    new_item.content = translated_content.encode('utf-8')
                    new_item.id = item.id
                    
                    translated_items.append(new_item)
                    
                except Exception as e:
                    print(f"Error translating {item.get_name()}: {e}")
                    # Keep original item if translation fails
                    translated_items.append(item)
            else:
                # Non-text items (images, CSS, etc.) - keep as is
                translated_items.append(item)
        
        # Add all items to the new book
        for item in translated_items:
            new_book.add_item(item)
        
        # Preserve table of contents - only include EpubHtml items
        if book.toc:
            new_book.toc = [item for item in book.toc if isinstance(item, epub.EpubHtml)]
        
        # Preserve spine
        if book.spine:
            new_book.spine = book.spine
        
        # Preserve navigation files
        if book.guide:
            new_book.guide = book.guide
        
        print(f"Writing translated EPUB: {output_path}")
        epub.write_epub(output_path, new_book, {})
        
        print(f"Translation complete! Output saved to: {output_path}")
        return output_path


def main():
    """Main entry point for command-line usage."""
    if len(sys.argv) < 2:
        print("Usage: python epub_translator.py <input.epub> [output.epub]")
        print("\nExample:")
        print("  python epub_translator.py book.epub")
        print("  python epub_translator.py book.epub book_chinese.epub")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    translator = EPUBTranslator()
    
    try:
        translator.translate_epub(input_file, output_file)
        print("\n✓ Translation completed successfully!")
    except FileNotFoundError as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
