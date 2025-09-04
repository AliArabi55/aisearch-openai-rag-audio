"""
فحص التكوينات الدلالية المتاحة في المؤشر
"""
import os
from dotenv import load_dotenv
from azure.search.documents.indexes import SearchIndexClient
from azure.core.credentials import AzureKeyCredential

# تحميل الإعدادات
load_dotenv(os.path.join(os.path.dirname(__file__), 'app', 'backend', '.env'))

# إعداد العميل
search_key = os.environ.get("AZURE_SEARCH_API_KEY")
search_endpoint = os.environ.get("AZURE_SEARCH_ENDPOINT")
search_index = os.environ.get("AZURE_SEARCH_INDEX")

# إنشاء عميل إدارة المؤشرات
index_client = SearchIndexClient(
    endpoint=search_endpoint,
    credential=AzureKeyCredential(search_key)
)

try:
    # الحصول على معلومات المؤشر
    index = index_client.get_index(search_index)
    
    print(f"📊 المؤشر: {index.name}")
    print(f"📋 الحقول:")
    for field in index.fields:
        print(f"   - {field.name}: {field.type}")
    
    print(f"\n🧠 التكوينات الدلالية:")
    if index.semantic_search and index.semantic_search.configurations:
        for config in index.semantic_search.configurations:
            print(f"   - {config.name}")
    else:
        print("   لا توجد تكوينات دلالية")
        
except Exception as e:
    print(f"❌ خطأ: {e}")
