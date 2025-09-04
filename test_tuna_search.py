"""
اختبار البحث عن Tuna Pizza
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

# إنشاء عميل البحث
search_client = SearchClient(
    endpoint=search_endpoint,
    index_name=search_index,
    credential=AzureKeyCredential(search_key)
)

# البحث عن تونة
searches = ["tuna", "Tuna Pizza", "Medium Tuna", "Tuna Pizza Medium"]

for search_query in searches:
    print(f"\n🔍 البحث عن: {search_query}")
    print("="*50)
    
    try:
        results = search_client.search(
            search_text=search_query,
            select=["ID", "Name", "Price", "ingredients"],
            top=5
        )
        
        found_results = False
        for i, doc in enumerate(results, 1):
            found_results = True
            print(f"\n{i}. 📝 الاسم: {doc.get('Name', 'غير متوفر')}")
            if 'Price' in doc:
                print(f"   💰 السعر: {doc['Price']} جنيه")
            if 'ingredients' in doc:
                print(f"   🥗 المكونات: {doc['ingredients']}")
            print(f"   🔢 ID: {doc.get('ID', 'غير متوفر')}")
        
        if not found_results:
            print("❌ لم يتم العثور على نتائج")
            
    except Exception as e:
        print(f"❌ خطأ في البحث: {e}")
