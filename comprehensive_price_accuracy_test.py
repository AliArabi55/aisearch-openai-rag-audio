#!/usr/bin/env python3
"""
comprehensive_price_accuracy_test.py
🔍 اختبار شامل لدقة الأسعار والبحث الدلالي
"""

import asyncio
import json
import sys
import os
from typing import Dict, List, Optional
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

# إعداد الترميز للنصوص العربية
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

# تحميل متغيرات البيئة من مجلد app/backend
env_path = os.path.join(os.path.dirname(__file__), "app", "backend", ".env")
load_dotenv(env_path)

# الأسعار المرجعية التي أعطاها المستخدم
REFERENCE_PRICES = {
    "Large Crispy Chicken Calzone": 180,
    "Large BBQ Chicken Calzone": 180,
    "Onion Rings Plate": 30,
    "Double Cheesy Crispy Sandwich": 220,
    "Double American Crispy Sandwich": 210,
    "Double Vibes Crispy Sandwich": 230,
    "Double Crazy Ranch Crispy Sandwich": 250,
    "Double Juicy Crispy Sandwich": 230,
    "Double Delight Crispy Sandwich": 230,
    "Double Tasty Crispy Sandwich": 220,
    "Single Cheesy Crispy Sandwich": 120,
    "Single American Crispy Sandwich": 125,
    "Single Tasty Crispy Sandwich": 120,
    "Single Juicy Crispy Sandwich": 125,
    "Single Crazy Ranch Crispy Sandwich": 135,
    "Single Vibes Crispy Sandwich": 125,
    "Single Delight Crispy Sandwich": 125,
    "Double Cheesy Beef Burger": 210,
    "Double American Beef Burger": 210,
    "Double Vibes Beef Burger": 220,
    "Mushroom Beef Pizza Burger": 145,
    "Crispy Cheese Bacon Pizza Burger": 135,
    "Medium Hot Dog Pizza": 115,
    "Double Cheese Bacon Mix Sandwich": 230,
    "Medium Hot Dog Calzone": 110,
    "Double Cheese Bacon Burger": 220,
    "Beef Chili Fries": 60,
    "Blue Cheese Beef Pizza Burger": 130,
    "Large Hot Dog Pizza": 145,
    "Single Mushroom Crispy Sandwich": 135,
    "Single American Beef Burger": 115,
    "Large Hot Dog Calzone": 125,
    "Double Mushroom Crispy Sandwich": 240,
    "Single Cheese Bacon Burger": 115,
    "Double Blue Cheese Burger": 210,
    "Single Cheesy Beef Burger": 110,
    "Blue Cheese Crispy Pizza Burger": 135,
    "Medium Sausage Calzone": 140,
    "Single Blue Cheese Burger": 110,
    "Large Sausage Pizza": 185,
    "Double Blue Cheese Mix Sandwich": 220,
    "Spicy Beef Pizza Burger": 120,
    "Single Cheese Bacon Crispy Sandwich": 120,
    "Double Cheese Bacon Crispy Sandwich": 220,
    "Medium Sausage Pizza": 150,
    "Large Sausage Calzone": 165,
    "Single Spicy Burger": 110,
    "Single Blue Cheese Crispy Sandwich": 115,
    "Double Spicy Mix Sandwich": 200,
    "Double Blue Cheese Crispy Sandwich": 220,
    "Medium Salami Pizza": 115,
    "Spicy Crispy Pizza Burger": 125,
    "Double Spicy Burger": 185,
    "Medium Salami Calzone": 110,
    "Large Salami Pizza": 135,
    "Large Salami Calzone": 130,
    "Mexican Beef Pizza Burger": 130,
    "Medium Beef Bacon Calzone": 120,
    "Large Beef Bacon Calzone": 160,
    "Large Beef Bacon Pizza": 175,
    "Mexican Crispy Pizza Burger": 135,
    "Single Zinger Crispy Sandwich": 115,
    "Double Zinger Crispy Sandwich": 190,
    "Double Mexican Mix Sandwich": 210,
    "Single Mexican Burger": 115,
    "Double Mexican Burger": 200,
    "Medium Beef Bacon Pizza": 140,
    "Single Special Burger": 130,
    "Double Special Mix Sandwich": 230,
    "Large Smoked Turkey Calzone": 130,
    "Medium Smoked Turkey Pizza": 130,
    "Special Crispy Pizza Burger": 150,
    "Special Beef Pizza Burger": 145,
    "Large Smoked Turkey Pizza": 145,
    "Double Special Burger": 230,
    "Medium Smoked Turkey Calzone": 110,
    "Single Mexican Crispy Sandwich": 120,
    "Double Mexican Crispy Sandwich": 200,
    "Medium Mixed Meats Calzone": 160,
    "Large Mixed Meats Calzone": 200,
    "Single Special Crispy Sandwich": 135,
    "Double Special Crispy Sandwich": 240,
    "Medium Mixed Meats Pizza": 185,
    "Large Mixed Meats Pizza": 225,
    "Large Chicken Pizza": 185,
    "Medium Chicken Calzone": 130,
    "Large Chicken Calzone": 165,
    "Large Chicken Ranch Calzone": 185,
    "Medium Chicken Pizza": 150,
    "Medium Chicken Ranch Calzone": 160,
    "Large Chicken Ranch Pizza": 200,
    "Medium Chicken Ranch Pizza": 170,
    "Medium BBQ Chicken Pizza": 155,
    "Medium BBQ Chicken Calzone": 145,
    "Large BBQ Chicken Pizza": 185,
    "Large Crispy Chicken Pizza": 205,
    "Medium Crispy Chicken Pizza": 170,
    "Medium Crispy Chicken Calzone": 160,
    "Medium Tuna Pizza": 150,
    "Medium Tuna Calzone": 140,
    "Large Tuna Pizza": 185,
    "Large Shrimp Pizza": 195,
    "Medium Shrimp Pizza": 170,
    "Large Cuttlefish Pizza": 195,
    "Medium Cuttlefish Pizza": 170,
    "Medium Seafood Pizza": 185,
    "Large Seafood Pizza": 210,
    "Large Crab Pizza": 175,
    "Medium Crab Pizza": 140,
    "Large Deluxe Seafood Pizza with Caviar": 220,
    "Medium Deluxe Seafood Calzone": 165,
    "Medium Deluxe Seafood Pizza with Caviar": 200,
    "Medium Anchovy Pizza": 160,
    "Large Anchovy Pizza": 175,
    "Medium Anchovy Calzone": 125
}

async def test_semantic_search_accuracy():
    """
    🔍 اختبار دقة البحث الدلالي والأسعار
    """
    print("🔍 بدء اختبار البحث الدلالي وصحة الأسعار...")
    print("=" * 70)
    
    # إعداد Azure Search
    search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
    search_key = os.getenv("AZURE_SEARCH_API_KEY")
    search_index = os.getenv("AZURE_SEARCH_INDEX")
    semantic_config = os.getenv("AZURE_SEARCH_SEMANTIC_CONFIGURATION")
    
    if not all([search_endpoint, search_key, search_index]):
        print("❌ متغيرات البيئة مفقودة!")
        return
    
    search_client = SearchClient(
        endpoint=search_endpoint,
        index_name=search_index,
        credential=AzureKeyCredential(search_key)
    )
    
    # نتائج الاختبار
    test_results = {
        "semantic_working": False,
        "total_items": len(REFERENCE_PRICES),
        "found_items": 0,
        "price_matches": 0,
        "price_mismatches": [],
        "missing_items": [],
        "semantic_scores": []
    }
    
    print(f"📊 اختبار {len(REFERENCE_PRICES)} منتج...")
    print()
    
    for item_name, expected_price in REFERENCE_PRICES.items():
        try:
            # البحث الدلالي
            search_results = search_client.search(
                search_text=item_name,
                query_type="semantic",
                semantic_configuration_name=semantic_config,
                top=3,
                select="ID,Name,ingredients,Price",
                search_fields=["ingredients"]
            )
            
            found = False
            best_match = None
            
            for result in search_results:
                result_name = result.get("Name", "")
                result_price = result.get("Price", 0)
                semantic_score = result.get("@search.reranker_score", 0)
                
                # إضافة النقاط الدلالية
                if semantic_score > 0:
                    test_results["semantic_scores"].append(semantic_score)
                    test_results["semantic_working"] = True
                
                # مطابقة دقيقة للاسم
                if result_name.strip().lower() == item_name.strip().lower():
                    found = True
                    best_match = {
                        "name": result_name,
                        "price": result_price,
                        "semantic_score": semantic_score,
                        "expected_price": expected_price
                    }
                    break
            
            if found:
                test_results["found_items"] += 1
                
                # فحص السعر
                if best_match["price"] == expected_price:
                    test_results["price_matches"] += 1
                    print(f"✅ {item_name}: سعر صحيح ({best_match['price']} جنيه) - نقاط دلالية: {best_match['semantic_score']:.2f}")
                else:
                    test_results["price_mismatches"].append({
                        "item": item_name,
                        "expected_price": expected_price,
                        "actual_price": best_match["price"],
                        "semantic_score": best_match["semantic_score"]
                    })
                    print(f"❌ {item_name}: سعر خاطئ! متوقع: {expected_price}, فعلي: {best_match['price']} - نقاط دلالية: {best_match['semantic_score']:.2f}")
            else:
                test_results["missing_items"].append(item_name)
                print(f"🔍 {item_name}: لم يتم العثور عليه")
                
        except Exception as e:
            print(f"❌ خطأ في البحث عن {item_name}: {str(e)}")
    
    # تقرير شامل
    print()
    print("=" * 70)
    print("📊 تقرير الاختبار الشامل")
    print("=" * 70)
    
    # حالة البحث الدلالي
    if test_results["semantic_working"]:
        avg_semantic_score = sum(test_results["semantic_scores"]) / len(test_results["semantic_scores"])
        print(f"✅ البحث الدلالي: يعمل بنجاح")
        print(f"📊 متوسط النقاط الدلالية: {avg_semantic_score:.2f}")
        print(f"📈 نطاق النقاط: {min(test_results['semantic_scores']):.2f} - {max(test_results['semantic_scores']):.2f}")
    else:
        print(f"❌ البحث الدلالي: لا يعمل أو لا يحتوي على نقاط دلالية")
    
    print()
    
    # إحصائيات العثور على المنتجات
    found_percentage = (test_results["found_items"] / test_results["total_items"]) * 100
    print(f"🔍 نتائج البحث:")
    print(f"   📦 إجمالي المنتجات: {test_results['total_items']}")
    print(f"   ✅ تم العثور عليها: {test_results['found_items']} ({found_percentage:.1f}%)")
    print(f"   ❌ لم يتم العثور عليها: {len(test_results['missing_items'])}")
    
    print()
    
    # إحصائيات الأسعار
    if test_results["found_items"] > 0:
        price_accuracy = (test_results["price_matches"] / test_results["found_items"]) * 100
        print(f"💰 دقة الأسعار:")
        print(f"   ✅ أسعار صحيحة: {test_results['price_matches']} ({price_accuracy:.1f}%)")
        print(f"   ❌ أسعار خاطئة: {len(test_results['price_mismatches'])}")
    
    # تفاصيل الأسعار الخاطئة
    if test_results["price_mismatches"]:
        print()
        print("❌ تفاصيل الأسعار الخاطئة:")
        for mismatch in test_results["price_mismatches"][:10]:  # أول 10 فقط
            print(f"   🍕 {mismatch['item']}")
            print(f"      💰 متوقع: {mismatch['expected_price']} جنيه")
            print(f"      💸 فعلي: {mismatch['actual_price']} جنيه")
            print(f"      📊 نقاط دلالية: {mismatch['semantic_score']:.2f}")
            print()
    
    # المنتجات المفقودة
    if test_results["missing_items"]:
        print()
        print("🔍 منتجات لم يتم العثور عليها:")
        for missing in test_results["missing_items"][:10]:  # أول 10 فقط
            print(f"   🔍 {missing}")
    
    # حفظ التقرير
    with open("price_accuracy_report.json", "w", encoding="utf-8") as f:
        json.dump(test_results, f, indent=2, ensure_ascii=False)
    
    print()
    print("📄 تم حفظ التقرير التفصيلي في: price_accuracy_report.json")
    print("=" * 70)

async def test_specific_search_samples():
    """
    🎯 اختبار عينات محددة من البحث
    """
    print()
    print("🎯 اختبار عينات البحث...")
    print("=" * 50)
    
    # إعداد Azure Search
    search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
    search_key = os.getenv("AZURE_SEARCH_API_KEY")
    search_index = os.getenv("AZURE_SEARCH_INDEX")
    semantic_config = os.getenv("AZURE_SEARCH_SEMANTIC_CONFIGURATION")
    
    search_client = SearchClient(
        endpoint=search_endpoint,
        index_name=search_index,
        credential=AzureKeyCredential(search_key)
    )
    
    # عينات للاختبار
    test_samples = [
        "Crispy Chicken",
        "BBQ Chicken",
        "Double Burger",
        "Pizza Large",
        "Seafood",
        "أكل دجاج مقرمش",
        "برجر دبل",
        "بيتزا كبيرة"
    ]
    
    for sample in test_samples:
        print(f"🔍 البحث عن: '{sample}'")
        
        try:
            # البحث الدلالي
            results = search_client.search(
                search_text=sample,
                query_type="semantic",
                semantic_configuration_name=semantic_config,
                top=3,
                select="ID,Name,ingredients,Price",
                search_fields=["ingredients"]
            )
            
            found_any = False
            for i, result in enumerate(results, 1):
                found_any = True
                name = result.get("Name", "بدون اسم")
                price = result.get("Price", "غير محدد")
                semantic_score = result.get("@search.reranker_score", 0)
                
                print(f"   {i}. {name}")
                print(f"      💰 السعر: {price} جنيه")
                print(f"      📊 النقاط الدلالية: {semantic_score:.2f}")
            
            if not found_any:
                print("   ❌ لم يتم العثور على نتائج")
        
        except Exception as e:
            print(f"   ❌ خطأ: {str(e)}")
        
        print()

async def main():
    """
    🚀 تشغيل جميع الاختبارات
    """
    print("🚀 بدء الاختبار الشامل للبحث الدلالي والأسعار")
    print("=" * 70)
    
    await test_semantic_search_accuracy()
    await test_specific_search_samples()
    
    print("✅ اكتمل الاختبار الشامل!")

if __name__ == "__main__":
    asyncio.run(main())
