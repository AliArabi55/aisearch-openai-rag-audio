#!/usr/bin/env python3
"""
فحص حقول الفهرس في Azure AI Search
"""

import os
import sys
from dotenv import load_dotenv
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

def inspect_index():
    """فحص حقول الفهرس"""
    
    # تحميل المتغيرات
    load_dotenv()
    
    print("🔍 فحص حقول الفهرس...")
    
    # إنشاء عميل البحث
    search_client = SearchClient(
        endpoint=os.environ.get("AZURE_SEARCH_ENDPOINT"),
        index_name=os.environ.get("AZURE_SEARCH_INDEX"),
        credential=AzureKeyCredential(os.environ.get("AZURE_SEARCH_API_KEY"))
    )
    
    try:
        # البحث عن أول عنصر وعرض جميع الحقول
        results = search_client.search("*", top=1, include_total_count=True)
        
        for result in results:
            print("\n📊 جميع الحقول المتاحة:")
            print("=" * 50)
            for key, value in result.items():
                print(f"  {key}: {value}")
            break
            
    except Exception as e:
        print(f"❌ خطأ: {e}")

if __name__ == "__main__":
    inspect_index()
