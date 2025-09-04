#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار البحث الدلالي النهائي مع التحقق من الإعدادات
Final Semantic Search Test with Configuration Verification
"""

import asyncio
import os
import sys
from azure.search.documents import SearchClient
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

class FinalSemanticTester:
    def __init__(self):
        # تحميل متغيرات البيئة
        load_dotenv("app/backend/.env")
        
        self.search_endpoint = os.environ.get("AZURE_SEARCH_ENDPOINT")
        self.search_key = os.environ.get("AZURE_SEARCH_API_KEY")
        self.search_index = os.environ.get("AZURE_SEARCH_INDEX")
        self.semantic_config = os.environ.get("AZURE_SEARCH_SEMANTIC_CONFIGURATION")
        
        print_arabic(f"🔗 نقطة النهاية: {self.search_endpoint}")
        print_arabic(f"📋 الفهرس: {self.search_index}")
        print_arabic(f"🧠 إعداد البحث الدلالي: {self.semantic_config}")
        
        if not all([self.search_endpoint, self.search_key, self.search_index]):
            raise ValueError("Missing required Azure Search configuration")
        
        self.credential = AzureKeyCredential(self.search_key)
        self.search_client = SearchClient(
            endpoint=self.search_endpoint,
            index_name=self.search_index,
            credential=self.credential
        )
        
        print_arabic("✅ تم تهيئة مختبر البحث الدلالي النهائي")
    
    async def test_semantic_search_working(self, query):
        """اختبار البحث الدلالي مع التحقق من العمل"""
        try:
            print_arabic(f"\n🧠 البحث الدلالي لـ: '{query}'")
            print_arabic(f"🔧 باستخدام الإعداد: {self.semantic_config}")
            
            results = self.search_client.search(
                search_text=query,
                top=3,
                select=["ID", "Name", "ingredients", "Price"],
                query_type="semantic",
                semantic_configuration_name=self.semantic_config,
                query_caption="extractive"
            )
            
            items = []
            for result in results:
                # استخراج الـ captions للبحث الدلالي
                captions = []
                if hasattr(result, "@search.captions") and result.get("@search.captions"):
                    for caption in result["@search.captions"]:
                        captions.append(caption.get("text", "") or caption.get("highlights", ""))
                
                items.append({
                    "id": result.get("ID"),
                    "name": result.get("Name"),
                    "ingredients": result.get("ingredients"),
                    "price": result.get("Price"),
                    "score": getattr(result, "@search.score", None),
                    "reranker_score": getattr(result, "@search.reranker_score", None),
                    "captions": captions
                })
            
            if items:
                print_arabic(f"✅ البحث الدلالي يعمل! تم العثور على {len(items)} نتيجة:")
                for i, item in enumerate(items, 1):
                    print_arabic(f"   {i}. {item['name']} - {item['price']} جنيه")
                    if item['reranker_score']:
                        print_arabic(f"      🧠 النقاط الدلالية: {item['reranker_score']:.3f}")
                    if item['captions']:
                        print_arabic(f"      📝 مقاطع مطابقة: {', '.join(item['captions'][:2])}")
                return True, items
            else:
                print_arabic("❌ لم يتم العثور على نتائج دلالية")
                return False, []
            
        except Exception as e:
            print_arabic(f"❌ خطأ في البحث الدلالي: {str(e)}")
            return False, []
    
    async def verify_semantic_working(self):
        """التحقق من أن البحث الدلالي يعمل"""
        print_arabic("🔍 التحقق من عمل البحث الدلالي...")
        print_arabic("=" * 60)
        
        test_queries = [
            "pizza tuna",
            "chicken burger", 
            "seafood"
        ]
        
        working_count = 0
        
        for query in test_queries:
            success, results = await self.test_semantic_search_working(query)
            if success:
                working_count += 1
        
        if working_count == len(test_queries):
            print_arabic(f"\n🎉 ممتاز! البحث الدلالي يعمل بشكل مثالي")
            print_arabic(f"✅ نجح في {working_count}/{len(test_queries)} اختبارات")
            return True
        elif working_count > 0:
            print_arabic(f"\n⚠️  البحث الدلالي يعمل جزئياً")
            print_arabic(f"✅ نجح في {working_count}/{len(test_queries)} اختبارات")
            return True
        else:
            print_arabic(f"\n❌ البحث الدلالي لا يعمل")
            print_arabic(f"❌ فشل في جميع الاختبارات")
            return False

async def main():
    """الدالة الرئيسية"""
    print_arabic("🚀 اختبار نهائي للبحث الدلالي")
    
    try:
        tester = FinalSemanticTester()
        is_working = await tester.verify_semantic_working()
        
        if is_working:
            print_arabic(f"\n🏁 النتيجة: البحث الدلالي يعمل! ✅")
            print_arabic(f"🎯 يمكن الآن إنشاء واجهة الاختبار")
        else:
            print_arabic(f"\n🏁 النتيجة: البحث الدلالي لا يعمل ❌")
            print_arabic(f"🔧 يحتاج إصلاح الإعدادات")
        
    except KeyboardInterrupt:
        print_arabic("\n⏹️  تم إيقاف الاختبار بواسطة المستخدم")
    except Exception as e:
        print_arabic(f"\n❌ خطأ عام: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
