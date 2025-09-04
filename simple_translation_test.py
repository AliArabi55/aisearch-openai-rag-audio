#!/usr/bin/env python3

"""اختبار نظام الترجمة الحقيقي - مبسط"""

import sys
import os
import asyncio

# إضافة المسار
backend_path = os.path.join(os.path.dirname(__file__), 'app', 'backend')
sys.path.insert(0, backend_path)

async def test_translation():
    print("🌍 بدء اختبار الترجمة الحقيقية...")
    
    try:
        from translation_utils import translate_to_english_real
        
        # نص تجريبي
        arabic_text = "أريد بيتزا تونة وسط"
        print(f"النص العربي: {arabic_text}")
        
        # ترجمة
        translated = await translate_to_english_real(arabic_text)
        print(f"الترجمة: {translated}")
        
    except Exception as e:
        print(f"خطأ: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_translation())
