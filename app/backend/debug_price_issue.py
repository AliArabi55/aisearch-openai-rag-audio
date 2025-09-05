#!/usr/bin/env python3
"""
فحص بيانات AI Search والتحقق من أسعار العناصر
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

# Load environment variables
current_dir = Path(__file__).parent
env_path = current_dir / ".env"
load_dotenv(env_path)

def check_search_data():
    """فحص بيانات البحث والأسعار"""
    
    # إعدادات Azure Search
    endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
    api_key = os.getenv("AZURE_SEARCH_API_KEY")
    index_name = os.getenv("AZURE_SEARCH_INDEX")
    
    if not all([endpoint, api_key, index_name]):
        print("❌ خطأ: معلومات Azure Search غير مكتملة")
        return
    
    try:
        # إنشاء SearchClient
        search_client = SearchClient(
            endpoint=endpoint,
            index_name=index_name,
            credential=AzureKeyCredential(api_key)
        )
        
        print("🔍 فحص البيانات في AI Search...")
        print("=" * 50)
        
        # البحث عن جميع العناصر
        results = search_client.search(
            search_text="*",
            top=10,
            select="ID,Name,ingredients,Price"
        )
        
        print("📊 العناصر الموجودة في قاعدة البيانات:")
        print("-" * 50)
        
        count = 0
        for result in results:
            count += 1
            id_val = result.get("ID", "غير محدد")
            name_val = result.get("Name", "غير محدد")
            price_val = result.get("Price", "غير محدد")
            ingredients_val = result.get("ingredients", "غير محدد")
            
            print(f"🔸 العنصر {count}:")
            print(f"   📌 ID: {id_val}")
            print(f"   🏷️ الاسم: {name_val}")
            print(f"   💰 السعر: {price_val} (نوع: {type(price_val)})")
            print(f"   🥘 المكونات: {ingredients_val}")
            print()
        
        if count == 0:
            print("❌ لا توجد عناصر في قاعدة البيانات")
        else:
            print(f"✅ تم العثور على {count} عنصر")
        
        # اختبار بحث محدد عن البيتزا
        print("\n" + "=" * 50)
        print("🧪 اختبار البحث عن 'بيتزا':")
        print("-" * 50)
        
        pizza_results = search_client.search(
            search_text="بيتزا",
            top=5,
            select="ID,Name,ingredients,Price"
        )
        
        for result in pizza_results:
            name_val = result.get("Name", "غير محدد")
            price_val = result.get("Price", "غير محدد")
            
            print(f"🍕 {name_val}")
            print(f"   💰 السعر: {price_val} (نوع: {type(price_val)})")
            print(f"   🔍 تحقق السعر: {price_val and str(price_val).strip() and str(price_val) != 'غير محدد'}")
            print()
            
    except Exception as e:
        print(f"❌ خطأ في الاتصال: {e}")

if __name__ == "__main__":
    check_search_data()
