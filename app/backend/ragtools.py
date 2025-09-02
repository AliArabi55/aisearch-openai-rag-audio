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

# قاموس الترجمة من العربية للإنجليزية (النطق العربي)
TRANSLATION_DICT = {
    # الأطعمة الرئيسية
    'كالزونى': 'Calzoni', 'كالزوني': 'Calzoni',
    'بيتزا': 'Pizza', 'بيتزه': 'Pizza',
    'برجر': 'Burger', 'برغر': 'Burger',
    
    # اللحوم والدواجن
    'فراخ': 'Ferakh', 'دجاج': 'Ferakh', 'فرخ': 'Ferakh',
    'لحمة': 'Beef', 'لحم': 'Beef', 'بيف': 'Beef',
    'سجق': 'Sojok', 'سوجوك': 'Sojok',
    'سلامي': 'Salami', 'سلاميه': 'Salami',
    'هوت دوج': 'Hot Dog', 'هوتدوج': 'Hot Dog',
    'بيف بيكون': 'Beef Bacon', 'بيكون': 'Bacon',
    'رومي مدخن': 'Romi Medakhan', 'رومى مدخن': 'Romi Medakhan',
    'مفروم': 'Mafroum', 'بسطرمة': 'Pastirma', 'بستورمه': 'Pastirma',
    
    # الأجبان والصلصات
    'جبنة': 'Cheese', 'جبن': 'Cheese',
    'موتزاريلا': 'Mozzarella', 'موزاريلا': 'Mozzarella',
    'شيدر': 'Cheddar', 'تشيدر': 'Cheddar',
    'روكفور': 'Roquefort', 'ركفور': 'Roquefort',
    'صلصة': 'Sauce', 'صوص': 'Sauce',
    'مايونيز': 'Mayonez', 'مايونيز': 'Mayonez',
    'رانش': 'Ranch', 'باربكيو': 'Barbecue', 'باربيكيو': 'Barbecue',
    
    # الخضروات والإضافات
    'مشروم': 'Mushroom', 'عيش غراب': 'Mushroom',
    'خيار': 'Khyar', 'خس': 'Khas', 'بصل': 'Basal',
    'طماطم': 'Tomato', 'طماطة': 'Tomato',
    'هالابينو': 'Halapeno', 'هالبينو': 'Halapeno',
    'فلفل': 'Felfel', 'زيتون': 'Zatoon',
    
    # المأكولات البحرية
    'جمبري': 'Gambary', 'جمبرى': 'Gambary',
    'سيبيا': 'Sepia', 'سيبيه': 'Sepia',
    'كابوريا': 'Kaboria', 'كابوريه': 'Kaboria',
    'تونة': 'Tuna', 'تونه': 'Tuna',
    'أنشوجة': 'Anshoga', 'انشوجه': 'Anshoga',
    
    # الأحجام والأنواع
    'كبير': 'Kbeer', 'كبيرة': 'Kbeer',
    'وسط': 'Wost', 'وسطة': 'Wost',
    'سنجل': 'Single', 'سينجل': 'Single',
    'دبل': 'Double', 'دوبل': 'Double',
    
    # الأنواع المتخصصة
    'كريسبي': 'Crispy', 'كريسبى': 'Crispy',
    'مشوي': 'Mashwi', 'مشويه': 'Mashwi',
    'سبايسي': 'Spicy', 'سبايسى': 'Spicy',
    'مكسيكان': 'Mexican', 'مكسيكانى': 'Mexican',
    'أمريكان': 'American', 'امريكان': 'American',
    'بلو': 'Blue', 'تشيزي': 'Cheesy', 'تشيزى': 'Cheesy',
    'جوسي': 'Juicy', 'جوسى': 'Juicy',
    'ديلايت': 'Delight', 'ديلايه': 'Delight',
    'تيستي': 'Tasty', 'تيستى': 'Tasty',
    'فايبس': 'Vibes', 'فايبز': 'Vibes',
    'كريزي رانش': 'Crazy Ranch', 'كريزى رانش': 'Crazy Ranch',
    'زينجر': 'Zinger', 'زينغر': 'Zinger',
    'سبيشال': 'Special', 'سبيشيال': 'Special',
    
    # الأطباق المركبة
    'مشاكل لحوم': 'Meshakel Lohoum', 'مشاكل لحمة': 'Meshakel Lohoum',
    'فوسفور': 'Fosfor', 'فوسفر': 'Fosfor',
    'سي فود': 'Seafood', 'سى فود': 'Seafood',
    
    # كلمات إضافية مهمة
    'طبق': 'Taba', 'طبقة': 'Taba',
    'اونيون': 'Onion', 'أونيون': 'Onion',
    'اونيون رينج': 'Onion Ring', 'اونيون رينجز': 'Onion Rings',
    'رينج': 'Ring', 'رينجز': 'Rings',
    'كرسبي': 'Crispy', 'كرسبى': 'Crispy',
    'موتزاريلا ستيكس': 'Mozzarella Sticks',
    'ستيكس': 'Sticks', 'شرائح': 'Shara2eh',
    'اناناس': 'Pineapple', 'أناناس': 'Pineapple',
    'هالبينو': 'Halapeno', 'هالابينو': 'Halapeno',
    'شيلي': 'Chili', 'تشيلي': 'Chili',
    'بيكون': 'Bacon', 'يسطرمه': 'Pastrami',
    'مبشور': 'Mabshour', 'بشر': 'Bash'
}

def translate_to_english(arabic_text: str) -> str:
    """ترجمة النص العربي إلى الكتابة الإنجليزية (النطق العربي)"""
    if not arabic_text:
        return arabic_text
    
    # تنظيف النص
    text = arabic_text.strip().lower()
    
    # البحث عن أطول مطابقة أولاً (للعبارات المركبة)
    translated_words = []
    words = text.split()
    i = 0
    
    while i < len(words):
        found_match = False
        
        # محاولة البحث عن مطابقة من 3 كلمات
        if i + 2 < len(words):
            three_word_phrase = ' '.join(words[i:i+3])
            if three_word_phrase in TRANSLATION_DICT:
                translated_words.append(TRANSLATION_DICT[three_word_phrase])
                i += 3
                found_match = True
                continue
        
        # محاولة البحث عن مطابقة من كلمتين
        if i + 1 < len(words):
            two_word_phrase = ' '.join(words[i:i+2])
            if two_word_phrase in TRANSLATION_DICT:
                translated_words.append(TRANSLATION_DICT[two_word_phrase])
                i += 2
                found_match = True
                continue
        
        # البحث عن كلمة واحدة
        if words[i] in TRANSLATION_DICT:
            translated_words.append(TRANSLATION_DICT[words[i]])
            found_match = True
        else:
            # إذا لم توجد ترجمة، ترجم الكلمة للإنجليزية العادية
            english_word = transliterate_arabic_to_english(words[i])
            translated_words.append(english_word)
        
        i += 1
    
    result = ' '.join(translated_words)
    print(f"🔄 ترجمة: '{arabic_text}' → '{result}'")
    return result

def transliterate_arabic_to_english(arabic_word: str) -> str:
    """ترجمة الكلمات العربية للإنجليزية بناءً على النطق"""
    # قاموس الحروف العربية للإنجليزية
    arabic_to_english = {
        'ا': 'a', 'أ': 'a', 'آ': 'aa', 'إ': 'e',
        'ب': 'b', 'ت': 't', 'ث': 'th', 'ج': 'g', 'ح': 'h',
        'خ': 'kh', 'د': 'd', 'ذ': 'th', 'ر': 'r', 'ز': 'z',
        'س': 's', 'ش': 'sh', 'ص': 's', 'ض': 'd', 'ط': 't',
        'ظ': 'z', 'ع': 'a', 'غ': 'gh', 'ف': 'f', 'ق': 'q',
        'ك': 'k', 'ل': 'l', 'م': 'm', 'ن': 'n', 'ه': 'h',
        'و': 'w', 'ي': 'y', 'ى': 'a', 'ة': 'a', 'ء': 'a'
    }
    
    result = ''
    for char in arabic_word:
        if char in arabic_to_english:
            result += arabic_to_english[char]
        elif char.isspace():
            result += ' '
        else:
            result += char  # احتفظ بالحروف الإنجليزية والأرقام كما هي
    
    # تنظيف النتيجة (إزالة التكرارات وتحسين النطق)
    result = result.replace('aa', 'a').replace('ee', 'e').replace('oo', 'o')
    return result.capitalize()

def format_arabic_text(text):
    """تنسيق النص العربي للعرض الصحيح في التيرمينال"""
    try:
        # علامات Unicode للتحكم في الاتجاه
        rtl_mark = '\u202E'  # Right-to-Left Override
        pop_mark = '\u202C'  # Pop Directional Formatting
        
        # تطبيق الاتجاه الصحيح للنص العربي
        formatted_text = f"{rtl_mark}{text}{pop_mark}"
        return formatted_text
    except:
        return text

_search_tool_schema = {
    "type": "function",
    "name": "search",
    "description": "البحث في قاعدة المعرفة واختياريا إضافة منتج للطلب. يمكنك البحث بالعربية العادية - سيتم الترجمة تلقائياً. " + \
                   "النتائج تظهر كـ: [ID] اسم المنتج - المكونات (السعر جنيه).",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "استعلام البحث بالعربية العادية - سيتم ترجمته تلقائياً"
            },
            "add_to_order": {
                "type": "boolean",
                "description": "هل تريد إضافة المنتج الأول من نتائج البحث للطلب؟ استخدم true عندما يطلب العميل منتجاً",
                "default": False
            }
        },
        "required": ["query"],
        "additionalProperties": False
    }
}

_get_order_summary_schema = {
    "type": "function",
    "name": "get_order_summary",
    "description": "عرض ملخص الطلب الحالي مع الأسعار والمكونات. استخدم هذه الأداة عندما يريد العميل مراجعة طلبه.",
    "parameters": {
        "type": "object",
        "properties": {},
        "additionalProperties": False
    }
}

_confirm_order_schema = {
    "type": "function",
    "name": "confirm_order", 
    "description": "تأكيد الطلب النهائي. استخدم هذه الأداة عندما يؤكد العميل أن الطلب صحيح ولا يريد إضافة شيء آخر.",
    "parameters": {
        "type": "object",
        "properties": {},
        "additionalProperties": False
    }
}

_clear_order_schema = {
    "type": "function",
    "name": "clear_order",
    "description": "مسح الطلب الحالي. استخدم عندما يريد العميل البدء من جديد.",
    "parameters": {
        "type": "object",
        "properties": {},
        "additionalProperties": False
    }
}

_grounding_tool_schema = {
    "type": "function",
    "name": "report_grounding",
    "description": "الإبلاغ عن استخدام مصدر من قاعدة المعرفة كجزء من الإجابة (في الواقع، اقتباس المصدر).",
    "parameters": {
        "type": "object",
        "properties": {
            "sources": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "description": "قائمة بأسماء المصادر من البيان الأخير المستخدم فعلاً"
            }
        },
        "required": ["sources"],
        "additionalProperties": False
    }
}

_show_all_tool_schema = {
    "type": "function", 
    "name": "show_all_items",
    "description": "عرض جميع المنتجات المتاحة في المطعم عندما يطلب العميل رؤية كل المنتجات أو القائمة الكاملة",
    "parameters": {
        "type": "object",
        "properties": {},
        "additionalProperties": False
    }
}

async def _search_tool(
    search_client: SearchClient, 
    semantic_configuration: str | None,
    identifier_field: str,
    content_field: str,
    embedding_field: str,
    use_vector_query: bool,
    args: Any) -> ToolResult:
    
    original_query = args["query"]
    add_to_order = args.get("add_to_order", False)
    
    # ترجمة الاستعلام تلقائياً للإنجليزية
    translated_query = translate_to_english(original_query)
    
    # طباعة بترميز صحيح للعربية مع دعم RTL
    try:
        # إضافة علامات Unicode للاتجاه الصحيح
        rtl_mark = '\u202E'  # Right-to-Left Override
        ltr_mark = '\u202D'  # Left-to-Right Override
        pop_mark = '\u202C'  # Pop Directional Formatting
        
        # تنسيق النص مع الاتجاه الصحيح
        search_text = f"🔍 البحث عن: '{original_query}' → '{translated_query}'"
        order_text = f"إضافة للطلب: {'نعم' if add_to_order else 'لا'}"
        fields_text = f"📋 استخدام الحقول: ID={identifier_field}, Content={content_field}"
        
        print(f"{search_text} | {order_text}")
        print(fields_text)
    except UnicodeEncodeError:
        print(f"Search for: '{original_query}' → '{translated_query}' | Add to order: {add_to_order}")
        print(f"Using fields: ID={identifier_field}, Content={content_field}")
    
    # بحث نصي بسيط في Azure AI Search باستخدام الاستعلام المترجم
    search_results = await search_client.search(
        search_text=translated_query,  # استخدام الاستعلام المترجم
        query_type="simple",  # البحث النصي البسيط يدعم العربية جيداً
        top=5,
        select=f"{identifier_field},Name,{content_field},Price",
        search_mode="any"  # البحث عن أي كلمة من الكلمات المدخلة
    )
    
    result = ""
    result_count = 0
    found_items = []  # لحفظ النتائج للاستخدام في الطلب
    
    async for r in search_results:
        result_count += 1
        try:
            result_text = format_arabic_text(f"📋 نتيجة {result_count}")
            print(f"{result_text}: {r}")
        except UnicodeEncodeError:
            print(f"Result {result_count}: {r}")
        
        # استخدام الحقول الصحيحة
        id_field = r.get(identifier_field, f"Item_{result_count}")
        name_field = r.get('Name', "منتج غير معروف")
        content_field_value = r.get(content_field, "بدون وصف")
        price = r.get('Price', 'سعر غير محدد')
        
        # حفظ بيانات المنتج للاستخدام في الطلب
        item_data = {
            'ID': id_field,
            'Name': name_field,
            'ingredients': content_field_value,
            'Price': price
        }
        found_items.append(item_data)
        
        # لا نضيف شيئاً لـ result هنا - سنُرسل العنصر الأول فقط للموديل
    
    if result_count == 0:
        try:
            no_results_text = format_arabic_text("❌ لم توجد نتائج للبحث!")
            print(no_results_text)
        except UnicodeEncodeError:
            print("No results found!")
        
        # عندما لا توجد نتائج، قل "ليس عندي" فقط
        result = "ليس عندي."
        return ToolResult(result, ToolResultDirection.TO_SERVER)
    else:
        try:
            found_text = format_arabic_text(f"✅ وجدت {result_count} نتائج")
            print(found_text)
        except UnicodeEncodeError:
            print(f"Found {result_count} results")
        
        # إرسال العنصر الأول فقط للموديل بصيغة مبسطة
        if found_items:
            first_item = found_items[0]
            name = first_item['Name']
            price = first_item['Price']
            ingredients = first_item['ingredients'] or "غير محدد"
            
            # الصيغة المبسطة للموديل - العنصر الأول فقط
            result = f"{name} - {price} جنيه\nالمكونات: {ingredients}"
        
        # إذا طُلب إضافة المنتج للطلب وتم العثور على نتائج
        if add_to_order and found_items:
            first_item = found_items[0]  # إضافة أول نتيجة
            success, order_message = order_manager.add_item(first_item)
            
            if success:
                # الحصول على ملخص الطلب المحدث
                order_summary = order_manager.get_order_summary()
                
                result += f"\n\n✅ {order_message}\n\n"
                result += f"📋 الطلب الحالي ({order_summary['total_items']} قطعة):\n"
                for item in order_summary['items']:
                    result += f"• {item['quantity']}x {item['name']} - {item['price']} ج\n"
                result += f"\n💰 الإجمالي: {order_summary['total_price']} جنيه"
                
                # إرسال بيانات الطلب للواجهة الأمامية
                order_response = {
                    "action": "order_updated",
                    "message": order_message,
                    "order_summary": order_summary,
                    "order_table": order_summary["table_html"]
                }
                
                return ToolResult(result, ToolResultDirection.TO_CLIENT)
            else:
                result += f"\n❌ {order_message}"
        else:
            # مجرد عرض النتائج بدون إضافة للطلب - لا نضيف نصائح إضافية
            pass
    
    return ToolResult(result, ToolResultDirection.TO_SERVER)

async def _get_order_summary_tool(args: Any) -> ToolResult:
    """عرض ملخص الطلب الحالي"""
    try:
        order_summary = order_manager.get_order_summary()
        
        if order_summary['total_items'] == 0:
            return ToolResult("الطلب فارغ حالياً", ToolResultDirection.TO_SERVER)
        
        # إرسال الملخص للواجهة الأمامية
        response = {
            "action": "show_order_summary",
            "order_summary": order_summary,
            "order_table": order_summary["table_html"]
        }
        
        return ToolResult(order_summary['formatted_summary'], ToolResultDirection.TO_CLIENT)
        
    except Exception as e:
        print(f"خطأ في عرض ملخص الطلب: {e}")
        return ToolResult("خطأ في عرض ملخص الطلب", ToolResultDirection.TO_SERVER)

async def _confirm_order_tool(args: Any) -> ToolResult:
    """تأكيد الطلب النهائي"""
    try:
        success, confirmation_message, confirmed_order = order_manager.confirm_order()
        
        if success:
            # إرسال تأكيد الطلب للواجهة الأمامية
            response = {
                "action": "order_confirmed",
                "confirmation_message": confirmation_message,
                "order_details": confirmed_order
            }
            
            return ToolResult(confirmation_message, ToolResultDirection.TO_CLIENT)
        else:
            return ToolResult("لا يمكن تأكيد طلب فارغ", ToolResultDirection.TO_SERVER)
            
    except Exception as e:
        print(f"خطأ في تأكيد الطلب: {e}")
        return ToolResult("خطأ في تأكيد الطلب", ToolResultDirection.TO_SERVER)

async def _clear_order_tool(args: Any) -> ToolResult:
    """مسح الطلب الحالي"""
    try:
        message = order_manager.clear_order()
        
        # إرسال إشعار المسح للواجهة الأمامية
        response = {
            "action": "order_cleared",
            "message": message
        }
        
        return ToolResult("تم مسح الطلب", ToolResultDirection.TO_CLIENT)
        
    except Exception as e:
        print(f"خطأ في مسح الطلب: {e}")
        return ToolResult("خطأ في مسح الطلب", ToolResultDirection.TO_SERVER)
        # إضافة اقتراحات إذا لم توجد نتائج
        result = "عذراً، لم أجد هذا المنتج. جرب البحث عن:\n"
        result += "🍕 بيتزا (فراخ، سي فود، كابوريا)\n"
        result += "🍔 برجر (بيف، دجاج، تشيزي)\n"
        result += "أو قل 'اعرض كل المنتجات'"
    else:
        print(f"وجدت {result_count} نتائج")
    
    return ToolResult(result, ToolResultDirection.TO_SERVER)

KEY_PATTERN = re.compile(r'^[a-zA-Z0-9_=\-]+$')

# TODO: move from sending all chunks used for grounding eagerly to only sending links to 
# the original content in storage, it'll be more efficient overall
async def _report_grounding_tool(search_client: SearchClient, identifier_field: str, title_field: str, content_field: str, args: Any) -> None:
    sources = [s for s in args["sources"] if KEY_PATTERN.match(s)]
    list = " OR ".join(sources)
    print(f"Grounding source: {list}")
    # Use search instead of filter to align with how the index is structured
    search_results = await search_client.search(search_text=list, 
                                                search_fields=[identifier_field], 
                                                select=[identifier_field, title_field, content_field], 
                                                top=len(sources), 
                                                query_type="full")
    
    docs = []
    async for r in search_results:
        docs.append({"ID": r[identifier_field], "Name": r[title_field], "ingredients": r[content_field]})
    return ToolResult({"sources": docs}, ToolResultDirection.TO_CLIENT)

async def _show_all_tool(search_client: SearchClient, identifier_field: str, content_field: str) -> ToolResult:
    print("عرض جميع المنتجات المتاحة")
    
    # البحث عن جميع المنتجات بدون ترتيب
    search_results = await search_client.search(
        search_text="*", 
        query_type="simple",
        top=50,  # عرض حتى 50 منتج
        select=f"{identifier_field},Name,{content_field},Price"
        # إزالة order_by لأن حقل Name غير قابل للترتيب
    )
    
    result = "🍽️ **قائمة المطعم الكاملة** 🍽️\n\n"
    result_count = 0
    
    # تجميع المنتجات حسب النوع
    pizzas = []
    burgers = []
    others = []
    
    async for r in search_results:
        result_count += 1
        
        id_field = r.get(identifier_field, f"Item_{result_count}")
        name_field = r.get('Name', "منتج غير معروف")
        content_field_value = r.get(content_field, "بدون وصف")
        price = r.get('Price', 'غير محدد')
        
        item_info = f"[{id_field}] {name_field} - {price} جنيه"
        
        if "بيتزا" in name_field:
            pizzas.append(item_info)
        elif "برجر" in name_field:
            burgers.append(item_info)
        else:
            others.append(item_info)
    
    if pizzas:
        result += "🍕 **البيتزا:**\n"
        for pizza in pizzas:
            result += f"   {pizza}\n"
        result += "\n"
    
    if burgers:
        result += "🍔 **البرجر:**\n" 
        for burger in burgers:
            result += f"   {burger}\n"
        result += "\n"
            
    if others:
        result += "🍽️ **منتجات أخرى:**\n"
        for other in others:
            result += f"   {other}\n"
        result += "\n"
    
    result += f"📊 إجمالي المنتجات: {result_count}\n"
    result += "قل اسم أي منتج للحصول على تفاصيل أكثر!"
    
    return ToolResult(result, ToolResultDirection.TO_SERVER)

def attach_rag_tools(rtmt: RTMiddleTier,
    credentials: AzureKeyCredential | DefaultAzureCredential,
    search_endpoint: str, search_index: str,
    semantic_configuration: str | None,
    identifier_field: str,
    content_field: str,
    embedding_field: str,
    title_field: str,
    use_vector_query: bool
    ) -> None:
    if not isinstance(credentials, AzureKeyCredential):
        credentials.get_token("https://search.azure.com/.default") # warm this up before we start getting requests
    search_client = SearchClient(search_endpoint, search_index, credentials, user_agent="RTMiddleTier")

    # أدوات البحث الأساسية
    rtmt.tools["search"] = Tool(schema=_search_tool_schema, target=lambda args: _search_tool(search_client, semantic_configuration, identifier_field, content_field, embedding_field, use_vector_query, args))
    rtmt.tools["report_grounding"] = Tool(schema=_grounding_tool_schema, target=lambda args: _report_grounding_tool(search_client, identifier_field, title_field, content_field, args))
    rtmt.tools["show_all_items"] = Tool(schema=_show_all_tool_schema, target=lambda args: _show_all_tool(search_client, identifier_field, content_field))
    
    # أدوات إدارة الطلبات
    rtmt.tools["get_order_summary"] = Tool(schema=_get_order_summary_schema, target=_get_order_summary_tool)
    rtmt.tools["confirm_order"] = Tool(schema=_confirm_order_schema, target=_confirm_order_tool)
    rtmt.tools["clear_order"] = Tool(schema=_clear_order_schema, target=_clear_order_tool)
