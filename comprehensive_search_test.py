#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار شامل للبحث بالعربية والإنجليزية مع تحليل مفصل للنتائج
Comprehensive Arabic/English Search Test with Detailed Analysis
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

class ComprehensiveSearchTester:
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
        
        # 5 عناصر للاختبار الشامل
        self.test_items = [
            {
                "name": "بيتزا تونة وسط",
                "arabic_queries": ["بيتزا تونة", "تونة وسط", "بيتزا التونة"],
                "english_queries": ["tuna pizza", "medium tuna", "tuna"],
                "expected_price": 150,  # من نتائج الاختبار السابق
                "price_tolerance": 20
            },
            {
                "name": "برجر لحمة",
                "arabic_queries": ["برجر لحمة", "برجر بقري", "برجر"],
                "english_queries": ["beef burger", "burger", "meat burger"],
                "expected_price": 110,  # من نتائج الاختبار السابق
                "price_tolerance": 15
            },
            {
                "name": "كالزونى",
                "arabic_queries": ["كالزونى", "كالزوني", "كالزونة"],
                "english_queries": ["calzone", "calzoni"],
                "expected_price": 125,  # من نتائج الاختبار السابق
                "price_tolerance": 25
            },
            {
                "name": "بيتزا دجاج",
                "arabic_queries": ["بيتزا دجاج", "بيتزا فراخ", "دجاج"],
                "english_queries": ["chicken pizza", "chicken", "crispy chicken"],
                "expected_price": 170,  # من نتائج سابقة
                "price_tolerance": 20
            },
            {
                "name": "بيتزا مأكولات بحرية",
                "arabic_queries": ["مأكولات بحرية", "بيتزا سي فود", "جمبري"],
                "english_queries": ["seafood pizza", "seafood", "shrimp pizza"],
                "expected_price": 210,  # من نتائج سابقة
                "price_tolerance": 25
            }
        ]
        
        print_arabic("✅ تم تهيئة مختبر البحث الشامل")
        print_arabic(f"🔗 الاتصال بـ: {self.search_index}")
    
    async def search_item(self, query, language="auto"):
        """البحث عن عنصر واحد"""
        try:
            results = self.search_client.search(
                search_text=query,
                top=3,
                select=["ID", "Name", "ingredients", "Price"]
            )
            
            items = []
            for result in results:
                items.append({
                    "id": result.get("ID"),
                    "name": result.get("Name"),
                    "ingredients": result.get("ingredients"), 
                    "price": float(result.get("Price")) if result.get("Price") else None,
                    "score": getattr(result, "@search.score", None)
                })
            
            return items
            
        except Exception as e:
            print_arabic(f"❌ خطأ في البحث عن '{query}': {str(e)}")
            return []
    
    def evaluate_search_quality(self, query, results, expected_item):
        """تقييم جودة البحث"""
        evaluation = {
            "query": query,
            "found_results": len(results) > 0,
            "relevant_result": False,
            "price_accurate": False,
            "best_match": None,
            "price_difference": None,
            "quality_score": 0
        }
        
        if not results:
            return evaluation
        
        # البحث عن أفضل تطابق
        best_match = results[0]  # أعلى نتيجة
        evaluation["best_match"] = best_match
        evaluation["found_results"] = True
        evaluation["quality_score"] += 25
        
        # فحص الصلة
        name = best_match["name"].lower()
        ingredients = best_match["ingredients"].lower() if best_match["ingredients"] else ""
        
        # كلمات مفتاحية للصلة
        query_words = query.lower().split()
        relevance_score = 0
        
        for word in query_words:
            if word in name or word in ingredients:
                relevance_score += 1
        
        if relevance_score > 0:
            evaluation["relevant_result"] = True
            evaluation["quality_score"] += 35
        
        # فحص السعر
        if best_match["price"] and expected_item["expected_price"]:
            price_diff = abs(best_match["price"] - expected_item["expected_price"])
            evaluation["price_difference"] = price_diff
            
            if price_diff <= expected_item["price_tolerance"]:
                evaluation["price_accurate"] = True
                evaluation["quality_score"] += 40
            elif price_diff <= expected_item["price_tolerance"] * 2:
                evaluation["quality_score"] += 20  # جزئياً صحيح
        
        return evaluation
    
    async def test_item_comprehensively(self, test_item):
        """اختبار شامل لعنصر واحد"""
        print_arabic(f"\n🎯 اختبار شامل: {test_item['name']}")
        print_arabic(f"💰 السعر المتوقع: {test_item['expected_price']} ± {test_item['price_tolerance']} جنيه")
        print_arabic("=" * 70)
        
        all_evaluations = []
        
        # اختبار البحث بالعربية
        print_arabic(f"\n🔤 اختبار البحث بالعربية:")
        for i, query in enumerate(test_item["arabic_queries"], 1):
            print_arabic(f"\n   {i}. البحث بـ: '{query}'")
            results = await self.search_item(query, "arabic")
            evaluation = self.evaluate_search_quality(query, results, test_item)
            all_evaluations.append({**evaluation, "language": "arabic"})
            
            if results:
                best = evaluation["best_match"]
                print_arabic(f"      ✅ {best['name']} - {best['price']} جنيه")
                if evaluation["relevant_result"]:
                    print_arabic(f"      🎯 ذات صلة")
                if evaluation["price_accurate"]:
                    print_arabic(f"      💰 السعر دقيق")
                elif evaluation["price_difference"]:
                    print_arabic(f"      ⚠️  فرق السعر: {evaluation['price_difference']:.0f} جنيه")
            else:
                print_arabic(f"      ❌ لا توجد نتائج")
        
        # اختبار البحث بالإنجليزية
        print_arabic(f"\n🔤 اختبار البحث بالإنجليزية:")
        for i, query in enumerate(test_item["english_queries"], 1):
            print_arabic(f"\n   {i}. البحث بـ: '{query}'")
            results = await self.search_item(query, "english")
            evaluation = self.evaluate_search_quality(query, results, test_item)
            all_evaluations.append({**evaluation, "language": "english"})
            
            if results:
                best = evaluation["best_match"]
                print_arabic(f"      ✅ {best['name']} - {best['price']} جنيه")
                if evaluation["relevant_result"]:
                    print_arabic(f"      🎯 ذات صلة")
                if evaluation["price_accurate"]:
                    print_arabic(f"      💰 السعر دقيق")
                elif evaluation["price_difference"]:
                    print_arabic(f"      ⚠️  فرق السعر: {evaluation['price_difference']:.0f} جنيه")
            else:
                print_arabic(f"      ❌ لا توجد نتائج")
        
        # تحليل الأداء للعنصر
        arabic_evals = [e for e in all_evaluations if e["language"] == "arabic"]
        english_evals = [e for e in all_evaluations if e["language"] == "english"]
        
        arabic_avg = sum(e["quality_score"] for e in arabic_evals) / len(arabic_evals) if arabic_evals else 0
        english_avg = sum(e["quality_score"] for e in english_evals) / len(english_evals) if english_evals else 0
        
        print_arabic(f"\n📊 ملخص النتائج لـ {test_item['name']}:")
        print_arabic(f"   🇸🇦 العربية: {arabic_avg:.1f}/100")
        print_arabic(f"   🇺🇸 الإنجليزية: {english_avg:.1f}/100")
        
        return all_evaluations
    
    async def run_full_test(self):
        """تشغيل الاختبار الكامل"""
        print_arabic("🚀 اختبار شامل لدقة البحث في Azure AI Search")
        print_arabic("=" * 70)
        print_arabic("🎯 الهدف: قياس دقة البحث بالعربية والإنجليزية")
        print_arabic("📊 سيتم اختبار 5 عناصر مختلفة")
        
        all_evaluations = []
        
        for i, test_item in enumerate(self.test_items, 1):
            print_arabic(f"\n{'='*70}")
            print_arabic(f"🧪 اختبار العنصر {i}/5")
            
            item_evaluations = await self.test_item_comprehensively(test_item)
            all_evaluations.extend(item_evaluations)
        
        # التحليل النهائي
        print_arabic(f"\n{'='*70}")
        print_arabic("📈 التحليل النهائي الشامل")
        print_arabic("=" * 70)
        
        # تقسيم النتائج حسب اللغة
        arabic_results = [e for e in all_evaluations if e["language"] == "arabic"]
        english_results = [e for e in all_evaluations if e["language"] == "english"]
        
        # إحصائيات عامة
        total_tests = len(all_evaluations)
        found_results = sum(1 for e in all_evaluations if e["found_results"])
        relevant_results = sum(1 for e in all_evaluations if e["relevant_result"])
        accurate_prices = sum(1 for e in all_evaluations if e["price_accurate"])
        
        avg_quality = sum(e["quality_score"] for e in all_evaluations) / total_tests if total_tests > 0 else 0
        
        print_arabic(f"📊 إحصائيات عامة:")
        print_arabic(f"   🔍 إجمالي الاختبارات: {total_tests}")
        print_arabic(f"   ✅ وُجدت نتائج: {found_results}/{total_tests} ({found_results/total_tests*100:.1f}%)")
        print_arabic(f"   🎯 نتائج ذات صلة: {relevant_results}/{total_tests} ({relevant_results/total_tests*100:.1f}%)")
        print_arabic(f"   💰 أسعار دقيقة: {accurate_prices}/{total_tests} ({accurate_prices/total_tests*100:.1f}%)")
        print_arabic(f"   📈 متوسط الجودة: {avg_quality:.1f}/100")
        
        # مقارنة اللغات
        if arabic_results and english_results:
            arabic_avg = sum(e["quality_score"] for e in arabic_results) / len(arabic_results)
            english_avg = sum(e["quality_score"] for e in english_results) / len(english_results)
            
            arabic_relevant = sum(1 for e in arabic_results if e["relevant_result"])
            english_relevant = sum(1 for e in english_results if e["relevant_result"])
            
            print_arabic(f"\n🌍 مقارنة اللغات:")
            print_arabic(f"   🇸🇦 العربية: {arabic_avg:.1f}/100 (نتائج ذات صلة: {arabic_relevant}/{len(arabic_results)})")
            print_arabic(f"   🇺🇸 الإنجليزية: {english_avg:.1f}/100 (نتائج ذات صلة: {english_relevant}/{len(english_results)})")
            
            if english_avg > arabic_avg:
                print_arabic(f"   📊 الإنجليزية أفضل بـ {english_avg - arabic_avg:.1f} نقطة")
            elif arabic_avg > english_avg:
                print_arabic(f"   📊 العربية أفضل بـ {arabic_avg - english_avg:.1f} نقطة")
            else:
                print_arabic(f"   📊 الأداء متساوٍ")
        
        # أفضل وأسوأ النتائج
        best_queries = sorted(all_evaluations, key=lambda x: x["quality_score"], reverse=True)[:3]
        worst_queries = sorted(all_evaluations, key=lambda x: x["quality_score"])[:3]
        
        print_arabic(f"\n🏆 أفضل الاستعلامات:")
        for i, query in enumerate(best_queries, 1):
            print_arabic(f"   {i}. '{query['query']}' ({query['language']}) - {query['quality_score']}/100")
        
        print_arabic(f"\n⚠️  أسوأ الاستعلامات:")
        for i, query in enumerate(worst_queries, 1):
            print_arabic(f"   {i}. '{query['query']}' ({query['language']}) - {query['quality_score']}/100")
        
        # تقييم الأداء العام
        print_arabic(f"\n🎯 التقييم النهائي:")
        if avg_quality >= 80:
            print_arabic("   🎉 ممتاز! النظام يعمل بدقة عالية")
            print_arabic("   ✅ البحث موثوق وأسعار دقيقة")
        elif avg_quality >= 60:
            print_arabic("   👍 جيد! النظام يعمل بشكل مقبول")
            print_arabic("   ⚠️  قد تحتاج بعض الاستعلامات تحسين")
        elif avg_quality >= 40:
            print_arabic("   ⚠️  متوسط! يحتاج تحسين")
            print_arabic("   🔧 راجع إعدادات البحث والفهرس")
        else:
            print_arabic("   ❌ ضعيف! يحتاج مراجعة شاملة")
            print_arabic("   🛠️  قد تحتاج إعادة تكوين النظام")
        
        return {
            "total_tests": total_tests,
            "found_results": found_results,
            "relevant_results": relevant_results,
            "accurate_prices": accurate_prices,
            "average_quality": avg_quality,
            "arabic_average": sum(e["quality_score"] for e in arabic_results) / len(arabic_results) if arabic_results else 0,
            "english_average": sum(e["quality_score"] for e in english_results) / len(english_results) if english_results else 0,
            "all_evaluations": all_evaluations
        }

async def main():
    """الدالة الرئيسية"""
    print_arabic("🚀 بدء الاختبار الشامل لدقة البحث")
    
    try:
        tester = ComprehensiveSearchTester()
        results = await tester.run_full_test()
        
        print_arabic(f"\n🏁 انتهى الاختبار الشامل!")
        print_arabic(f"📋 النتيجة النهائية: {results['average_quality']:.1f}/100")
        print_arabic(f"🇸🇦 العربية: {results['arabic_average']:.1f}/100")
        print_arabic(f"🇺🇸 الإنجليزية: {results['english_average']:.1f}/100")
        
    except KeyboardInterrupt:
        print_arabic("\n⏹️  تم إيقاف الاختبار بواسطة المستخدم")
    except Exception as e:
        print_arabic(f"\n❌ خطأ: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
