#!/usr/bin/env python3
"""
اختبار مباشر لإظهار ناتج البحث الدلالي بالضبط
"""
import sys
sys.path.append('app/backend')

import asyncio
import json
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from translation_utils import translate_arabic_to_english
import os

async def show_exact_search_output():
    """إظهار ناتج البحث الدلالي بالضبط كما يأتي من Azure"""
    
    print("🔍 البحث الدلالي المباشر لـ: 'اريد بيتزا تونة وسط'")
    print("=" * 60)
    
    # قراءة الإعدادات
    try:
        from dotenv import load_dotenv
        load_dotenv('app/backend/.env')
        
        search_endpoint = os.getenv('AZURE_SEARCH_ENDPOINT')
        search_key = os.getenv('AZURE_SEARCH_ADMIN_KEY')
        search_index = os.getenv('AZURE_SEARCH_INDEX')
        semantic_config = os.getenv('AZURE_SEARCH_SEMANTIC_CONFIGURATION')
        
        print(f"📋 إعدادات البحث:")
        print(f"   المؤشر: {search_index}")
        print(f"   التكوين الدلالي: {semantic_config}")
        
        # إنشاء العميل
        credentials = AzureKeyCredential(search_key)
        search_client = SearchClient(search_endpoint, search_index, credentials)
        
    except Exception as e:
        print(f"❌ خطأ في الإعداد: {e}")
        return
    
    # النص الأصلي
    original_query = "اريد بيتزا تونة وسط"
    print(f"\n🎯 النص الأصلي: '{original_query}'")
    
    # الترجمة
    try:
        translated_query = translate_arabic_to_english(original_query)
        print(f"🔄 النص المترجم: '{translated_query}'")
    except Exception as e:
        print(f"❌ خطأ في الترجمة: {e}")
        translated_query = original_query
    
    print(f"\n🔍 تنفيذ البحث الدلالي...")
    print("-" * 60)
    
    try:
        # تنفيذ البحث الدلالي بالضبط كما في ragtools
        search_results = search_client.search(
            search_text=translated_query,
            search_fields=["Name", "ingredients"],  # البحث في الاسم والمكونات
            select="ID,Name,ingredients,Price",
            query_type="semantic",
            semantic_configuration_name=semantic_config,
            query_caption="extractive",
            query_answer="extractive",
            top=5
        )
        
        print("📄 النتائج الخام من Azure AI Search:")
        print("=" * 60)
        
        result_count = 0
        all_results = []
        
        for doc in search_results:
            result_count += 1
            
            # تحويل النتيجة لقاموس للعرض
            result_dict = dict(doc)
            all_results.append(result_dict)
            
            print(f"\n--- النتيجة {result_count} ---")
            print(f"🆔 ID: {result_dict.get('ID', 'غير محدد')}")
            print(f"📝 Name: {result_dict.get('Name', 'غير محدد')}")
            print(f"🥗 ingredients: {result_dict.get('ingredients', 'غير محدد')}")
            print(f"💰 Price: {result_dict.get('Price', 'غير محدد')}")
            
            # النقاط (إذا كانت متوفرة)
            if '@search.score' in result_dict:
                print(f"📊 Search Score: {result_dict['@search.score']}")
            if '@search.reranker_score' in result_dict:
                print(f"🎯 Semantic Score: {result_dict['@search.reranker_score']}")
            if '@search.captions' in result_dict:
                print(f"📋 Captions: {result_dict['@search.captions']}")
        
        print(f"\n📊 ملخص النتائج:")
        print(f"   إجمالي النتائج: {result_count}")
        
        if result_count == 0:
            print("   ❌ لم يتم العثور على أي نتائج")
        else:
            print("   ✅ تم العثور على نتائج")
        
        # حفظ النتائج الخام في ملف JSON
        with open('raw_search_results.json', 'w', encoding='utf-8') as f:
            json.dump({
                'query': {
                    'original': original_query,
                    'translated': translated_query
                },
                'config': {
                    'search_fields': ['Name', 'ingredients'],
                    'query_type': 'semantic',
                    'semantic_configuration': semantic_config
                },
                'results': all_results,
                'total_count': result_count
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 تم حفظ النتائج الخام في: raw_search_results.json")
        
    except Exception as e:
        print(f"❌ خطأ في البحث: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(show_exact_search_output())
