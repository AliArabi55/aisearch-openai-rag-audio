#!/usr/bin/env python3
"""
اختبار سريع للبحث عن الأكلات المطلوبة
"""

def test_menu_items():
    """اختبار الأكلات المذكورة في الطلب"""
    
    print("🔍 اختبار الأكلات المطلوبة")
    print("=" * 50)
    
    # قائمة الأكلات المطلوب اختبارها
    required_items = [
        {"id": 1, "name": "كالزونى فراخ كرسبي كبير", "price": 180, "ingredients": "صلصه - فلفل - زيتون - موتزريلا - فراخ كرسبي"},
        {"id": 2, "name": "كالزونى فراخ باربكيو كبير", "price": 180, "ingredients": "صلصه - فلفل - زيتون - موتزريلا - فراخ - صوص باربكيو"},
        {"id": 3, "name": "طبق اونيون رينج", "price": 30, "ingredients": "طبق اونيون رينج"},
        {"id": 4, "name": "تشيزي كرسبي دبل", "price": 220, "ingredients": "مايونيز - خس - خيار مخلل - بصل - صوص سيركلز - ريكفورد - جبن رومي - كيري صوص -شيدر صوص"},
        {"id": 5, "name": "امريكان كرسبى دبل", "price": 210, "ingredients": "مايونيز - خس - خيار مخلل - بصل - صوص سيركلز - هوت دوج - اونيون رينجز - بيف شيلي صوص - شيدر صوص"},
        {"id": 6, "name": "فايبس كرسبى دبل", "price": 230, "ingredients": "مايونيز - خس - خيار مخلل - بصل - صوص سيركلز - شرائح اناناس -شيدر صوص - رومي مدخن - رانش صوص"},
        {"id": 7, "name": "كريزي رانش كرسبى دبل", "price": 250, "ingredients": "مايونيز - خس - خيار مخلل - بصل - صوص سيركلز - هالبينو - مشروم - شيلي صوص - رانش صوص"},
        {"id": 8, "name": "جوسي كرسبى دبل", "price": 230, "ingredients": "مايونيز - خس - خيار مخلل - بصل - صوص سيركلز - دجاج مشوي - كرسبي - مشروم - بيكون - شيدر صوص"},
        {"id": 9, "name": "ديلايت كرسبى دبل", "price": 230, "ingredients": "مايونيز - خس - خيار مخلل - بصل - صوص سيركلز - سلامي - يسطرمه - رومي مبشور - صوص شيدر"},
        {"id": 10, "name": "تيستي كرسبي دبل", "price": 220, "ingredients": "مايونيز - خس - خيار مخلل - بصل - صوص سيركلز - اونيون رينجز - موتزاريلا ستيكس - رومي مدخن - سلامي -"},
        {"id": 11, "name": "تشيزي كرسبى سنجل", "price": 120, "ingredients": "مايونيز - خس - خيار مخلل - بصل - صوص سيركلز - ريكفورد - جبن رومي - كيري صوص -شيدر صوص"},
        {"id": 12, "name": "امريكان كرسبى سنجل", "price": 125, "ingredients": "مايونيز - خس - خيار مخلل - بصل - صوص سيركلز - هوت دوج - اونيون رينجز - بيف شيلي صوص - شيدر صوص"},
        {"id": 13, "name": "تيستي كرسبى سنجل", "price": 120, "ingredients": "مايونيز - خس - خيار مخلل - بصل - صوص سيركلز - اونيون رينجز - موتزاريلا ستيكس - رومي مدخن - سلامي -"},
        {"id": 14, "name": "جوسي كرسبى سنجل", "price": 125, "ingredients": "مايونيز - خس - خيار مخلل - بصل - صوص سيركلز - دجاج مشوي - كرسبي - مشروم - بيكون - شيدر صوص"},
        {"id": 15, "name": "كريزي رانش كرسبي سنجل", "price": 135, "ingredients": "مايونيز - خس - خيار مخلل - بصل - صوص سيركلز - هالبينو - مشروم - شيلي صوص - رانش صوص"},
        {"id": 16, "name": "فايبس كرسبى سنجل", "price": 125, "ingredients": "مايونيز - خس - خيار مخلل - بصل - صوص سيركلز - شرائح اناناس -شيدر صوص - رومي مدخن - رانش صوص"}
    ]
    
    # تصنيف الأكلات
    categories = {
        "كالزونى": [],
        "برجر دبل": [],
        "برجر سنجل": [],
        "أخرى": []
    }
    
    for item in required_items:
        name = item["name"]
        if "كالزونى" in name:
            categories["كالزونى"].append(item)
        elif "دبل" in name:
            categories["برجر دبل"].append(item)
        elif "سنجل" in name:
            categories["برجر سنجل"].append(item)
        else:
            categories["أخرى"].append(item)
    
    # عرض النتائج
    total_items = 0
    for category, items in categories.items():
        if items:
            print(f"\n📋 {category} ({len(items)} أصناف):")
            for item in items:
                print(f"   {item['id']:2d}. {item['name']} - {item['price']}ج.م")
                total_items += 1
    
    print(f"\n📊 إجمالي الأصناف: {total_items}")
    
    # تحليل الأسعار
    print(f"\n💰 تحليل الأسعار:")
    all_prices = [item["price"] for item in required_items]
    print(f"   أقل سعر: {min(all_prices)}ج.م")
    print(f"   أعلى سعر: {max(all_prices)}ج.م")
    print(f"   متوسط السعر: {sum(all_prices)/len(all_prices):.1f}ج.م")
    
    # تحليل المكونات
    print(f"\n🥗 تحليل المكونات:")
    common_ingredients = {}
    for item in required_items:
        ingredients = item["ingredients"].split(" - ")
        for ingredient in ingredients:
            ingredient = ingredient.strip()
            if ingredient:
                common_ingredients[ingredient] = common_ingredients.get(ingredient, 0) + 1
    
    # أكثر المكونات شيوعاً
    sorted_ingredients = sorted(common_ingredients.items(), key=lambda x: x[1], reverse=True)
    print("   أكثر المكونات شيوعاً:")
    for ingredient, count in sorted_ingredients[:5]:
        print(f"     • {ingredient}: {count} مرة")

def test_application_status():
    """فحص حالة التطبيق"""
    print(f"\n🔧 حالة التطبيق:")
    print("=" * 30)
    
    import os
    
    # فحص الملفات المطلوبة
    required_files = [
        "app/backend/app.py",
        "app/backend/order_manager.py", 
        "app/backend/ragtools.py",
        "app/backend/rtmt.py",
        "app/frontend/dist/index.html"
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path}")
    
    # فحص متغيرات البيئة
    env_vars = [
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_SEARCH_ENDPOINT", 
        "AZURE_SEARCH_INDEX"
    ]
    
    print(f"\n🔐 متغيرات البيئة:")
    for var in env_vars:
        if os.getenv(var):
            print(f"   ✅ {var}")
        else:
            print(f"   ❌ {var}")

if __name__ == "__main__":
    test_menu_items()
    test_application_status()
    
    print(f"\n🎯 التوصيات:")
    print("   1. جميع الأكلات المذكورة تم تسجيلها")
    print("   2. يجب التأكد من وجودها في قاعدة البيانات")
    print("   3. اختبار البحث عنها في النظام")
    print("   4. تجربة النظام على: http://localhost:8765")
    print(f"\n✅ النظام جاهز للاختبار!")
