#!/usr/bin/env python3
"""
test_semantic_search.py - اختبار البحث الدلالي المباشر
Direct semantic search testing
"""

import asyncio
import json
import sys
import os
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.models import QueryType, VectorQuery

# إضافة مجلد backend للمسار
sys.path.append('.')

from translation_utils import translate_and_extract_for_search

async def test_semantic_search():
    """اختبار البحث الدلالي لبيتزا سيفود"""
    
    # إعداد البحث
    search_endpoint = ""
    search_key = ""
    search_index = "english22-index"
    semantic_config = "english22-index-semantic-configuration"
    
    print("🔍 اختبار البحث الدلالي لـ: 'بيتزا سيفود كبير'")
    print("=" * 60)
    
    # إنشاء client البحث
    search_client = SearchClient(
        endpoint=search_endpoint,
        index_name=search_index,
        credential=AzureKeyCredential(search_key)
    )
    
    # الاستعلام الأصلي
    original_query = "بيتزا سيفود كبير"
    print(f"📝 الطلب الأصلي: {original_query}")
    
    # ترجمة الاستعلام
    translated_query, method = translate_and_extract_for_search(original_query)
    print(f"🔄 الاستعلام المترجم: {translated_query}")
    print(f"📊 طريقة الترجمة: {method}")
    print()
    
    # إجراء البحث الدلالي
    try:
        print("🚀 إجراء البحث الدلالي...")
        
        # البحث بـ Semantic Search
        semantic_results = search_client.search(
            search_text=translated_query,
            top=10,
            query_type=QueryType.SEMANTIC,
            semantic_configuration_name=semantic_config,
            select=["ID", "Name", "ingredients", "Price"]
        )
        
        print("📋 نتائج البحث الدلالي:")
        print("-" * 40)
        
        found_items = []
        for i, result in enumerate(semantic_results, 1):
            item_id = result.get("ID", "غير محدد")
            name = result.get("Name", "غير محدد")
            ingredients = result.get("ingredients", "غير محدد")
            price = result.get("Price", "غير محدد")
            search_score = result.get("@search.score", 0)
            reranker_score = result.get("@search.reranker_score", None)
            
            print(f"  {i}. {name}")
            print(f"     💰 السعر: {price}")
            print(f"     🧊 المكونات: {ingredients}")
            print(f"     📊 Search Score: {search_score:.4f}")
            
            if reranker_score:
                print(f"     🎯 Semantic Score: {reranker_score:.4f}")
            
            print(f"     🔑 ID: {item_id}")
            print()
            
            found_items.append({
                'ID': item_id,
                'Name': name,
                'ingredients': ingredients,
                'Price': price,
                'search_score': search_score,
                'semantic_score': reranker_score
            })
        
        # فحص النتائج
        print("🎯 تحليل النتائج:")
        print("-" * 30)
        
        seafood_found = False
        large_found = False
        
        for item in found_items:
            name_lower = item['Name'].lower()
            ingredients_lower = item['ingredients'].lower()
            
            # فحص وجود سيفود
            if any(seafood in name_lower or seafood in ingredients_lower 
                   for seafood in ['seafood', 'سيفود', 'جمبري', 'shrimp', 'calamari', 'fish']):
                seafood_found = True
                print(f"✅ وجد سيفود: {item['Name']}")
            
            # فحص وجود كبير
            if any(size in name_lower 
                   for size in ['large', 'كبير', 'لارج', 'big']):
                large_found = True
                print(f"✅ وجد مقاس كبير: {item['Name']}")
        
        if not seafood_found:
            print("❌ لم يتم العثور على بيتزا سيفود")
        
        if not large_found:
            print("❌ لم يتم العثور على مقاس كبير")
        
        # اختبار البحث العادي للمقارنة
        print("\n" + "=" * 60)
        print("🔍 مقارنة بالبحث العادي:")
        
        regular_results = search_client.search(
            search_text=translated_query,
            top=5,
            select=["ID", "Name", "ingredients", "Price"]
        )
        
        print("📋 نتائج البحث العادي:")
        for i, result in enumerate(regular_results, 1):
            name = result.get("Name", "غير محدد")
            price = result.get("Price", "غير محدد")
            search_score = result.get("@search.score", 0)
            
            print(f"  {i}. {name} - {price} - Score: {search_score:.4f}")
        
        return found_items
        
    except Exception as e:
        print(f"❌ خطأ في البحث: {e}")
        return []

async def test_price_extraction():
    """اختبار استخراج السعر"""
    
    # محاكاة نتيجة البحث
    mock_result = {
        'ID': 'test_123',
        'Name': 'Large Seafood Pizza',
        'ingredients': 'Shrimp, calamari, fish, cheese, tomato sauce',
        'Price': '250'  # سعر كسلسلة نصية
    }
    
    print("\n" + "=" * 60)
    print("💰 اختبار استخراج السعر:")
    print("-" * 30)
    
    price_str = mock_result.get('Price', '0')
    print(f"📝 السعر الأصلي: '{price_str}'")
    
    # تنظيف السعر
    import re
    clean_price = re.sub(r'[^\d.]', '', str(price_str))
    price_float = float(clean_price) if clean_price else 0
    
    print(f"🧹 السعر منظف: '{clean_price}'")
    print(f"🔢 السعر كرقم: {price_float}")
    
    # محاكاة إرسال للموديل
    model_input = f"""
إليك نتائج البحث:
الاسم: {mock_result['Name']}
السعر: {price_float} جنيه
المكونات: {mock_result['ingredients']}

هذا هو السعر الذي يجب أن يستخدمه الموديل: {price_float} جنيه
"""
    
    print("\n📤 البيانات المرسلة للموديل:")
    print(model_input)
    
    return price_float

if __name__ == "__main__":
    print("🎯 بدء اختبار النظام الكامل")
    print("=" * 60)
    
    # تشغيل الاختبارات
    asyncio.run(test_semantic_search())
    asyncio.run(test_price_extraction())
    
    print("\n" + "=" * 60)
    print("✅ انتهى الاختبار")
