import asyncio
import json
import sys
from typing import Any
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorQuery
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential
from rtmt import ToolResult, ToolResultDirection, Tool, RTMiddleTier
from translation_utils import translate_and_extract_for_search
from translation_settings import TranslationSettings

# إعداد الترميز للنصوص العربية
if sys.platform.startswith('win'):
    import codecs
    codecs.register_error('ignore', codecs.ignore_errors)

# تعريف schema للأداة
_search_tool_schema = {
    "type": "function",
    "name": "search",
    "description": "البحث في قاعدة بيانات المطعم عن عناصر الطعام والمشروبات",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "كلمة أو جملة البحث (بالعربية أو الإنجليزية)"
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
    """
    أداة البحث الرئيسية
    """
    query = args.get("query", "")
    
    if not query:
        return ToolResult("❌ الرجاء إدخال كلمة للبحث", ToolResultDirection.TO_CLIENT)
    
    # ترجمة الاستعلام والاستخراج - التعامل مع الـ tuple المُعاد
    search_query, current_mode = translate_and_extract_for_search(query)
    translation_enabled = TranslationSettings.is_translation_enabled()
    
    print(f"🔍 البحث الأصلي: {query}")
    if translation_enabled:
        print(f"🎯 البحث بالإنجليزية: {search_query}")
    else:
        print(f"📝 البحث بالعربية: {search_query}")
    print(f"🔧 البحث الدلالي: {'مفعل' if semantic_configuration else 'معطل'}")
    print(f"⚙️ وضع الترجمة: {current_mode}")
    
    try:
        search_results = None
        search_successful_with_name = False
        
        # محاولة البحث مع حقل Name أولاً
        try:
            if semantic_configuration:
                search_results = search_client.search(
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
                search_results = search_client.search(
                    search_text=search_query,
                    query_type="simple",
                    top=5,
                    select=f"{identifier_field},Name,{content_field},Price",
                    search_fields=["Name", content_field]
                )
            
            # تجربة قراءة النتائج للتأكد من نجاح البحث
            results_list = list(search_results)
            search_results = results_list  # إعادة تعيين للاستخدام لاحقاً
            search_successful_with_name = True
            print("✅ البحث نجح مع حقل Name")
            
        except Exception as name_search_error:
            # إذا فشل البحث مع Name، حاول بدونه
            if "not searchable" in str(name_search_error):
                print("⚠️ حقل Name غير قابل للبحث، البحث بحقل ingredients فقط...")
                
                if semantic_configuration:
                    search_results = search_client.search(
                        search_text=search_query,
                        query_type="semantic",
                        semantic_configuration_name=semantic_configuration,
                        top=5,
                        select=f"{identifier_field},Name,{content_field},Price",
                        search_fields=[content_field],
                        query_caption="extractive",
                        query_answer="extractive"
                    )
                else:
                    search_results = search_client.search(
                        search_text=search_query,
                        query_type="simple",
                        top=5,
                        select=f"{identifier_field},Name,{content_field},Price",
                        search_fields=[content_field]
                    )
                print("✅ البحث نجح مع حقل ingredients فقط")
            else:
                # إذا كان خطأ آخر، ارمي الخطأ
                raise name_search_error
                        select=f"{identifier_field},Name,{content_field},Price",
                        search_fields=[content_field],
                        query_caption="extractive",
                        query_answer="extractive"
                    )
                else:
                    search_results = search_client.search(
                        search_text=search_query,
                        query_type="simple",
                        top=5,
                        select=f"{identifier_field},Name,{content_field},Price",
                        search_fields=[content_field]
                    )
                print("✅ البحث نجح مع حقل ingredients فقط")
            else:
                # إذا كان خطأ آخر، ارمي الخطأ
                raise name_search_error
        
        docs = []
        for r in search_results:
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
        if translation_enabled:
            result_text += f"🎯 البحث بالإنجليزية: '{search_query}'\n"
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

async def _show_all_tool(search_client: SearchClient, identifier_field: str, content_field: str) -> ToolResult:
    """عرض جميع العناصر المتاحة"""
    try:
        search_results = search_client.search(
            search_text="*",
            top=50,
            select=f"{identifier_field},Name,{content_field},Price"
        )
    
        docs = []
        for r in search_results:
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

async def _report_grounding_tool(search_client: SearchClient, identifier_field: str, title_field: str, content_field: str, args: Any) -> None:
    """أداة التقرير (غير مستخدمة حالياً)"""
    query = args.get("query")
    if query:
        search_results = search_client.search(
            query, 
            top=5,
            search_fields=[title_field, content_field],
            select=[identifier_field, title_field, content_field], 
        )
        
        docs = []
        for r in search_results:
            docs.append({"ID": r[identifier_field], "Name": r[title_field], "ingredients": r[content_field]})
