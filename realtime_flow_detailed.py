"""
🎯 محاكي شامل لمسار طلب: "أريد بيتزا تونة وسط"
=====================================================

هذا الملف يحاكي بالتفصيل جميع العمليات التي تحدث في النظام
"""
import os
import sys
import asyncio
from pathlib import Path

# إضافة مسار backend
backend_path = Path(__file__).parent / 'app' / 'backend'
sys.path.insert(0, str(backend_path))

from dotenv import load_dotenv
load_dotenv(backend_path / '.env')

# استيراد الموديولات المطلوبة
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

print("🎯 محاكي شامل لطلب: 'أريد بيتزا تونة وسط'")
print("=" * 80)

async def simulate_realtime_request():
    """محاكي لطلب الريل تايم الكامل"""
    
    user_query = "أريد بيتزا تونة وسط"
    
    print(f"👤 المستخدم يقول: '{user_query}'")
    print()
    
    # =================== الخطوة 1: تحويل الصوت لنص ===================
    print("1️⃣ 🎤 تحويل الصوت إلى نص:")
    print("   🔄 OpenAI Realtime API يحول الصوت")
    print(f"   ✅ النص المستخرج: '{user_query}'")
    print()
    
    # =================== الخطوة 2: فهم الطلب ===================
    print("2️⃣ 🤖 OpenAI يفهم الطلب:")
    print("   🧠 تحليل النص...")
    print("   🎯 اكتشاف نية المستخدم: طلب بحث عن منتج")
    print("   🔧 اختيار الأداة: search()")
    print(f"   📤 استدعاء: search(query='{user_query}')")
    print()
    
    # =================== الخطوة 3: ragtools.py ===================
    print("3️⃣ 🔧 ragtools.py يستقبل الطلب:")
    print("   📥 _search_tool() تبدأ المعالجة")
    print(f"   📝 المعامل المستقبل: query='{user_query}'")
    print()
    
    # =================== الخطوة 4: الذاكرة المؤقتة ===================
    print("4️⃣ 🧠 فحص الذاكرة المؤقتة:")
    print(f"   🔍 البحث في SEARCH_CACHE عن: '{user_query}'")
    print("   ❌ لم يُعثر على نتيجة محفوظة")
    print("   ⏭️ الانتقال للبحث الجديد")
    print()
    
    # =================== الخطوة 5: الترجمة ===================
    print("5️⃣ 🌍 ترجمة الطلب:")
    print("   📝 النص الأصلي: 'أريد بيتزا تونة وسط'")
    print("   🔄 translation_utils.py يترجم...")
    
    # قاموس الترجمة
    translation_dict = {
        "أريد": "",  # كلمة طلب - تُحذف
        "بيتزا": "pizza",
        "تونة": "tuna", 
        "وسط": "medium"
    }
    
    translated = "pizza tuna medium"
    print(f"   ✅ النص المترجم: '{translated}'")
    print("   📋 الكلمات المترجمة:")
    for ar, en in translation_dict.items():
        if en:
            print(f"      - {ar} → {en}")
    print()
    
    # =================== الخطوة 6: البحث في Azure ===================
    print("6️⃣ 🔍 البحث في Azure AI Search:")
    search_endpoint = os.environ.get("AZURE_SEARCH_ENDPOINT")
    search_index = os.environ.get("AZURE_SEARCH_INDEX")
    search_key = os.environ.get("AZURE_SEARCH_API_KEY")
    
    print(f"   🌐 الخادم: {search_endpoint}")
    print(f"   📋 الفهرس: {search_index}")
    print(f"   🔧 نوع البحث: Semantic Search")
    print(f"   ⚙️ التكوين: english22-Semantic-configuration")
    print(f"   🎯 النص المبحوث: '{translated}'")
    print()
    
    # إجراء البحث الفعلي
    try:
        search_client = SearchClient(
            endpoint=search_endpoint,
            index_name=search_index,
            credential=AzureKeyCredential(search_key)
        )
        
        print("   🔄 إرسال طلب البحث...")
        results = search_client.search(
            search_text=translated,
            query_type="semantic",
            semantic_configuration_name="english22-Semantic-configuration",
            select=["ID", "Name", "Price", "ingredients"],
            top=3
        )
        
        print("   📊 استلام النتائج من Azure:")
        found_items = []
        for i, doc in enumerate(results, 1):
            name = doc.get('Name', 'غير متوفر')
            price = doc.get('Price', 'غير متوفر')
            ingredients = doc.get('ingredients', 'غير متوفر')
            item_id = doc.get('ID', 'غير متوفر')
            
            print(f"      {i}. 🆔 ID: {item_id}")
            print(f"         📝 الاسم: {name}")
            print(f"         💰 السعر: {price} جنيه")
            print(f"         🥄 المكونات: {ingredients[:100]}...")
            
            found_items.append({
                'id': item_id,
                'name': name,
                'price': price,
                'ingredients': ingredients
            })
            
        print()
        
        # =================== الخطوة 7: تنسيق النتيجة ===================
        if found_items:
            best_match = found_items[0]
            print("7️⃣ 📤 تنسيق النتيجة للموديل:")
            print("   🎯 اختيار أفضل نتيجة...")
            print(f"   📝 المنتج: {best_match['name']}")
            print(f"   💰 السعر: {best_match['price']} جنيه")
            print("   🔧 model_input_settings.py ينسق البيانات...")
            
            formatted_response = f"{best_match['name']} متوفر بسعر {best_match['price']} جنيه"
            print(f"   ✅ النص المُعد للموديل: '{formatted_response}'")
            print()
            
            # =================== الخطوة 8: الذاكرة المؤقتة ===================
            print("8️⃣ 💾 حفظ في الذاكرة المؤقتة:")
            print(f"   🔑 المفتاح: '{user_query}'")
            print(f"   📄 القيمة: النتيجة المنسقة")
            print(f"   ⏰ مدة الحفظ: 5 دقائق")
            print("   ✅ تم الحفظ بنجاح")
            print()
            
            # =================== الخطوة 9: الرد للموديل ===================
            print("9️⃣ 📤 إرسال النتيجة إلى OpenAI:")
            print(f"   📨 ToolResult.text: '{formatted_response}'")
            print("   🔄 rtmt.py يرسل النتيجة للموديل")
            print()
            
            # =================== الخطوة 10: النطق ===================
            print("🔟 🗣️ OpenAI Realtime ينطق الإجابة:")
            print(f"   🎤 الرد المنطوق: '{formatted_response}'")
            print("   🔊 تحويل النص إلى صوت")
            print("   📻 إرسال الصوت للمستخدم")
            print()
            
        else:
            print("❌ لم يتم العثور على نتائج")
            
    except Exception as e:
        print(f"   ❌ خطأ في البحث: {e}")
    
    # =================== ملخص المسار ===================
    print("📋 ملخص المسار الكامل:")
    print("=" * 50)
    print("👤 صوت المستخدم")
    print("   ↓")
    print("🎤 OpenAI Realtime (تحويل صوت → نص)")
    print("   ↓") 
    print("🤖 OpenAI (فهم الطلب)")
    print("   ↓")
    print("🔧 ragtools.py (معالجة البحث)")
    print("   ↓")
    print("🧠 فحص الذاكرة المؤقتة")
    print("   ↓")
    print("🌍 ترجمة عربي → إنجليزي")
    print("   ↓")
    print("🔍 Azure AI Search (البحث الدلالي)")
    print("   ↓")
    print("📊 استرجاع النتائج + الأسعار")
    print("   ↓")
    print("📤 تنسيق النتيجة للموديل")
    print("   ↓")
    print("💾 حفظ في الذاكرة المؤقتة (5 دقائق)")
    print("   ↓")
    print("🗣️ OpenAI Realtime (نطق الإجابة)")
    print("   ↓")
    print("🔊 صوت للمستخدم")
    
    print("\n🎯 النقاط الأساسية:")
    print("=" * 30)
    print("✅ جميع الأسعار من Azure AI Search")
    print("✅ لا توجد قاعدة بيانات محلية")
    print("✅ البحث الدلالي يفهم المعنى")
    print("✅ الذاكرة المؤقتة تسرع الردود")
    print("✅ الترجمة تلقائية ودقيقة")

if __name__ == "__main__":
    asyncio.run(simulate_realtime_request())
