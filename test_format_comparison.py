#!/usr/bin/env python3
"""
اختبار التنسيق الحالي مقارنة بالمطلوب
"""
import sys
sys.path.append('app/backend')

from model_input_settings import generate_model_input

def test_current_vs_desired_format():
    """اختبار التنسيق الحالي مقابل المطلوب"""
    
    print("📊 مقارنة التنسيق الحالي مع المطلوب")
    print("=" * 60)
    
    # بيانات اختبار مطابقة للنتيجة المذكورة
    test_doc = {
        'ID': '109',
        'Name': 'Large Tuna Pizza',
        'ingredients': 'Sauce - Pepper - Olives - Mozzarella - Tuna',
        'Price': '185',
        'search_score': 4.27659,
        'semantic_score': 2.329744815826416
    }
    
    print("🔍 البيانات الأصلية من البحث:")
    print(f"🆔 ID: {test_doc['ID']}")
    print(f"📝 Name: {test_doc['Name']}")
    print(f"🥗 ingredients: {test_doc['ingredients']}")
    print(f"💰 Price: {test_doc['Price']}")
    print(f"📊 Search Score: {test_doc['search_score']}")
    print(f"🎯 Semantic Score: {test_doc['semantic_score']}")
    
    print(f"\n📤 ما يُرسل للنموذج حالياً:")
    current_output = generate_model_input([test_doc], "بيتزا تونة", "Tuna Pizza")
    print(current_output)
    
    print(f"\n🎯 ما هو مطلوب للنموذج:")
    desired_output = f"1- {test_doc['Name']}, {test_doc['Price']}"
    print(desired_output)
    
    print(f"\n💾 ما يُحفظ في الذاكرة المؤقتة (مطلوب):")
    cache_data = {
        'ID': test_doc['ID'],
        'Name': test_doc['Name'], 
        'ingredients': test_doc['ingredients'],
        'Price': test_doc['Price']
    }
    for key, value in cache_data.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    test_current_vs_desired_format()
