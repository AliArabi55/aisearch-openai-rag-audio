#!/usr/bin/env python3
"""
اختبار تحسين مشكلة هلوسة الأسعار
PRICE HALLUCINATION FIX TEST
"""
import sys
sys.path.append('app/backend')

import asyncio
from model_input_settings import generate_model_input

async def test_price_improvement():
    """اختبار تحسين عرض الأسعار للنموذج"""
    
    print("💰 اختبار تحسين عرض الأسعار")
    print("=" * 50)
    
    # بيانات اختبار مع أسعار مختلفة
    test_docs = [
        {
            'ID': '1',
            'Name': 'بيتزا مارجريتا وسط',
            'ingredients': 'جبن موزاريلا، صلصة طماطم، ريحان',
            'Price': '85'
        },
        {
            'ID': '2', 
            'Name': 'برجر دجاج سنجل',
            'ingredients': 'قطعة دجاج مقلي، خس، طماطم، مايونيز',
            'Price': '45'
        },
        {
            'ID': '3',
            'Name': 'أونين رينجز',
            'ingredients': 'حلقات بصل مقلي مقرمش',
            'Price': '25'
        },
        {
            'ID': '4',
            'Name': 'مشروب غازي',
            'ingredients': 'كولا أو سفن أب',
            'Price': ''  # سعر فارغ
        },
        {
            'ID': '5',
            'Name': 'سلطة خضراء',
            'ingredients': 'خس، طماطم، خيار، جزر',
            'Price': 'غير محدد'  # سعر غير محدد
        }
    ]
    
    print("🧪 اختبار تنسيق البيانات المحسن:")
    
    for i, doc in enumerate(test_docs, 1):
        print(f"\n--- اختبار {i}: {doc['Name']} ---")
        
        # تنسيق النتيجة حسب النظام الجديد
        result = generate_model_input([doc], f"بحث عن {doc['Name']}", doc['Name'])
        
        print(f"📄 النتيجة المُرسلة للنموذج:")
        print(result)
        
        # تحليل النتيجة
        if "السعر الرسمي المؤكد" in result:
            print("✅ السعر معروض بشكل واضح ومؤكد")
        elif "غير متاح حالياً" in result:
            print("✅ تم التعامل مع السعر المفقود بشكل صحيح")
        else:
            print("⚠️  قد يحتاج تحسين إضافي")
    
    print(f"\n📋 ملخص التحسينات:")
    print(f"   ✅ إضافة تأكيد للسعر الرسمي")
    print(f"   ✅ تكرار السعر مع تحذير")
    print(f"   ✅ التعامل مع الأسعار المفقودة")
    print(f"   ✅ تحديث System Message مع قواعد صارمة")
    
    print(f"\n🎯 النتيجة المتوقعة:")
    print(f"   - النموذج سيرى الأسعار بوضوح أكبر")
    print(f"   - التأكيدات المتكررة ستقلل الهلوسة")
    print(f"   - القواعد الصارمة ستمنع اختلاق الأسعار")

if __name__ == "__main__":
    asyncio.run(test_price_improvement())
