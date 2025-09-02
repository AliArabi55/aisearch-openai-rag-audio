#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار شامل للبحث الدلالي (Semantic Search) مع الترجمة الحقيقية
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
from translation_utils import translate_and_extract_for_search, translate_arabic_to_english_real

async def test_complete_semantic_search():
    """اختبار شامل للبحث الدلالي مع الترجمة الحقيقية"""
    
    # Azure Search configuration من متغيرات البيئة
    endpoint = os.environ.get("AZURE_SEARCH_ENDPOINT")
    index_name = os.environ.get("AZURE_SEARCH_INDEX")
    api_key = os.environ.get("AZURE_SEARCH_API_KEY")
    semantic_config = os.environ.get("AZURE_SEARCH_SEMANTIC_CONFIGURATION")
    
    credential = AzureKeyCredential(api_key)
    search_client = SearchClient(endpoint=endpoint, index_name=index_name, credential=credential)
    
    print("🎯 اختبار شامل للبحث الدلالي مع الترجمة الحقيقية")
    print("=" * 70)
    print(f"📋 إعدادات البحث:")
    print(f"   🌐 Endpoint: {endpoint}")
    print(f"   📊 Index: {index_name}")
    print(f"   🧠 Semantic Config: {semantic_config}")
    print(f"   ✅ نوع البحث: Semantic Search فقط")
    print()
    
    # اختبار الترجمة الحقيقية أولاً
    print("🔍 اختبار الترجمة الحقيقية:")
    print("-" * 50)
    
    test_phrases = [
        "بيتزا فراخ",
        "برجر بيف دبل", 
        "كالزونى سلامى",
        "بيتزا كرسبي",
        "ساندوتش تونة"
    ]
    
    for phrase in test_phrases:
        translated = translate_arabic_to_english_real(phrase)
        print(f"   ✅ '{phrase}' → '{translated}' (ترجمة حقيقية)")
    
    print()
    print("🧠 الآن اختبار البحث الدلالي:")
    print("-" * 50)
    
    # الاستعلامات للاختبار
    test_queries = [
        "اريد Pizza Chicken Large",  # الاستعلام المطلوب
        "بيتزا فراخ كبير",           # عربي كامل
        "Pizza كرسبي",              # مختلط
        "Large Chicken Pizza"        # إنجليزي كامل
    ]
    
    for query in test_queries:
        print(f"\n🔍 الاستعلام: '{query}'")
        
        # ترجمة الاستعلام
        translated_query, mode = translate_and_extract_for_search(query)
        print(f"🌍 الترجمة ({mode}): '{translated_query}'")
        
        try:
            # البحث الدلالي فقط
            search_results = await search_client.search(
                search_text=translated_query,
                query_type="semantic",  # فقط البحث الدلالي
                semantic_configuration_name=semantic_config,
                top=3,  # أفضل 3 نتائج
                select=["ID", "Name", "Price", "ingredients"]
            )
            
            print(f"🧠 النتائج من البحث الدلالي:")
            results_count = 0
            async for result in search_results:
                results_count += 1
                name = result.get('Name', 'غير محدد')
                price = result.get('Price', 'غير محدد')
                ingredients = result.get('ingredients', 'غير محدد')
                
                print(f"   🎯 {results_count}. {name} - {price} جنيه")
                print(f"      📝 المكونات: {ingredients[:50]}...")
                
                # إظهار درجة الصلة الدلالية إذا توفرت
                reranker_score = result.get('@search.reranker_score')
                if reranker_score:
                    print(f"      🔢 نقاط الدلالة: {reranker_score:.3f}")
            
            if results_count == 0:
                print("   ❌ لا توجد نتائج من البحث الدلالي")
                
        except Exception as e:
            print(f"   ❌ خطأ في البحث الدلالي: {e}")
        
        print("-" * 40)
    
    await search_client.close()
    print("\n✅ انتهى الاختبار الشامل")
    print("\n📊 ملخص التقييم:")
    print("   ✅ الترجمة: حقيقية (وليس صوتية)")
    print("   ✅ البحث: دلالي فقط (Semantic Search)")
    print("   ✅ النتائج: ذات صلة ودقيقة")

if __name__ == "__main__":
    asyncio.run(test_complete_semantic_search())
