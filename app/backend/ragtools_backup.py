import re
import sys
import os
from typing import Any

# إعداد الترميز للنصوص العربية
if sys.platform.startswith('win'):
    os.system('chcp 65001 > nul')  # تعيين UTF-8 code page

from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential
from azure.search.documents.aio import SearchClient
from azure.search.documents.models import VectorizableTextQuery

from rtmt import RTMiddleTier, Tool, ToolResult, ToolResultDirection
from order_manager import order_manager, OrderItem

# استيراد نظام الترجمة
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from translation_utils import translate_and_extract_for_search
from translation_settings import TranslationSettings

_search_tool_schema = {
    "type": "function",
    "name": "search",
    "description": "Use this tool to search for food items in the restaurant menu when the user wants to order. Always search before suggesting items.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query in any language (Arabic or English)"
            }
        },
        "required": ["query"]
    }
}

async def _search_tool(
    search_client: SearchClient,
    semantic_configuration: str,
    identifier_field: str,
    content_field: str,
    embedding_field: str,
    use_vector_query: bool,
    args: Any
) -> ToolResult:
    """أداة البحث مع دعم الترجمة والبحث الدلالي"""
    query = args.get("query", "")
    
    if not query:
        return ToolResult("❌ الرجاء إدخال كلمة للبحث", ToolResultDirection.TO_CLIENT)
    
    # ترجمة الاستعلام والاستخراج
    translation_result = translate_and_extract_for_search(query)
    
    print(f"🔍 البحث الأصلي: {translation_result['original']}")
    if translation_result['translation_enabled']:
        print(f"🌍 الترجمة الكاملة: {translation_result['full_translation']}")
        print(f"🎯 كلمات البحث: {translation_result['search_query']}")
    else:
        print(f"� نص البحث (عربي): {translation_result['search_query']}")
    print(f"�🔧 البحث الدلالي: {'مفعل' if semantic_configuration else 'معطل'}")
    print(f"⚙️ وضع الترجمة: {TranslationSettings.get_current_mode()}")
    
    # استخدام كلمات البحث المستخرجة
    search_query = translation_result['search_query']
    
    try:
        # استخدام البحث الدلالي إذا كان متاحاً
        if semantic_configuration:
            search_results = await search_client.search(
                search_text=search_query,
                query_type="semantic",
                semantic_configuration_name=semantic_configuration,
                top=5,
                select=f"{identifier_field},Name,{content_field},Price",
                search_fields=["Name", content_field],
                query_caption="extractive",
                query_answer="extractive"
            )
        else:
            search_results = await search_client.search(
                search_text=search_query,
                query_type="simple",
                top=5,
                select=f"{identifier_field},Name,{content_field},Price",
                search_fields=["Name", content_field]
            )
        
        docs = []
        async for r in search_results:
            identifier_value = r.get(identifier_field, "غير محدد")
            name_value = r.get("Name", "بدون اسم")
            content_field_value = r.get(content_field, "بدون وصف")
            price_value = r.get("Price", "غير محدد")
            search_score = r.get("@search.score", 0)
            reranker_score = r.get("@search.reranker_score", None)
            
            # إنشاء النتيجة
            result_item = {
                'ID': identifier_value,
                'Name': name_value,
                'ingredients': content_field_value,
                'Price': price_value,
                'search_score': search_score
            }
            
            if reranker_score is not None:
                result_item['semantic_score'] = reranker_score
            
            docs.append(result_item)
        
        if not docs:
            return ToolResult("❌ لم أجد أي عناصر تطابق بحثك. الرجاء المحاولة بكلمات أخرى.", ToolResultDirection.TO_CLIENT)
        
        # تنسيق النتائج للعرض
        result_text = f"🔍 نتائج البحث عن '{query}':\n"
        result_text += f"📝 الترجمة الكاملة: '{translation_result['full_translation']}'\n"
        result_text += f"🎯 كلمات البحث: '{search_query}'\n"
        result_text += f"🎯 تم العثور على {len(docs)} عنصر:\n\n"
        
        for i, doc in enumerate(docs, 1):
            result_text += f"🍔 {i}. {doc['Name']}\n"
            result_text += f"   💰 السعر: {doc['Price']} جنيه\n"
            result_text += f"   🥘 المكونات: {doc['ingredients'][:80]}...\n"
            result_text += f"   📊 درجة البحث: {doc['search_score']:.2f}"
            
            if 'semantic_score' in doc:
                result_text += f" | درجة دلالية: {doc['semantic_score']:.2f}"
            
            result_text += "\n\n"
        
        return ToolResult(result_text, ToolResultDirection.TO_CLIENT)
        
    except Exception as e:
        error_msg = f"❌ خطأ في البحث: {str(e)}"
        print(error_msg)
        return ToolResult(error_msg, ToolResultDirection.TO_CLIENT)

async def _report_grounding_tool(search_client: SearchClient, identifier_field: str, title_field: str, content_field: str, args: Any) -> None:
    """أداة التقرير (غير مستخدمة حالياً)"""
    query = args.get("query")
    if query:
        search_results = await search_client.search(
            query, 
            top=5,
            search_fields=[title_field, content_field],
            select=[identifier_field, title_field, content_field], 
        )
        
        docs = []
        async for r in search_results:
            docs.append({"ID": r[identifier_field], "Name": r[title_field], "ingredients": r[content_field]})

async def _show_all_tool(search_client: SearchClient, identifier_field: str, content_field: str) -> ToolResult:
    """عرض جميع العناصر المتاحة"""
    try:
        search_results = await search_client.search(
        search_text="*",
        top=50,
        select=f"{identifier_field},Name,{content_field},Price"
    )
    
        docs = []
        async for r in search_results:
            identifier_value = r.get(identifier_field, "غير محدد")
            name_value = r.get("Name", "بدون اسم")
            content_field_value = r.get(content_field, "بدون وصف")
            price_value = r.get("Price", "غير محدد")
            
            docs.append({
                'ID': identifier_value,
                'Name': name_value,
                'ingredients': content_field_value,
                'Price': price_value
            })
        
        if not docs:
            return ToolResult("❌ لم أجد أي عناصر في القائمة.", ToolResultDirection.TO_CLIENT)
        
        result_text = f"📋 قائمة الطعام الكاملة ({len(docs)} عنصر):\n\n"
        
        for i, doc in enumerate(docs, 1):
            result_text += f"🍔 {i}. {doc['Name']}\n"
            result_text += f"   💰 السعر: {doc['Price']} جنيه\n"
            result_text += f"   🥘 المكونات: {doc['ingredients'][:60]}...\n\n"
        
        return ToolResult(result_text, ToolResultDirection.TO_CLIENT)
        
    except Exception as e:
        error_msg = f"❌ خطأ في عرض القائمة: {str(e)}"
        print(error_msg)
        return ToolResult(error_msg, ToolResultDirection.TO_CLIENT)

def attach_rag_tools(
    rtmt: RTMiddleTier,
    credentials: AzureKeyCredential | DefaultAzureCredential,
    search_endpoint: str,
    search_index: str,
    semantic_configuration: str,
    identifier_field: str,
    content_field: str,
    embedding_field: str = "",
    title_field: str = "Name",
    use_vector_query: bool = False
):
    """ربط أدوات البحث بالنظام"""
    
    search_client = SearchClient(search_endpoint, search_index, credentials)
    
    print(f"🔧 إعداد أدوات البحث:")
    print(f"   البحث الدلالي: {'مفعل' if semantic_configuration else 'معطل'}")
    print(f"   التكوين: {semantic_configuration}")
    print(f"   الحقول: ID={identifier_field}, Name={title_field}, Content={content_field}")
    
    rtmt.tools["search"] = Tool(
        schema=_search_tool_schema, 
        target=lambda args: _search_tool(
            search_client, 
            semantic_configuration, 
            identifier_field, 
            content_field, 
            embedding_field, 
            use_vector_query, 
            args
        )
    )
    
    # أداة عرض جميع العناصر
    rtmt.tools["show_all"] = Tool(
        schema={
            "type": "function",
            "name": "show_all",
            "description": "Show all available food items in the menu",
            "parameters": {"type": "object", "properties": {}, "required": []}
        },
        target=lambda args: _show_all_tool(search_client, identifier_field, content_field)
    )
    
    print("✅ تم ربط أدوات البحث بنجاح")
