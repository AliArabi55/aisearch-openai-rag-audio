#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبار شامل للنظام الجديد مع Azure Search
"""

import sys
import asyncio
sys.path.append("app/backend")

from ragtools import _search_tool
from translation_settings import get_translation_settings
import time

async def test_search_with_modes():
    """اختبار البحث مع الأوضاع المختلفة"""
    print("🧪 اختبار شامل للنظام مع Azure Search")
    print("=" * 60)
    
    settings = get_translation_settings()
    print(f"🔧 الوضع الحالي: {settings.get_mode()}")
    print()
    
    # قائمة الاختبارات
    test_queries = [
        "بيتزا فراخ",
        "برجر بيف", 
        "كالزونى سلامى",
        "كرسبي زنجر"
    ]
    
    for query in test_queries:
        print(f"🔍 البحث عن: {query}")
        print("-" * 40)
        
        try:
            result = await _search_tool(query)
            
            if result:
                print(f"   ✅ النتيجة: {result}")
            else:
                print("   ❌ لم يتم العثور على نتائج")
                
        except Exception as e:
            print(f"   ❌ خطأ في البحث: {e}")
            
        print()
        time.sleep(1)  # انتظار قصير بين البحوث
    
    print("✅ انتهاء الاختبار!")

if __name__ == "__main__":
    asyncio.run(test_search_with_modes())
