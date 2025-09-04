"""
اختبار نهائي للبحث الدلالي والنظام
"""
import sys
import os
import asyncio
from pathlib import Path

# إضافة مسار backend للوصول للموديولات
backend_path = Path(__file__).parent / 'app' / 'backend'
sys.path.insert(0, str(backend_path))

from dotenv import load_dotenv
load_dotenv(backend_path / '.env')

from ragtools import search_function

async def test_search():
    """اختبار البحث الذي يستخدمه Real-time"""
    
    print("🎯 اختبار البحث النهائي")
    print("="*50)
    
    # اختبار 1: "انا اريد بيتزا تونة وسط"
    test_queries = [
        "انا اريد بيتزا تونة وسط",
        "بيتزا التونة الوسط", 
        "medium tuna pizza",
        "اريد تونة"
    ]
    
    for query in test_queries:
        print(f"\n🔍 البحث: {query}")
        try:
            # استدعاء دالة البحث مباشرة
            result = await search_function(query, add_to_order=False)
            print(f"✅ النتيجة: {result.text[:200]}...")
        except Exception as e:
            print(f"❌ خطأ: {e}")

if __name__ == "__main__":
    asyncio.run(test_search())
