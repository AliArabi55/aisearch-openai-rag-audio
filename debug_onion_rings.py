#!/usr/bin/env python3
"""
debug_onion_rings.py
🔍 تتبع مشكلة Onion Rings
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

async def debug_onion_rings():
    """
    🔍 تتبع مشكلة Onion Rings المحددة
    """
    print("🔍 تتبع مشكلة Onion Rings")
    print("=" * 60)
    
    # إعداد Azure Search
    search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
    search_key = os.getenv("AZURE_SEARCH_API_KEY")
    search_index = os.getenv("AZURE_SEARCH_INDEX")
    semantic_config = os.getenv("AZURE_SEARCH_SEMANTIC_CONFIGURATION")
    
    search_client = SearchClient(
        endpoint=search_endpoint,
        index_name=search_index,
        credential=AzureKeyCredential(search_key)
    )
    
    # البحث المباشر عن Onion Rings
    search_queries = [
        "Onion Rings",
        "Onion",
        "Rings", 
        "أونين رينجز",
        "اونين رينج",
        "حلقات البصل"
    ]
    
    for query in search_queries:
        print(f"\n🔍 البحث عن: '{query}'")
        print("-" * 40)
        
        try:
            # البحث الدلالي
            results = search_client.search(
                search_text=query,
                query_type="semantic",
                semantic_configuration_name=semantic_config,
                top=10,
                select="ID,Name,ingredients,Price",
                search_fields=["Name", "ingredients"]
            )
            
            found_any = False
            for i, result in enumerate(results, 1):
                found_any = True
                name = result.get("Name", "")
                price = result.get("Price", "")
                ingredients = result.get("ingredients", "")
                semantic_score = result.get("@search.reranker_score", 0)
                search_score = result.get("@search.score", 0)
                
                print(f"   {i}. {name}")
                print(f"      💰 السعر: {price} جنيه")
                print(f"      🥘 المكونات: {ingredients}")
                print(f"      📊 النقاط الدلالية: {semantic_score:.2f}")
                print(f"      🔍 نقاط البحث: {search_score:.2f}")
                
                # فحص مطابقة دقيقة
                if "Onion Rings" in name:
                    print("      ✅ مطابقة دقيقة للاسم!")
                elif "onion" in name.lower() and "ring" in name.lower():
                    print("      ⚠️ مطابقة جزئية للاسم")
                elif "onion" in ingredients.lower():
                    print("      🔍 موجود في المكونات")
                print()
            
            if not found_any:
                print("   ❌ لم يتم العثور على نتائج")
                
        except Exception as e:
            print(f"   ❌ خطأ: {str(e)}")
    
    # البحث المباشر في جميع العناصر
    print(f"\n📋 البحث في جميع العناصر عن 'Onion':")
    print("-" * 40)
    
    try:
        all_results = search_client.search(
            search_text="*",
            top=200,
            select="ID,Name,ingredients,Price"
        )
        
        onion_items = []
        for result in all_results:
            name = result.get("Name", "")
            ingredients = result.get("ingredients", "")
            
            if ("onion" in name.lower() or 
                "onion" in ingredients.lower() or
                "ring" in name.lower()):
                onion_items.append(result)
        
        print(f"📊 عدد العناصر التي تحتوي على 'onion': {len(onion_items)}")
        
        for item in onion_items:
            name = item.get("Name", "")
            price = item.get("Price", "")
            ingredients = item.get("ingredients", "")
            
            print(f"   • {name} - {price} جنيه")
            print(f"     المكونات: {ingredients}")
            
            if "Onion Rings" in name:
                print("     🎯 هذا هو Onion Rings!")
            print()
            
    except Exception as e:
        print(f"❌ خطأ في البحث الشامل: {str(e)}")
    
    print("\n✅ اكتمل التتبع!")

if __name__ == "__main__":
    asyncio.run(debug_onion_rings())
