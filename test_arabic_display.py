#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار عرض النصوص العربية في التيرمينال
"""

import sys
import os

# إعداد الترميز للنصوص العربية
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

def format_arabic_rtl(text):
    """تنسيق النص العربي لاتجاه RTL الصحيح"""
    try:
        # علامات Unicode للتحكم في الاتجاه
        rtl_mark = '\u202E'  # Right-to-Left Override
        pop_mark = '\u202C'  # Pop Directional Formatting
        
        # تطبيق الاتجاه الصحيح للنص العربي
        formatted_text = f"{rtl_mark}{text}{pop_mark}"
        return formatted_text
    except:
        return text

def test_arabic_display():
    """اختبار عرض النصوص العربية"""
    
    print("🧪 اختبار عرض النصوص العربية في التيرمينال")
    print("=" * 60)
    
    # اختبار النصوص العربية المختلفة
    test_texts = [
        "🔍 البحث عن: 'بيتزا فراخ كبيرة' | إضافة للطلب: نعم",
        "📋 استخدام الحقول: ID=ID, Content=ingredients", 
        "✅ وجدت 5 نتائج",
        "❌ لم توجد نتائج للبحث!",
        "🍽️ [105] بيتزا فراخ كرسبي وسط",
        "المكونات: صلصه - فلفل - زيتون - موتزريلا - فراخ كرسبي",
        "السعر: 170 جنيه",
        "🛒 تم إضافة بيتزا فراخ كرسبي وسط للطلب",
        "📊 إجمالي الطلب: 2 أصناف - 255 جنيه",
        "🎉 تم تأكيد الطلب برقم: ORD_20250901_141500_1"
    ]
    
    print("\n📝 اختبار النصوص العربية بدون RTL:")
    print("-" * 40)
    
    for i, text in enumerate(test_texts, 1):
        try:
            print(f"{i:2d}. {text}")
        except UnicodeEncodeError as e:
            print(f"{i:2d}. ERROR: Cannot display Arabic text - {e}")
        except Exception as e:
            print(f"{i:2d}. UNEXPECTED ERROR: {e}")
    
    print("\n📝 اختبار النصوص العربية مع RTL:")
    print("-" * 40)
    
    for i, text in enumerate(test_texts, 1):
        try:
            formatted_text = format_arabic_rtl(text)
            print(f"{i:2d}. {formatted_text}")
        except UnicodeEncodeError as e:
            print(f"{i:2d}. ERROR: Cannot display Arabic text - {e}")
        except Exception as e:
            print(f"{i:2d}. UNEXPECTED ERROR: {e}")
    
    print("\n🔤 اختبار الأحرف العربية المختلفة:")
    print("-" * 40)
    
    # اختبار أحرف مختلفة
    arabic_chars = [
        "أ ب ت ث ج ح خ د ذ ر ز س ش ص ض",
        "ط ظ ع غ ف ق ك ل م ن ه و ي", 
        "ا إ آ ة ى ء",
        "فراخ - موتزريلا - صلصة - جنيه",
        "تشيزي كرسبي - امريكان - فايبس - كريزي رانش",
        "كالزونى - اونيون رينج - سي فود - انشوجة"
    ]
    
    for i, chars in enumerate(arabic_chars, 1):
        try:
            print(f"{i}. {chars}")
        except UnicodeEncodeError as e:
            print(f"{i}. ERROR: Cannot display Arabic characters - {e}")
    
    print("\n🎯 اختبار الأرقام العربية والإنجليزية:")
    print("-" * 40)
    
    numbers_test = [
        "الأرقام الإنجليزية: 1 2 3 4 5 6 7 8 9 0",
        "الأرقام العربية: ١ ٢ ٣ ٤ ٥ ٦ ٧ ٨ ٩ ٠",
        "الأسعار: 120ج.م - 180 جنيه - $15",
        "الهواتف: 01234567890 - +20 123 456 7890"
    ]
    
    for i, text in enumerate(numbers_test, 1):
        try:
            print(f"{i}. {text}")
        except UnicodeEncodeError as e:
            print(f"{i}. ERROR: Cannot display numbers - {e}")
    
    print("\n🎨 اختبار الرموز والإيموجي:")
    print("-" * 40)
    
    symbols_test = [
        "🍕 🍔 🥤 🍟 🌭 🥪 🌮 🌯 🥙",
        "✅ ❌ ⚠️ 🔍 📋 📊 🛒 🎉",
        "💰 💳 💸 💴 💵 💶 💷",
        "📱 📞 📧 📨 📩 📤 📥"
    ]
    
    for i, text in enumerate(symbols_test, 1):
        try:
            print(f"{i}. {text}")
        except UnicodeEncodeError as e:
            print(f"{i}. ERROR: Cannot display symbols - {e}")
    
    print("\n" + "=" * 60)
    print("🏁 انتهى اختبار النصوص العربية")
    
    # معلومات النظام
    print(f"\n📋 معلومات النظام:")
    print(f"Platform: {sys.platform}")
    print(f"Encoding: {sys.stdout.encoding}")
    print(f"Python Version: {sys.version}")
    
    try:
        import locale
        print(f"Locale: {locale.getlocale()}")
    except:
        print("Locale: غير متوفر")

if __name__ == "__main__":
    test_arabic_display()
