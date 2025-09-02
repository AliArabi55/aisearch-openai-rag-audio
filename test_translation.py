# اختبار الترجمة التلقائية
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app', 'backend'))

from ragtools import translate_to_english

# اختبارات الترجمة
test_cases = [
    "بيتزا فراخ كبير",
    "كالزونى سجق وسط", 
    "برجر أمريكان كريسبي دبل",
    "مشاكل لحوم كبير",
    "جمبري وسط",
    "رانش صوص"
]

print("🧪 اختبار الترجمة التلقائية:")
print("=" * 50)

for test in test_cases:
    result = translate_to_english(test)
    print(f"'{test}' → '{result}'")

print("=" * 50)
print("✅ تم الانتهاء من الاختبار")
