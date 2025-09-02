#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from translation_utils import translate_and_extract_for_search
from translation_settings import TranslationSettings

def test_translation_modes():
    """اختبار جميع أوضاع الترجمة المختلفة"""
    
    test_query = "بيتزا جمبري كبير"
    
    print("🧪 اختبار أوضاع الترجمة المختلفة")
    print("=" * 60)
    print(f"📝 النص المراد اختباره: {test_query}")
    print()
    
    # الوضع 1: ترجمة مع القاموس
    print("🔄 الوضع 1: ترجمة مع القاموس")
    TranslationSettings.ENABLE_TRANSLATION = True
    TranslationSettings.USE_DICTIONARY = True
    TranslationSettings.EXTRACT_FOOD_KEYWORDS_ONLY = True
    
    result1 = translate_and_extract_for_search(test_query)
    print(f"   ➤ الترجمة: {result1['full_translation']}")
    print(f"   ➤ البحث: {result1['search_query']}")
    print(f"   ➤ الوضع: {TranslationSettings.get_current_mode()}")
    print("-" * 40)
    
    # الوضع 2: ترجمة بدون القاموس
    print("🔄 الوضع 2: ترجمة بدون القاموس")
    TranslationSettings.ENABLE_TRANSLATION = True
    TranslationSettings.USE_DICTIONARY = False
    TranslationSettings.EXTRACT_FOOD_KEYWORDS_ONLY = True
    
    result2 = translate_and_extract_for_search(test_query)
    print(f"   ➤ الترجمة: {result2['full_translation']}")
    print(f"   ➤ البحث: {result2['search_query']}")
    print(f"   ➤ الوضع: {TranslationSettings.get_current_mode()}")
    print("-" * 40)
    
    # الوضع 3: بدون ترجمة (عربي مباشر)
    print("🔄 الوضع 3: بدون ترجمة (عربي مباشر)")
    TranslationSettings.ENABLE_TRANSLATION = False
    TranslationSettings.USE_DICTIONARY = True  # لا يهم القيمة هنا
    TranslationSettings.EXTRACT_FOOD_KEYWORDS_ONLY = True
    
    result3 = translate_and_extract_for_search(test_query)
    print(f"   ➤ النص الأصلي: {result3['full_translation']}")
    print(f"   ➤ البحث: {result3['search_query']}")
    print(f"   ➤ الوضع: {TranslationSettings.get_current_mode()}")
    print("-" * 40)
    
    # الوضع 4: ترجمة مع القاموس بدون استخراج كلمات الطعام
    print("🔄 الوضع 4: ترجمة مع القاموس (كامل النص)")
    TranslationSettings.ENABLE_TRANSLATION = True
    TranslationSettings.USE_DICTIONARY = True
    TranslationSettings.EXTRACT_FOOD_KEYWORDS_ONLY = False
    
    result4 = translate_and_extract_for_search(test_query)
    print(f"   ➤ الترجمة: {result4['full_translation']}")
    print(f"   ➤ البحث: {result4['search_query']}")
    print(f"   ➤ الوضع: {TranslationSettings.get_current_mode()}")
    print("-" * 40)
    
    # إعادة ضبط الإعدادات للوضع الافتراضي
    TranslationSettings.ENABLE_TRANSLATION = True
    TranslationSettings.USE_DICTIONARY = True
    TranslationSettings.EXTRACT_FOOD_KEYWORDS_ONLY = True
    
    print("✅ تم اختبار جميع الأوضاع بنجاح!")
    print(f"🔧 الوضع الحالي: {TranslationSettings.get_current_mode()}")

def demonstrate_toggle_functions():
    """عرض كيفية التبديل بين الأوضاع"""
    print("\n🔀 عرض وظائف التبديل:")
    print("=" * 40)
    
    print(f"الوضع الحالي: {TranslationSettings.get_current_mode()}")
    
    print("تبديل الترجمة...")
    new_mode = TranslationSettings.toggle_translation()
    print(f"الوضع الجديد: {new_mode}")
    
    print("تبديل القاموس...")
    new_mode = TranslationSettings.toggle_dictionary()
    print(f"الوضع الجديد: {new_mode}")
    
    # إعادة الترجمة للحالة المفعلة
    TranslationSettings.ENABLE_TRANSLATION = True

if __name__ == "__main__":
    test_translation_modes()
    demonstrate_toggle_functions()
