"""
اختبار AI Search الدلالي للتحقق من الأسعار الحقيقية
"""
import os
from dotenv import load_dotenv
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

# تحميل الإعدادات
load_dotenv(os.path.join(os.path.dirname(__file__), 'app', 'backend', '.env'))

# إعداد العميل
search_key = os.environ.get("AZURE_SEARCH_API_KEY")
search_endpoint = os.environ.get("AZURE_SEARCH_ENDPOINT")
search_index = os.environ.get("AZURE_SEARCH_INDEX")

print(f"🔍 اختبار الأسعار في مؤشر: {search_index}")
print("="*60)

# إنشاء عميل البحث
search_client = SearchClient(
    endpoint=search_endpoint,
    index_name=search_index,
    credential=AzureKeyCredential(search_key)
)

# الاختبارات المطلوبة
test_searches = [
    {"query": "بيتزا تونة كبير", "expected_price": "185", "description": "بيتزا تونه كبير"},
    {"query": "onion rings", "expected_price": "30", "description": "طبق اونيون رينج"},
    {"query": "بيتزا سي فود وسط", "expected_price": "185", "description": "بيتزا سي فود وسط"},
    {"query": "large tuna pizza", "expected_price": "185", "description": "بيتزا تونة كبير"},
    {"query": "medium seafood pizza", "expected_price": "185", "description": "بيتزا سي فود وسط"}
]

def test_search(query, expected_price, description):
    print(f"\n🔍 البحث عن: {query}")
    print(f"📋 المطلوب: {description}")
    print(f"💰 السعر المتوقع: {expected_price} جنيه")
    
    try:
        # البحث العادي
        results = search_client.search(
            search_text=query,
            select=["ID", "Name", "Price", "ingredients"],
            top=3
        )
        
        print("\n📊 النتائج من البحث العادي:")
        found_correct = False
        for i, doc in enumerate(results, 1):
            name = doc.get('Name', 'غير متوفر')
            price = str(doc.get('Price', 'غير متوفر'))
            print(f"   {i}. 📝 {name}")
            print(f"      💰 السعر: {price} جنيه")
            if 'ingredients' in doc:
                print(f"      🥗 المكونات: {doc['ingredients']}")
            print(f"      🔢 ID: {doc.get('ID', 'غير متوفر')}")
            
            # التحقق من صحة السعر
            if price == expected_price:
                print(f"      ✅ السعر صحيح!")
                found_correct = True
            elif i == 1:  # النتيجة الأولى
                print(f"      ❌ السعر خاطئ! متوقع: {expected_price}")
        
        if not found_correct:
            print("      ⚠️ لم يتم العثور على السعر الصحيح في النتائج")
            
    except Exception as e:
        print(f"❌ خطأ في البحث: {e}")

# تنفيذ جميع الاختبارات
for test in test_searches:
    test_search(test["query"], test["expected_price"], test["description"])
    
print("\n" + "="*60)
print("🔍 اختبار البحث المباشر بالأسماء الدقيقة:")

# اختبار مباشر بالأسماء
direct_searches = [
    "Large Tuna Pizza",
    "Medium Seafood Pizza", 
    "Onion Rings"
]

for search_term in direct_searches:
    print(f"\n🎯 البحث المباشر: {search_term}")
    try:
        results = search_client.search(
            search_text=search_term,
            select=["ID", "Name", "Price", "ingredients"],
            top=1
        )
        
        for doc in results:
            print(f"   📝 الاسم: {doc.get('Name', 'غير متوفر')}")
            print(f"   💰 السعر: {doc.get('Price', 'غير متوفر')} جنيه")
            print(f"   🔢 ID: {doc.get('ID', 'غير متوفر')}")
            break
    except Exception as e:
        print(f"   ❌ خطأ: {e}")

print("\n🏁 انتهى الاختبار")
