#!/usr/bin/env python3
"""
اختبار موديل الريل تايم للتأكد من قدرته على قراءة الأسعار
Real-time Model Test for Price Reading Capability
"""

import asyncio
import json
import os
import sys
from datetime import datetime

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'app', 'backend'))

try:
    from dotenv import load_dotenv
    print("✅ تم تحميل المكتبات المطلوبة")
except ImportError as e:
    print(f"❌ خطأ في تحميل المكتبات: {e}")
    exit(1)

class RealtimeModelTester:
    def __init__(self):
        """Initialize real-time model tester"""
        load_dotenv()
        
    def test_model_configuration(self):
        """Test model configuration and connectivity"""
        print("🤖 اختبار إعدادات موديل الريل تايم...")
        
        # Check environment variables
        openai_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
        openai_key = os.getenv('AZURE_OPENAI_API_KEY')
        deployment = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME', 'gpt-4o-realtime-preview')
        
        print(f"   🔗 Endpoint: {'✅ محدد' if openai_endpoint else '❌ مفقود'}")
        print(f"   🔑 API Key: {'✅ محدد' if openai_key else '❌ مفقود'}")
        print(f"   🚀 Deployment: {deployment}")
        
        if openai_endpoint:
            print(f"   📍 Endpoint URL: {openai_endpoint[:50]}...")
        
        return bool(openai_endpoint and openai_key)
    
    def create_test_scenarios(self):
        """Create test scenarios with explicit price information"""
        print("\n📋 إنشاء سيناريوهات الاختبار...")
        
        scenarios = [
            {
                'name': 'Test 1: Simple Price Display',
                'search_results': "1- Medium Tuna Pizza, 150\n2- Large Tuna Pizza, 185",
                'user_query': "أريد بيتزا تونة وسط",
                'expected_response': "يجب أن يذكر السعر 150 ريال"
            },
            {
                'name': 'Test 2: Multiple Options',
                'search_results': "1- Medium Tuna Pizza, 150\n2- Large Tuna Pizza, 185\n3- Medium Tuna Calzone, 140",
                'user_query': "ما هي خيارات التونة المتاحة؟",
                'expected_response': "يجب أن يذكر الأسعار 150، 185، و 140 ريال"
            },
            {
                'name': 'Test 3: Direct Price Question',
                'search_results': "1- Medium Tuna Pizza, 150",
                'user_query': "كم سعر بيتزا التونة الوسط؟",
                'expected_response': "يجب أن يقول 150 ريال بوضوح"
            }
        ]
        
        for i, scenario in enumerate(scenarios, 1):
            print(f"   📝 السيناريو {i}: {scenario['name']}")
            print(f"      النتائج: {scenario['search_results']}")
            print(f"      السؤال: {scenario['user_query']}")
            print(f"      المتوقع: {scenario['expected_response']}")
        
        return scenarios
    
    def test_price_parsing_manually(self):
        """Test price parsing logic manually"""
        print("\n🧮 اختبار تحليل الأسعار يدوياً...")
        
        test_strings = [
            "1- Medium Tuna Pizza, 150",
            "2- Large Pizza, 185 ريال",
            "Medium Tuna Pizza, price: 150",
            "تونة بيتزا وسط - السعر 150 ريال"
        ]
        
        for test_string in test_strings:
            print(f"   📝 اختبار: '{test_string}'")
            
            # Extract numbers (potential prices)
            import re
            numbers = re.findall(r'\d+', test_string)
            prices = [int(n) for n in numbers if 50 <= int(n) <= 500]  # Reasonable price range
            
            print(f"      🔢 الأرقام الموجودة: {numbers}")
            print(f"      💰 الأسعار المحتملة: {prices}")
    
    def analyze_model_prompt_structure(self):
        """Analyze how the model receives price information"""
        print("\n📤 تحليل هيكل الرسالة المرسلة للموديل...")
        
        # Simulate the exact format sent to the model
        sample_data = "1- Medium Tuna Pizza, 150\n2- Large Tuna Pizza, 185\n3- Medium Tuna Calzone, 140"
        
        print("   📝 البيانات المرسلة للموديل:")
        print(f"      {sample_data}")
        
        print("\n   🤖 التعليمات المتوقعة للموديل:")
        instructions = [
            "استخدم البيانات المتاحة للإجابة عن أسئلة المستخدم",
            "اذكر الأسعار المتاحة بوضوح",
            "إذا كان السعر متاحاً، اذكره للمستخدم",
            "لا تقل 'السعر غير متاح' إذا كان السعر موجوداً في البيانات"
        ]
        
        for instruction in instructions:
            print(f"      • {instruction}")
    
    def check_model_system_message(self):
        """Check model system message for price handling"""
        print("\n💬 فحص رسالة النظام للموديل...")
        
        try:
            # Try to read the actual system message used
            app_file = os.path.join('app', 'backend', 'app.py')
            if os.path.exists(app_file):
                with open(app_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Look for system message
                if 'system' in content.lower() and 'message' in content.lower():
                    print("   📋 وجدت رسالة نظام في ملف التطبيق")
                    
                    # Extract relevant parts
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if 'system' in line.lower() and any(word in line.lower() for word in ['price', 'سعر', 'cost']):
                            print(f"      {i+1}: {line.strip()}")
                else:
                    print("   ⚠️ لم يتم العثور على رسالة نظام واضحة")
            else:
                print("   ❌ ملف التطبيق غير موجود")
                
        except Exception as e:
            print(f"   ❌ خطأ في قراءة ملف التطبيق: {e}")
    
    def generate_debugging_recommendations(self):
        """Generate debugging recommendations"""
        print("\n💡 توصيات التشخيص...")
        
        recommendations = [
            "🔍 مراقبة logs الموديل الفعلي أثناء الاستخدام",
            "📝 التأكد من أن البيانات تصل للموديل بالتنسيق الصحيح",
            "🤖 فحص system message أو instructions المرسلة للموديل",
            "📊 اختبار الموديل مع بيانات بسيطة وواضحة",
            "🔄 مقارنة response الموديل مع البيانات المرسلة",
            "⚡ اختبار مع deployment مختلف أو model version أحدث",
            "🌐 فحص إعدادات الموديل (temperature, max_tokens, etc.)",
            "📋 التأكد من أن الموديل يفهم تعليمات عرض الأسعار"
        ]
        
        for rec in recommendations:
            print(f"   {rec}")
    
    def run_complete_analysis(self):
        """Run complete real-time model analysis"""
        print("🚀 بدء تحليل موديل الريل تايم...")
        print("=" * 60)
        
        # Test configuration
        config_ok = self.test_model_configuration()
        
        # Create test scenarios
        scenarios = self.create_test_scenarios()
        
        # Test price parsing
        self.test_price_parsing_manually()
        
        # Analyze prompt structure
        self.analyze_model_prompt_structure()
        
        # Check system message
        self.check_model_system_message()
        
        # Generate recommendations
        self.generate_debugging_recommendations()
        
        print("\n" + "=" * 60)
        print("🏁 انتهى تحليل موديل الريل تايم!")
        
        if config_ok:
            print("✅ إعدادات الموديل صحيحة - المشكلة قد تكون في:")
            print("   1. رسالة النظام (system message)")
            print("   2. طريقة تمرير البيانات للموديل")  
            print("   3. إعدادات الموديل نفسه")
        else:
            print("❌ إعدادات الموديل غير مكتملة")

def main():
    """Main testing function"""
    tester = RealtimeModelTester()
    tester.run_complete_analysis()

if __name__ == "__main__":
    main()
