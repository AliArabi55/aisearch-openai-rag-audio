#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبار البحث باللغة العربية مع Azure AI Search
"""

import asyncio
import sys
import os
sys.path.append('app/backend')

from dotenv import load_dotenv
from azure.search.documents.aio import SearchClient
from azure.core.credentials import AzureKeyCredential
from translation_utils import translate_and_extract_for_search

load_dotenv('app/backend/.env')

async def test_arabic_search():
    """اختبار البحث باللغة العربية"""
    
    print("🔍 اختبار البحث باللغة العربية مع Azure AI Search")
    print("=" * 60)
    
    # إعداد Azure Search
    search_endpoint = os.environ.get("AZURE_SEARCH_ENDPOINT")
    search_key = os.environ.get("AZURE_SEARCH_API_KEY") 
    search_index = os.environ.get("AZURE_SEARCH_INDEX")
    
    print(f"📋 إعدادات البحث:")
    print(f"   Endpoint: {search_endpoint}")
    print(f"   Index: {search_index}")
    print()
    
    search_client = SearchClient(
        endpoint=search_endpoint,
        index_name=search_index,
        credential=AzureKeyCredential(search_key)
    )
    
    # الاستعلامات العربية للاختبار
    arabic_queries = [
        "اريد بيتزا فراخ كبير",
        "عايز برجر بيف دبل",
        "هات كالزونى سلامى",
        "اطلب بيتزا هوت دوج وسط",
        "بيتزا كرسبي",
        "برجر امريكان",
        "كالزونى سجق"
    ]
    
    for query in arabic_queries:
        print(f"🔍 الاستعلام العربي: {query}")
        
        # ترجمة الاستعلام
        translated_query, mode = translate_and_extract_for_search(query)
        print(f"🌍 الترجمة ({mode}): {translated_query}")
        
        try:
            # البحث في Azure Search (بدون تحديد search_fields)
            search_results = await search_client.search(
                search_text=translated_query,
                top=3,
                select=["ID", "Name", "Price", "ingredients"]
            )
            
            print("📊 النتائج:")
            results_count = 0
            async for result in search_results:
                results_count += 1
                print(f"   {results_count}. {result['Name']} - {result['Price']} جنيه")
                print(f"      المكونات: {result['ingredients'][:50]}...")
            
            if results_count == 0:
                print("   ❌ لا توجد نتائج")
                
        except Exception as e:
            print(f"   ❌ خطأ في البحث: {e}")
        
        print("-" * 50)
    
    await search_client.close()
    print("✅ انتهى الاختبار")

if __name__ == "__main__":
    asyncio.run(test_arabic_search())
