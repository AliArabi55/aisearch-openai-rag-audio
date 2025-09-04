#!/usr/bin/env python3
import sys
sys.path.append('app/backend')

def fix_onion_rings_translation():
    """إصلاح ترجمة أونين رينجز بشكل مباشر"""
    
    from translation_utils import translate_arabic_to_english
    
    # اختبار الترجمة الحالية
    test_cases = [
        "أونين رينجز",
        "اونين رينجز",
        "حلقات البصل"
    ]
    
    print("🔧 اختبار الترجمة الحالية:")
    for text in test_cases:
        result = translate_arabic_to_english(text)
        print(f"   '{text}' → '{result}'")
    
    # إنشاء دالة ترجمة محسنة خاصة
    def enhanced_translate(text):
        """ترجمة محسنة لأونين رينجز"""
        
        # قاموس خاص لأونين رينجز
        onion_rings_dictionary = {
            "أونين رينجز": "Onion Rings",
            "اونين رينجز": "Onion Rings", 
            "أونيان رينجز": "Onion Rings",
            "اونيان رينجز": "Onion Rings",
            "حلقات البصل": "Onion Rings",
            "حلقات بصل": "Onion Rings",
            "رينجز": "Rings",
            "بصل مقلي": "Fried Onion"
        }
        
        text = text.strip()
        
        # فحص مباشر
        if text in onion_rings_dictionary:
            return onion_rings_dictionary[text]
        
        # ترجمة عامة
        return translate_arabic_to_english(text)
    
    print("\n🚀 اختبار الترجمة المحسنة:")
    for text in test_cases:
        result = enhanced_translate(text)
        print(f"   '{text}' → '{result}'")
    
    return enhanced_translate

if __name__ == "__main__":
    fix_onion_rings_translation()
