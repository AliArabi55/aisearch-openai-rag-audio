#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
البحث عن إعدادات البحث الدلالي الصحيحة في Azure Search
Finding Correct Semantic Search Configurations in Azure Search
"""

import asyncio
import os
import sys
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

# إعداد الترميز للنصوص العربية
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

def print_arabic(text):
    """طباعة النصوص العربية بشكل صحيح"""
    try:
        print(text.encode('utf-8').decode('utf-8'))
    except:
        print(text)

class SemanticConfigFinder:
    def __init__(self):
        # تحميل متغيرات البيئة
        load_dotenv("app/backend/.env")
        
        self.search_endpoint = os.environ.get("AZURE_SEARCH_ENDPOINT")
        self.search_key = os.environ.get("AZURE_SEARCH_API_KEY")
        self.search_index = os.environ.get("AZURE_SEARCH_INDEX")
        
        if not all([self.search_endpoint, self.search_key, self.search_index]):
            raise ValueError("Missing required Azure Search configuration")
        
        self.credential = AzureKeyCredential(self.search_key)
        self.index_client = SearchIndexClient(
            endpoint=self.search_endpoint,
            credential=self.credential
        )
        self.search_client = SearchClient(
            endpoint=self.search_endpoint,
            index_name=self.search_index,
            credential=self.credential
        )
        
        print_arabic("✅ تم تهيئة باحث إعدادات البحث الدلالي")
    
    def find_semantic_configurations(self):
        """البحث عن إعدادات البحث الدلالي المتاحة"""
        try:
            print_arabic(f"🔍 فحص الفهرس: {self.search_index}")
            
            # الحصول على تفاصيل الفهرس
            index = self.index_client.get_index(self.search_index)
            
            print_arabic(f"📋 اسم الفهرس: {index.name}")
            
            # فحص إعدادات البحث الدلالي
            if index.semantic_search and index.semantic_search.configurations:
                print_arabic(f"✅ البحث الدلالي مفعل!")
                print_arabic(f"📊 عدد الإعدادات المتاحة: {len(index.semantic_search.configurations)}")
                
                available_configs = []
                for i, config in enumerate(index.semantic_search.configurations, 1):
                    print_arabic(f"\n🔧 إعداد {i}: {config.name}")
                    available_configs.append(config.name)
                    
                    if config.prioritized_fields:
                        if config.prioritized_fields.title_field:
                            print_arabic(f"   🏷️  حقل العنوان: {config.prioritized_fields.title_field.field_name}")
                        if config.prioritized_fields.content_fields:
                            content_fields = [f.field_name for f in config.prioritized_fields.content_fields]
                            print_arabic(f"   📄 حقول المحتوى: {', '.join(content_fields)}")
                        if config.prioritized_fields.keyword_fields:
                            keyword_fields = [f.field_name for f in config.prioritized_fields.keyword_fields]
                            print_arabic(f"   🔑 حقول الكلمات المفتاحية: {', '.join(keyword_fields)}")
                
                return available_configs
            else:
                print_arabic("❌ البحث الدلالي غير مفعل في هذا الفهرس")
                return []
                
        except Exception as e:
            print_arabic(f"❌ خطأ في فحص الفهرس: {str(e)}")
            # محاولة البحث بدون إعدادات دلالية لمعرفة ما يعمل
            return self.try_common_configs()
    
    def try_common_configs(self):
        """تجربة الإعدادات الشائعة للبحث الدلالي"""
        print_arabic(f"\n🔄 تجربة الإعدادات الشائعة...")
        
        common_configs = [
            "default",
            "my-semantic-config", 
            "semantic-config",
            f"{self.search_index}-semantic",
            "english-semantic",
            "semantic"
        ]
        
        working_configs = []
        
        for config_name in common_configs:
            try:
                print_arabic(f"🧪 تجربة: {config_name}")
                
                results = self.search_client.search(
                    search_text="pizza",
                    top=1,
                    select=["ID", "Name"],
                    query_type="semantic",
                    semantic_configuration_name=config_name
                )
                
                # محاولة الحصول على النتيجة الأولى
                for result in results:
                    print_arabic(f"✅ {config_name} يعمل!")
                    working_configs.append(config_name)
                    break
                    
            except Exception as e:
                if "Unknown semantic configuration" in str(e):
                    print_arabic(f"❌ {config_name} غير موجود")
                else:
                    print_arabic(f"⚠️  {config_name}: {str(e)[:50]}...")
        
        return working_configs
    
    async def test_without_semantic(self):
        """اختبار البحث بدون إعدادات دلالية"""
        print_arabic(f"\n🔍 اختبار البحث الأساسي (بدون دلالي)...")
        
        try:
            results = self.search_client.search(
                search_text="pizza",
                top=3,
                select=["ID", "Name", "Price"]
            )
            
            items = []
            for result in results:
                items.append({
                    "name": result.get("Name"),
                    "price": result.get("Price")
                })
            
            if items:
                print_arabic(f"✅ البحث الأساسي يعمل! {len(items)} نتيجة:")
                for i, item in enumerate(items, 1):
                    print_arabic(f"   {i}. {item['name']} - {item['price']} جنيه")
                return True
            else:
                print_arabic(f"❌ لا توجد نتائج حتى للبحث الأساسي")
                return False
                
        except Exception as e:
            print_arabic(f"❌ خطأ في البحث الأساسي: {str(e)}")
            return False
    
    def suggest_solution(self, available_configs):
        """اقتراح الحل المناسب"""
        print_arabic(f"\n💡 الحلول المقترحة:")
        
        if available_configs:
            print_arabic(f"✅ تم العثور على إعدادات تعمل:")
            for config in available_configs:
                print_arabic(f"   📌 {config}")
            
            # اقتراح التحديث
            best_config = available_configs[0]
            print_arabic(f"\n🔧 قم بتحديث ملف .env:")
            print_arabic(f"   AZURE_SEARCH_SEMANTIC_CONFIGURATION={best_config}")
            
            return best_config
        else:
            print_arabic(f"❌ لم يتم العثور على إعدادات بحث دلالي")
            print_arabic(f"🛠️  الحلول:")
            print_arabic(f"   1. إنشاء إعداد بحث دلالي في Azure Portal")
            print_arabic(f"   2. استخدام البحث الأساسي فقط")
            print_arabic(f"   3. تفعيل البحث الدلالي للفهرس")
            
            return None

async def main():
    """الدالة الرئيسية"""
    print_arabic("🔍 البحث عن إعدادات البحث الدلالي الصحيحة")
    print_arabic("=" * 60)
    
    try:
        finder = SemanticConfigFinder()
        
        # اختبار البحث الأساسي أولاً
        basic_works = await finder.test_without_semantic()
        
        if basic_works:
            # البحث عن إعدادات البحث الدلالي
            configs = finder.find_semantic_configurations()
            
            # اقتراح الحل
            suggested_config = finder.suggest_solution(configs)
            
            if suggested_config:
                print_arabic(f"\n🎯 يمكن الآن استخدام: {suggested_config}")
            else:
                print_arabic(f"\n⚠️  سنستخدم البحث الأساسي فقط")
        else:
            print_arabic(f"\n❌ مشكلة في الاتصال بـ Azure Search")
        
    except KeyboardInterrupt:
        print_arabic("\n⏹️  تم إيقاف البحث بواسطة المستخدم")
    except Exception as e:
        print_arabic(f"\n❌ خطأ عام: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
