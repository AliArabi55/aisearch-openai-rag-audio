"""
🔧 فحص التكوينات الدلالية المتاحة في Azure Search
=========================================================
"""
import os
from dotenv import load_dotenv
from azure.search.documents.indexes import SearchIndexClient
from azure.core.credentials import AzureKeyCredential

# تحميل الإعدادات
load_dotenv(os.path.join(os.path.dirname(__file__), 'app', 'backend', '.env'))

print("🔍 فحص التكوينات الدلالية المتاحة")
print("=" * 50)

search_endpoint = os.environ.get("AZURE_SEARCH_ENDPOINT")
search_index = os.environ.get("AZURE_SEARCH_INDEX") 
search_key = os.environ.get("AZURE_SEARCH_API_KEY")

print(f"🌐 الخادم: {search_endpoint}")
print(f"📋 الفهرس: {search_index}")

try:
    # إنشاء عميل الفهرس
    index_client = SearchIndexClient(
        endpoint=search_endpoint,
        credential=AzureKeyCredential(search_key)
    )
    
    # الحصول على تفاصيل الفهرس
    index = index_client.get_index(search_index)
    
    print("\n🧠 التكوينات الدلالية المتاحة:")
    if hasattr(index, 'semantic_search') and index.semantic_search:
        configurations = index.semantic_search.configurations
        if configurations:
            for i, config in enumerate(configurations, 1):
                print(f"  {i}. {config.name}")
        else:
            print("  ❌ لا توجد تكوينات دلالية")
    else:
        print("  ❌ البحث الدلالي غير مفعل في هذا الفهرس")
        
    print("\n📊 الحقول المتاحة:")
    for field in index.fields:
        print(f"  - {field.name} ({field.type})")
        
except Exception as e:
    print(f"❌ خطأ: {e}")
