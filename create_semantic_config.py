#!/usr/bin/env python3
"""
إنشاء إعداد البحث الدلالي باستخدام Python SDK
يتطلب مفتاح Admin Key وليس مفتاح البحث العادي
"""

import os
from dotenv import load_dotenv
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import SemanticConfiguration, SemanticPrioritizedFields, SemanticField
from azure.core.credentials import AzureKeyCredential

def create_semantic_configuration():
    """إنشاء إعداد البحث الدلالي"""
    
    load_dotenv("app/backend/.env")
    
    search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
    # ⚠️ يحتاج Admin Key وليس API Key العادي
    admin_key = input("أدخل Admin Key من Azure Portal: ")
    search_index = os.getenv("AZURE_SEARCH_INDEX")
    
    print(f"🔧 إنشاء إعداد البحث الدلالي...")
    print(f"🔗 الخادم: {search_endpoint}")
    print(f"📊 الفهرس: {search_index}")
    
    try:
        # إنشاء Index Client
        client = SearchIndexClient(
            endpoint=search_endpoint,
            credential=AzureKeyCredential(admin_key)
        )
        
        # الحصول على الفهرس الحالي
        index = client.get_index(search_index)
        
        # إنشاء الإعداد الدلالي
        semantic_config = SemanticConfiguration(
            name="english22-semantic-configuration",
            prioritized_fields=SemanticPrioritizedFields(
                title_field=SemanticField(field_name="Name"),
                content_fields=[SemanticField(field_name="ingredients")]
            )
        )
        
        # إضافة الإعداد للفهرس
        if not index.semantic_search:
            index.semantic_search = {}
        
        if not index.semantic_search.configurations:
            index.semantic_search.configurations = []
        
        index.semantic_search.configurations.append(semantic_config)
        
        # تحديث الفهرس
        client.create_or_update_index(index)
        
        print("✅ تم إنشاء إعداد البحث الدلالي بنجاح!")
        print("🔄 يمكنك الآن استخدام البحث الدلالي")
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في إنشاء الإعداد: {str(e)}")
        print("💡 تأكد من استخدام Admin Key وليس API Key")
        return False

if __name__ == "__main__":
    create_semantic_configuration()
