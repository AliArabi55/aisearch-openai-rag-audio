#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
أدوات الترجمة المحسنة مع دعم أفضل للنصوص العربية
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
        "محتاج": "I need",
        "ممكن": "Can I have",
        "سعر": "price",
        "كام": "how much",
        "ايه": "what",
        "شو": "what",
        "فين": "where"
    }
    
    result = text
    for arabic, english in basic_words.items():
        # استخدام borders للكلمات لتجنب الاستبدال الخاطئ
        result = re.sub(r'\\b' + re.escape(arabic) + r'\\b', english, result, flags=re.IGNORECASE)
    
    return result

def translate_arabic_to_english_real(text):
    """
    ترجمة من العربي للإنجليزي
    """
    if not text:
        return ""
    
    # إذا كان النص إنجليزي أصلاً، أرجعه كما هو
    if not is_arabic_text(text):
        return text.strip()
    
    # ترجمة الكلمات الأساسية
    translated = basic_word_mapping(text)
    
    # تنظيف النص
    translated = translated.strip()
    
    return translated

def translate_and_extract_for_search(query):
    """
    ترجمة واستخراج للبحث - محسنة
    """
    if not query:
        return "", "no_translation"
    
    # فحص إذا كان النص عربي
    if is_arabic_text(query):
        # ترجمة النص
        translated = translate_arabic_to_english_real(query)
        mode = "arabic_to_english"
        
        # إذا لم تتغير الترجمة كثيراً، استخدم النص الأصلي
        if translated == query:
            # احتفظ بالنص العربي الأصلي للبحث الدلالي
            return query, "arabic_semantic"
        else:
            return translated, mode
    else:
        return query, "english_direct"

# للتوافق مع الكود القديم
def get_real_translation_dictionary():
    """قاموس فارغ - للتوافق مع الكود القديم"""
    return {}

def translate_to_english(text):
    """Wrapper للدالة الجديدة"""
    return translate_arabic_to_english_real(text)
