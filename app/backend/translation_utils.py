#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
أدوات الترجمة الحقيقية من العربية إلى الإنجليزية
نظام ترجمة دقيق للمصطلحات الغذائية والمطاعم
"""

import re
from translation_settings import TranslationSettings

def get_real_translation_dictionary():
    """
    قاموس ترجمة حقيقي للمصطلحات الغذائية
    """
    return {
        # أطباق رئيسية
        "بيتزا": "Pizza",
        "برجر": "Burger", 
        "كالزونى": "Calzone",
        "كالزوني": "Calzone",
        
        # أنواع اللحوم والبروتين
        "فراخ": "Chicken",
        "دجاج": "Chicken",
        "بيف": "Beef",
        "لحم": "Beef",
        "لحمة": "Beef",
        "سلامي": "Salami",
        "سلامى": "Salami",
        "جمبري": "Shrimp",
        "تونة": "Tuna",
        "تونه": "Tuna",
        "سجق": "Sausage",
        "انشوجه": "Anchovy",
        "كابوريا": "Crab",
        "بيكون": "Bacon",
        "باكون": "Bacon",
        
        # الجبن والإضافات
        "جبن": "Cheese",
        "جبنة": "Cheese",
        "موزاريلا": "Mozzarella",
        "شيدر": "Cheddar",
        "رومي": "Romano",
        "رومى": "Romano",
        
        # الصوصات
        "صوص": "Sauce",
        "صلصة": "Sauce",
        "مايونيز": "Mayonnaise",
        "باربكيو": "Barbecue",
        "رانش": "Ranch",
        
        # الخضروات
        "طماطم": "Tomato",
        "بصل": "Onion", 
        "أونين رينجز": "Onion Rings",
        "اونين رينجز": "Onion Rings",
        "أونيان رينجز": "Onion Rings", 
        "اونيان رينجز": "Onion Rings",
        "حلقات البصل": "Onion Rings",
        "حلقات بصل": "Onion Rings",
        "رينجز": "Rings",
        "فلفل": "Pepper",
        "خس": "Lettuce",
        "خيار": "Cucumber",
        "مشروم": "Mushroom",
        "زيتون": "Olives",
        
        # الأحجام
        "كبير": "Large",
        "وسط": "Medium", 
        "صغير": "Small",
        "كبيرة": "Large",
        "وسطة": "Medium",
        "صغيرة": "Small",
        
        # أنواع الطبخ
        "كرسبي": "Crispy",
        "كرسبى": "Crispy",
        "مقلي": "Fried",
        "مشوي": "Grilled",
        "مشوى": "Grilled",
        "مدخن": "Smoked",
        
        # أخرى
        "سنجل": "Single",
        "دبل": "Double",
        "سبيشيال": "Special",
        "مكس": "Mix",
        "مختلط": "Mixed",
        "امريكان": "American",
        "هوت": "Hot",
        "دوج": "Dog"
    }

def translate_arabic_to_english_real(text):
    """
    ترجمة حقيقية من العربية إلى الإنجليزية
    """
    if not text or not text.strip():
        return ""
    
    dictionary = get_real_translation_dictionary()
    text = text.strip()
    
    # أولاً نحاول ترجمة النص كاملاً إذا كان موجوداً في القاموس
    if text in dictionary:
        return dictionary[text]
    
    # ثم نحاول البحث عن عبارات فرعية
    for arabic_phrase, english_phrase in dictionary.items():
        if len(arabic_phrase.split()) > 1:  # عبارات متعددة الكلمات
            if arabic_phrase in text:
                text = text.replace(arabic_phrase, english_phrase)
    
    # أخيراً نترجم الكلمات المتبقية واحدة بواحدة
    words = text.split()
    translated_words = []
    
    for word in words:
        # إزالة علامات الترقيم
        clean_word = re.sub(r'[^\w\s]', '', word)
        
        # البحث عن الكلمة في القاموس
        if clean_word in dictionary:
            translated_words.append(dictionary[clean_word])
        else:
            # إذا لم توجد في القاموس، نحاول البحث عن كلمات مشابهة
            found = False
            for arabic_word, english_word in dictionary.items():
                if len(arabic_word.split()) == 1:  # كلمات مفردة فقط
                    if clean_word in arabic_word or arabic_word in clean_word:
                        translated_words.append(english_word)
                        found = True
                        break
            
            if not found:
                # الاحتفاظ بالكلمة كما هي إذا لم توجد ترجمة
                translated_words.append(word)
    
    return " ".join(translated_words)

def translate_arabic_to_english(text):
    """
    ترجمة النص العربي إلى الإنجليزية - ترجمة حقيقية
    """
    if not text or not text.strip():
        return ""
    
    # التحقق من إعدادات الترجمة
    if not TranslationSettings.ENABLE_TRANSLATION:
        return text  # إرجاع النص العربي كما هو
    
    # ترجمة حقيقية باستخدام القاموس
    translated = translate_arabic_to_english_real(text)
    return translated

def translate_and_extract_for_search(text):
    """
    ترجمة النص للبحث مع إظهار معلومات الوضع
    """
    settings = TranslationSettings()
    mode = settings.get_mode()
    
    if TranslationSettings.ENABLE_TRANSLATION:
        result = translate_arabic_to_english(text)
        return result, mode
    else:
        return text, mode