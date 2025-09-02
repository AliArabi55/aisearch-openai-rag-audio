#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from dotenv import load_dotenv

# إضافة مجلد backend للمسار
backend_path = os.path.join(os.path.dirname(__file__), 'app', 'backend')
sys.path.insert(0, backend_path)

from ragtools import translate_to_english

def test_new_translation_system():
    """اختبار نظام الترجمة الجديد للبيانات المحددة"""
    
    print("🧪 اختبار نظام الترجمة الجديد:")
    print("=" * 70)
    
    # البيانات من الجدول المرسل
    test_data = [
        "كالزونى فراخ كرسبي كبير",         # ID=1
        "كالزونى فراخ باربكيو كبير",        # ID=2  
        "طبق اونيون رينج",                 # ID=3
        "تشيزي كرسبي دبل",                 # ID=4
        "امريكان كرسبى دبل",               # ID=5
        "فايبس كرسبى دبل",                 # ID=6
        "كريزي رانش كرسبى دبل",            # ID=7
        "جوسي كرسبى دبل",                  # ID=8
        "ديلايت كرسبى دبل",                # ID=9
        "تيستي كرسبي دبل",                 # ID=10
        "تشيزي كرسبى سنجل",                # ID=11
        "امريكان كرسبى سنجل",              # ID=12
        "تيستي كرسبى سنجل",                # ID=13
        "جوسي كرسبى سنجل",                 # ID=14
        "كريزي رانش كرسبي سنجل",           # ID=15
        "فايبس كرسبى سنجل",                # ID=16
        "ديلايت كرسبي سنجل",               # ID=17
        "تشيزي برجر بيف دبل",              # ID=18
        "امريكان برجر بيف دبل",            # ID=19
        "فايبس برجر بيف دبل"               # ID=20
    ]
    
    print("📋 النتائج المتوقعة مقابل الترجمة الفعلية:")
    print("-" * 70)
    
    # نتائج متوقعة
    expected_results = {
        "طبق اونيون رينج": "Taba Onion Ring",
        "تشيزي كرسبي دبل": "Cheesy Crispy Double",
        "امريكان كرسبى دبل": "American Crispy Double",
        "كريزي رانش كرسبى دبل": "Crazy Ranch Crispy Double"
    }
    
    for item in test_data:
        translation = translate_to_english(item)
        
        # فحص إذا كان التطابق مع النتيجة المتوقعة
        if item in expected_results:
            expected = expected_results[item]
            status = "✅" if translation == expected else "❌"
            print(f"{status} '{item}' → '{translation}'")
            if translation != expected:
                print(f"   متوقع: '{expected}'")
        else:
            print(f"📝 '{item}' → '{translation}'")
    
    print("\n" + "=" * 70)
    print("✅ انتهى اختبار نظام الترجمة الجديد")
    
    # اختبار كلمات فردية
    print("\n🔤 اختبار ترجمة الكلمات الفردية:")
    print("-" * 50)
    
    individual_words = ["طبق", "اونيون", "رينج", "كرسبي", "برجر"]
    for word in individual_words:
        translation = translate_to_english(word)
        print(f"   '{word}' → '{translation}'")

if __name__ == "__main__":
    test_new_translation_system()
