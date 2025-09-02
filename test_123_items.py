#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار شامل للبحث الدلالي على قاعدة البيانات الجديدة - 123 عنصر
"""

import asyncio
from azure.search.documents.aio import SearchClient
from azure.core.credentials import AzureKeyCredential
import sys
import os
from dotenv import load_dotenv

# إضافة المجلد الحالي للمسار
sys.path.append(os.path.dirname(__file__))

# تحميل متغيرات البيئة
load_dotenv('app/backend/.env')

# استيراد أدوات الترجمة
from translation_utils import translate_and_extract_for_search

async def test_new_database_123_items():
    """اختبار شامل للبحث الدلالي على قاعدة البيانات الجديدة (123 عنصر)"""
    
    # Azure Search configuration من متغيرات البيئة
    endpoint = os.environ.get("AZURE_SEARCH_ENDPOINT")
    index_name = os.environ.get("AZURE_SEARCH_INDEX")
    api_key = os.environ.get("AZURE_SEARCH_API_KEY")
    semantic_config = os.environ.get("AZURE_SEARCH_SEMANTIC_CONFIGURATION")
    
    credential = AzureKeyCredential(api_key)
    search_client = SearchClient(endpoint=endpoint, index_name=index_name, credential=credential)
    
    print("🎯 اختبار شامل للبحث الدلالي على قاعدة البيانات الجديدة (123 عنصر)")
    print("=" * 80)
    print(f"📋 إعدادات البحث:")
    print(f"   🌐 Endpoint: {endpoint}")
    print(f"   📊 Index: {index_name}")
    print(f"   🧠 Semantic Config: {semantic_config}")
    print()
    
    # استعلامات شاملة للعناصر الموجودة في القائمة الجديدة
    test_queries = [
        # 1. بيتزا فراخ (العناصر 91, 95, 98, 103, 104, 105)
        "اريد بيتزا فراخ كبير",
        "بيتزا فراخ وسط",
        "بيتزا فراخ كرسبي",
        "بيتزا فراخ رانش",
        "بيتزا فراخ باربكيو",
        
        # 2. كالزونى فراخ (العناصر 1, 2, 92, 93, 94, 96, 97, 99, 102, 106)
        "كالزونى فراخ كبير",
        "كالزونى فراخ كرسبي",
        "كالزونى فراخ باربكيو",
        "كالزونى فراخ رانش",
        
        # 3. برجر وساندوتش (العناصر 4-50)
        "تشيزي كرسبي دبل",
        "امريكان كرسبى دبل", 
        "تيستي كرسبي",
        "برجر بيف دبل",
        "بيتزا برجر",
        
        # 4. هوت دوج (العناصر 24, 27, 31, 34)
        "بيتزا هوت دوج",
        "كالزونى هوت دوج",
        "هوت دوج كبير",
        "هوت دوج وسط",
        
        # 5. سلامى (العناصر 57, 60, 61, 62)
        "بيتزا سلامى",
        "كالزونى سلامى",
        "سلامى كبير",
        "سلامى وسط",
        
        # 6. سجق (العناصر 43, 46, 51, 52)
        "بيتزا سجق",
        "كالزونى سجق",
        "سجق كبير",
        
        # 7. مأكولات بحرية (العناصر 107-123)
        "بيتزا تونه",
        "بيتزا جمبري",
        "بيتزا سي فود",
        "بيتزا كابوريا",
        "بيتزا انشوجه",
        
        # 8. اختبارات عامة
        "حاجة كبيرة بالفراخ",
        "ساندوتش دبل جبن",
        "بيتزا مشكل لحوم",
        "كرسبي دبل",
        "حاجة بالباربكيو"
    ]
    
    print(f"🔍 عدد الاستعلامات للاختبار: {len(test_queries)}")
    print("-" * 60)
    
    successful_searches = 0
    total_searches = len(test_queries)
    high_quality_results = 0  # نتائج بنقاط عالية (> 2.5)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 الاختبار {i}/{total_searches}: '{query}'")
        
        # ترجمة الاستعلام
        translated_query, mode = translate_and_extract_for_search(query)
        print(f"🌍 الترجمة ({mode}): '{translated_query}'")
        
        try:
            # البحث الدلالي
            search_results = await search_client.search(
                search_text=translated_query,
                query_type="semantic",  # البحث الدلالي فقط
                semantic_configuration_name=semantic_config,
                top=3,  # أفضل 3 نتائج
                select=["ID", "Name", "Price", "ingredients"]
            )
            
            results_found = 0
            best_score = 0
            
            async for result in search_results:
                if results_found == 0:
                    print("🧠 النتائج من البحث الدلالي:")
                    
                results_found += 1
                name = result.get('Name', 'غير محدد')
                price = result.get('Price', 'غير محدد')
                id_val = result.get('ID', 'غير محدد')
                
                # درجة الصلة الدلالية
                reranker_score = result.get('@search.reranker_score', 0)
                if results_found == 1:  # أفضل نتيجة
                    best_score = reranker_score
                
                print(f"   🎯 {results_found}. ID: {id_val} | {name} - {price} جنيه")
                print(f"      🔢 نقاط الدلالة: {reranker_score:.3f}")
            
            if results_found > 0:
                successful_searches += 1
                if best_score > 2.5:
                    high_quality_results += 1
                    quality_icon = "🌟"
                else:
                    quality_icon = "✅"
                print(f"   {quality_icon} وجد {results_found} نتائج")
            else:
                print("   ❌ لا توجد نتائج")
                
        except Exception as e:
            print(f"   ❌ خطأ في البحث: {e}")
        
        print("-" * 50)
    
    # إحصائيات نهائية
    success_rate = (successful_searches / total_searches) * 100
    quality_rate = (high_quality_results / total_searches) * 100
    
    print(f"\n📊 الإحصائيات النهائية:")
    print("=" * 60)
    print(f"   🎯 إجمالي الاستعلامات: {total_searches}")
    print(f"   ✅ الاستعلامات الناجحة: {successful_searches}")
    print(f"   🌟 النتائج عالية الجودة (> 2.5): {high_quality_results}")
    print(f"   ❌ الاستعلامات الفاشلة: {total_searches - successful_searches}")
    print(f"   📈 معدل النجاح: {success_rate:.1f}%")
    print(f"   ⭐ معدل الجودة العالية: {quality_rate:.1f}%")
    
    # تقييم شامل
    print(f"\n🎯 التقييم الشامل:")
    print("-" * 30)
    
    if success_rate >= 90 and quality_rate >= 70:
        print("   🏆 ممتاز! النظام يعمل بأعلى كفاءة")
        print("   💯 جودة النتائج عالية جداً")
    elif success_rate >= 80 and quality_rate >= 60:
        print("   🎉 جيد جداً! النظام يعمل بكفاءة عالية")
        print("   ⭐ جودة النتائج جيدة")
    elif success_rate >= 70:
        print("   👍 جيد! النظام يعمل بشكل مقبول")
        print("   ✅ النتائج مناسبة")
    else:
        print("   ⚠️ يحتاج تحسين")
    
    # معلومات قاعدة البيانات
    print(f"\n📋 معلومات قاعدة البيانات:")
    print("-" * 30)
    print("   📊 العناصر: 123 عنصر")
    print("   🍕 البيتزا: متنوعة (فراخ، سلامى، سجق، مأكولات بحرية)")
    print("   🥟 الكالزونى: جميع الأنواع")
    print("   🍔 البرجر والساندوتش: خيارات متعددة")
    print("   🌊 المأكولات البحرية: تونة، جمبري، سي فود")
    
    await search_client.close()
    print("\n✅ انتهى الاختبار الشامل")

if __name__ == "__main__":
    asyncio.run(test_new_database_123_items())
