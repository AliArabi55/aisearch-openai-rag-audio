#!/usr/bin/env python3
"""
Test script to verify the price fix is working correctly
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app', 'backend'))

from ragtools import search_and_format_for_model

def test_price_availability():
    """Test that prices are now available after our fix"""
    print("🔍 Testing price availability after fix...")
    print("=" * 50)
    
    # Test with common food items
    test_queries = [
        "بيتزا",  # Pizza
        "برجر",   # Burger  
        "شاورما", # Shawarma
        "سلطة",   # Salad
        "chicken" # English test
    ]
    
    for query in test_queries:
        print(f"\n🍽️ Testing query: '{query}'")
        try:
            result = search_and_format_for_model(query)
            print(f"📋 Result: {result}")
            
            # Check if "السعر غير متاح" appears in result
            if "السعر غير متاح" in result:
                print("❌ ERROR: Price still not available!")
            elif "ريال" in result or any(char.isdigit() for char in result):
                print("✅ SUCCESS: Price found in result!")
            else:
                print("⚠️ WARNING: Unclear if price is available")
                
        except Exception as e:
            print(f"❌ Error testing query '{query}': {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Price availability test completed!")

if __name__ == "__main__":
    test_price_availability()
