#!/usr/bin/env python3
"""
إصلاح خاص لترجمة أونين رينجز
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app', 'backend'))

from translation_utils import translate_arabic_to_english_real

def test_and_fix_onion_rings():
    """اختبار وإصلاح ترجمة أونين رينجز"""
    
    test_inputs = [
        "أونين رينجز",
        "اونين رينجز", 
        "أونيان رينجز",
        "اونيان رينجز",
        "حلقات البصل",
        "حلقات بصل",
        "onion rings"
    ]
    
    print("🔍 اختبار ترجمة أونين رينجز...")
    
    for test_input in test_inputs:
        result = translate_arabic_to_english_real(test_input)
        success = "Onion" in result or "onion" in result.lower()
        status = "✅" if success else "❌"
        print(f"   '{test_input}' → '{result}' {status}")
    
    # Direct test with manual mapping
    print("\n🛠️ اختبار الترجمة المباشرة...")
    
    # Manual translation for onion rings
    manual_mapping = {
        "أونين رينجز": "Onion Rings",
        "اونين رينجز": "Onion Rings",
        "أونيان رينجز": "Onion Rings", 
        "اونيان رينجز": "Onion Rings"
    }
    
    for arabic, expected in manual_mapping.items():
        print(f"   قاموس مباشر: '{arabic}' → '{expected}'")

if __name__ == "__main__":
    test_and_fix_onion_rings()
