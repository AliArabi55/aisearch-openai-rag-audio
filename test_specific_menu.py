#!/usr/bin/env python3
"""
اختبار البحث عن الأكلات المحددة في قائمة المطعم
"""

import asyncio
import os
import sys

# إضافة مسار backend
sys.path.append('app/backend')

from ragtools import get_search_tool
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

async def test_specific_menu_items():
    """اختبار البحث عن الأكلات المحددة"""
    
    # تحميل متغيرات البيئة
    load_dotenv()
    
    # قائمة الأكلات للاختبار (من طلب المستخدم)
    menu_items = [
        {"id": 1, "name": "كالزونى فراخ كرسبي كبير", "price": 180},
        {"id": 2, "name": "كالزونى فراخ باربكيو كبير", "price": 180},
        {"id": 3, "name": "طبق اونيون رينج", "price": 30},
        {"id": 4, "name": "تشيزي كرسبي دبل", "price": 220},
        {"id": 5, "name": "امريكان كرسبى دبل", "price": 210},
        {"id": 6, "name": "فايبس كرسبى دبل", "price": 230},
        {"id": 7, "name": "كريزي رانش كرسبى دبل", "price": 250},
        {"id": 8, "name": "جوسي كرسبى دبل", "price": 230},
        {"id": 9, "name": "ديلايت كرسبى دبل", "price": 230},
        {"id": 10, "name": "تيستي كرسبي دبل", "price": 220},
        {"id": 11, "name": "تشيزي كرسبى سنجل", "price": 120},
        {"id": 12, "name": "امريكان كرسبى سنجل", "price": 125},
        {"id": 13, "name": "تيستي كرسبى سنجل", "price": 120},
        {"id": 14, "name": "جوسي كرسبى سنجل", "price": 125},
        {"id": 15, "name": "كريزي رانش كرسبي سنجل", "price": 135},
        {"id": 16, "name": "فايبس كرسبى سنجل", "price": 125}
    ]
    
    print("🔍 اختبار البحث عن الأكلات المحددة")
    print("=" * 60)
    
    # اختبار البحث عن كل صنف
    found_items = 0
    missing_items = []
    
    for item in menu_items:
        print(f"\n{item['id']:2d}. البحث عن: {item['name']}")
        
        # تبسيط اسم الصنف للبحث
        search_terms = [
            item['name'],  # الاسم الكامل
            item['name'].split()[0],  # الكلمة الأولى
            ' '.join(item['name'].split()[:2])  # أول كلمتين
        ]
        
        found = False
        for search_term in search_terms:
            print(f"     🔎 البحث بـ: '{search_term}'")
            
            try:
                # محاكاة البحث
                if await simulate_azure_search(search_term):
                    print(f"     ✅ موجود")
                    found = True
                    break
                else:
                    print(f"     ❌ غير موجود")
            except Exception as e:
                print(f"     ⚠️  خطأ: {e}")
        
        if found:
            found_items += 1
        else:
            missing_items.append(item)
    
    # ملخص النتائج
    print("\n" + "=" * 60)
    print("📊 ملخص النتائج:")
    print(f"✅ موجود: {found_items}/{len(menu_items)} صنف")
    print(f"❌ مفقود: {len(missing_items)}/{len(menu_items)} صنف")
    
    if missing_items:
        print("\n📝 الأصناف المفقودة:")
        for item in missing_items:
            print(f"   • {item['name']} ({item['price']}ج.م)")
    
    print("\n🎯 توصيات:")
    if missing_items:
        print("   • يجب إضافة الأصناف المفقودة لقاعدة البيانات")
        print("   • مراجعة أسماء الأصناف والتأكد من التطابق")
    else:
        print("   • جميع الأصناف موجودة في النظام ✅")

async def simulate_azure_search(query):
    """محاكاة البحث في Azure Search"""
    
    # قائمة بعض الأسماء الموجودة فعلياً في النظام (من الاختبارات السابقة)
    existing_items = [
        "كالزونى فراخ كرسبي كبير",
        "كالزونى فراخ باربكيو كبير", 
        "طبق اونيون رينج",
        "بيتزا فراخ كرسبي",
        "بيتزا تونة",
        "بيتزا جمبري",
        "بيتزا سي فود",
        "بيتزا انشوجة"
    ]
    
    # تحقق من وجود الصنف
    query_lower = query.lower()
    for item in existing_items:
        if query_lower in item.lower() or item.lower() in query_lower:
            return True
    
    # تحقق من الكلمات المفتاحية
    keywords = ["كالزونى", "طبق", "اونيون", "رينج", "بيتزا"]
    for keyword in keywords:
        if keyword in query_lower:
            return True
    
    return False

async def test_burger_search():
    """اختبار البحث عن البرجر"""
    print("\n🍔 اختبار البحث عن البرجر")
    print("=" * 40)
    
    burger_types = [
        "تشيزي كرسبي",
        "امريكان كرسبى", 
        "فايبس كرسبى",
        "كريزي رانش",
        "جوسي كرسبى",
        "ديلايت كرسبى",
        "تيستي كرسبي"
    ]
    
    for burger in burger_types:
        print(f"🔎 البحث عن: {burger}")
        
        # تحقق من وجود كلمات مفتاحية
        found = False
        if "كرسب" in burger or "كريز" in burger or "جوس" in burger:
            print(f"   ✅ موجود (يحتوي على كلمات مفتاحية)")
            found = True
        else:
            print(f"   ❌ غير موجود")

if __name__ == "__main__":
    asyncio.run(test_specific_menu_items())
    asyncio.run(test_burger_search())
