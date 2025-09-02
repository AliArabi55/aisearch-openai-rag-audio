#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app', 'backend'))

from ragtools import get_search_client

def test_search():
    print("🔍 Testing Azure AI Search...")
    try:
        search_client = get_search_client()
        
        # البحث عن جميع العناصر
        result = search_client.search("*", top=10)
        docs = list(result)
        
        print(f"✅ Total documents found: {len(docs)}")
        
        if docs:
            print("\n📋 Sample items:")
            for i, doc in enumerate(docs[:5]):
                name = doc.get('Name', 'Unknown')
                price = doc.get('Price', 'N/A')
                print(f"{i+1}. {name} - {price} جنيه")
        
        # البحث عن العدد الإجمالي
        total_result = search_client.search("*", top=200)
        total_docs = list(total_result)
        print(f"\n📊 Total items in database: {len(total_docs)}")
        
        return len(total_docs)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 0

if __name__ == "__main__":
    test_search()
