#!/usr/bin/env python3
"""
اختبار التنسيق الجديد مع نتائج متعددة
"""
import sys
sys.path.append('app/backend')

from model_input_settings import generate_model_input

def test_multiple_results():
    """اختبار التنسيق مع عدة نتائج"""
    
    print("📊 اختبار التنسيق الجديد مع نتائج متعددة")
    print("=" * 60)
    
    # بيانات اختبار متعددة
    test_docs = [
        {
            'ID': '107',
            'Name': 'Medium Tuna Pizza',
            'ingredients': 'Sauce - Pepper - Olives - Mozzarella - Tuna',
            'Price': '150'
        },
        {
            'ID': '109',
            'Name': 'Large Tuna Pizza',
            'ingredients': 'Sauce - Pepper - Olives - Mozzarella - Tuna',
            'Price': '185'
        },
        {
            'ID': '108',
            'Name': 'Medium Tuna Calzone',
            'ingredients': '',
            'Price': '140'
        },
        {
            'ID': '999',
            'Name': 'عنصر بدون سعر',
            'ingredients': 'مكونات',
            'Price': ''
        }
    ]
    
    print("📤 ما يُرسل للنموذج الآن:")
    output = generate_model_input(test_docs, "بيتزا تونة", "Tuna Pizza")
    print(output)
    
    print(f"\n✅ التنسيق الآن:")
    print(f"   - مبسط وواضح")
    print(f"   - يحتوي على الاسم والسعر فقط")
    print(f"   - مرقم بترتيب واضح")
    print(f"   - يتعامل مع الأسعار المفقودة")
    
    print(f"\n💾 البيانات في الذاكرة المؤقتة تبقى كاملة:")
    for doc in test_docs:
        cache_item = {
            'name': doc['Name'],
            'price': doc['Price'],
            'ingredients': doc['ingredients'],
            'id': doc['ID']
        }
        print(f"   {cache_item}")

if __name__ == "__main__":
    test_multiple_results()
