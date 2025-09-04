#!/usr/bin/env python3
import sys
sys.path.append('app/backend')

from translation_utils import translate_arabic_to_english, get_real_translation_dictionary

# اختبار القاموس
dictionary = get_real_translation_dictionary()
print("🔍 البحث في القاموس:")
print(f"   أونين رينجز: {'أونين رينجز' in dictionary}")
print(f"   اونين رينجز: {'اونين رينجز' in dictionary}")
print(f"   حلقات البصل: {'حلقات البصل' in dictionary}")

if 'أونين رينجز' in dictionary:
    print(f"   ترجمة أونين رينجز: {dictionary['أونين رينجز']}")

# اختبار الترجمة
test_phrases = [
    "أونين رينجز",
    "اونين رينجز", 
    "حلقات البصل",
    "بصل"
]

print("\n🔧 اختبار الترجمة:")
for phrase in test_phrases:
    result = translate_arabic_to_english(phrase)
    print(f"   '{phrase}' → '{result}'")
