#!/usr/bin/env python3
"""
أداة اختبار مبسطة للتحقق من عمل Azure AI Search
"""

import os
import sys
from dotenv import load_dotenv
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

def test_search():
    """اختبار البحث في Azure AI Search"""
    
    # تحميل المتغيرات
    load_dotenv()
    
    print("🔍 اختبار Azure AI Search...")
    print(f"🔗 Endpoint: {os.environ.get('AZURE_SEARCH_ENDPOINT')}")
    print(f"📊 Index: {os.environ.get('AZURE_SEARCH_INDEX')}")
    
    # إنشاء عميل البحث
    search_client = SearchClient(
        endpoint=os.environ.get("AZURE_SEARCH_ENDPOINT"),
        index_name=os.environ.get("AZURE_SEARCH_INDEX"),
        credential=AzureKeyCredential(os.environ.get("AZURE_SEARCH_API_KEY"))
    )
    
    # اختبار البحث
    queries = [
        "tuna pizza medium",
        "بيتزا تونة وسط",
        "burger",
        "برجر"
    ]
    
    for query in queries:
        print(f"\n📝 البحث عن: '{query}'")
        print("=" * 50)
        
        try:
            results = search_client.search(
                query,
                include_total_count=True,
                top=3,
                semantic_configuration_name=os.environ.get("AZURE_SEARCH_SEMANTIC_CONFIGURATION"),
                query_type="semantic"
            )
            
            count = 0
            for result in results:
                count += 1
                name = result.get('Name', 'غير معروف')
                price = result.get('Price', 'غير متاح')  # تغيير من 'price' إلى 'Price'
                ingredients = result.get('ingredients', '')
                
                print(f"  📋 النتيجة {count}:")
                print(f"     الاسم: {name}")
                print(f"     السعر: {price} جنيه")
                print(f"     المكونات: {ingredients}")
                print()
            
            if count == 0:
                print("  ❌ لا توجد نتائج")
                
        except Exception as e:
            print(f"  ❌ خطأ: {e}")

if __name__ == "__main__":
    test_search()
