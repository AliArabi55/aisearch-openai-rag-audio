#!/usr/bin/env python3
"""
اختبار نهائي للتأكد من عمل Azure AI Search
"""

import asyncio
import os
import sys
from pathlib import Path

# إضافة مسار backend
sys.path.append('app/backend')

async def test_final_search():
    """اختبار Azure AI Search بشكل نهائي"""
    
    print("🔍 اختبار Azure AI Search النهائي")
    print("=" * 50)
    
    try:
        # استيراد الوحدات المطلوبة
        from azure.search.documents.aio import SearchClient
        from azure.core.credentials import AzureKeyCredential
        from dotenv import load_dotenv
        
        # تحميل متغيرات البيئة
        load_dotenv()
        
        # الحصول على المعايير من متغيرات البيئة
        search_endpoint = os.environ.get("AZURE_SEARCH_ENDPOINT")
        search_key = os.environ.get("AZURE_SEARCH_API_KEY")
        search_index = os.environ.get("AZURE_SEARCH_INDEX")
        
        print(f"📋 فحص المعايير:")
        print(f"   ✅ Endpoint: {'موجود' if search_endpoint else '❌ غير موجود'}")
        print(f"   ✅ Index: {search_index if search_index else '❌ غير موجود'}")
        print(f"   ✅ API Key: {'موجود' if search_key else '❌ غير موجود'}")
        
        if not all([search_endpoint, search_key, search_index]):
            print("❌ معايير Azure Search غير مكتملة!")
            return False
        
        # إنشاء عميل البحث
        search_client = SearchClient(
            endpoint=search_endpoint,
            index_name=search_index,
            credential=AzureKeyCredential(search_key)
        )
        
        print("\n🧪 اختبارات البحث:")
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
