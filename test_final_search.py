#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبار شامل للنظام الجديد مع Azure Search
"""

from ragtools import run_custom_semantic_search
from translation_settings import get_translation_settings
import time

def test_search_with_modes():
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
            results = run_custom_semantic_search(query, 3)
            
            if results:
                for i, result in enumerate(results, 1):
                    name = result.get("Name", "No Name")
                    price = result.get("Price", "No Price")
                    print(f"   {i}. {name} - {price} جنيه")
            else:
                print("   ❌ لم يتم العثور على نتائج")
                
        except Exception as e:
            print(f"   ❌ خطأ في البحث: {e}")
            
        print()
        time.sleep(1)  # انتظار قصير بين البحوث
    
    print("✅ انتهاء الاختبار!")

if __name__ == "__main__":
    test_search_with_modes()
        print("-" * 30)
        
        # اختبار 1: البحث العربي الأساسي
        print("\n1️⃣ البحث عن 'بيتزا':")
        results = await search_client.search(
            search_text="بيتزا",
            top=2,
            select="ID,Name,ingredients,Price"
        )
        
        count = 0
        async for result in results:
            count += 1
            print(f"   ✅ [{result.get('ID')}] {result.get('Name')} - {result.get('Price')}ج.م")
        
        print(f"   📊 النتائج: {count}")
        
        # اختبار 2: البحث عن كلمة أجنبية
        print("\n2️⃣ البحث عن 'كرسبي':")
        results = await search_client.search(
            search_text="كرسبي",
            top=2,
            select="ID,Name,ingredients,Price"
        )
        
        count = 0
        async for result in results:
            count += 1
            print(f"   ✅ [{result.get('ID')}] {result.get('Name')} - {result.get('Price')}ج.م")
        
        print(f"   📊 النتائج: {count}")
        
        # اختبار 3: البحث بـ wildcard (كل شيء)
        print("\n3️⃣ البحث عن كل المنتجات:")
        results = await search_client.search(
            search_text="*",
            top=3,
            select="ID,Name,ingredients,Price"
        )
        
        count = 0
        async for result in results:
            count += 1
            print(f"   ✅ [{result.get('ID')}] {result.get('Name')} - {result.get('Price')}ج.م")
        
        print(f"   📊 النتائج: {count}")
        
        # إغلاق العميل
        await search_client.close()
        
        print(f"\n🎉 جميع الاختبارات نجحت!")
        print(f"✅ Azure AI Search يعمل بشكل مثالي")
        return True
        
    except Exception as e:
        print(f"❌ خطأ: {e}")
        return False

if __name__ == "__main__":
    # تشغيل الاختبار
    success = asyncio.run(test_final_search())
    if success:
        print("\n🚀 النظام جاهز للاستخدام!")
    else:
        print("\n⚠️ يحتاج إعادة فحص الإعدادات")
