"""
🔍 محاكي شامل: مسار "أريد بيتزا تونة وسط" مع البحث الدلالي
================================================================

هذا المحاكي يوضح خطوة بخطوة ما يحدث عندما يسأل المستخدم عن "أريد بيتزا تونة وسط"
مع استخدام البحث الدلالي (Semantic Search)
"""
import os
import sys
from dotenv import load_dotenv
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

# تحميل الإعدادات
load_dotenv(os.path.join(os.path.dirname(__file__), 'app', 'backend', '.env'))

print("🎯 محاكي مسار: 'أريد بيتزا تونة وسط' مع البحث الدلالي")
print("=" * 80)

# عرض الإعدادات
print("🔧 إعدادات Azure Search:")
search_endpoint = os.environ.get("AZURE_SEARCH_ENDPOINT")
search_index = os.environ.get("AZURE_SEARCH_INDEX") 
search_key = os.environ.get("AZURE_SEARCH_API_KEY")
semantic_config = os.environ.get("AZURE_SEARCH_SEMANTIC_CONFIGURATION")

print(f"🌐 الخادم: {search_endpoint}")
print(f"📋 الفهرس: {search_index}")
print(f"🧠 التكوين الدلالي: {semantic_config}")
print(f"🔑 المفتاح: {'✅ موجود' if search_key else '❌ مفقود'}")

print("\n" + "=" * 80)
print("🔄 المسار الكامل خطوة بخطوة:")

# الخطوة 1: المستخدم يتكلم
print("\n1️⃣ 🎤 المستخدم يقول: 'أريد بيتزا تونة وسط'")
user_input = "أريد بيتزا تونة وسط"
print(f"   📝 النص الملتقط: {user_input}")

# الخطوة 2: OpenAI يفهم الطلب
print("\n2️⃣ 🤖 OpenAI Realtime يحلل الطلب:")
print("   🧠 فهم الطلب: المستخدم يريد البحث عن منتج")
print("   🔧 استدعاء الأداة: search(query='أريد بيتزا تونة وسط')")

# الخطوة 3: فحص الذاكرة المؤقتة
print("\n3️⃣ 🧠 ragtools.py - فحص الذاكرة المؤقتة:")
print(f"   🔍 البحث عن: '{user_input}' في الذاكرة")
print("   ❌ لم يتم العثور على النتيجة في الذاكرة - سيتم البحث الجديد")

# الخطوة 4: الترجمة
print("\n4️⃣ 🌍 translation_utils.py - ترجمة الطلب:")
# محاكاة الترجمة
translation_dict = {
    "أريد": "want",
    "بيتزا": "pizza", 
    "تونة": "tuna",
    "وسط": "medium"
}

words = user_input.split()
translated_words = []
for word in words:
    if word in translation_dict:
        translated_words.append(translation_dict[word])
    else:
        translated_words.append(word)

english_query = " ".join(translated_words)
print(f"   📝 الطلب الأصلي: {user_input}")
print(f"   🔄 بعد الترجمة: {english_query}")
print(f"   ✅ الاستعلام النهائي: 'pizza tuna medium'")

# الخطوة 5: إعداد البحث في Azure
print("\n5️⃣ 🔍 إعداد البحث في Azure AI Search:")
print(f"   🌐 الاتصال بـ: {search_endpoint}")
print(f"   📋 في الفهرس: {search_index}")
print(f"   🧠 نوع البحث: Semantic Search")
print(f"   ⚙️ التكوين: {semantic_config}")

# إنشاء عميل البحث
try:
    search_client = SearchClient(
        endpoint=search_endpoint,
        index_name=search_index,
        credential=AzureKeyCredential(search_key)
    )
    print("   ✅ تم إنشاء عميل البحث بنجاح")
except Exception as e:
    print(f"   ❌ خطأ في إنشاء العميل: {e}")

# الخطوة 6: تنفيذ البحث الدلالي
print("\n6️⃣ 📊 تنفيذ البحث الدلالي:")
try:
    print(f"   🔍 البحث عن: 'pizza tuna medium'")
    print("   📤 إرسال الطلب إلى Azure...")
    
    search_results = search_client.search(
        search_text="pizza tuna medium",
        query_type="semantic",
        semantic_configuration_name=semantic_config,
        select=["ID", "Name", "Price", "ingredients"],
        top=3,
        search_fields=["ingredients"],  # البحث في المكونات فقط
        query_caption="extractive",
        query_answer="extractive"
    )
    
    print("   ✅ تم استلام النتائج من Azure")
    
    # عرض النتائج
    print("\n7️⃣ 📋 النتائج من Azure AI Search:")
    results_list = list(search_results)
    
    if results_list:
        for i, doc in enumerate(results_list, 1):
            name = doc.get('Name', 'غير متوفر')
            price = doc.get('Price', 'غير متوفر') 
            ingredients = doc.get('ingredients', 'غير متوفر')
            doc_id = doc.get('ID', 'غير متوفر')
            
            print(f"   {i}. 🆔 ID: {doc_id}")
            print(f"      📝 الاسم: {name}")
            print(f"      💰 السعر: {price} جنيه")
            print(f"      🥄 المكونات: {ingredients[:100]}...")
            print()
            
        # أفضل نتيجة
        best_match = results_list[0]
        best_name = best_match.get('Name', '')
        best_price = best_match.get('Price', '')
        
        print("8️⃣ 🎯 model_input_settings.py - تنسيق النتيجة:")
        formatted_response = f"{best_name} متوفر بسعر {best_price} جنيه"
        print(f"   📝 النص المُنسق للموديل: {formatted_response}")
        
        print("\n9️⃣ 💾 حفظ في الذاكرة المؤقتة:")
        print(f"   🔑 المفتاح: '{user_input}'")
        print(f"   💾 القيمة: '{formatted_response}'")
        print(f"   ⏱️ مدة البقاء: 5 دقائق")
        
        print("\n🔟 📤 إرسال النتيجة لـ OpenAI Realtime:")
        print(f"   📨 النص المُرسل: '{formatted_response}'")
        
        print("\n1️⃣1️⃣ 🗣️ OpenAI ينطق الإجابة:")
        print(f"   🎤 المستخدم يسمع: '{formatted_response}'")
        
    else:
        print("   ❌ لم يتم العثور على نتائج")
        
except Exception as e:
    print(f"   ❌ خطأ في البحث: {e}")

print("\n" + "=" * 80)
print("🎯 ملخص المسار:")
print("📍 المصدر الوحيد للأسعار: Azure AI Search")
print("📍 نوع البحث: Semantic Search (بحث دلالي)")
print("📍 الترجمة: من العربي للإنجليزي تلقائياً")
print("📍 الذاكرة المؤقتة: 5 دقائق فقط")
print("📍 جميع البيانات: حية ومباشرة من السحابة")

print("\n🏁 انتهى المحاكي الشامل للنظام!")
