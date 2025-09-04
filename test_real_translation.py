#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبار نظام الترجمة الحقيقي
Test Real Translation System
"""

import asyncio
import sys
import os

# إضافة مجلد backend للمسار
sys.path.append(os.path.join(os.path.dirname(__file__), 'app', 'backend'))

from translation_utils import translate_to_english_real, smart_translate

async def test_real_translation():
    """اختبار نظام الترجمة الحقيقي"""
    
    print("=" * 80)
    print("🌍 اختبار نظام الترجمة الحقيقي - Real Translation System Test")
    print("=" * 80)
    
    # جمل تجريبية
    test_sentences = [
        "أريد بيتزا تونة وسط",
        "عايز كباب دجاج كبير",
        "طلب سلطة خضراء صغيرة",
        "هات شاورما لحمة مع خضار",
        "أريد عصير برتقال طازج"
    ]
    
    for i, arabic_text in enumerate(test_sentences, 1):
        print(f"\n{i}. النص العربي: {arabic_text}")
        print("-" * 50)
        
        try:
            # استخدام الترجمة الحقيقية
            translated = await translate_to_english_real(arabic_text)
            print(f"   🤖 الترجمة الحقيقية: {translated}")
            
            # استخدام الترجمة الذكية
            smart_translated = await smart_translate(arabic_text)
            print(f"   🧠 الترجمة الذكية: {smart_translated}")
            
        except Exception as e:
            print(f"   ❌ خطأ في الترجمة: {e}")
    
    print("\n" + "=" * 80)
    print("✅ انتهى اختبار نظام الترجمة")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_real_translation())
