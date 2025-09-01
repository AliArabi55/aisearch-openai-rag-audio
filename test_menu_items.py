#!/usr/bin/env python3
"""
اختبار البحث عن الأكلات المذكورة في قائمة الطعام
"""

import asyncio
import sys
import os

# إضافة مسار backend للوصول للملفات
sys.path.append(os.path.join(os.path.dirname(__file__), 'app', 'backend'))

from ragtools import _search_tool

# قائمة الأكلات للاختبار
test_items = [
    {
        "id": 1,
        "name": "كالزونى فراخ كرسبي كبير",
        "price": 180,
        "ingredients": "صلصه - فلفل - زيتون - موتزريلا - فراخ كرسبي"
    },
    {
        "id": 2,
        "name": "كالزونى فراخ باربكيو كبير",
        "price": 180,
        "ingredients": "صلصه - فلفل - زيتون - موتزريلا - فراخ - صوص باربكيو"
    },
    {
        "id": 3,
        "name": "طبق اونيون رينج",
        "price": 30,
        "ingredients": "طبق اونيون رينج"
    },
    {
        "id": 4,
        "name": "تشيزي كرسبي دبل",
        "price": 220,
        "ingredients": "مايونيز - خس - خيار مخلل - بصل - صوص سيركلز - ريكفورد - جبن رومي - كيري صوص -شيدر صوص"
    },
    {
        "id": 5,
        "name": "امريكان كرسبى دبل",
        "price": 210,
        "ingredients": "مايونيز - خس - خيار مخلل - بصل - صوص سيركلز - هوت دوج - اونيون رينجز - بيف شيلي صوص - شيدر صوص"
    }
]

async def test_search_for_items():
    """اختبار البحث عن الأكلات"""
    print("=== اختبار البحث عن الأكلات ===")
    
    # اختبار البحث عن كل صنف
    search_queries = [
        "كالزونى فراخ كرسبي",
        "كالزونى باربكيو", 
        "اونيون رينج",
        "تشيزي كرسبي",
        "امريكان كرسبى",
        "فايبس كرسبى",
        "كريزي رانش",
        "جوسي كرسبى",
        "ديلايت كرسبى",
        "تيستي كرسبي"
    ]
    
    print(f"سيتم اختبار {len(search_queries)} استعلام بحث")
    print("-" * 50)
    
    for i, query in enumerate(search_queries, 1):
        print(f"\n{i}. البحث عن: '{query}'")
        try:
            # محاكاة البحث (سيتم استبدالها بالبحث الفعلي)
            results = await simulate_search(query)
            
            if results:
                print(f"   ✅ تم العثور على {len(results)} نتيجة")
                for j, result in enumerate(results[:3], 1):  # عرض أول 3 نتائج فقط
                    print(f"      {j}. {result['name']} - {result['price']}ج.م")
            else:
                print("   ❌ لم يتم العثور على نتائج")
                
        except Exception as e:
            print(f"   ❌ خطأ في البحث: {e}")
    
    print("\n" + "=" * 50)

async def simulate_search(query):
    """محاكاة البحث في البيانات الوهمية"""
    results = []
    query_lower = query.lower()
    
    for item in test_items:
        if query_lower in item['name'].lower() or query_lower in item['ingredients'].lower():
            results.append(item)
    
    return results

async def test_order_management():
    """اختبار إدارة الطلبات"""
    print("\n=== اختبار إدارة الطلبات ===")
    
    try:
        # استيراد OrderManager
        from order_manager import OrderManager
        
        # إنشاء instance جديد
        order_manager = OrderManager()
        
        # إضافة بعض الأصناف للطلب
        print("1. إضافة كالزونى فراخ كرسبي كبير...")
        order_manager.add_item("كالزونى فراخ كرسبي كبير", 180, "صلصه - فلفل - زيتون - موتزريلا - فراخ كرسبي")
        
        print("2. إضافة طبق اونيون رينج...")
        order_manager.add_item("طبق اونيون رينج", 30, "طبق اونيون رينج")
        
        print("3. إضافة تشيزي كرسبي دبل...")
        order_manager.add_item("تشيزي كرسبي دبل", 220, "مايونيز - خس - خيار مخلل - بصل - صوص سيركلز - ريكفورد - جبن رومي - كيري صوص -شيدر صوص")
        
        # عرض ملخص الطلب
        print("\n--- ملخص الطلب ---")
        summary = order_manager.get_order_summary()
        print(f"إجمالي الأصناف: {summary['total_items']}")
        print(f"إجمالي السعر: {summary['total_price']}ج.م")
        
        # عرض الطلب في شكل جدول HTML
        print("\n--- عرض الطلب ---")
        table_html = order_manager.get_order_table()
        print("✅ تم إنشاء جدول HTML للطلب بنجاح")
        
        # تأكيد الطلب
        print("\n4. تأكيد الطلب...")
        confirmation = order_manager.confirm_order()
        print(f"✅ تم تأكيد الطلب برقم: {confirmation['order_id']}")
        
        print("✅ جميع وظائف إدارة الطلبات تعمل بنجاح!")
        
    except Exception as e:
        print(f"❌ خطأ في اختبار إدارة الطلبات: {e}")

if __name__ == "__main__":
    print("🔍 اختبار نظام المطعم")
    print("=" * 50)
    
    # تشغيل الاختبارات
    asyncio.run(test_search_for_items())
    asyncio.run(test_order_management())
    
    print("\n🎉 انتهى الاختبار!")
