#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار البحث الدلالي للاستعلام: اريد بيتزا فراخ كبير
"""

import asyncio
from azure.search.documents.aio import SearchClient
from azure.core.credentials import AzureKeyCredential
import sys
import os
from dotenv import load_dotenv

# إضافة المجلد الحالي للمسار
sys.path.append(os.path.dirname(__file__))

# تحميل متغيرات البيئة
load_dotenv('app/backend/.env')

# استيراد أدوات الترجمة
from translation_utils import translate_and_extract_for_search

async def test_specific_query():
    """اختبار استعلام محدد مع البحث الدلالي"""
    
    # Azure Search configuration من متغيرات البيئة
    endpoint = os.environ.get("AZURE_SEARCH_ENDPOINT")
    index_name = os.environ.get("AZURE_SEARCH_INDEX")
    api_key = os.environ.get("AZURE_SEARCH_API_KEY")
    semantic_config = os.environ.get("AZURE_SEARCH_SEMANTIC_CONFIGURATION")
    
    credential = AzureKeyCredential(api_key)
    search_client = SearchClient(endpoint=endpoint, index_name=index_name, credential=credential)
    
    print("🎯 اختبار البحث الدلالي للاستعلام: اريد بيتزا فراخ كبير")
    print("=" * 70)
    print(f"📋 إعدادات البحث:")
    print(f"   🌐 Endpoint: {endpoint}")
    print(f"   📊 Index: {index_name}")
    print(f"   🧠 Semantic Config: {semantic_config}")
    print()
    
    # الاستعلام المطلوب
    query = "اريد بيتزا فراخ كبير"
    
    print(f"🔍 الاستعلام: '{query}'")
    
    # ترجمة الاستعلام
    translated_query, mode = translate_and_extract_for_search(query)
    print(f"🌍 الترجمة ({mode}): '{translated_query}'")
    print()
    
    try:
        # البحث الدلالي
        search_results = await search_client.search(
            search_text=translated_query,
            query_type="semantic",  # البحث الدلالي
            semantic_configuration_name=semantic_config,
            top=5,  # أفضل 5 نتائج
            select=["ID", "Name", "Price", "ingredients"]
        )
        
        print(f"🧠 النتائج من البحث الدلالي:")
        print("-" * 50)
        
        results_count = 0
        async for result in search_results:
            results_count += 1
            name = result.get('Name', 'غير محدد')
            price = result.get('Price', 'غير محدد')
            ingredients = result.get('ingredients', 'غير محدد')
            id_val = result.get('ID', 'غير محدد')
            
            print(f"🎯 {results_count}. ID: {id_val} | {name} - {price} جنيه")
            print(f"    📝 المكونات: {ingredients}")
            
            # إظهار درجة الصلة الدلالية
            reranker_score = result.get('@search.reranker_score')
            if reranker_score:
                print(f"    🔢 نقاط الدلالة: {reranker_score:.3f}")
            print()
        
        if results_count == 0:
            print("❌ لا توجد نتائج من البحث الدلالي")
            
    except Exception as e:
        print(f"❌ خطأ في البحث الدلالي: {e}")
    
    await search_client.close()
    print("✅ انتهى الاختبار")

if __name__ == "__main__":
    asyncio.run(test_specific_query())
