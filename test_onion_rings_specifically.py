#!/usr/bin/env python3
import asyncio
import json
import sys
sys.path.append('app/backend')

from ragtools import get_search_tool
from translation_utils import translate_to_english

async def test_onion_rings_variations():
    """اختبار شامل لجميع تغيرات كلمة أونين رينجز"""
    
    print("🧅 اختبار شامل لمشكلة أونين رينجز")
    print("=" * 60)
    
    # إعداد أداة البحث
    try:
        search_tool = get_search_tool()
        print("✅ تم إعداد أداة البحث بنجاح")
    except Exception as e:
        print(f"❌ خطأ في إعداد أداة البحث: {e}")
        return
    
    # قائمة بجميع الطرق المختلفة للبحث عن أونين رينجز
    search_variations = [
        "أونين رينجز",
        "اونين رينجز", 
        "أونيان رينجز",
        "اونيان رينجز",
        "حلقات البصل",
        "onion rings",
        "Onion Rings",
        "ONION RINGS",
        "onion ring",
        "Onion Ring",
        "rings",
        "بصل مقلي",
        "بصل حلقات"
    ]
    
    print(f"🔍 سأختبر {len(search_variations)} طريقة بحث مختلفة:")
    for i, term in enumerate(search_variations, 1):
        print(f"   {i}. {term}")
    
    print("\n" + "=" * 60)
    
    results_summary = []
    
    for i, search_term in enumerate(search_variations, 1):
        print(f"\n🧪 اختبار {i}: البحث عن '{search_term}'")
        print("-" * 40)
        
        try:
            # ترجمة النص
            translated_term = translate_to_english(search_term)
            print(f"   📝 الترجمة: '{search_term}' → '{translated_term}'")
            
            # تنفيذ البحث
            search_params = {"query": search_term}
            result = await search_tool.run_impl(search_params)
            
            if result and hasattr(result, 'content'):
                content = result.content
                print(f"   ✅ نتيجة البحث: {content[:100]}...")
                
                # تحليل النتيجة
                if "onion" in content.lower() or "بصل" in content:
                    if "price" in content.lower() or "سعر" in content or "جنيه" in content or "LE" in content:
                        price_match = True
                        # استخراج السعر
                        import re
                        price_pattern = r'(\d+(?:\.\d+)?)\s*(?:LE|جنيه|pounds?)'
                        prices = re.findall(price_pattern, content)
                        extracted_price = prices[0] if prices else "غير محدد"
                        print(f"   💰 السعر المستخرج: {extracted_price}")
                    else:
                        price_match = False
                        extracted_price = "لا يوجد سعر"
                        print(f"   ⚠️  لا يوجد سعر في النتيجة")
                    
                    results_summary.append({
                        'search_term': search_term,
                        'translated_term': translated_term,
                        'found': True,
                        'has_price': price_match,
                        'price': extracted_price,
                        'content_preview': content[:200]
                    })
                else:
                    print(f"   ❌ لم يتم العثور على أونين رينجز")
                    results_summary.append({
                        'search_term': search_term,
                        'translated_term': translated_term,
                        'found': False,
                        'has_price': False,
                        'price': None,
                        'content_preview': content[:100] if content else "لا يوجد محتوى"
                    })
            else:
                print(f"   ❌ لا توجد نتائج للبحث")
                results_summary.append({
                    'search_term': search_term,
                    'translated_term': translated_term,
                    'found': False,
                    'has_price': False,
                    'price': None,
                    'content_preview': "لا توجد نتائج"
                })
                
        except Exception as e:
            print(f"   💥 خطأ في البحث: {e}")
            results_summary.append({
                'search_term': search_term,
                'translated_term': translated_term,
                'found': False,
                'has_price': False,
                'price': None,
                'error': str(e)
            })
        
        # انتظار قصير بين الاختبارات
        await asyncio.sleep(0.5)
    
    print("\n" + "=" * 60)
    print("📊 ملخص شامل للنتائج:")
    print("=" * 60)
    
    found_count = sum(1 for r in results_summary if r['found'])
    price_count = sum(1 for r in results_summary if r.get('has_price', False))
    
    print(f"📈 إحصائيات عامة:")
    print(f"   🔍 إجمالي عمليات البحث: {len(results_summary)}")
    print(f"   ✅ عدد النتائج الموجودة: {found_count}")
    print(f"   💰 عدد النتائج مع السعر: {price_count}")
    print(f"   ❌ عدد النتائج غير الموجودة: {len(results_summary) - found_count}")
    
    print(f"\n📋 تفاصيل كل بحث:")
    for i, result in enumerate(results_summary, 1):
        status = "✅ موجود" if result['found'] else "❌ غير موجود"
        price_status = f"💰 {result['price']}" if result.get('has_price') else "💸 بدون سعر"
        print(f"   {i:2d}. '{result['search_term']}' → {status} {price_status}")
    
    # تحليل أنماط المشاكل
    print(f"\n🔍 تحليل المشاكل:")
    
    # البحث عن تباين في النتائج
    found_items = [r for r in results_summary if r['found']]
    if found_items:
        prices = [r['price'] for r in found_items if r.get('has_price')]
        unique_prices = set(prices)
        
        if len(unique_prices) > 1:
            print(f"   ⚠️  تباين في الأسعار المرجعة: {unique_prices}")
        elif len(unique_prices) == 1:
            print(f"   ✅ سعر ثابت في جميع النتائج: {list(unique_prices)[0]}")
        else:
            print(f"   ❌ لا توجد أسعار في أي نتيجة")
    
    # حفظ النتائج التفصيلية
    with open('onion_rings_test_results.json', 'w', encoding='utf-8') as f:
        json.dump(results_summary, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 تم حفظ النتائج التفصيلية في: onion_rings_test_results.json")
    
    # توصيات لحل المشكلة
    print(f"\n💡 توصيات لحل المشكلة:")
    if found_count == 0:
        print("   🔧 المشكلة: لا يتم العثور على أونين رينجز مطلقاً")
        print("   💬 الحل المقترح: تحقق من بيانات الفهرس والترجمة")
    elif found_count < len(results_summary) / 2:
        print("   🔧 المشكلة: نتائج غير متسقة - أحياناً يجد وأحياناً لا يجد")
        print("   💬 الحل المقترح: مراجعة آلية الترجمة والبحث الدلالي")
    elif len(set(r['price'] for r in found_items if r.get('has_price'))) > 1:
        print("   🔧 المشكلة: أسعار متضاربة لنفس المنتج")
        print("   💬 الحل المقترح: مراجعة بيانات المنتج في الفهرس")
    else:
        print("   ✅ النتائج متسقة نسبياً")

if __name__ == "__main__":
    asyncio.run(test_onion_rings_variations())
