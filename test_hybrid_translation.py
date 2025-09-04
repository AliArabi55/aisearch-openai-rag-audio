#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبار نظام الترجمة الهجين الجديد
"""

import sys
import os

# إضافة المسار
sys.path.append(os.path.dirname(__file__))

from translation_utils import translate_arabic_to_english_real

def test_hybrid_translation():
    """اختبار النظام الهجين"""
    
    print("🧪 اختبار نظام الترجمة الهجين الجديد")
    print("=" * 60)
    
    test_cases = [
        "أريد بيتزا تونة وسط",           # قاموس كامل
        "عايز كباب دجاج كبير",          # قاموس + ترجمة 
        "طلب سلطة خضراء صغيرة",         # قاموس + ترجمة
        "أريد شاورما لحمة",             # مختلط
        "هات عصير برتقال طازج"          # ترجمة Google
    ]
    
    for i, text in enumerate(test_cases, 1):
        print(f"\n{i}. النص العربي: '{text}'")
        print("-" * 40)
        
        try:
            result = translate_arabic_to_english_real(text)
            print(f"   ✅ النتيجة: '{result}'")
        except Exception as e:
            print(f"   ❌ خطأ: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 انتهى الاختبار")

if __name__ == "__main__":
    test_hybrid_translation()
