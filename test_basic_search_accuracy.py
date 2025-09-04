#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار البحث الأساسي مع دقة النتائج والأسعار
Basic Search Testing - Result and Price Accuracy
"""

import asyncio
import os
import sys
import random
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

class BasicSearchAccuracyTester:
    def __init__(self):
        # تحميل متغيرات البيئة
        load_dotenv("app/backend/.env")
        
        self.search_endpoint = os.environ.get("AZURE_SEARCH_ENDPOINT")
        self.search_key = os.environ.get("AZURE_SEARCH_API_KEY")
        self.search_index = os.environ.get("AZURE_SEARCH_INDEX")
        
        if not all([self.search_endpoint, self.search_key, self.search_index]):
            raise ValueError("Missing required Azure Search configuration")
        
        self.credential = AzureKeyCredential(self.search_key)
        self.search_client = SearchClient(
            endpoint=self.search_endpoint,
            index_name=self.search_index,
            credential=self.credential
        )
        
        # عناصر الاختبار مع الأسعار المتوقعة (باللغة الإنجليزية للتطابق مع الفهرس)
        self.test_items = [
            {"name": "تونة", "search_term": "tuna", "expected_price_range": [130, 140], "description": "بيتزا تونة"},
            {"name": "برجر", "search_term": "burger", "expected_price_range": [90, 100], "description": "برجر لحمة"},
            {"name": "فراخ", "search_term": "chicken", "expected_price_range": [80, 90], "description": "فراخ بروستد"},
            {"name": "سلطة", "search_term": "salad", "expected_price_range": [40, 50], "description": "سلطة خضراء"},
            {"name": "مكرونة", "search_term": "pasta", "expected_price_range": [70, 80], "description": "مكرونة بالفراخ"},
            {"name": "مارجريتا", "search_term": "margherita", "expected_price_range": [135, 145], "description": "بيتزا مارجريتا"},
            {"name": "شاورما", "search_term": "shawarma", "expected_price_range": [50, 60], "description": "ساندوتش شاورما"},
            {"name": "عصير", "search_term": "juice", "expected_price_range": [20, 30], "description": "عصير برتقال"},
            {"name": "كالزونى", "search_term": "calzone", "expected_price_range": [75, 85], "description": "كالزونى باللحمة"},
            {"name": "حلويات", "search_term": "sweet", "expected_price_range": [115, 125], "description": "حلويات شرقية"}
        ]
        
        print_arabic("✅ تم تهيئة مختبر البحث الأساسي")
        print_arabic(f"🔗 الاتصال بـ: {self.search_index}")
    
    async def search_item(self, query):
        """البحث عن عنصر واحد"""
        try:
            results = self.search_client.search(
                search_text=query,
                top=5,
                select=["ID", "Name", "ingredients", "Price"]
            )
            
            items = []
            for result in results:
                items.append({
                    "id": result.get("ID"),
                    "name": result.get("Name"),
                    "ingredients": result.get("ingredients"), 
                    "price": result.get("Price"),
                    "score": getattr(result, "@search.score", None)
                })
            
            return items
            
        except Exception as e:
            print_arabic(f"❌ خطأ في البحث عن '{query}': {str(e)}")
            return []
    
    def evaluate_result(self, test_item, search_results):
        """تقييم نتيجة البحث"""
        evaluation = {
            "search_term": test_item["search_term"],
            "arabic_name": test_item["name"],
            "description": test_item["description"],
            "expected_price_range": test_item["expected_price_range"],
            "found_relevant": False,
            "price_in_range": False,
            "best_match": None,
            "all_results": search_results,
            "accuracy_score": 0
        }
        
        if not search_results:
            return evaluation
        
        # البحث عن أفضل تطابق
        best_match = None
        best_score = 0
        
        for result in search_results:
            # حساب التطابق بناءً على الاسم والمكونات
            name = result["name"].lower() if result["name"] else ""
            ingredients = result["ingredients"].lower() if result["ingredients"] else ""
            search_term = test_item["search_term"].lower()
            
            # حساب نقاط التطابق
            score = 0
            if search_term in name:
                score += 3  # تطابق في الاسم يحصل على نقاط أعلى
            if search_term in ingredients:
                score += 2  # تطابق في المكونات
            
            # إضافة نقاط البحث الأساسية
            if result["score"]:
                score += result["score"]
            
            if score > best_score:
                best_score = score
                best_match = result
        
        if best_match:
            evaluation["best_match"] = best_match
            evaluation["found_relevant"] = True
            evaluation["accuracy_score"] += 50
            
            # فحص السعر
            if best_match["price"]:
                price = float(best_match["price"])
                min_price, max_price = test_item["expected_price_range"]
                if min_price <= price <= max_price:
                    evaluation["price_in_range"] = True
                    evaluation["accuracy_score"] += 50
        
        return evaluation
    
    async def test_single_item(self, test_item):
        """اختبار عنصر واحد"""
        print_arabic(f"\n🔍 اختبار: {test_item['description']}")
        print_arabic(f"🔤 البحث بـ: '{test_item['search_term']}'")
        print_arabic(f"💰 السعر المتوقع: {test_item['expected_price_range'][0]}-{test_item['expected_price_range'][1]} جنيه")
        print_arabic("-" * 70)
        
        # البحث
        search_results = await self.search_item(test_item["search_term"])
        
        if search_results:
            print_arabic(f"✅ تم العثور على {len(search_results)} نتيجة:")
            for i, result in enumerate(search_results[:3], 1):
                price_str = result['price'] if result['price'] else "غير محدد"
                ingredients_str = result['ingredients'] if result['ingredients'] else "غير محدد"
                score_str = f"{result['score']:.3f}" if result['score'] else "غير محدد"
                
                print_arabic(f"   {i}. {result['name']} - {price_str} جنيه")
                print_arabic(f"      المكونات: {ingredients_str}")
                print_arabic(f"      النقاط: {score_str}")
        else:
            print_arabic("❌ لم يتم العثور على نتائج")
        
        # تقييم النتيجة
        evaluation = self.evaluate_result(test_item, search_results)
        
        if evaluation["found_relevant"]:
            print_arabic(f"\n✅ أفضل تطابق: {evaluation['best_match']['name']}")
            print_arabic(f"💰 السعر: {evaluation['best_match']['price']} جنيه")
            if evaluation["price_in_range"]:
                print_arabic("✅ السعر ضمن النطاق المتوقع")
            else:
                print_arabic("⚠️  السعر خارج النطاق المتوقع")
        else:
            print_arabic("❌ لم يتم العثور على تطابق مناسب")
        
        print_arabic(f"📊 نقاط الدقة: {evaluation['accuracy_score']}/100")
        
        return evaluation
    
    async def run_comprehensive_test(self, num_items=5):
        """تشغيل اختبار شامل لعدد محدد من العناصر"""
        print_arabic("🎯 مختبر دقة البحث الأساسي في Azure AI Search")
        print_arabic("=" * 70)
        print_arabic(f"📊 سيتم اختبار {num_items} عناصر عشوائية")
        
        # اختيار عناصر عشوائية
        selected_items = random.sample(self.test_items, min(num_items, len(self.test_items)))
        
        all_evaluations = []
        
        for item_index, test_item in enumerate(selected_items, 1):
            print_arabic(f"\n{'='*70}")
            print_arabic(f"🎮 اختبار العنصر {item_index}/{num_items}")
            
            evaluation = await self.test_single_item(test_item)
            all_evaluations.append(evaluation)
        
        # تحليل النتائج الإجمالية
        print_arabic(f"\n{'='*70}")
        print_arabic("📈 تحليل النتائج الإجمالية")
        print_arabic("=" * 70)
        
        total_tests = len(all_evaluations)
        found_relevant = sum(1 for eval in all_evaluations if eval["found_relevant"])
        price_correct = sum(1 for eval in all_evaluations if eval["price_in_range"])
        both_correct = sum(1 for eval in all_evaluations if eval["found_relevant"] and eval["price_in_range"])
        
        avg_accuracy = sum(eval["accuracy_score"] for eval in all_evaluations) / total_tests if total_tests > 0 else 0
        
        print_arabic(f"📊 إجمالي الاختبارات: {total_tests}")
        print_arabic(f"✅ العناصر ذات الصلة: {found_relevant}/{total_tests} ({found_relevant/total_tests*100:.1f}%)")
        print_arabic(f"💰 الأسعار المناسبة: {price_correct}/{total_tests} ({price_correct/total_tests*100:.1f}%)")
        print_arabic(f"🎯 كلاهما صحيح: {both_correct}/{total_tests} ({both_correct/total_tests*100:.1f}%)")
        print_arabic(f"📈 متوسط النقاط: {avg_accuracy:.1f}/100")
        
        # عرض أمثلة للنتائج الناجحة
        successful_tests = [eval for eval in all_evaluations if eval["found_relevant"]]
        if successful_tests:
            print_arabic(f"\n✅ أمثلة النتائج الناجحة:")
            for test in successful_tests[:3]:
                print_arabic(f"   🔍 '{test['search_term']}' ← {test['best_match']['name']} ({test['best_match']['price']} جنيه)")
        
        # تفاصيل الأخطاء
        errors = [eval for eval in all_evaluations if not eval["found_relevant"]]
        if errors:
            print_arabic(f"\n⚠️  اختبارات فشلت ({len(errors)} اختبار):")
            for error in errors:
                print_arabic(f"   🔍 '{error['search_term']}' ({error['description']})")
        
        # تقييم الأداء
        if avg_accuracy >= 80:
            print_arabic("\n🎉 ممتاز! البحث يعمل بدقة عالية")
        elif avg_accuracy >= 60:
            print_arabic("\n👍 جيد! البحث يعمل بشكل مقبول") 
        else:
            print_arabic("\n⚠️  يحتاج تحسين! البحث يحتاج لمراجعة")
        
        return {
            "total_tests": total_tests,
            "found_relevant": found_relevant,
            "price_correct": price_correct,
            "both_correct": both_correct,
            "average_accuracy": avg_accuracy,
            "all_evaluations": all_evaluations
        }

async def main():
    """الدالة الرئيسية"""
    print_arabic("🚀 بدء اختبار دقة البحث الأساسي")
    
    try:
        tester = BasicSearchAccuracyTester()
        
        # تشغيل الاختبار لـ 5 عناصر
        results = await tester.run_comprehensive_test(num_items=5)
        
        print_arabic(f"\n🏁 انتهى الاختبار بنجاح!")
        print_arabic(f"📋 النتيجة النهائية: {results['average_accuracy']:.1f}/100")
        
    except KeyboardInterrupt:
        print_arabic("\n⏹️  تم إيقاف الاختبار بواسطة المستخدم")
    except Exception as e:
        print_arabic(f"\n❌ خطأ: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
