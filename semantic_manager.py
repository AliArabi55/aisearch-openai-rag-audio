#!/usr/bin/env python3
"""
أداة شاملة لإدارة البحث الدلالي في Azure AI Search
تقرأ جميع الإعدادات من ملف .env
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
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError

class SemanticSearchManager:
    """مدير البحث الدلالي"""
    
    def __init__(self):
        """تهيئة المدير"""
        load_dotenv("app/backend/.env")
        
        # قراءة الإعدادات من ملف .env
        self.search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
        self.search_index = os.getenv("AZURE_SEARCH_INDEX") 
        self.api_key = os.getenv("AZURE_SEARCH_API_KEY")
        self.admin_key = os.getenv("AZURE_SEARCH_ADMIN_KEY")
        self.semantic_config_name = os.getenv("AZURE_SEARCH_SEMANTIC_CONFIGURATION")
        self.title_field = os.getenv("AZURE_SEARCH_TITLE_FIELD", "Name")
        self.content_field = os.getenv("AZURE_SEARCH_CONTENT_FIELD", "ingredients")
        
        # التحقق من الإعدادات المطلوبة
        self._validate_settings()
    
    def _validate_settings(self):
        """التحقق من صحة الإعدادات"""
        required_settings = {
            "AZURE_SEARCH_ENDPOINT": self.search_endpoint,
            "AZURE_SEARCH_INDEX": self.search_index,
            "AZURE_SEARCH_API_KEY": self.api_key,
            "AZURE_SEARCH_ADMIN_KEY": self.admin_key,
            "AZURE_SEARCH_SEMANTIC_CONFIGURATION": self.semantic_config_name
        }
        
        missing = []
        for key, value in required_settings.items():
            if not value:
                missing.append(key)
        
        if missing:
            print("❌ الإعدادات التالية مفقودة من ملف .env:")
            for setting in missing:
                print(f"   🔹 {setting}")
            raise ValueError("إعدادات مفقودة في ملف .env")
        
        print("✅ جميع الإعدادات موجودة في ملف .env")
    
    def print_current_settings(self):
        """طباعة الإعدادات الحالية"""
        print("📋 الإعدادات الحالية:")
        print("=" * 40)
        print(f"🔗 الخادم: {self.search_endpoint}")
        print(f"📊 الفهرس: {self.search_index}")
        print(f"🧠 الإعداد الدلالي: {self.semantic_config_name}")
        print(f"🏷️ حقل العنوان: {self.title_field}")
        print(f"📄 حقل المحتوى: {self.content_field}")
        print()
    
    def check_semantic_config_exists(self):
        """التحقق من وجود الإعداد الدلالي"""
        try:
            search_client = SearchClient(
                endpoint=self.search_endpoint,
                index_name=self.search_index,
                credential=AzureKeyCredential(self.api_key)
            )
            
            # اختبار البحث الدلالي
            results = search_client.search(
                search_text="test",
                query_type="semantic",
                semantic_configuration_name=self.semantic_config_name,
                top=1
            )
            
            # محاولة قراءة النتائج
            for result in results:
                pass
            
            print("✅ الإعداد الدلالي موجود ويعمل")
            return True
            
        except Exception as e:
            if "Unknown semantic configuration" in str(e):
                print("❌ الإعداد الدلالي غير موجود")
                return False
            else:
                print(f"⚠️ خطأ في التحقق: {str(e)}")
                return False
    
    def create_semantic_config(self):
        """إنشاء الإعداد الدلالي"""
        try:
            print("🔗 الاتصال بـ Azure Search...")
            client = SearchIndexClient(
                endpoint=self.search_endpoint,
                credential=AzureKeyCredential(self.admin_key)
            )
            
            # الحصول على الفهرس الحالي
            print("📋 جلب معلومات الفهرس...")
            index = client.get_index(self.search_index)
            
            print(f"✅ تم جلب الفهرس: {index.name}")
            
            # عرض الحقول المتاحة
            print("\n📊 الحقول المتاحة في الفهرس:")
            for field in index.fields:
                searchable = "✅" if field.searchable else "❌"
                print(f"   🔹 {field.name} ({field.type}) - قابل للبحث: {searchable}")
            
            # إنشاء الإعداد الدلالي
            print(f"\n🧠 إنشاء الإعداد الدلالي: {self.semantic_config_name}")
            
            semantic_config = SemanticConfiguration(
                name=self.semantic_config_name,
                prioritized_fields=SemanticPrioritizedFields(
                    title_field=SemanticField(field_name=self.title_field),
                    content_fields=[SemanticField(field_name=self.content_field)]
                )
            )
            
            # التحقق من وجود semantic_search في الفهرس
            if not hasattr(index, 'semantic_search') or index.semantic_search is None:
                print("🔧 إنشاء قسم البحث الدلالي...")
                index.semantic_search = SemanticSearch(configurations=[])
            
            if not index.semantic_search.configurations:
                index.semantic_search.configurations = []
            
            # التحقق من عدم وجود الإعداد مسبقاً
            existing_configs = [config.name for config in index.semantic_search.configurations]
            if self.semantic_config_name in existing_configs:
                print(f"⚠️ الإعداد {self.semantic_config_name} موجود مسبقاً")
                print("🔄 سيتم تحديثه...")
                index.semantic_search.configurations = [
                    config for config in index.semantic_search.configurations 
                    if config.name != self.semantic_config_name
                ]
            
            # إضافة الإعداد الجديد
            index.semantic_search.configurations.append(semantic_config)
            
            # تحديث الفهرس
            print("💾 حفظ التغييرات...")
            result = client.create_or_update_index(index)
            
            print("\n🎉 تم إنشاء إعداد البحث الدلالي بنجاح!")
            print(f"✅ اسم الإعداد: {self.semantic_config_name}")
            print(f"🏷️ حقل العنوان: {self.title_field}")
            print(f"📄 حقل المحتوى: {self.content_field}")
            
            return True
            
        except HttpResponseError as e:
            print(f"\n❌ خطأ HTTP: {e.status_code}")
            print(f"📝 الرسالة: {e.message}")
            
            if e.status_code == 401:
                print("💡 السبب المحتمل: Admin Key خاطئ")
                print("🔧 الحل: تحقق من AZURE_SEARCH_ADMIN_KEY في ملف .env")
            elif e.status_code == 403:
                print("💡 السبب المحتمل: لا توجد صلاحيات كافية")
                print("🔧 الحل: تأكد من صلاحيات الكتابة على الفهرس")
            elif e.status_code == 404:
                print("💡 السبب المحتمل: الفهرس غير موجود")
                print(f"🔧 الحل: تأكد من اسم الفهرس: {self.search_index}")
            
            return False
            
        except Exception as e:
            print(f"\n❌ خطأ غير متوقع: {str(e)}")
            return False
    
    def test_semantic_search(self, query="pizza"):
        """اختبار البحث الدلالي"""
        print(f"\n🧪 اختبار البحث الدلالي بكلمة: {query}")
        
        try:
            search_client = SearchClient(
                endpoint=self.search_endpoint,
                index_name=self.search_index,
                credential=AzureKeyCredential(self.api_key)
            )
            
            # البحث الدلالي
            results = search_client.search(
                search_text=query,
                query_type="semantic",
                semantic_configuration_name=self.semantic_config_name,
                top=3
            )
            
            result_count = 0
            for result in results:
                result_count += 1
                title = result.get(self.title_field, 'بلا عنوان')
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
    
    def run_full_setup(self):
        """تشغيل الإعداد الكامل للبحث الدلالي"""
        print("🚀 مدير البحث الدلالي الشامل")
        print("=" * 50)
        
        try:
            # طباعة الإعدادات
            self.print_current_settings()
            
            # التحقق من وجود الإعداد
            if self.check_semantic_config_exists():
                print("✅ البحث الدلالي جاهز للاستخدام")
                self.test_semantic_search()
            else:
                print("🔧 إنشاء إعداد البحث الدلالي...")
                if self.create_semantic_config():
                    print("\n🔄 اختبار البحث الدلالي بعد الإنشاء...")
                    self.test_semantic_search()
                else:
                    print("❌ فشل في إنشاء البحث الدلالي")
                    return False
            
            print("\n" + "=" * 50)
            print("✅ تم الانتهاء من إعداد البحث الدلالي")
            return True
            
        except Exception as e:
            print(f"❌ خطأ في الإعداد: {str(e)}")
            return False

def main():
    """الدالة الرئيسية"""
    try:
        manager = SemanticSearchManager()
        manager.run_full_setup()
    except Exception as e:
        print(f"❌ خطأ في التهيئة: {str(e)}")
        print("\n💡 تأكد من:")
        print("   🔹 وجود ملف app/backend/.env")
        print("   🔹 صحة جميع الإعدادات المطلوبة")

if __name__ == "__main__":
    main()
