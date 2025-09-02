#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import os
import sys
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.aio import SearchClient
from dotenv import load_dotenv

# تحميل المتغيرات البيئية
load_dotenv(os.path.join(os.path.dirname(__file__), 'app', 'backend', '.env'))

# إضافة مجلد backend للمسار
backend_path = os.path.join(os.path.dirname(__file__), 'app', 'backend')
sys.path.insert(0, backend_path)

from ragtools import translate_to_english

async def test_search_with_new_translations():
    """اختبار البحث الفعلي مع الترجمات الجديدة"""
    
    # إعداد Azure AI Search
    service_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
    index_name = os.getenv("AZURE_SEARCH_INDEX")
    key = os.getenv("AZURE_SEARCH_API_KEY")
    
    if not all([service_endpoint, index_name, key]):
        print("❌ متغيرات Azure Search غير متوفرة")
        return
    
    search_client = SearchClient(
        endpoint=service_endpoint,
        index_name=index_name,
        credential=AzureKeyCredential(key)
    )
    
    print("🧪 اختبار البحث الفعلي مع الترجمات الجديدة:")
    print("=" * 80)
    
    # الاستعلامات للاختبار
    test_queries = [
        "طبق اونيون رينج",
        "تشيزي كرسبي دبل", 
        "امريكان كرسبى دبل",
        "كريزي رانش كرسبى دبل",
        "فايبس كرسبى دبل",
        "جوسي كرسبى دبل",
        "ديلايت كرسبى دبل",
        "تيستي كرسبي دبل"
    ]
    
    for query in test_queries:
        print(f"\n🔍 اختبار البحث عن: '{query}'")
        
        # ترجمة الاستعلام
        translated_query = translate_to_english(query)
        print(f"🔄 الترجمة: '{query}' → '{translated_query}'")
        
        # البحث في Azure Search
        try:
            search_results = await search_client.search(
                search_text=translated_query,
                query_type="simple",
                top=3,
                select="ID,Name,ingredients,Price",
                search_mode="any"
            )
            
            result_count = 0
            async for result in search_results:
                result_count += 1
                print(f"📋 نتيجة {result_count}: ID={result.get('ID')}, Name={result.get('Name')}, Price={result.get('Price')}")
                print(f"   المكونات: {result.get('ingredients', 'غير محدد')}")
            
            if result_count == 0:
                print("❌ لم توجد نتائج")
            else:
                print(f"✅ وُجد {result_count} نتائج")
                
        except Exception as e:
            print(f"❌ خطأ في البحث: {e}")
    
    await search_client.close()
    print("\n" + "=" * 80)
    print("✅ انتهى اختبار البحث")

if __name__ == "__main__":
    print("🔄 بدء اختبار البحث الفعلي...")
    asyncio.run(test_search_with_new_translations())
