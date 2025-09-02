#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import sys
import os

# إضافة مسار app/backend للواردات
sys.path.append(os.path.join(os.path.dirname(__file__), 'app', 'backend'))

from azure.core.credentials import AzureKeyCredential
from azure.search.documents.aio import SearchClient
from ragtools import _search_tool

async def test_search_output():
    print("🧪 اختبار النتائج الجديدة...")
    
    # تحميل متغيرات البيئة
    from dotenv import load_dotenv
    env_path = os.path.join(os.path.dirname(__file__), 'app', 'backend', '.env')
    load_dotenv(env_path)
    
    # إعداد عميل البحث
    search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
    search_key = os.getenv("AZURE_SEARCH_API_KEY") 
    search_index = os.getenv("AZURE_SEARCH_INDEX", "new-circls-index")
    
    credential = AzureKeyCredential(search_key)
    search_client = SearchClient(search_endpoint, search_index, credential)
    
    # اختبار البحث مع add_to_order=False
    print("\n📋 اختبار البحث بدون إضافة للطلب:")
    args = {
        "query": "بيتزا فسفور",
        "add_to_order": False
    }
    
    result = await _search_tool(
        search_client=search_client,
        semantic_configuration=None,
        identifier_field="ID",
        content_field="ingredients", 
        embedding_field="",
        use_vector_query=False,
        args=args
    )
    
    print("النتيجة المُرسلة للموديل:")
    print("=" * 50)
    print(result.text)
    print("=" * 50)
    
    await search_client.close()

if __name__ == "__main__":
    asyncio.run(test_search_output())
