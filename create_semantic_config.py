#!/usr/bin/env python3
"""
إنشاء إعداد البحث الدلالي تلقائياً في Azure AI Search
يتطلب Admin Key من Azure Portal
"""

import os
import json
from dotenv import load_dotenv
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SemanticConfiguration, 
    SemanticPrioritizedFields, 
    SemanticField,
    SemanticSearch
)
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError

def get_admin_key():
    """قراءة Admin Key من ملف .env"""
    
    admin_key = os.getenv("AZURE_SEARCH_ADMIN_KEY")
    
    if not admin_key:
        print("❌ Admin Key غير موجود في ملف .env")
        print("📝 أضف المتغير التالي في app/backend/.env:")
        print("   AZURE_SEARCH_ADMIN_KEY=your_admin_key_here")
        print()
        print("📍 يمكنك الحصول على Admin Key من:")
        print("   1️⃣ Azure Portal")
        print("   2️⃣ AI Search Service")
        print("   3️⃣ Settings -> Keys")
        print("   4️⃣ انسخ 'Primary admin key' أو 'Secondary admin key'")
        return None
    
    if len(admin_key) < 30:
        print("⚠️ Admin Key قصير جداً، تأكد من نسخ المفتاح كاملاً")
        return None
    
    print("✅ تم العثور على Admin Key في ملف .env")
    return admin_key

def create_semantic_configuration():
    """إنشاء إعداد البحث الدلالي"""
    
    # تحميل الإعدادات
    load_dotenv("app/backend/.env")
    
    search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
    search_index = os.getenv("AZURE_SEARCH_INDEX")
    semantic_config_name = os.getenv("AZURE_SEARCH_SEMANTIC_CONFIGURATION")
    
    print("🎯 إنشاء إعداد البحث الدلالي")
    print("=" * 50)
    print(f"🔗 الخادم: {search_endpoint}")
    print(f"📊 الفهرس: {search_index}")
    print(f"🧠 اسم الإعداد: {semantic_config_name}")
    print()
    
    # الحصول على Admin Key
    admin_key = get_admin_key()
    if not admin_key:
        return False
    
    try:
        # إنشاء Index Client
        print("🔗 الاتصال بـ Azure Search...")
        client = SearchIndexClient(
            endpoint=search_endpoint,
            credential=AzureKeyCredential(admin_key)
        )
        
        # الحصول على الفهرس الحالي
        print("📋 جلب معلومات الفهرس...")
        index = client.get_index(search_index)
        
        print(f"✅ تم جلب الفهرس: {index.name}")
        
        # عرض الحقول المتاحة
        print("\n📊 الحقول المتاحة في الفهرس:")
        for field in index.fields:
            print(f"   🔹 {field.name} ({field.type}) - searchable: {field.searchable}")
        
        # إنشاء الإعداد الدلالي
        print(f"\n🧠 إنشاء الإعداد الدلالي: {semantic_config_name}")
        
        semantic_config = SemanticConfiguration(
            name=semantic_config_name,
            prioritized_fields=SemanticPrioritizedFields(
                title_field=SemanticField(field_name="Name"),
                content_fields=[SemanticField(field_name="ingredients")]
            )
        )
        
        # التحقق من وجود semantic_search في الفهرس
        if not hasattr(index, 'semantic_search') or index.semantic_search is None:
            print("🔧 إنشاء قسم البحث الدلالي...")
            index.semantic_search = SemanticSearch(configurations=[])
        
        if not index.semantic_search.configurations:
            index.semantic_search.configurations = []
        
        # التحقق من عدم وجود الإعداد مسبقاً
        existing_config = None
        for config in index.semantic_search.configurations:
            if config.name == semantic_config_name:
                existing_config = config
                break
        
        if existing_config:
            print(f"⚠️ الإعداد {semantic_config_name} موجود مسبقاً")
            print("🔄 سيتم تحديثه...")
            index.semantic_search.configurations = [
                config for config in index.semantic_search.configurations 
                if config.name != semantic_config_name
            ]
        
        # إضافة الإعداد الجديد
        index.semantic_search.configurations.append(semantic_config)
        
        # تحديث الفهرس
        print("💾 حفظ التغييرات...")
        result = client.create_or_update_index(index)
        
        print("\n🎉 تم إنشاء إعداد البحث الدلالي بنجاح!")
        print(f"✅ اسم الإعداد: {semantic_config_name}")
        print(f"🏷️ حقل العنوان: Name")
        print(f"📄 حقل المحتوى: ingredients")
        print()
        print("🔄 يمكنك الآن استخدام البحث الدلالي في التطبيق")
        
        return True
        
    except HttpResponseError as e:
        error_msg = str(e)
        print(f"\n❌ خطأ HTTP: {e.status_code}")
        print(f"📝 الرسالة: {e.message}")
        
        if e.status_code == 401:
            print("💡 السبب المحتمل: Admin Key خاطئ")
            print("🔧 الحل: تأكد من استخدام Admin Key وليس Query Key")
        elif e.status_code == 403:
            print("💡 السبب المحتمل: لا توجد صلاحيات كافية")
            print("🔧 الحل: تأكد من صلاحيات الكتابة على الفهرس")
        elif e.status_code == 404:
            print("💡 السبب المحتمل: الفهرس غير موجود")
            print(f"🔧 الحل: تأكد من اسم الفهرس: {search_index}")
        
        return False
        
    except Exception as e:
        print(f"\n❌ خطأ غير متوقع: {str(e)}")
        print("💡 تأكد من:")
        print("   🔹 Admin Key صحيح")
        print("   🔹 اتصال الإنترنت")
        print("   🔹 صلاحيات الوصول")
        
        return False

def test_semantic_search_after_creation():
    """اختبار البحث الدلالي بعد إنشاء الإعداد"""
    
    print("\n🧪 اختبار البحث الدلالي بعد الإنشاء...")
    
    load_dotenv("app/backend/.env")
    
    search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
    search_key = os.getenv("AZURE_SEARCH_API_KEY")
    search_index = os.getenv("AZURE_SEARCH_INDEX")
    semantic_config = os.getenv("AZURE_SEARCH_SEMANTIC_CONFIGURATION")
    
    try:
        from azure.search.documents import SearchClient
        
        search_client = SearchClient(
            endpoint=search_endpoint,
            index_name=search_index,
            credential=AzureKeyCredential(search_key)
        )
        
        # اختبار البحث الدلالي
        results = search_client.search(
            search_text="pizza",
            query_type="semantic",
            semantic_configuration_name=semantic_config,
            top=3
        )
        
        result_count = 0
        for result in results:
            result_count += 1
            title = result.get('Name', 'بلا عنوان')
            score = result.get('@search.score', 0)
            semantic_score = result.get('@search.reranker_score', 'غير متوفر')
            
            print(f"   🧠 النتيجة {result_count}: {title}")
            print(f"      📊 نقاط البحث: {score:.2f}")
            print(f"      🎯 نقاط دلالية: {semantic_score}")
            print()
        
        if result_count > 0:
            print(f"🎉 البحث الدلالي يعمل بنجاح! وجد {result_count} نتائج")
            return True
        else:
            print("⚠️ البحث الدلالي لا يعيد نتائج")
            return False
            
    except Exception as e:
        print(f"❌ فشل اختبار البحث الدلالي: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 مساعد إنشاء البحث الدلالي")
    print("=" * 50)
    print()
    
    success = create_semantic_configuration()
    
    if success:
        print("\n" + "=" * 50)
        test_semantic_search_after_creation()
    else:
        print("\n❌ فشل في إنشاء البحث الدلالي")
        print("💡 جرب الإنشاء اليدوي في Azure Portal:")
        print("   🌐 https://portal.azure.com")
        print("   📋 AI Search -> neslst11mune -> Indexes -> english22-index")
        print("   🧠 Semantic configurations -> Add semantic configuration")
    
    print("\n" + "=" * 50)
    print("✅ انتهى المساعد")
