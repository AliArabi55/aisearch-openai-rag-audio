#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار البحث الدلالي - دقة النتائج والأسعار
Semantic Search Testing - Result and Price Accuracy
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

class SemanticSearchAccuracyTester:
    def __init__(self):
        # تحميل متغيرات البيئة
        load_dotenv("app/backend/.env")
        
        self.search_endpoint = os.environ.get("AZURE_SEARCH_ENDPOINT")
        self.search_key = os.environ.get("AZURE_SEARCH_API_KEY")
        self.search_index = os.environ.get("AZURE_SEARCH_INDEX")
        self.semantic_config = os.environ.get("AZURE_SEARCH_SEMANTIC_CONFIGURATION")
        
        if not all([self.search_endpoint, self.search_key, self.search_index]):
            raise ValueError("Missing required Azure Search configuration")
        
        self.credential = AzureKeyCredential(self.search_key)
        self.search_client = SearchClient(
            endpoint=self.search_endpoint,
            index_name=self.search_index,
            credential=self.credential
        )
        
        # عناصر الاختبار مع الأسعار المتوقعة
        self.test_items = [
            {"name": "بيتزا تونة وسط", "expected_price": 130, "variations": ["تونة وسط", "pizza tuna medium", "بيتزا التونة الوسط"]},
            {"name": "برجر لحمة دبل", "expected_price": 95, "variations": ["برجر دبل", "double burger", "برجر لحم دبل"]},
            {"name": "فراخ بروستد", "expected_price": 85, "variations": ["بروستد", "fried chicken", "فراخ مقلية"]},
            {"name": "سلطة خضراء", "expected_price": 45, "variations": ["سلطة", "green salad", "سلطة طازجة"]},
            {"name": "مكرونة بالفراخ", "expected_price": 75, "variations": ["مكرونة فراخ", "pasta chicken", "باستا بالدجاج"]},
            {"name": "بيتزا مارجريتا كبير", "expected_price": 140, "variations": ["مارجريتا كبير", "margherita large", "بيتزا مارجريتا لارج"]},
            {"name": "ساندوتش شاورما", "expected_price": 55, "variations": ["شاورما", "shawarma sandwich", "ساندوتش شاورما لحمة"]},
            {"name": "عصير برتقال", "expected_price": 25, "variations": ["عصير برتقال طبيعي", "orange juice", "برتقال فريش"]},
            {"name": "كالزونى باللحمة", "expected_price": 80, "variations": ["كالزونى لحمة", "calzone meat", "كالزوني لحم"]},
            {"name": "حلويات شرقية", "expected_price": 120, "variations": ["حلويات", "oriental sweets", "حلوى شرقية"]}
        ]
        
        print_arabic("✅ تم تهيئة مختبر البحث الدلالي")
        print_arabic(f"🔗 الاتصال بـ: {self.search_index}")
    
    async def search_item(self, query, use_semantic=True):
        """البحث عن عنصر واحد"""
        try:
            if use_semantic and self.semantic_config:
                results = self.search_client.search(
                    search_text=query,
                    top=3,
                    select=["ID", "Name", "ingredients", "Price"],
                    query_type="semantic",
                    semantic_configuration_name=self.semantic_config,
                    query_caption="extractive"
                )
            else:
                results = self.search_client.search(
                    search_text=query,
                    top=3,
                    select=["ID", "Name", "ingredients", "Price"]
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
            
            return items
            
        except Exception as e:
            print_arabic(f"❌ خطأ في البحث عن '{query}': {str(e)}")
            return []
    
    def evaluate_result(self, query, expected_item, search_results):
        """تقييم نتيجة البحث"""
        evaluation = {
            "query": query,
            "expected_name": expected_item["name"],
            "expected_price": expected_item["expected_price"],
            "found": False,
            "correct_price": False,
            "actual_name": None,
            "actual_price": None,
            "accuracy_score": 0,
            "top_result": None,
            "all_results": search_results
        }
        
        if not search_results:
            return evaluation
        
        # أخذ أول نتيجة (الأعلى نقاطاً)
        top_result = search_results[0]
        evaluation["top_result"] = top_result
        evaluation["actual_name"] = top_result["name"]
        evaluation["actual_price"] = top_result["price"]
        
        # فحص إذا كان العنصر موجود (بناءً على التشابه في الاسم)
        expected_keywords = expected_item["name"].lower().split()
        actual_name = top_result["name"].lower() if top_result["name"] else ""
        
        # حساب التطابق
        matches = sum(1 for keyword in expected_keywords if keyword in actual_name)
        similarity = matches / len(expected_keywords) if expected_keywords else 0
        
        if similarity >= 0.5:  # 50% تشابه على الأقل
            evaluation["found"] = True
            evaluation["accuracy_score"] += 50
        
        # فحص السعر
        if top_result["price"] and abs(float(top_result["price"]) - expected_item["expected_price"]) <= 5:
            evaluation["correct_price"] = True
            evaluation["accuracy_score"] += 50
        
        return evaluation
    
    async def test_single_item(self, test_item):
        """اختبار عنصر واحد مع جميع اختلافاته"""
        print_arabic(f"\n🔍 اختبار: {test_item['name']} (السعر المتوقع: {test_item['expected_price']} جنيه)")
        print_arabic("-" * 70)
        
        results = []
        
        # اختبار الاسم الأساسي
        queries_to_test = [test_item['name']] + test_item['variations']
        
        for i, query in enumerate(queries_to_test):
            print_arabic(f"\n🔤 الاستعلام {i+1}: '{query}'")
            
            # البحث الدلالي
            search_results = await self.search_item(query, use_semantic=True)
            
            if search_results:
                print_arabic(f"✅ تم العثور على {len(search_results)} نتيجة")
                top_result = search_results[0]
                print_arabic(f"   📍 أعلى نتيجة: {top_result['name']}")
                print_arabic(f"   💰 السعر: {top_result['price']} جنيه")
                if top_result['reranker_score']:
                    print_arabic(f"   🧠 النقاط الدلالية: {top_result['reranker_score']:.3f}")
                if top_result['captions']:
                    print_arabic(f"   📝 مقاطع مطابقة: {', '.join(top_result['captions'][:2])}")
            else:
                print_arabic("❌ لم يتم العثور على نتائج")
            
            # تقييم النتيجة
            evaluation = self.evaluate_result(query, test_item, search_results)
            results.append(evaluation)
        
        return results
    
    async def run_comprehensive_test(self, num_items=5):
        """تشغيل اختبار شامل لعدد محدد من العناصر"""
        print_arabic("🎯 مختبر دقة البحث الدلالي")
        print_arabic("=" * 70)
        print_arabic(f"📊 سيتم اختبار {num_items} عناصر عشوائية")
        
        # اختيار عناصر عشوائية
        selected_items = random.sample(self.test_items, min(num_items, len(self.test_items)))
        
        all_evaluations = []
        
        for item_index, test_item in enumerate(selected_items, 1):
            print_arabic(f"\n{'='*70}")
            print_arabic(f"🎮 اختبار العنصر {item_index}/{num_items}")
            
            item_results = await self.test_single_item(test_item)
            all_evaluations.extend(item_results)
        
        # تحليل النتائج الإجمالية
        print_arabic(f"\n{'='*70}")
        print_arabic("📈 تحليل النتائج الإجمالية")
        print_arabic("=" * 70)
        
        total_tests = len(all_evaluations)
        found_correct = sum(1 for eval in all_evaluations if eval["found"])
        price_correct = sum(1 for eval in all_evaluations if eval["correct_price"])
        both_correct = sum(1 for eval in all_evaluations if eval["found"] and eval["correct_price"])
        
        avg_accuracy = sum(eval["accuracy_score"] for eval in all_evaluations) / total_tests if total_tests > 0 else 0
        
        print_arabic(f"📊 إجمالي الاختبارات: {total_tests}")
        print_arabic(f"✅ العناصر الموجودة: {found_correct}/{total_tests} ({found_correct/total_tests*100:.1f}%)")
        print_arabic(f"💰 الأسعار الصحيحة: {price_correct}/{total_tests} ({price_correct/total_tests*100:.1f}%)")
        print_arabic(f"🎯 كلاهما صحيح: {both_correct}/{total_tests} ({both_correct/total_tests*100:.1f}%)")
        print_arabic(f"📈 متوسط النقاط: {avg_accuracy:.1f}/100")
        
        # تفاصيل الأخطاء
        errors = [eval for eval in all_evaluations if not eval["found"] or not eval["correct_price"]]
        if errors:
            print_arabic(f"\n⚠️  الأخطاء المكتشفة ({len(errors)} خطأ):")
            for error in errors[:5]:  # أول 5 أخطاء
                print_arabic(f"   🔍 '{error['query']}':")
                print_arabic(f"      المتوقع: {error['expected_name']} ({error['expected_price']} جنيه)")
                if error['actual_name']:
                    print_arabic(f"      الفعلي: {error['actual_name']} ({error['actual_price']} جنيه)")
                else:
                    print_arabic(f"      الفعلي: لم يتم العثور على نتائج")
        
        # تقييم الأداء
        if avg_accuracy >= 80:
            print_arabic("\n🎉 ممتاز! البحث الدلالي يعمل بدقة عالية")
        elif avg_accuracy >= 60:
            print_arabic("\n👍 جيد! البحث الدلالي يعمل بشكل مقبول")
        else:
            print_arabic("\n⚠️  يحتاج تحسين! البحث الدلالي يحتاج لمراجعة")
        
        return {
            "total_tests": total_tests,
            "found_correct": found_correct,
            "price_correct": price_correct,
            "both_correct": both_correct,
            "average_accuracy": avg_accuracy,
            "all_evaluations": all_evaluations
        }

async def main():
    """الدالة الرئيسية"""
    print_arabic("🚀 بدء اختبار دقة البحث الدلالي")
    
    try:
        tester = SemanticSearchAccuracyTester()
        
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
