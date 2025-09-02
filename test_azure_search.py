#!/usr/bin/env python3

import asyncio
import os
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.aio import SearchClient

async def test_azure_search():
    # قراءة بيانات البيئة
    search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
    search_key = os.getenv("AZURE_SEARCH_API_KEY") 
    search_index = os.getenv("AZURE_SEARCH_INDEX", "new-circls-index")
    
    print(f"🔍 Testing Azure AI Search...")
    print(f"Endpoint: {search_endpoint}")
    print(f"Index: {search_index}")
    
    if not search_endpoint or not search_key:
        print("❌ Missing Azure Search credentials")
        return
    
    # إنشاء عميل البحث
    credential = AzureKeyCredential(search_key)
    search_client = SearchClient(search_endpoint, search_index, credential)
    
    try:
        # البحث عن جميع العناصر
        result = await search_client.search("*", top=200)
        docs = []
        async for doc in result:
            docs.append(doc)
        
        print(f"✅ Total items in database: {len(docs)}")
        
        if docs:
            print("\n📋 Sample items:")
            for i, doc in enumerate(docs[:5]):
                name = doc.get('Name', 'Unknown')
                price = doc.get('Price', 'N/A')
                print(f"{i+1}. {name} - {price} جنيه")
        
        # اختبار البحث بالعربية
        print(f"\n🔍 Testing Arabic search...")
        arabic_result = await search_client.search("بيتزا", top=3)
        arabic_docs = []
        async for doc in arabic_result:
            arabic_docs.append(doc)
        
        print(f"Found {len(arabic_docs)} pizza items")
        for doc in arabic_docs[:2]:
            print(f"- {doc.get('Name', 'Unknown')}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await search_client.close()

if __name__ == "__main__":
    # تحميل متغيرات البيئة
    from dotenv import load_dotenv
    
    # تحميل من مجلد app/backend
    env_path = os.path.join(os.path.dirname(__file__), 'app', 'backend', '.env')
    load_dotenv(env_path)
    
    asyncio.run(test_azure_search())
