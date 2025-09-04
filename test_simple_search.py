"""
اختبار البحث البسيط بدون semantic
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

print(f"🔍 Endpoint: {search_endpoint}")
print(f"📊 Index: {search_index}")
print(f"🔑 Key: {search_key[:10]}..." if search_key else "No key")

# إنشاء عميل البحث
search_client = SearchClient(
    endpoint=search_endpoint,
    index_name=search_index,
    credential=AzureKeyCredential(search_key)
)

# تنفيذ بحث بسيط
search_query = "تونة"
print(f"\n🔍 البحث عن: {search_query}")

try:
    # البحث البسيط
    results = search_client.search(
        search_text=search_query,
        select=["ID", "Name", "Price", "ingredients"],
        top=3
    )
    
    print("\n📋 النتائج:")
    found_results = False
    for i, doc in enumerate(results, 1):
        found_results = True
        print(f"\n{i}. 📝 الاسم: {doc.get('Name', 'غير متوفر')}")
        if 'Price' in doc:
            print(f"   💰 السعر: {doc['Price']}")
        if 'ingredients' in doc:
            print(f"   🥗 المكونات: {doc['ingredients']}")
        print(f"   🔢 ID: {doc.get('ID', 'غير متوفر')}")
    
    if not found_results:
        print("❌ لم يتم العثور على نتائج")
        
except Exception as e:
    print(f"❌ خطأ في البحث: {e}")

# اختبار بحث آخر
print("\n" + "="*50)
search_query2 = "pizza"
print(f"🔍 البحث عن: {search_query2}")

try:
    results2 = search_client.search(
        search_text=search_query2,
        select=["ID", "Name", "Price", "ingredients"],
        top=3
    )
    
    print("\n📋 النتائج:")
    found_results2 = False
    for i, doc in enumerate(results2, 1):
        found_results2 = True
        print(f"\n{i}. 📝 الاسم: {doc.get('Name', 'غير متوفر')}")
        if 'Price' in doc:
            print(f"   💰 السعر: {doc['Price']}")
        if 'ingredients' in doc:
            print(f"   🥗 المكونات: {doc['ingredients']}")
        print(f"   🔢 ID: {doc.get('ID', 'غير متوفر')}")
    
    if not found_results2:
        print("❌ لم يتم العثور على نتائج")
        
except Exception as e:
    print(f"❌ خطأ في البحث: {e}")
