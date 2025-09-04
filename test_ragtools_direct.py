"""
اختبار مباشر لدالة البحث في ragtools
"""
import sys
import os
import asyncio

# إضافة مسار backend
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app', 'backend'))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), 'app', 'backend', '.env'))

# import ragtools
import importlib.util
spec = importlib.util.spec_from_file_location("ragtools", os.path.join(os.path.dirname(__file__), 'app', 'backend', 'ragtools.py'))
ragtools = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ragtools)

async def test_search_function():
    print("🧪 اختبار دالة البحث المباشرة من ragtools")
    print("="*60)
    
    # مسح الذاكرة المؤقتة أولاً
    ragtools.clear_cache()
    print("🗑️ تم مسح الذاكرة المؤقتة")
    
    test_queries = [
        "بيتزا تونة كبير",
        "onion rings", 
        "بيتزا سي فود وسط",
        "large tuna pizza",
        "medium seafood pizza"
    ]
    
    for query in test_queries:
        print(f"\n🔍 اختبار: {query}")
        try:
            # استدعاء دالة البحث مباشرة
            result = await ragtools.search_function(query, add_to_order=False)
            
            print(f"📤 النتيجة:")
            print("─" * 40)
            print(result.text)
            print("─" * 40)
            
        except Exception as e:
            print(f"❌ خطأ: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_search_function())
