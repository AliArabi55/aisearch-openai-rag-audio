#!/usr/bin/env python3
"""
Test script to verify the price fix is working correctly by testing generate_model_input directly
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app', 'backend'))

def test_generate_model_input():
    """Test that the enhanced price validation is working"""
    
    try:
        from model_input_settings import generate_model_input
        print("✅ Successfully imported generate_model_input")
    except ImportError as e:
        print(f"❌ Failed to import: {e}")
        return

    print("🔍 Testing enhanced price validation...")
    print("=" * 60)
    
    # Test cases - simulate what Azure Search returns
    test_cases = [
        {
            "name": "Test with valid integer price",
            "docs": [
                {
                    'ID': '1',
                    'Name': 'بيتزا مارجريتا',
                    'ingredients': 'جبن موتزاريلا، طماطم، ريحان',
                    'Price': 220  # Integer price
                }
            ]
        },
        {
            "name": "Test with string price", 
            "docs": [
                {
                    'ID': '2',
                    'Name': 'برجر كلاسيك',
                    'ingredients': 'لحم بقري، خس، طماطم',
                    'Price': "145"  # String price
                }
            ]
        },
        {
            "name": "Test with None price",
            "docs": [
                {
                    'ID': '3', 
                    'Name': 'سلطة يونانية',
                    'ingredients': 'خس، طماطم، زيتون، جبن فيتا',
                    'Price': None  # None price
                }
            ]
        },
        {
            "name": "Test with 'غير محدد' price",
            "docs": [
                {
                    'ID': '4',
                    'Name': 'شاورما دجاج', 
                    'ingredients': 'دجاج، خضروات، صوص',
                    'Price': "غير محدد"  # Arabic "not specified"
                }
            ]
        },
        {
            "name": "Test with empty string price",
            "docs": [
                {
                    'ID': '5',
                    'Name': 'سمك مشوي',
                    'ingredients': 'سمك، ليمون، أعشاب',
                    'Price': ""  # Empty string
                }
            ]
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}: {test_case['name']}")
        print(f"   Input Price: {test_case['docs'][0]['Price']} (Type: {type(test_case['docs'][0]['Price']).__name__})")
        
        try:
            result = generate_model_input(test_case['docs'], "test query", "test search")
            print(f"   Result: {result}")
            
            # Check if "السعر غير متاح" appears
            if "السعر غير متاح" in result:
                print("   ❌ FAIL: Price showing as unavailable!")
            elif any(char.isdigit() for char in result) and ("ريال" in result or "220" in result or "145" in result):
                print("   ✅ PASS: Price properly displayed!")
            elif test_case['docs'][0]['Price'] in [None, "", "غير محدد"]:
                print("   ✅ PASS: Correctly handled invalid price!")
            else:
                print("   ⚠️ UNCLEAR: Result unclear")
                
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 Enhanced price validation test completed!")

if __name__ == "__main__":
    test_generate_model_input()
