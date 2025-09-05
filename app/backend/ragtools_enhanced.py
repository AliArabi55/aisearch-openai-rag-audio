#!/usr/bin/env python3
"""
ragtools.py محسن مع تتبع تفصيلي لكل خطوة
Enhanced ragtools.py with detailed step-by-step tracking
"""
import asyncio
import json
import sys
from typing import Any, Dict, List
from datetime import datetime, timedelta
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorQuery
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential
from rtmt import ToolResult, ToolResultDirection, Tool, RTMiddleTier
from translation_utils import translate_and_extract_for_search
from model_input_settings import ModelInputSettings, generate_model_input

# إصلاح خاص لترجمة أونين رينجز
def fix_onion_rings_translation(text):
    """إصلاح خاص لترجمة أونين رينجز والمصطلحات المشابهة"""
    
    # قاموس إصلاح سريع
    onion_fixes = {
        "أونين رينجز": "Onion Rings",
        "اونين رينجز": "Onion Rings", 
        "أونيان رينجز": "Onion Rings",
        "اونيان رينجز": "Onion Rings",
        "حلقات البصل": "Onion Rings",
        "حلقات بصل": "Onion Rings"
    }
    
    text = text.strip()
    
    # فحص مباشر للترجمة الخاصة
    if text in onion_fixes:
        return onion_fixes[text], "ترجمة محسنة لأونين رينجز"
    
    # ترجمة عامة
    return translate_and_extract_for_search(text)

# إعداد الترميز للنصوص العربية
if sys.platform.startswith('win'):
    import codecs
    codecs.register_error('ignore', codecs.ignore_errors)

# 🧠 ذاكرة مؤقتة عامة لحفظ نتائج البحث - 5 دقائق فقط
SEARCH_CACHE = {}
CACHE_EXPIRY_MINUTES = 5

def get_cache_key(query: str) -> str:
    """إنشاء مفتاح للذاكرة المؤقتة"""
    return f"search_{query.lower().strip()}"

def is_cache_valid(timestamp: datetime) -> bool:
    """فحص صحة الذاكرة المؤقتة"""
    return datetime.now() - timestamp < timedelta(minutes=CACHE_EXPIRY_MINUTES)

def get_from_cache(query: str) -> Dict:
    """استرجاع من الذاكرة المؤقتة"""
    cache_key = get_cache_key(query)
    if cache_key in SEARCH_CACHE:
        cached_data = SEARCH_CACHE[cache_key]
        if is_cache_valid(cached_data['timestamp']):
            print("🧠 استرجاع من الذاكرة المؤقتة")
            return cached_data['data']
        else:
            # حذف البيانات المنتهية الصلاحية
            del SEARCH_CACHE[cache_key]
    return None

def save_to_cache(query: str, data: Dict):
    """حفظ في الذاكرة المؤقتة"""
    cache_key = get_cache_key(query)
    SEARCH_CACHE[cache_key] = {
        'data': data,
        'timestamp': datetime.now()
    }
    print("💾 تم حفظ النتائج في الذاكرة المؤقتة")

def clear_cache():
    """حذف جميع البيانات من الذاكرة المؤقتة - يستخدم عند انتهاء المكالمة"""
    global SEARCH_CACHE
    SEARCH_CACHE.clear()
    print("🗑️ تم حذف الذاكرة المؤقتة")

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

# 🆕 schema لأداة السؤال عن المكونات
_ingredients_tool_schema = {
    "type": "function",
    "name": "get_ingredients",
    "description": "الحصول على مكونات طبق معين من الذاكرة المؤقتة",
    "parameters": {
        "type": "object",
        "properties": {
            "item_name": {
                "type": "string",
                "description": "اسم الطبق المراد معرفة مكوناته"
            }
        },
        "required": ["item_name"]
    }
}

async def _search_tool_enhanced(
    search_client: SearchClient,
    semantic_configuration: str,
    identifier_field: str,
    content_field: str,
    embedding_field: str,
    use_vector_query: bool,
    args: Any
) -> ToolResult:
    """
    أداة البحث المحسنة مع تتبع مفصل لكل خطوة
    """
    query = args.get("query", "")
    
    if not query:
        return ToolResult("❌ الرجاء إدخال كلمة للبحث", ToolResultDirection.TO_CLIENT)
    
    print(f"\n{'='*60}")
    print(f"🎯 بداية عملية البحث التفصيلية")
    print(f"{'='*60}")
    
    # الخطوة 1: إظهار الطلب الأصلي
    print(f"📝 الخطوة 1: الطلب الأصلي المُدخل بالعربي")
    print(f"   النص الأصلي: '{query}'")
    print(f"   نوع النص: {type(query)}")
    print(f"   عدد الأحرف: {len(query)}")
    
    # الخطوة 2: ترجمة النص
    print(f"\n🌍 الخطوة 2: ترجمة النص")
    search_query, current_mode = fix_onion_rings_translation(query)
    print(f"   النص بعد الترجمة: '{search_query}'")
    print(f"   طريقة الترجمة: {current_mode}")
    print(f"   نوع النص المترجم: {type(search_query)}")
    
    # الخطوة 3: إعداد البحث
    print(f"\n🔧 الخطوة 3: إعداد البحث في Azure AI Search")
    print(f"   البحث الدلالي: {'مفعل' if semantic_configuration else 'معطل'}")
    print(f"   التكوين الدلالي: {semantic_configuration}")
    print(f"   حقول البحث: Name, {content_field}")
    print(f"   عدد النتائج المطلوبة: 5")
    
    try:
        # الخطوة 4: تنفيذ البحث
        print(f"\n🔍 الخطوة 4: تنفيذ البحث في Azure")
        search_results = None
        
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
        
        # تحويل النتائج إلى قائمة
        results_list = list(search_results)
        print(f"   ✅ البحث نجح - تم العثور على {len(results_list)} نتائج")
        
        # الخطوة 5: عرض نتائج البحث من Azure
        print(f"\n📊 الخطوة 5: نتائج البحث من Azure AI Search")
        docs = []
        
        for i, r in enumerate(results_list, 1):
            identifier_value = r.get(identifier_field, "غير محدد")
            name_value = r.get("Name", "بدون اسم")
            content_field_value = r.get(content_field, "بدون وصف")
            price_value = r.get("Price", "غير محدد")
            search_score = r.get("@search.score", 0)
            
            print(f"   📦 نتيجة {i}:")
            print(f"      🏷️ ID: {identifier_value}")
            print(f"      📌 الاسم: {name_value}")
            print(f"      💰 السعر: {price_value} (نوع: {type(price_value).__name__})")
            print(f"      🥘 المكونات: {content_field_value[:50]}{'...' if len(content_field_value) > 50 else ''}")
            print(f"      📊 نقاط البحث: {search_score}")
            
            # إنشاء النتيجة للمعالجة
            result_item = {
                'ID': identifier_value,
                'Name': name_value,
                'ingredients': content_field_value,
                'Price': price_value,
                'search_score': search_score
            }
            docs.append(result_item)
        
        if not docs:
            error_msg = "❌ لم أجد أي عناصر تطابق بحثك"
            print(f"\n❌ النتيجة: {error_msg}")
            return ToolResult(error_msg, ToolResultDirection.TO_CLIENT)
        
        # الخطوة 6: تحضير البيانات للموديل
        print(f"\n🤖 الخطوة 6: تحضير البيانات للموديل")
        print(f"   إعدادات الموديل الحالية: {ModelInputSettings.get_current_mode()}")
        
        result_text = generate_model_input(docs, query, search_query)
        
        print(f"   📝 النص المُحضر للموديل:")
        print(f"   {'='*40}")
        print(result_text)
        print(f"   {'='*40}")
        print(f"   📏 طول النص: {len(result_text)} حرف")
        print(f"   📄 عدد الأسطر: {len(result_text.split('\\n'))}")
        
        # تحليل النص للأسعار
        price_count = result_text.count('جنيه')
        number_count = len([word for word in result_text.split() if word.isdigit()])
        print(f"   💰 كلمة 'جنيه' تظهر: {price_count} مرة")
        print(f"   🔢 أرقام في النص: {number_count}")
        
        # الخطوة 7: النتيجة النهائية
        print(f"\n✅ الخطوة 7: إرسال النتيجة للموديل")
        print(f"   حالة العملية: نجحت بالكامل")
        print(f"   البيانات المرسلة: {len(result_text)} حرف مع {len(docs)} عنصر")
        print(f"{'='*60}")
        
        return ToolResult(result_text, ToolResultDirection.TO_CLIENT)
        
    except Exception as e:
        error_msg = f"❌ خطأ في البحث: {str(e)}"
        print(f"\n❌ خطأ في الخطوة: {error_msg}")
        print(f"{'='*60}")
        return ToolResult(error_msg, ToolResultDirection.TO_CLIENT)

# باقي الدوال...
async def _show_all_tool(search_client: SearchClient, identifier_field: str, content_field: str) -> ToolResult:
    """عرض جميع العناصر المتاحة"""
    try:
        search_results = search_client.search(
            search_text="*",
            query_type="simple",
            top=10,
            select=f"{identifier_field},Name,{content_field},Price"
        )
        
        docs = list(search_results)
        
        if not docs:
            return ToolResult("❌ لا توجد عناصر في القاعدة", ToolResultDirection.TO_CLIENT)
        
        result_text = "📋 جميع العناصر المتاحة:\\n\\n"
        
        for doc in docs:
            name = doc.get("Name", "بدون اسم")
            price = doc.get("Price", "غير محدد")
            
            result_text += f"• {name}"
            if price != "غير محدد":
                result_text += f" - {price} جنيه"
            result_text += "\\n"
        
        return ToolResult(result_text, ToolResultDirection.TO_CLIENT)
        
    except Exception as e:
        return ToolResult(f"❌ خطأ في عرض العناصر: {str(e)}", ToolResultDirection.TO_CLIENT)

def attach_rag_tools(rtmt: RTMiddleTier, credentials, search_endpoint: str, search_index: str, semantic_configuration: str, identifier_field: str, content_field: str, embedding_field: str, title_field: str, use_vector_query: bool):
    """
    ربط أدوات البحث المحسنة مع Real-time Model
    """
    
    print("🔧 إعداد أدوات البحث:")
    print(f"   البحث الدلالي: {'مفعل' if semantic_configuration else 'معطل'}")
    print(f"   التكوين: {semantic_configuration}")
    print(f"   الحقول: ID={identifier_field}, Name={title_field}, Content={content_field}")
    print(f"   🧠 الذاكرة المؤقتة: مفعلة ({CACHE_EXPIRY_MINUTES} دقيقة)")
    
    search_credential = credentials
    search_client = SearchClient(
        endpoint=search_endpoint,
        index_name=search_index,
        credential=search_credential
    )
    
    # ربط أداة البحث المحسنة
    async def search_wrapper(args: Any) -> ToolResult:
        return await _search_tool_enhanced(
            search_client, semantic_configuration, identifier_field, 
            content_field, embedding_field, use_vector_query, args
        )
    
    # ربط أداة عرض الكل
    async def show_all_wrapper(args: Any) -> ToolResult:
        return await _show_all_tool(search_client, identifier_field, content_field)
    
    # ربط أداة حذف الذاكرة المؤقتة
    async def clear_cache_wrapper(args: Any) -> ToolResult:
        clear_cache()
        return ToolResult("🗑️ تم حذف الذاكرة المؤقتة", ToolResultDirection.TO_CLIENT)
    
    rtmt.tools["search"] = Tool(schema=_search_tool_schema, target=search_wrapper)
    rtmt.tools["show_all"] = Tool(schema={
        "type": "function",
        "name": "show_all",
        "description": "عرض جميع العناصر المتاحة في المطعم",
        "parameters": {"type": "object", "properties": {}, "required": []}
    }, target=show_all_wrapper)
    
    rtmt.tools["clear_cache"] = Tool(schema={
        "type": "function", 
        "name": "clear_cache",
        "description": "حذف الذاكرة المؤقتة",
        "parameters": {"type": "object", "properties": {}, "required": []}
    }, target=clear_cache_wrapper)
    
    print("✅ تم ربط أدوات البحث بنجاح")
    print(f"🎛️ إعدادات الموديل: {ModelInputSettings.get_current_mode()}")
    print(f"🔧 الأدوات المتاحة: search, show_all, clear_cache")
