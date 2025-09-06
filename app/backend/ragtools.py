#!/usr/bin/env python3
"""
ragtools.py محسن مع ذاكرة مؤقتة وإدخال محسن للموديل
Enhanced ragtools.py with memory cache and improved model input
"""
import asyncio
import json
import sys
import re
from typing import Any, Dict, List
from datetime import datetime, timedelta
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorQuery
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential
from rtmt import ToolResult, ToolResultDirection, Tool, RTMiddleTier
from translation_utils import translate_and_extract_for_search
from model_input_settings import ModelInputSettings, generate_model_input
from order_manager import order_manager, add_to_current_order, get_current_order_summary, confirm_current_order, clear_current_order

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

# 🎛️ schema لأداة التحكم في إعدادات الموديل
_model_settings_tool_schema = {
    "type": "function",
    "name": "model_settings",
    "description": "التحكم في ما يدخل للموديل من معلومات (الاسم، السعر، المكونات)",
    "parameters": {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "description": "العملية المطلوبة",
                "enum": ["status", "name_price_only", "enable_ingredients", "disable_ingredients", "toggle_ingredients", "full_details"]
            }
        },
        "required": ["action"]
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
    أداة البحث الرئيسية مع البحث الذكي والذاكرة المؤقتة
    """
    query = args.get("query", "")
    
    if not query:
        return ToolResult("❌ الرجاء إدخال كلمة للبحث", ToolResultDirection.TO_CLIENT)
    
    # 🧠 فحص الذاكرة المؤقتة أولاً
    cached_result = get_from_cache(query)
    if cached_result:
        return ToolResult(cached_result['response_text'], ToolResultDirection.TO_CLIENT)
    
    # ترجمة الاستعلام والاستخراج (مع إصلاح أونين رينجز)
    search_query, current_mode = fix_onion_rings_translation(query)
    
    print(f"\n{'='*50}")
    print(f"🎯 تتبع عملية البحث التفصيلي")
    print(f"{'='*50}")
    print(f"📝 الخطوة 1: الطلب الأصلي: '{query}'")
    print(f"� الخطوة 2: النص المترجم: '{search_query}'")
    print(f"🔧 الخطوة 3: البحث الدلالي: {'مفعل' if semantic_configuration else 'معطل'}")
    print(f"⚙️ الخطوة 4: وضع الترجمة: {current_mode}")
    
    try:
        search_results = None
        search_method_used = ""
        
        # محاولة البحث الدلالي في Name و ingredients معاً
        try:
            if semantic_configuration:
                search_results = search_client.search(
                    search_text=search_query,
                    query_type="semantic", 
                    semantic_configuration_name=semantic_configuration,
                    top=5,
                    select=f"{identifier_field},Name,{content_field},Price",
                    search_fields=["Name", content_field],  # البحث في Name و ingredients معاً
                    query_caption="extractive",
                    query_answer="extractive"
                )
            else:
                search_results = search_client.search(
                    search_text=search_query,
                    query_type="simple",
                    top=5,
                    select=f"{identifier_field},Name,{content_field},Price",
                    search_fields=["Name", content_field]  # البحث في Name و ingredients معاً
                )
            
            # تجربة تحويل النتائج إلى قائمة للتأكد من عدم وجود خطأ
            results_list = list(search_results)
            search_results = results_list
            search_method_used = "Name and ingredients"
            print("✅ البحث نجح مع حقلي Name و ingredients معاً")
            
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
                
                search_method_used = "ingredients only"
                print("✅ البحث نجح مع حقل ingredients فقط")
            else:
                # إذا كان خطأ آخر، ارمي الخطأ
                raise name_search_error
        
        # معالجة النتائج وإعدادها للذاكرة المؤقتة
        docs = []
        cache_data = {
            'items': [],
            'query': query,
            'search_method': search_method_used
        }
        
        print(f"📊 الخطوة 6: عدد النتائج الفعلية: {len(list(search_results))}")
        
        result_counter = 0
        for r in search_results:
            result_counter += 1
            identifier_value = r.get(identifier_field, "غير محدد")
            name_value = r.get("Name", "بدون اسم")
            content_field_value = r.get(content_field, "بدون وصف")
            price_value = r.get("Price", "غير محدد")
            search_score = r.get("@search.score", 0)
            reranker_score = r.get("@search.reranker_score", None)
            
            print(f"  📋 نتيجة {result_counter}: {name_value} - السعر: {price_value}")
            
            # إنشاء النتيجة للعرض
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
            
            # 💾 حفظ في الذاكرة المؤقتة للاستعلام عن المكونات لاحقاً
            cache_data['items'].append({
                'name': name_value,
                'price': price_value,
                'ingredients': content_field_value,
                'id': identifier_value
            })
        
        if not docs:
            response_text = "❌ لم أجد أي عناصر تطابق بحثك. الرجاء المحاولة بكلمات أخرى."
            return ToolResult(response_text, ToolResultDirection.TO_CLIENT)
        
        # 🎯 تنسيق النتائج للموديل حسب الإعدادات
        print(f"📤 {ModelInputSettings.get_current_mode()}")
        result_text = generate_model_input(docs, query, search_query)
        
        # إضافة معلومات تقنية للتطوير (لا تظهر للمستخدم النهائي)
        technical_info = f"\n� معلومات تقنية:\n"
        technical_info += f"   📊 طريقة البحث: {search_method_used}\n"
        technical_info += f"   🎯 عدد النتائج: {len(docs)}\n"
        
        # في بيئة التطوير، أضف المعلومات التقنية
        if any(doc.get('search_score', 0) > 0 for doc in docs):
            result_text += technical_info
        
        # 💾 حفظ النتائج في الذاكرة المؤقتة
        cache_data['response_text'] = result_text
        save_to_cache(query, cache_data)
        
        print(f"🎯 الخطوة 7: النتيجة النهائية التي ستُرسل للموديل:")
        print(f"{'='*50}")
        print(result_text[:300] + "..." if len(result_text) > 300 else result_text)
        print(f"{'='*50}")
        
        return ToolResult(result_text, ToolResultDirection.TO_CLIENT)
        
    except Exception as e:
        error_msg = f"❌ خطأ في البحث: {str(e)}"
        print(error_msg)
        return ToolResult(error_msg, ToolResultDirection.TO_CLIENT)

async def _get_ingredients_tool(args: Any) -> ToolResult:
    """
    🆕 أداة للحصول على مكونات طبق من الذاكرة المؤقتة
    """
    item_name = args.get("item_name", "").strip()
    
    if not item_name:
        return ToolResult("❌ الرجاء تحديد اسم الطبق", ToolResultDirection.TO_CLIENT)
    
    print(f"🔍 البحث عن مكونات: {item_name}")
    
    # البحث في جميع البيانات المخزنة في الذاكرة المؤقتة
    for cache_key, cache_info in SEARCH_CACHE.items():
        if is_cache_valid(cache_info['timestamp']):
            for item in cache_info['data']['items']:
                # مطابقة اسم الطبق (مرونة في المطابقة)
                if (item_name.lower() in item['name'].lower() or 
                    item['name'].lower() in item_name.lower()):
                    
                    ingredients_text = f"🥘 مكونات {item['name']}:\n"
                    ingredients_text += f"💰 السعر: {item['price']} جنيه\n"
                    ingredients_text += f"📝 المكونات: {item['ingredients']}"
                    
                    print(f"✅ تم العثور على المكونات في الذاكرة المؤقتة")
                    return ToolResult(ingredients_text, ToolResultDirection.TO_CLIENT)
    
    return ToolResult(f"❌ لم أجد معلومات عن '{item_name}' في الذاكرة المؤقتة. جرب البحث عنه أولاً.", ToolResultDirection.TO_CLIENT)

async def _model_settings_tool(args: Any) -> ToolResult:
    """
    أداة التحكم في إعدادات ما يدخل للموديل
    """
    action = args.get("action", "status")
    
    print(f"🎛️ تغيير إعدادات الموديل: {action}")
    
    if action == "status":
        current_mode = ModelInputSettings.get_current_mode()
        config = ModelInputSettings.get_display_config()
        
        status_text = f"📊 حالة إعدادات الموديل:\n"
        status_text += f"{current_mode}\n\n"
        status_text += f"📋 التفاصيل:\n"
        status_text += f"   ✅ الاسم: {'مفعل' if config['name'] else 'معطل'}\n"
        status_text += f"   💰 السعر: {'مفعل' if config['price'] else 'معطل'}\n"
        status_text += f"   🥘 المكونات: {'مفعل' if config['ingredients'] else 'معطل'}\n"
        status_text += f"   📊 نقاط البحث: {'مفعل' if config['search_score'] else 'معطل'}\n"
        status_text += f"   📏 أقصى نتائج: {config['max_results']}"
        
        return ToolResult(status_text, ToolResultDirection.TO_CLIENT)
    
    elif action == "name_price_only":
        result = ModelInputSettings.set_name_and_price_only()
        return ToolResult(result, ToolResultDirection.TO_CLIENT)
    
    elif action == "enable_ingredients":
        result = ModelInputSettings.enable_ingredients()
        return ToolResult(result, ToolResultDirection.TO_CLIENT)
    
    elif action == "disable_ingredients":
        result = ModelInputSettings.disable_ingredients()
        return ToolResult(result, ToolResultDirection.TO_CLIENT)
    
    elif action == "toggle_ingredients":
        result = ModelInputSettings.toggle_ingredients()
        return ToolResult(result, ToolResultDirection.TO_CLIENT)
    
    elif action == "full_details":
        result = ModelInputSettings.set_full_details()
        return ToolResult(result, ToolResultDirection.TO_CLIENT)
    
    else:
        return ToolResult(f"❌ عملية غير معروفة: {action}", ToolResultDirection.TO_CLIENT)

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
            return ToolResult("❌ لا توجد عناصر في قاعدة البيانات", ToolResultDirection.TO_CLIENT)
        
        # 🎯 عرض مُبسط - Name والسعر فقط
        result_text = f"📋 قائمة الطعام ({len(docs)} عنصر):\n\n"
        
        for i, doc in enumerate(docs, 1):
            result_text += f"{i}. {doc['Name']} - {doc['Price']} جنيه\n"
            if i % 10 == 0:  # فاصل كل 10 عناصر
                result_text += "\n"
        
        return ToolResult(result_text, ToolResultDirection.TO_CLIENT)
        
    except Exception as e:
        error_msg = f"❌ خطأ في عرض العناصر: {str(e)}"
        print(error_msg)
        return ToolResult(error_msg, ToolResultDirection.TO_CLIENT)

def attach_rag_tools(rtmt: RTMiddleTier, credentials, search_endpoint: str, search_index: str, semantic_configuration: str, identifier_field: str, content_field: str, embedding_field: str, title_field: str, use_vector_query: bool):
    """ربط أدوات البحث مع الذاكرة المؤقتة"""
    
    # إنشاء search client
    search_client = SearchClient(search_endpoint, search_index, credentials)
    
    print("🔧 إعداد أدوات البحث:")
    print(f"   البحث الدلالي: {'مفعل' if semantic_configuration else 'معطل'}")
    print(f"   التكوين: {semantic_configuration}")
    print(f"   الحقول: ID={identifier_field}, Name={title_field}, Content={content_field}")
    print(f"   🧠 الذاكرة المؤقتة: مفعلة ({CACHE_EXPIRY_MINUTES} دقيقة)")
    
    async def search_wrapper(args: Any) -> ToolResult:
        return await _search_tool(search_client, semantic_configuration, identifier_field, content_field, embedding_field, use_vector_query, args)
    
    async def ingredients_wrapper(args: Any) -> ToolResult:
        return await _get_ingredients_tool(args)
    
    async def show_all_wrapper(args: Any) -> ToolResult:
        return await _show_all_tool(search_client, identifier_field, content_field)
    
    async def model_settings_wrapper(args: Any) -> ToolResult:
        return await _model_settings_tool(args)
    
    # ربط الأدوات
    rtmt.tools["search"] = Tool(schema=_search_tool_schema, target=search_wrapper)
    rtmt.tools["get_ingredients"] = Tool(schema=_ingredients_tool_schema, target=ingredients_wrapper)
    rtmt.tools["model_settings"] = Tool(schema=_model_settings_tool_schema, target=model_settings_wrapper)
    
    # أداة عرض جميع العناصر
    show_all_schema = {
        "type": "function", 
        "name": "show_all",
        "description": "عرض جميع عناصر قائمة الطعام المتاحة",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
    rtmt.tools["show_all"] = Tool(schema=show_all_schema, target=show_all_wrapper)
    
    # أداة إضافة للطلب (في حالة استدعائها منفصلة)
    add_to_order_schema = {
        "type": "function",
        "name": "add_to_order", 
        "description": "إضافة عنصر للطلب - استخدم search مع add_to_order=true بدلاً من ذلك",
        "parameters": {
            "type": "object",
            "properties": {
                "item_name": {"type": "string", "description": "اسم العنصر"},
                "price": {"type": "string", "description": "السعر"}
            },
            "required": ["item_name"]
        }
    }
    
    async def add_to_order_wrapper(args: Any) -> ToolResult:
        """أداة إضافة للطلب - توجه المستخدم لاستخدام search"""
        return ToolResult("استخدم 'search' مع add_to_order=true بدلاً من استخدام add_to_order منفصلة", ToolResultDirection.TO_CLIENT)
    
    rtmt.tools["add_to_order"] = Tool(schema=add_to_order_schema, target=add_to_order_wrapper)
    
    # أداة مسح الذاكرة المؤقتة
    clear_cache_schema = {
        "type": "function",
        "name": "clear_cache",
        "description": "مسح الذاكرة المؤقتة للحصول على نتائج محدثة",
        "parameters": {
            "type": "object", 
            "properties": {},
            "required": []
        }
    }
    
    async def clear_cache_wrapper(args: Any) -> ToolResult:
        """مسح الذاكرة المؤقتة"""
        clear_cache()
        return ToolResult("🗑️ تم مسح الذاكرة المؤقتة بنجاح", ToolResultDirection.TO_CLIENT)
    
    rtmt.tools["clear_cache"] = Tool(schema=clear_cache_schema, target=clear_cache_wrapper)
    
    # 🆕 أداة تأكيد الطلب
    confirm_order_schema = {
        "type": "function",
        "name": "confirm_order",
        "description": "تأكيد الطلب الحالي وإتمام الشراء",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
    
    async def confirm_order_wrapper(args: Any) -> ToolResult:
        """تأكيد الطلب"""
        try:
            result = confirm_current_order()
            return ToolResult(json.dumps(result, ensure_ascii=False), ToolResultDirection.TO_CLIENT)
        except Exception as e:
            return ToolResult(f"خطأ في تأكيد الطلب: {e}", ToolResultDirection.TO_CLIENT)
    
    rtmt.tools["confirm_order"] = Tool(schema=confirm_order_schema, target=confirm_order_wrapper)
    
    # 🆕 أداة إضافة عنصر محدد للطلب
    add_item_to_order_schema = {
        "type": "function", 
        "name": "add_item_to_order",
        "description": "إضافة عنصر محدد للطلب بعد البحث عنه وتأكيد الرغبة من المستخدم",
        "parameters": {
            "type": "object",
            "properties": {
                "item_id": {"type": "string", "description": "معرف العنصر"},
                "item_name": {"type": "string", "description": "اسم العنصر"},
                "price": {"type": "string", "description": "سعر العنصر"},
                "quantity": {"type": "integer", "description": "الكمية المطلوبة", "default": 1}
            },
            "required": ["item_id", "item_name", "price"]
        }
    }
    
    async def add_item_to_order_wrapper(args: Any) -> ToolResult:
        """إضافة عنصر للطلب"""
        try:
            item_id = args.get("item_id", "")
            item_name = args.get("item_name", "")
            price_str = args.get("price", "0")
            quantity = args.get("quantity", 1)
            
            # تنظيف السعر
            price = float(re.sub(r'[^\d.]', '', str(price_str)))
            
            result = add_to_current_order(item_id, item_name, price, quantity)
            return ToolResult(json.dumps(result, ensure_ascii=False), ToolResultDirection.TO_CLIENT)
        except Exception as e:
            return ToolResult(f"خطأ في إضافة العنصر: {e}", ToolResultDirection.TO_CLIENT)
    
    rtmt.tools["add_item_to_order"] = Tool(schema=add_item_to_order_schema, target=add_item_to_order_wrapper)
    
    # 🆕 أداة عرض الطلب الحالي
    show_current_order_schema = {
        "type": "function",
        "name": "show_current_order", 
        "description": "عرض الطلب الحالي مع التفاصيل والإجمالي",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
    
    async def show_current_order_wrapper(args: Any) -> ToolResult:
        """عرض الطلب الحالي"""
        try:
            result = get_current_order_summary()
            return ToolResult(json.dumps(result, ensure_ascii=False), ToolResultDirection.TO_CLIENT)
        except Exception as e:
            return ToolResult(f"خطأ في عرض الطلب: {e}", ToolResultDirection.TO_CLIENT)
    
    rtmt.tools["show_current_order"] = Tool(schema=show_current_order_schema, target=show_current_order_wrapper)
    
    # 🆕 أداة اكتشاف كلمات الإنهاء
    check_goodbye_schema = {
        "type": "function",
        "name": "check_goodbye",
        "description": "فحص إذا كان المستخدم يريد إنهاء المحادثة (سلام، مع السلامة، إلى اللقاء)",
        "parameters": {
            "type": "object",
            "properties": {
                "user_message": {"type": "string", "description": "رسالة المستخدم للفحص"}
            },
            "required": ["user_message"]
        }
    }
    
    async def check_goodbye_wrapper(args: Any) -> ToolResult:
        """فحص كلمات الإنهاء"""
        try:
            user_message = args.get("user_message", "").lower().strip()
            
            # كلمات الإنهاء
            goodbye_words = [
                "سلام", "مع السلامة", "إلى اللقاء", "إلي اللقاء", 
                "باي", "goodbye", "bye", "سلامه", "اللقاء"
            ]
            
            for word in goodbye_words:
                if word in user_message:
                    # مسح الذاكرة المؤقتة عند الإنهاء
                    clear_cache()
                    result = {
                        "action": "end_conversation",
                        "message": "شكراً لك! تم إنهاء المحادثة. نتطلع لخدمتك مرة أخرى.",
                        "should_disconnect": True
                    }
                    return ToolResult(json.dumps(result, ensure_ascii=False), ToolResultDirection.TO_CLIENT)
            
            result = {
                "action": "continue_conversation", 
                "should_disconnect": False
            }
            return ToolResult(json.dumps(result, ensure_ascii=False), ToolResultDirection.TO_CLIENT)
            
        except Exception as e:
            return ToolResult(f"خطأ في فحص الإنهاء: {e}", ToolResultDirection.TO_CLIENT)
    
    rtmt.tools["check_goodbye"] = Tool(schema=check_goodbye_schema, target=check_goodbye_wrapper)
    
    print(f"✅ تم ربط أدوات البحث بنجاح")
    print(f"🎛️ إعدادات الموديل: {ModelInputSettings.get_current_mode()}")
    print(f"🔧 الأدوات المتاحة: search, get_ingredients, model_settings, show_all, add_to_order, confirm_order, add_item_to_order, show_current_order, check_goodbye, clear_cache")
