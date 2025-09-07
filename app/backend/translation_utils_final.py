#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
أدوات الترجمة البسيطة والفعالة
"""

import re

def is_arabic_text(text):
    """فحص إذا كان النص يحتوي على أحرف عربية"""
    if not text:
        return False
    arabic_chars = len(re.findall(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]', text))
    total_chars = len(re.findall(r'[a-zA-Z\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]', text))
    if total_chars == 0:
        return False
    return arabic_chars > total_chars * 0.3

def basic_word_mapping(text):
    """ترجمة أساسية للكلمات الشائعة"""
    if not text:
        return text
    
    # قاموس الترجمة الأساسي
    basic_words = {
        "بيتزا": "Pizza",
        "برجر": "Burger", 
        "ساندويتش": "Sandwich",
        "دجاج": "Chicken",
        "فراخ": "Chicken",
        "لحم": "Beef",
        "جبن": "Cheese",
        "تونه": "Tuna",
        "تونة": "Tuna",
        "كبير": "Large",
        "وسط": "Medium",
        "صغير": "Small",
        "اريد": "I want",
        "عايز": "I want",
        "محتاج": "I need"
    }
    
    result = text
    for arabic, english in basic_words.items():
        result = result.replace(arabic, english)
    
    return result

def translate_and_extract_for_search(query):
    """ترجمة للبحث"""
    if not query:
        return "", "no_translation"
    
    # فحص إذا كان النص عربي
    if is_arabic_text(query):
        # ترجمة النص
        translated = basic_word_mapping(query)
        return translated, "arabic_to_english"
    else:
        return query, "english_direct"

# للتوافق مع الكود القديم
def get_real_translation_dictionary():
    """قاموس فارغ"""
    return {}

def translate_to_english(text):
    """ترجمة بسيطة"""
    return basic_word_mapping(text)

def translate_arabic_to_english_real(text):
    """ترجمة من العربي للإنجليزي"""
    return basic_word_mapping(text) if is_arabic_text(text) else text
