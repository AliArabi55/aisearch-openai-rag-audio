#!/usr/bin/env python3
"""
اختبار مباشر للبحث الدلالي في Azure AI Search
يختبر ما إذا كان البحث الدلالي يعمل فعلاً أم لا
"""

import os
from dotenv import load_dotenv
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

def test_semantic_search():
    """اختبار البحث الدلالي مباشرة"""
    
    # تحميل المتغيرات
    load_dotenv("app/backend/.env")
    
    search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
    search_key = os.getenv("AZURE_SEARCH_API_KEY")
    search_index = os.getenv("AZURE_SEARCH_INDEX")
    semantic_config = os.getenv("AZURE_SEARCH_SEMANTIC_CONFIGURATION")
    
    print(f"🔍 اختبار البحث الدلالي مباشرة")
    print("=" * 50)
    print(f"🔗 النقطة النهاية: {search_endpoint}")
    print(f"📋 الفهرس: {search_index}")
    print(f"🧠 الإعداد الدلالي: {semantic_config}")
    print()
    
    try:
        # إنشاء العميل
        search_client = SearchClient(
            endpoint=search_endpoint,
            index_name=search_index,
            credential=AzureKeyCredential(search_key)
        )
        
        print("✅ تم إنشاء Search Client بنجاح")
        
        # اختبار البحث العادي أولاً
        print("\n📝 اختبار البحث العادي...")
        basic_results = search_client.search(
            search_text="pizza",
            top=3
        )
        
        basic_count = 0
        for result in basic_results:
            basic_count += 1
            print(f"   🔹 النتيجة {basic_count}: {result.get('title', 'بلا عنوان')}")
        
        print(f"✅ البحث العادي يعمل - وجد {basic_count} نتائج")
        
        # اختبار البحث الدلالي
        print("\n🧠 اختبار البحث الدلالي...")
        
        try:
            semantic_results = search_client.search(
                search_text="pizza",
                query_type="semantic",
                semantic_configuration_name=semantic_config,
                top=3
            )
            
            semantic_count = 0
            for result in semantic_results:
                semantic_count += 1
                print(f"   🧠 النتيجة الدلالية {semantic_count}: {result.get('title', 'بلا عنوان')}")
                # طباعة النقاط الدلالية إذا كانت متوفرة
                if hasattr(result, '@search.reranker_score'):
                    print(f"      📊 النقاط الدلالية: {result['@search.reranker_score']}")
            
            if semantic_count > 0:
                print(f"🎉 البحث الدلالي يعمل بنجاح! - وجد {semantic_count} نتائج")
                return True
            else:
                print("⚠️ البحث الدلالي لا يعيد نتائج")
                return False
                
        except Exception as semantic_error:
            print(f"❌ فشل البحث الدلالي: {str(semantic_error)}")
            
            # تحليل نوع الخطأ
            error_msg = str(semantic_error).lower()
            
            if "semantic" in error_msg and "not found" in error_msg:
                print("💡 السبب: إعداد البحث الدلالي غير موجود")
            elif "semantic" in error_msg and "not enabled" in error_msg:
                print("💡 السبب: البحث الدلالي غير مفعل على الفهرس")
            elif "query_type" in error_msg:
                print("💡 السبب: نوع الاستعلام غير مدعوم")
            else:
                print(f"💡 خطأ غير متوقع: {semantic_error}")
            
            return False
            
    except Exception as e:
        print(f"❌ خطأ في الاتصال: {str(e)}")
        return False

def test_with_different_configs():
    """اختبار مع إعدادات مختلفة للبحث الدلالي"""
    
    load_dotenv("app/backend/.env")
    
    search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
    search_key = os.getenv("AZURE_SEARCH_API_KEY")
    search_index = os.getenv("AZURE_SEARCH_INDEX")
    
    search_client = SearchClient(
        endpoint=search_endpoint,
        index_name=search_index,
        credential=AzureKeyCredential(search_key)
    )
    
    # قائمة الإعدادات المحتملة للبحث الدلالي
    possible_configs = [
        "default",
        "semantic-config",
        "english-semantic-config",
        "english22-semantic-configuration",
        f"{search_index}-semantic-config",
        f"{search_index}-config",
        "my-semantic-config"
    ]
    
    print("\n🔬 اختبار إعدادات مختلفة للبحث الدلالي...")
    print("=" * 50)
    
    for config in possible_configs:
        print(f"\n🧪 اختبار الإعداد: {config}")
        
        try:
            results = search_client.search(
                search_text="pizza",
                query_type="semantic",
                semantic_configuration_name=config,
                top=1
            )
            
            # محاولة قراءة النتائج
            result_count = 0
            for result in results:
                result_count += 1
                print(f"   ✅ يعمل! - النتيجة: {result.get('title', 'بلا عنوان')}")
                
                # إنشاء ملف .env محدث
                update_env_file(config)
                return config
                
        except Exception as e:
            print(f"   ❌ لا يعمل: {str(e)[:60]}...")
    
    print("\n💡 لم يتم العثور على إعداد دلالي يعمل")
    return None

def update_env_file(working_config):
    """تحديث ملف .env بالإعداد الصحيح"""
    
    print(f"\n📝 تحديث ملف .env بالإعداد الصحيح: {working_config}")
    
    env_path = "app/backend/.env"
    
    try:
        # قراءة الملف الحالي
        with open(env_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # تحديث السطر المطلوب
        lines = content.split('\n')
        updated_lines = []
        
        for line in lines:
            if line.startswith('AZURE_SEARCH_SEMANTIC_CONFIGURATION='):
                updated_lines.append(f'AZURE_SEARCH_SEMANTIC_CONFIGURATION={working_config}')
                print(f"   ✅ تم تحديث: {line} -> AZURE_SEARCH_SEMANTIC_CONFIGURATION={working_config}")
            else:
                updated_lines.append(line)
        
        # كتابة الملف المحدث
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(updated_lines))
        
        print(f"✅ تم تحديث ملف .env بنجاح")
        
    except Exception as e:
        print(f"❌ خطأ في تحديث ملف .env: {e}")

if __name__ == "__main__":
    print("🚀 بدء اختبار البحث الدلالي المباشر...")
    print()
    
    # اختبار الإعداد الحالي
    if test_semantic_search():
        print("\n🎉 البحث الدلالي يعمل بالإعداد الحالي!")
    else:
        print("\n🔍 البحث عن إعداد دلالي يعمل...")
        working_config = test_with_different_configs()
        
        if working_config:
            print(f"\n🎉 تم العثور على إعداد يعمل: {working_config}")
            print("📝 تم تحديث ملف .env تلقائياً")
            print("🔄 أعد تشغيل التطبيق لتطبيق التغييرات")
        else:
            print("\n❌ لم يتم العثور على أي إعداد دلالي يعمل")
            print("💡 قد تحتاج لإنشاء إعداد دلالي جديد في Azure Portal")
    
    print("\n" + "=" * 50)
    print("✅ انتهى الاختبار")
