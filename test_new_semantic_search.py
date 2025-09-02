#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار البحث الدلالي (Semantic Search) مع Azure AI Search
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

async def test_semantic_search():
    """اختبار البحث الدلالي مع Azure AI Search"""
    
    # Azure Search configuration من متغيرات البيئة
    endpoint = os.environ.get("AZURE_SEARCH_ENDPOINT")
    index_name = os.environ.get("AZURE_SEARCH_INDEX")
    api_key = os.environ.get("AZURE_SEARCH_API_KEY")
    semantic_config = os.environ.get("AZURE_SEARCH_SEMANTIC_CONFIGURATION")
    
    credential = AzureKeyCredential(api_key)
    search_client = SearchClient(endpoint=endpoint, index_name=index_name, credential=credential)
    
    print("🔍 اختبار البحث الدلالي (Semantic Search)")
    print("=" * 60)
    print(f"📋 إعدادات البحث:")
    print(f"   Endpoint: {endpoint}")
    print(f"   Index: {index_name}")
    print(f"   Semantic Config: {semantic_config}")
    print(f"   نوع البحث: Semantic Configuration")
    print()
    
    # الاستعلام المطلوب للاختبار
    test_query = "اريد Pizza Chicken Large"
    
    print(f"🔍 الاستعلام: {test_query}")
    
    # ترجمة الاستعلام
    translated_query, mode = translate_and_extract_for_search(test_query)
    print(f"🌍 الترجمة ({mode}): {translated_query}")
    
    try:
        # البحث الدلالي في Azure Search
        print("🧠 البحث باستخدام Semantic Configuration...")
        
        # استخدام البحث الدلالي
        search_results = await search_client.search(
            search_text=translated_query,
            query_type="semantic",  # تفعيل البحث الدلالي
            semantic_configuration_name=semantic_config,  # اسم التكوين الدلالي
            top=5,
            select=["ID", "Name", "Price", "ingredients"],
            query_caption="extractive",  # استخراج الملخص
            query_answer="extractive"    # استخراج الإجابة
        )
        
        print("📊 النتائج من البحث الدلالي:")
        results_count = 0
        async for result in search_results:
            results_count += 1
            name = result.get('Name', 'غير محدد')
            price = result.get('Price', 'غير محدد')
            ingredients = result.get('ingredients', 'غير محدد')
            
            print(f"   🎯 {results_count}. {name} - {price} جنيه")
            print(f"      📝 المكونات: {ingredients[:60]}...")
            
            # إظهار النتيجة الدلالية إذا كانت متوفرة
            if hasattr(result, '@search.reranker_score'):
                score = getattr(result, '@search.reranker_score', 'N/A')
                print(f"      🔢 نقاط الدلالة: {score}")
        
        if results_count == 0:
            print("   ❌ لا توجد نتائج من البحث الدلالي")
            print("   💡 سأجرب البحث العادي...")
            
            # البحث العادي كبديل
            search_results = await search_client.search(
                search_text=translated_query,
                top=3,
                select=["ID", "Name", "Price", "ingredients"]
            )
            
            print("📊 النتائج من البحث العادي:")
            async for result in search_results:
                results_count += 1
                name = result.get('Name', 'غير محدد')
                price = result.get('Price', 'غير محدد')
                ingredients = result.get('ingredients', 'غير محدد')
                print(f"   {results_count}. {name} - {price} جنيه")
                print(f"      المكونات: {ingredients[:50]}...")
                
    except Exception as e:
        print(f"   ❌ خطأ في البحث الدلالي: {e}")
        print("   💡 سأجرب البحث العادي...")
        
        try:
            # البحث العادي كبديل
            search_results = await search_client.search(
                search_text=translated_query,
                top=3,
                select=["ID", "Name", "Price", "ingredients"]
            )
            
            print("📊 النتائج من البحث العادي:")
            results_count = 0
            async for result in search_results:
                results_count += 1
                name = result.get('Name', 'غير محدد')
                price = result.get('Price', 'غير محدد')
                ingredients = result.get('ingredients', 'غير محدد')
                print(f"   {results_count}. {name} - {price} جنيه")
                print(f"      المكونات: {ingredients[:50]}...")
                
        except Exception as fallback_error:
            print(f"   ❌ خطأ في البحث العادي أيضاً: {fallback_error}")
    
    await search_client.close()
    print("\n✅ انتهى اختبار البحث الدلالي")

if __name__ == "__main__":
    asyncio.run(test_semantic_search())
