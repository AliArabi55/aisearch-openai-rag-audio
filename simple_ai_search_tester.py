#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
واجهة اختبار AI Search البسيطة - نسخة مبسطة
Simple AI Search Testing Interface - Simplified Version
"""

import os
import sys
from pathlib import Path

# إعداد الترميز للنصوص العربية
import locale
locale.setlocale(locale.LC_ALL, '')

if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

def print_arabic(text):
    """طباعة النصوص العربية بشكل صحيح"""
    try:
        print(text.encode('utf-8').decode('utf-8'))
    except:
        print(text)

class SimpleAISearchTester:
    def __init__(self):
        # تحميل متغيرات البيئة
        load_dotenv("app/backend/.env")
        
        self.search_endpoint = os.environ.get("AZURE_SEARCH_ENDPOINT")
        self.search_key = os.environ.get("AZURE_SEARCH_API_KEY")
        self.search_index = os.environ.get("AZURE_SEARCH_INDEX")
        self.semantic_config = os.environ.get("AZURE_SEARCH_SEMANTIC_CONFIGURATION")
        
        print_arabic("📋 إعدادات AI Search:")
        print_arabic(f"   🔗 Endpoint: {self.search_endpoint}")
        print_arabic(f"   📊 Index: {self.search_index}")
        print_arabic(f"   🧠 Semantic Config: {self.semantic_config}")
        print_arabic(f"   🔑 API Key: {'✅ موجود' if self.search_key else '❌ مفقود'}")
        
        if not all([self.search_endpoint, self.search_key, self.search_index]):
            raise ValueError("Missing required Azure Search configuration")
        
        self.credential = AzureKeyCredential(self.search_key)
        self.search_client = SearchClient(
            endpoint=self.search_endpoint,
            index_name=self.search_index,
            credential=self.credential
        )
        
        print_arabic("✅ تم تهيئة AI Search بنجاح")
    
    def search_basic(self, query, top=5):
        """بحث أساسي"""
        print_arabic(f"\n🔍 بحث أساسي عن: '{query}'")
        print_arabic("-" * 50)
        
        try:
            results = self.search_client.search(
                search_text=query,
                top=top,
                select=["ID", "Name", "ingredients", "Price"]
            )
            
            items = []
            for i, result in enumerate(results, 1):
                item = {
                    "rank": i,
                    "id": result.get("ID"),
                    "name": result.get("Name"), 
                    "ingredients": result.get("ingredients"),
                    "price": result.get("Price"),
                    "score": getattr(result, "@search.score", None)
                }
                items.append(item)
                
                print_arabic(f"{i}. {item['name']}")
                print_arabic(f"   📝 المكونات: {item['ingredients']}")
                print_arabic(f"   💰 السعر: {item['price']} جنيه")
                print_arabic(f"   📊 النقاط: {item['score']:.3f}" if item['score'] else "   📊 النقاط: غير متاح")
                print_arabic(f"   🆔 ID: {item['id']}")
                print_arabic("")
            
            if not items:
                print_arabic("😔 لم يتم العثور على نتائج")
            
            return items
            
        except Exception as e:
            print_arabic(f"❌ خطأ في البحث: {str(e)}")
            return []
    
    def search_semantic(self, query, top=5):
        """بحث دلالي"""
        print_arabic(f"\n🧠 بحث دلالي عن: '{query}'")
        print_arabic("-" * 50)
        
        try:
            if not self.semantic_config:
                print_arabic("❌ Semantic configuration غير محدد")
                return []
            
            results = self.search_client.search(
                search_text=query,
                top=top,
                select=["ID", "Name", "ingredients", "Price"],
                query_type="semantic",
                semantic_configuration_name=self.semantic_config,
                query_caption="extractive",
                query_answer="extractive"
            )
            
            items = []
            for i, result in enumerate(results, 1):
                # استخراج الـ captions
                captions = []
                if hasattr(result, "@search.captions") and result.get("@search.captions"):
                    for caption in result["@search.captions"]:
                        captions.append(caption.get("text", "") or caption.get("highlights", ""))
                
                item = {
                    "rank": i,
                    "id": result.get("ID"),
                    "name": result.get("Name"),
                    "ingredients": result.get("ingredients"), 
                    "price": result.get("Price"),
                    "score": getattr(result, "@search.score", None),
                    "reranker_score": getattr(result, "@search.reranker_score", None),
                    "captions": captions
                }
                items.append(item)
                
                print_arabic(f"{i}. {item['name']}")
                print_arabic(f"   📝 المكونات: {item['ingredients']}")
                print_arabic(f"   💰 السعر: {item['price']} جنيه")
                
                if item['reranker_score']:
                    print_arabic(f"   🧠 نقاط دلالية: {item['reranker_score']:.3f}")
                if item['score']:
                    print_arabic(f"   📊 نقاط أساسية: {item['score']:.3f}")
                
                if item['captions']:
                    print_arabic("   📄 مقاطع مطابقة:")
                    for caption in item['captions']:
                        if caption.strip():
                            print_arabic(f"      • {caption}")
                
                print_arabic(f"   🆔 ID: {item['id']}")
                print_arabic("")
            
            if not items:
                print_arabic("😔 لم يتم العثور على نتائج")
            
            return items
            
        except Exception as e:
            print_arabic(f"❌ خطأ في البحث الدلالي: {str(e)}")
            return []
    
    def compare_search(self, query, top=5):
        """مقارنة بين البحث الأساسي والدلالي"""
        print_arabic(f"\n⚖️  مقارنة البحث عن: '{query}'")
        print_arabic("=" * 60)
        
        basic_results = self.search_basic(query, top)
        semantic_results = self.search_semantic(query, top)
        
        print_arabic("\n📊 ملخص المقارنة:")
        print_arabic(f"   🔍 البحث الأساسي: {len(basic_results)} نتيجة")
        print_arabic(f"   🧠 البحث الدلالي: {len(semantic_results)} نتيجة")
        
        # تحليل الاختلافات
        basic_names = [r['name'] for r in basic_results]
        semantic_names = [r['name'] for r in semantic_results]
        
        common = set(basic_names) & set(semantic_names)
        basic_only = set(basic_names) - set(semantic_names)
        semantic_only = set(semantic_names) - set(basic_names)
        
        print_arabic(f"\n🔄 التحليل:")
        print_arabic(f"   ✅ نتائج مشتركة: {len(common)}")
        print_arabic(f"   🔍 فقط في الأساسي: {len(basic_only)}")
        print_arabic(f"   🧠 فقط في الدلالي: {len(semantic_only)}")
        
        if basic_only:
            print_arabic("\n🔍 نتائج فقط في البحث الأساسي:")
            for name in basic_only:
                print_arabic(f"   • {name}")
        
        if semantic_only:
            print_arabic("\n🧠 نتائج فقط في البحث الدلالي:")
            for name in semantic_only:
                print_arabic(f"   • {name}")
        
        return {
            "basic": basic_results,
            "semantic": semantic_results,
            "analysis": {
                "common": len(common),
                "basic_only": len(basic_only),
                "semantic_only": len(semantic_only)
            }
        }

def main():
    """الدالة الرئيسية التفاعلية"""
    print_arabic("🎯 مختبر AI Search التفاعلي")
    print_arabic("=" * 60)
    
    try:
        # تهيئة المختبر
        tester = SimpleAISearchTester()
        
        # استعلامات تجريبية
        test_queries = [
            "بيتزا تونة",
            "برجر",
            "حلويات",
            "سلطة",
            "مشروبات"
        ]
        
        print_arabic("\n🔬 استعلامات تجريبية متاحة:")
        for i, query in enumerate(test_queries, 1):
            print_arabic(f"   {i}. {query}")
        
        while True:
            print_arabic("\n" + "="*60)
            print_arabic("🎛️  اختر نوع البحث:")
            print_arabic("   1. 🔍 بحث أساسي")
            print_arabic("   2. 🧠 بحث دلالي") 
            print_arabic("   3. ⚖️  مقارنة")
            print_arabic("   4. 🔄 استعلام جديد")
            print_arabic("   5. ❌ خروج")
            
            choice = input("\n👆 اختر (1-5): ").strip()
            
            if choice == '5':
                print_arabic("👋 وداعاً!")
                break
            
            if choice == '4':
                query = input("🔤 أدخل استعلام البحث: ").strip()
                if not query:
                    print_arabic("⚠️  يرجى إدخال استعلام صحيح")
                    continue
            else:
                print_arabic("\n📝 اختر استعلام تجريبي:")
                for i, q in enumerate(test_queries, 1):
                    print_arabic(f"   {i}. {q}")
                
                try:
                    q_choice = int(input("👆 اختر (1-5): ").strip())
                    if 1 <= q_choice <= len(test_queries):
                        query = test_queries[q_choice - 1]
                    else:
                        print_arabic("⚠️  اختيار غير صحيح")
                        continue
                except ValueError:
                    print_arabic("⚠️  يرجى إدخال رقم صحيح")
                    continue
            
            try:
                top = int(input(f"📊 عدد النتائج (افتراضي 5): ").strip() or "5")
                top = max(1, min(top, 20))  # بين 1 و 20
            except ValueError:
                top = 5
            
            # تنفيذ البحث
            if choice == '1':
                tester.search_basic(query, top)
            elif choice == '2':
                tester.search_semantic(query, top)
            elif choice == '3':
                tester.compare_search(query, top)
            
            input("\n⏸️  اضغط Enter للمتابعة...")
    
    except KeyboardInterrupt:
        print_arabic("\n👋 تم الإيقاف بواسطة المستخدم")
    except Exception as e:
        print_arabic(f"\n❌ خطأ: {str(e)}")

if __name__ == "__main__":
    main()
