#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import os
import sys
from dotenv import load_dotenv

# إضافة مجلد backend للمسار
sys.path.append(os.path.join(os.path.dirname(__file__), 'app', 'backend'))

from ragtools import translate_to_english

def test_translation():
    """اختبار الترجمة للأصناف من الجدول المرسل"""
    
    print("🧪 اختبار الترجمة للأصناف من الجدول:")
    print("=" * 60)
    
    # الأصناف من الجدول المرسل
    test_items = [
        "كالزونى فراخ كرسبي كبير",
        "كالزونى فراخ باربكيو كبير", 
        "طبق اونيون رينج",
        "تشيزي كرسبي دبل",
        "امريكان كرسبى دبل",
        "فايبس كرسبى دبل",
        "كريزي رانش كرسبى دبل",
        "جوسي كرسبى دبل",
        "ديلايت كرسبى دبل",
        "تيستي كرسبي دبل",
        "بيتزا سي فود وسط"  # العنصر الذي سأل عنه المستخدم
    ]
    
    for item in test_items:
        translation = translate_to_english(item)
        print(f"📝 '{item}' → '{translation}'")
    
    print("\n" + "=" * 60)
    print("✅ انتهى اختبار الترجمة")

if __name__ == "__main__":
    test_translation()
