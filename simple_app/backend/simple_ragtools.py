import os
import json
import logging
from typing import List, Any, Optional
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from datetime import datetime

logger = logging.getLogger(__name__)

class SimpleRAGTools:
    def __init__(self, search_client: SearchClient):
        self.search_client = search_client
        
    def search_food(self, query: str, add_to_order: bool = False) -> str:
        """البحث في قائمة الطعام"""
        try:
            print(f"🔍 البحث عن: {query}")
            
            # البحث بإستخدام Azure AI Search
            results = self.search_client.search(
                query,
                include_total_count=True,
                top=5,
                semantic_configuration_name=os.environ.get("AZURE_SEARCH_SEMANTIC_CONFIGURATION"),
                query_type="semantic"
            )
            
            items = []
            for result in results:
                name = result.get('Name', 'غير معروف')
                price = result.get('Price', 0)  # تغيير من 'price' إلى 'Price'
                ingredients = result.get('ingredients', '')
                
                print(f"📋 عنصر: {name}, السعر: {price}, المكونات: {ingredients}")
                
                # تنسيق النتيجة مع التأكيد على وجود السعر
                item_text = f"الاسم: {name}, السعر: {price} جنيه"
                if ingredients:
                    item_text += f", المكونات: {ingredients}"
                
                items.append(item_text)
            
            if items:
                result_text = "\n".join(items)
                print(f"✅ النتائج النهائية:\n{result_text}")
                return result_text
            else:
                return "عذراً، لم أجد أي نتائج لطلبك."
                
        except Exception as e:
            print(f"❌ خطأ في البحث: {e}")
            return f"حدث خطأ في البحث: {str(e)}"

def attach_simple_rag_tools(rtmt, credentials, search_endpoint: str, search_index: str):
    """ربط أدوات RAG المبسطة"""
    
    search_client = SearchClient(
        endpoint=search_endpoint,
        index_name=search_index,
        credential=credentials
    )
    
    rag_tools = SimpleRAGTools(search_client)
    
    # إضافة الأداة للبحث
    rtmt.tools["search"] = {
        "type": "function",
        "name": "search",
        "description": "البحث في قائمة الطعام",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "كلمة البحث"
                },
                "add_to_order": {
                    "type": "boolean",
                    "description": "هل تريد إضافة للطلب",
                    "default": False
                }
            },
            "required": ["query"]
        },
        "function": rag_tools.search_food
    }
    
    print("✅ تم ربط أدوات RAG المبسطة")
