#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
فحص إعدادات الفهرس وإعدادات البحث الدلالي في Azure AI Search
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

class AzureSearchInspector:
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
    
    def inspect_index(self):
        """فحص تفاصيل الفهرس"""
        try:
            print_arabic("🔍 فحص تفاصيل الفهرس...")
            
            # الحصول على تفاصيل الفهرس
            index = self.index_client.get_index(self.search_index)
            
            print_arabic(f"📋 اسم الفهرس: {index.name}")
            print_arabic(f"📊 إعدادات البحث:")
            
            # فحص الحقول
            print_arabic(f"\n📝 الحقول المتاحة ({len(index.fields)}):")
            for field in index.fields:
                attrs = []
                if field.searchable: attrs.append("قابل للبحث")
                if field.filterable: attrs.append("قابل للتصفية")
                if field.sortable: attrs.append("قابل للترتيب")
                if field.facetable: attrs.append("قابل للتجميع")
                if field.retrievable: attrs.append("قابل للاسترجاع")
                
                print_arabic(f"   📌 {field.name} ({field.type}) - {', '.join(attrs)}")
            
            # فحص إعدادات البحث الدلالي
            print_arabic(f"\n🧠 إعدادات البحث الدلالي:")
            if index.semantic_search:
                print_arabic(f"   ✅ البحث الدلالي مفعل")
                print_arabic(f"   📝 عدد الإعدادات: {len(index.semantic_search.configurations)}")
                
                for config in index.semantic_search.configurations:
                    print_arabic(f"\n   🔧 إعداد: {config.name}")
                    if config.prioritized_fields:
                        if config.prioritized_fields.title_field:
                            print_arabic(f"      🏷️  حقل العنوان: {config.prioritized_fields.title_field.field_name}")
                        if config.prioritized_fields.content_fields:
                            content_fields = [f.field_name for f in config.prioritized_fields.content_fields]
                            print_arabic(f"      📄 حقول المحتوى: {', '.join(content_fields)}")
                        if config.prioritized_fields.keyword_fields:
                            keyword_fields = [f.field_name for f in config.prioritized_fields.keyword_fields]
                            print_arabic(f"      🔑 حقول الكلمات المفتاحية: {', '.join(keyword_fields)}")
            else:
                print_arabic("   ❌ البحث الدلالي غير مفعل")
            
            return index
            
        except Exception as e:
            print_arabic(f"❌ خطأ في فحص الفهرس: {str(e)}")
            return None
    
    def test_basic_search(self):
        """اختبار البحث الأساسي"""
        try:
            print_arabic(f"\n🔍 اختبار البحث الأساسي...")
            
            # بحث بسيط
            results = self.search_client.search(
                search_text="pizza",
                top=3,
                select=["ID", "Name", "ingredients", "Price"]
            )
            
            print_arabic(f"✅ نتائج البحث الأساسي لـ 'pizza':")
            count = 0
            for result in results:
                count += 1
                print_arabic(f"   {count}. {result.get('Name')} - {result.get('Price')} جنيه")
                print_arabic(f"      ID: {result.get('ID')}")
                print_arabic(f"      المكونات: {result.get('ingredients', 'غير متوفر')}")
            
            if count == 0:
                print_arabic("   ❌ لم يتم العثور على أي نتائج")
            
            return count > 0
            
        except Exception as e:
            print_arabic(f"❌ خطأ في البحث الأساسي: {str(e)}")
            return False
    
    def test_semantic_search(self, semantic_config_name):
        """اختبار البحث الدلالي"""
        try:
            print_arabic(f"\n🧠 اختبار البحث الدلالي باستخدام: {semantic_config_name}")
            
            results = self.search_client.search(
                search_text="pizza",
                top=3,
                select=["ID", "Name", "ingredients", "Price"],
                query_type="semantic",
                semantic_configuration_name=semantic_config_name,
                query_caption="extractive"
            )
            
            print_arabic(f"✅ نتائج البحث الدلالي لـ 'pizza':")
            count = 0
            for result in results:
                count += 1
                print_arabic(f"   {count}. {result.get('Name')} - {result.get('Price')} جنيه")
                print_arabic(f"      النقاط الدلالية: {getattr(result, '@search.reranker_score', 'غير متوفر')}")
                
                # فحص الـ captions
                if hasattr(result, "@search.captions") and result.get("@search.captions"):
                    captions = []
                    for caption in result["@search.captions"]:
                        captions.append(caption.get("text", "") or caption.get("highlights", ""))
                    if captions:
                        print_arabic(f"      مقاطع مطابقة: {', '.join(captions[:2])}")
            
            if count == 0:
                print_arabic("   ❌ لم يتم العثور على أي نتائج")
            
            return count > 0
            
        except Exception as e:
            print_arabic(f"❌ خطأ في البحث الدلالي: {str(e)}")
            return False
    
    def suggest_fix(self, index):
        """اقتراح حلول لإصلاح المشكلة"""
        print_arabic(f"\n🔧 اقتراحات الإصلاح:")
        
        if not index:
            print_arabic("   ❌ لا يمكن الوصول للفهرس - تحقق من الإعدادات")
            return
        
        if not index.semantic_search or not index.semantic_search.configurations:
            print_arabic("   ❌ البحث الدلالي غير مُعدّ - يجب تفعيله من Azure Portal")
            print_arabic("   💡 الخطوات:")
            print_arabic("      1. اذهب إلى Azure Portal")
            print_arabic("      2. افتح Azure AI Search service")
            print_arabic("      3. اختر الفهرس 'english22-index'")
            print_arabic("      4. اذهب إلى 'Semantic configurations'")
            print_arabic("      5. أنشئ إعداد جديد أو حدّث الموجود")
        else:
            # عرض الإعدادات المتاحة
            print_arabic("   ✅ إعدادات البحث الدلالي المتاحة:")
            for config in index.semantic_search.configurations:
                print_arabic(f"      📌 {config.name}")
            
            # اقتراح تحديث ملف .env
            if len(index.semantic_search.configurations) > 0:
                first_config = index.semantic_search.configurations[0].name
                print_arabic(f"\n   💡 جرب تحديث ملف .env:")
                print_arabic(f"      AZURE_SEARCH_SEMANTIC_CONFIGURATION={first_config}")

def main():
    """الدالة الرئيسية"""
    print_arabic("🔍 مفتش إعدادات Azure AI Search")
    print_arabic("=" * 50)
    
    try:
        inspector = AzureSearchInspector()
        
        # فحص الفهرس
        index = inspector.inspect_index()
        
        # اختبار البحث الأساسي
        basic_works = inspector.test_basic_search()
        
        # اختبار البحث الدلالي (إذا كان متاحاً)
        if index and index.semantic_search and index.semantic_search.configurations:
            for config in index.semantic_search.configurations:
                semantic_works = inspector.test_semantic_search(config.name)
                if semantic_works:
                    print_arabic(f"✅ البحث الدلالي يعمل مع: {config.name}")
                    break
        
        # اقتراح الحلول
        inspector.suggest_fix(index)
        
    except Exception as e:
        print_arabic(f"❌ خطأ عام: {str(e)}")

if __name__ == "__main__":
    main()
