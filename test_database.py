#!/usr/bin/env python3
"""
اختبار بسيط لقاعدة البيانات
"""
import os
import asyncio
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

load_dotenv()

async def test_database():
    """اختبار محتوى قاعدة البيانات"""
    
    search_client = SearchClient(
        endpoint=os.environ['AZURE_SEARCH_ENDPOINT'],
        index_name=os.environ['AZURE_SEARCH_INDEX_NAME'],
        credential=AzureKeyCredential(os.environ['AZURE_SEARCH_API_KEY'])
    )
    
    print("🔍 اختبار محتوى قاعدة البيانات")
    print("="*50)
    
    # البحث عن جميع العناصر
    try:
        results = search_client.search('*', top=10)
        results_list = list(results)
        print(f"📊 عدد العناصر: {len(results_list)}")
        
        if results_list:
            print("\n📋 أول 5 عناصر:")
            for i, item in enumerate(results_list[:5], 1):
                name = item.get("Name", "غير محدد")
                price = item.get("Price", "غير محدد") 
                ingredients = item.get("ingredients", "غير محدد")
                print(f"  {i}. {name} - {price}")
                print(f"     المكونات: {ingredients[:50]}...")
                print()
        
        # اختبار البحث عن pizza
        print("🍕 البحث عن 'pizza':")
        pizza_results = search_client.search('pizza', top=3)
        pizza_list = list(pizza_results)
        print(f"   عدد النتائج: {len(pizza_list)}")
        for item in pizza_list:
            print(f"   - {item.get('Name', 'غير محدد')}")
            
        # اختبار البحث عن tuna
        print("\n🐟 البحث عن 'tuna':")
        tuna_results = search_client.search('tuna', top=3)
        tuna_list = list(tuna_results)
        print(f"   عدد النتائج: {len(tuna_list)}")
        for item in tuna_list:
            print(f"   - {item.get('Name', 'غير محدد')}")
            
    except Exception as e:
        print(f"❌ خطأ: {e}")

if __name__ == "__main__":
    asyncio.run(test_database())
