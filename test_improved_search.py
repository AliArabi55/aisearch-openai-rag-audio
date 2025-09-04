#!/usr/bin/env python3
"""
test_improved_search.py
🔍 اختبار البحث المحسن في Name و ingredients معاً
"""

import asyncio
import os
import sys
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

# إعداد الترميز للنصوص العربية
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

# تحميل متغيرات البيئة من مجلد app/backend
env_path = os.path.join(os.path.dirname(__file__), "app", "backend", ".env")
load_dotenv(env_path)

async def test_improved_search():
    """
    🔍 اختبار البحث المحسن
    """
    print("🔍 اختبار البحث المحسن (Name + ingredients)")
    print("=" * 60)
    
    # إعداد Azure Search
    search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
    search_key = os.getenv("AZURE_SEARCH_API_KEY")
    search_index = os.getenv("AZURE_SEARCH_INDEX")
    semantic_config = os.getenv("AZURE_SEARCH_SEMANTIC_CONFIGURATION")
    
    if not all([search_endpoint, search_key, search_index]):
        print("❌ متغيرات البيئة مفقودة!")
        return
    
    search_client = SearchClient(
        endpoint=search_endpoint,
        index_name=search_index,
        credential=AzureKeyCredential(search_key)
    )
    
    # عينات للاختبار
    test_samples = [
        "Chicken Pizza",      # يجب أن يجد بالاسم مباشرة
        "Large Chicken",      # يجب أن يجد بالاسم مباشرة
        "BBQ",               # يجب أن يجد بالاسم والمكونات
        "Seafood",           # يجب أن يجد بالاسم والمكونات
        "Double Burger",     # يجب أن يجد بالاسم
        "cheese bacon",      # يجب أن يجد بالمكونات
        "Crispy Chicken",    # يجب أن يجد بالاسم والمكونات
        "Ranch"              # يجب أن يجد بالمكونات والاسم
    ]
    
    for sample in test_samples:
        print(f"\n🔍 البحث عن: '{sample}'")
        print("-" * 40)
        
        try:
            # البحث الدلالي مع Name و ingredients
            results = search_client.search(
                search_text=sample,
                query_type="semantic",
                semantic_configuration_name=semantic_config,
                top=5,
                select="ID,Name,ingredients,Price",
                search_fields=["Name", "ingredients"],  # البحث في الحقلين معاً
                query_caption="extractive",
                query_answer="extractive"
            )
            
            found_any = False
            for i, result in enumerate(results, 1):
                found_any = True
                name = result.get("Name", "بدون اسم")
                price = result.get("Price", "غير محدد")
                ingredients = result.get("ingredients", "غير محدد")
                semantic_score = result.get("@search.reranker_score", 0)
                search_score = result.get("@search.score", 0)
                
                print(f"   {i}. {name}")
                print(f"      💰 السعر: {price} جنيه")
                print(f"      🥘 المكونات: {ingredients[:50]}...")
                print(f"      📊 النقاط الدلالية: {semantic_score:.2f}")
                print(f"      🔍 نقاط البحث: {search_score:.2f}")
                print()
            
            if not found_any:
                print("   ❌ لم يتم العثور على نتائج")
        
        except Exception as e:
            print(f"   ❌ خطأ: {str(e)}")
    
    print("\n" + "=" * 60)
    print("✅ اكتمل اختبار البحث المحسن!")

if __name__ == "__main__":
    asyncio.run(test_improved_search())
