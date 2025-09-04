#!/usr/bin/env python3
"""
دليل إنشاء البحث الدلالي في Azure AI Search
خطوات مفصلة لحل مشكلة البحث الدلالي
"""

def create_semantic_search_guide():
    """دليل إنشاء البحث الدلالي"""
    
    print("🎯 دليل إنشاء البحث الدلالي في Azure AI Search")
    print("=" * 70)
    print()
    
    print("📋 معلومات الفهرس الحالي:")
    print("   🔗 الخادم: https://neslst11mune.search.windows.net")
    print("   📊 الفهرس: english22-index")
    print("   ❌ المشكلة: إعداد البحث الدلالي غير موجود")
    print()
    
    print("🚀 الحلول المتاحة:")
    print("=" * 40)
    print()
    
    print("🔧 الحل 1: إنشاء البحث الدلالي عبر Azure Portal")
    print("   1️⃣ اذهب إلى Azure Portal: https://portal.azure.com")
    print("   2️⃣ ابحث عن 'AI Search' أو 'Search services'")
    print("   3️⃣ اختر الخدمة: neslst11mune")
    print("   4️⃣ اذهب لـ Indexes -> english22-index")
    print("   5️⃣ اضغط على 'Semantic configurations'")
    print("   6️⃣ اضغط '+ Add semantic configuration'")
    print("   7️⃣ أدخل البيانات التالية:")
    print("      📝 Name: english22-semantic-configuration")
    print("      🏷️ Title field: Name")
    print("      📄 Content fields: ingredients")
    print("      🔖 Keywords fields: (اختياري)")
    print("   8️⃣ اضغط Save")
    print()
    
    print("💡 الحل 2: استخدام Azure CLI")
    print("   1️⃣ تشغيل Azure CLI:")
    print("      az login")
    print("   2️⃣ إنشاء الإعداد الدلالي:")
    print('      az search semantic-configuration create \\')
    print('        --resource-group <resource-group-name> \\')
    print('        --service-name neslst11mune \\')
    print('        --index-name english22-index \\')
    print('        --name english22-semantic-configuration \\')
    print('        --title-field Name \\')
    print('        --content-fields ingredients')
    print()
    
    print("🔧 الحل 3: استخدام Python SDK (للمطورين)")
    print("   📄 انظر الملف: create_semantic_config.py")
    print()
    
    print("⚠️ متطلبات مهمة:")
    print("   🏷️ يجب أن يكون الفهرس يحتوي على الحقول:")
    print("      - Name (للعناوين)")
    print("      - ingredients (للمحتوى)")
    print("   💰 البحث الدلالي يتطلب طبقة Standard أو أعلى")
    print("   🌍 البحث الدلالي متاح في مناطق معينة فقط")
    print()
    
    print("✅ بعد إنشاء الإعداد الدلالي:")
    print("   1️⃣ أعد تشغيل التطبيق")
    print("   2️⃣ اختبر البحث الدلالي باستخدام: test_semantic_directly.py")
    print("   3️⃣ يجب أن يعمل البحث الدلالي بنجاح!")
    print()
    
    print("🔍 لفحص الإعدادات الحالية:")
    print("   🌐 Azure Portal -> AI Search -> neslst11mune -> Indexes -> english22-index")
    print("   📊 تحقق من وجود 'Semantic configurations'")
    print()
    
    print("💡 نصائح إضافية:")
    print("   🚀 البحث الدلالي يحسن دقة النتائج بشكل كبير")
    print("   📈 يستخدم AI لفهم معنى الاستعلام بدلاً من مطابقة الكلمات فقط")
    print("   🎯 مفيد جداً للبحث عن المعاني والمفاهيم")
    print()
    
    print("🆘 إذا واجهت مشاكل:")
    print("   📧 تحقق من أن لديك صلاحيات الكتابة على Azure Search")
    print("   💰 تأكد من أن الخطة تدعم البحث الدلالي")
    print("   🌍 تأكد من أن المنطقة تدعم البحث الدلالي")
    print()
    
    return True

def create_python_solution():
    """إنشاء حل Python لإنشاء البحث الدلالي"""
    
    python_code = '''#!/usr/bin/env python3
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
'''
    
    with open("create_semantic_config.py", "w", encoding="utf-8") as f:
        f.write(python_code)
    
    print("📄 تم إنشاء ملف: create_semantic_config.py")
    print("💡 يمكنك تشغيله لإنشاء البحث الدلالي تلقائياً")

if __name__ == "__main__":
    print("🎯 حل مشكلة البحث الدلالي")
    print("=" * 50)
    print()
    
    # إنشاء الدليل
    create_semantic_search_guide()
    
    # إنشاء الحل البرمجي
    print("📝 إنشاء حل Python...")
    create_python_solution()
    
    print()
    print("🎉 تم إنشاء جميع الملفات والأدلة!")
    print("📋 اتبع الخطوات أعلاه لحل المشكلة")
    print("🚀 بعد إنشاء البحث الدلالي، البحث سيعمل بشكل ممتاز!")
