#!/usr/bin/env python3
"""
اختبار نهائي شامل للتأكد من حل جميع المشاكل
Final Comprehensive Test to Verify All Issues Are Resolved
"""

import asyncio
import time
import json
import requests
import sys
import os
from datetime import datetime
from typing import Dict, List, Any

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'app', 'backend'))

from dotenv import load_dotenv

class FinalSystemTest:
    def __init__(self):
        """Initialize final system test"""
        load_dotenv()
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'environment_check': {},
            'search_translation_test': {},
            'price_validation_test': {},
            'performance_test': {},
            'real_time_model_test': {},
            'summary': {}
        }
        
    def test_environment_setup(self) -> bool:
        """Test environment configuration"""
        print("🔧 اختبار إعداد البيئة...")
        
        required_vars = {
            'AZURE_SEARCH_ENDPOINT': os.getenv('AZURE_SEARCH_ENDPOINT'),
            'AZURE_SEARCH_INDEX_NAME': os.getenv('AZURE_SEARCH_INDEX_NAME'),
            'AZURE_SEARCH_API_KEY': os.getenv('AZURE_SEARCH_API_KEY'),
            'AZURE_OPENAI_ENDPOINT': os.getenv('AZURE_OPENAI_ENDPOINT'),
            'AZURE_OPENAI_API_KEY': os.getenv('AZURE_OPENAI_API_KEY')
        }
        
        all_ok = True
        for var, value in required_vars.items():
            status = "✅" if value and value != "YOUR_AZURE_OPENAI_ENDPOINT_HERE" else "❌"
            print(f"   {var}: {status}")
            if status == "❌":
                all_ok = False
        
        self.results['environment_check'] = {
            'all_configured': all_ok,
            'variables': {k: bool(v and v != "YOUR_AZURE_OPENAI_ENDPOINT_HERE") for k, v in required_vars.items()}
        }
        
        return all_ok
    
    def test_search_and_translation(self) -> Dict:
        """Test search with Arabic-to-English translation"""
        print("🔍 اختبار البحث والترجمة...")
        
        try:
            from translation_utils import translate_and_extract_for_search
            
            test_queries = [
                ("دجاج", "Chicken"),
                ("بيتزا", "Pizza"), 
                ("برجر", "Burger"),
                ("أونين رينجز", "Onion Rings")
            ]
            
            translation_results = []
            
            for arabic, expected_english in test_queries:
                translated, mode = translate_and_extract_for_search(arabic)
                
                result = {
                    'arabic': arabic,
                    'expected': expected_english,
                    'translated': translated,
                    'correct': translated.lower() == expected_english.lower(),
                    'mode': mode
                }
                
                translation_results.append(result)
                status = "✅" if result['correct'] else "❌"
                print(f"   '{arabic}' → '{translated}' {status}")
            
            correct_translations = sum(1 for r in translation_results if r['correct'])
            
            self.results['search_translation_test'] = {
                'results': translation_results,
                'total_tests': len(translation_results),
                'correct_translations': correct_translations,
                'success_rate': (correct_translations / len(translation_results)) * 100
            }
            
            return self.results['search_translation_test']
            
        except Exception as e:
            print(f"   ❌ خطأ في اختبار الترجمة: {e}")
            self.results['search_translation_test'] = {'error': str(e)}
            return {}
    
    def test_price_validation_fix(self) -> Dict:
        """Test that price validation fix is working"""
        print("💰 اختبار إصلاح التحقق من الأسعار...")
        
        try:
            from model_input_settings import generate_model_input
            
            test_cases = [
                {
                    'name': 'Integer Price Test',
                    'docs': [{'ID': '1', 'Name': 'Test Pizza', 'ingredients': 'test', 'Price': 220}],
                    'should_show_price': True
                },
                {
                    'name': 'String Price Test',
                    'docs': [{'ID': '2', 'Name': 'Test Burger', 'ingredients': 'test', 'Price': "145"}],
                    'should_show_price': True
                },
                {
                    'name': 'None Price Test',
                    'docs': [{'ID': '3', 'Name': 'Test Salad', 'ingredients': 'test', 'Price': None}],
                    'should_show_price': False
                }
            ]
            
            price_test_results = []
            
            for test in test_cases:
                result = generate_model_input(test['docs'], "test", "test")
                price_shown = "السعر غير متاح" not in result
                correct = price_shown == test['should_show_price']
                
                test_result = {
                    'test_name': test['name'],
                    'expected_price_shown': test['should_show_price'],
                    'price_actually_shown': price_shown,
                    'correct': correct,
                    'result_text': result
                }
                
                price_test_results.append(test_result)
                status = "✅" if correct else "❌"
                print(f"   {test['name']}: {status}")
            
            correct_tests = sum(1 for r in price_test_results if r['correct'])
            
            self.results['price_validation_test'] = {
                'results': price_test_results,
                'total_tests': len(price_test_results),
                'correct_tests': correct_tests,
                'success_rate': (correct_tests / len(price_test_results)) * 100
            }
            
            return self.results['price_validation_test']
            
        except Exception as e:
            print(f"   ❌ خطأ في اختبار الأسعار: {e}")
            self.results['price_validation_test'] = {'error': str(e)}
            return {}
    
    def test_search_performance(self) -> Dict:
        """Test search performance"""
        print("⚡ اختبار أداء البحث...")
        
        try:
            search_endpoint = os.getenv('AZURE_SEARCH_ENDPOINT')
            index_name = os.getenv('AZURE_SEARCH_INDEX_NAME')
            api_key = os.getenv('AZURE_SEARCH_API_KEY')
            
            headers = {
                'Content-Type': 'application/json',
                'api-key': api_key
            }
            
            # Test performance with English queries (known to work)
            test_queries = ["chicken", "pizza", "burger"]
            times = []
            
            for query in test_queries:
                search_payload = {
                    "search": query,
                    "top": 5,
                    "select": "ID,Name,ingredients,Price"
                }
                
                url = f'{search_endpoint}/indexes/{index_name}/docs/search?api-version=2023-11-01'
                
                start_time = time.time()
                response = requests.post(url, headers=headers, json=search_payload)
                search_time = time.time() - start_time
                
                times.append(search_time)
                print(f"   '{query}': {search_time:.3f}s")
            
            avg_time = sum(times) / len(times)
            performance_rating = 'fast' if avg_time < 0.5 else 'slow' if avg_time > 2 else 'medium'
            
            self.results['performance_test'] = {
                'individual_times': times,
                'average_time_seconds': avg_time,
                'performance_rating': performance_rating,
                'is_acceptable': avg_time < 3  # Less than 3 seconds is acceptable
            }
            
            print(f"   📊 متوسط الوقت: {avg_time:.3f}s ({performance_rating})")
            
            return self.results['performance_test']
            
        except Exception as e:
            print(f"   ❌ خطأ في اختبار الأداء: {e}")
            self.results['performance_test'] = {'error': str(e)}
            return {}
    
    def test_realtime_model_readiness(self) -> Dict:
        """Test if real-time model dependencies are ready"""
        print("🤖 اختبار جاهزية موديل الريل تايم...")
        
        try:
            # Check if real-time model endpoint is configured
            openai_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
            openai_key = os.getenv('AZURE_OPENAI_API_KEY')
            
            readiness_checks = {
                'openai_endpoint_configured': bool(openai_endpoint and openai_endpoint != "YOUR_AZURE_OPENAI_ENDPOINT_HERE"),
                'openai_key_configured': bool(openai_key and openai_key != "YOUR_AZURE_OPENAI_API_KEY_HERE"),
                'search_working': 'error' not in self.results.get('performance_test', {}),
                'translation_working': self.results.get('search_translation_test', {}).get('success_rate', 0) > 75,
                'price_validation_working': self.results.get('price_validation_test', {}).get('success_rate', 0) > 75
            }
            
            all_ready = all(readiness_checks.values())
            
            for check, status in readiness_checks.items():
                status_icon = "✅" if status else "❌"
                print(f"   {check}: {status_icon}")
            
            self.results['real_time_model_test'] = {
                'readiness_checks': readiness_checks,
                'overall_ready': all_ready,
                'ready_percentage': (sum(readiness_checks.values()) / len(readiness_checks)) * 100
            }
            
            return self.results['real_time_model_test']
            
        except Exception as e:
            print(f"   ❌ خطأ في اختبار الموديل: {e}")
            self.results['real_time_model_test'] = {'error': str(e)}
            return {}
    
    def generate_final_summary(self) -> Dict:
        """Generate final test summary"""
        print("📋 إنشاء الملخص النهائي...")
        
        # Calculate overall health score
        scores = []
        
        # Environment (20% weight)
        env_score = 100 if self.results['environment_check'].get('all_configured', False) else 0
        scores.append(('environment', env_score, 20))
        
        # Translation (25% weight)
        trans_score = self.results['search_translation_test'].get('success_rate', 0)
        scores.append(('translation', trans_score, 25))
        
        # Price validation (20% weight)
        price_score = self.results['price_validation_test'].get('success_rate', 0)
        scores.append(('price_validation', price_score, 20))
        
        # Performance (15% weight)
        perf_test = self.results['performance_test']
        perf_score = 100 if perf_test.get('is_acceptable', False) else 50
        scores.append(('performance', perf_score, 15))
        
        # Real-time readiness (20% weight)
        rt_score = self.results['real_time_model_test'].get('ready_percentage', 0)
        scores.append(('realtime_readiness', rt_score, 20))
        
        # Calculate weighted average
        total_score = sum(score * weight for _, score, weight in scores) / sum(weight for _, _, weight in scores)
        
        # Determine overall status
        if total_score >= 90:
            status = "ممتاز - النظام جاهز للاستخدام"
            status_icon = "🟢"
        elif total_score >= 75:
            status = "جيد - يحتاج تحسينات طفيفة" 
            status_icon = "🟡"
        elif total_score >= 50:
            status = "متوسط - يحتاج إصلاحات"
            status_icon = "🟠"
        else:
            status = "ضعيف - يحتاج إصلاحات جذرية"
            status_icon = "🔴"
        
        self.results['summary'] = {
            'total_score': total_score,
            'status': status,
            'status_icon': status_icon,
            'individual_scores': scores,
            'recommendations': self.get_recommendations()
        }
        
        return self.results['summary']
    
    def get_recommendations(self) -> List[str]:
        """Get improvement recommendations based on test results"""
        recommendations = []
        
        # Environment recommendations
        if not self.results['environment_check'].get('all_configured', False):
            recommendations.append("🔧 إكمال إعداد متغيرات البيئة المفقودة")
        
        # Translation recommendations
        trans_rate = self.results['search_translation_test'].get('success_rate', 0)
        if trans_rate < 100:
            recommendations.append("🌐 تحسين قاموس الترجمة العربية")
        
        # Price recommendations
        price_rate = self.results['price_validation_test'].get('success_rate', 0)
        if price_rate < 100:
            recommendations.append("💰 مراجعة منطق التحقق من الأسعار")
        
        # Performance recommendations
        perf_test = self.results['performance_test']
        if not perf_test.get('is_acceptable', False):
            recommendations.append("⚡ تحسين أداء البحث - استخدام تخزين مؤقت أو فهرسة أفضل")
        
        # Real-time recommendations
        rt_ready = self.results['real_time_model_test'].get('ready_percentage', 0)
        if rt_ready < 100:
            recommendations.append("🤖 إكمال إعداد موديل الريل تايم")
        
        return recommendations
    
    def run_complete_test(self) -> Dict:
        """Run complete system test"""
        print("🚀 بدء الاختبار النهائي الشامل...")
        print("=" * 70)
        
        # Run all tests
        self.test_environment_setup()
        print()
        
        self.test_search_and_translation()
        print()
        
        self.test_price_validation_fix()
        print()
        
        self.test_search_performance()
        print()
        
        self.test_realtime_model_readiness()
        print()
        
        summary = self.generate_final_summary()
        
        # Print final summary
        print("=" * 70)
        print("🏆 النتيجة النهائية:")
        print(f"   {summary['status_icon']} إجمالي النقاط: {summary['total_score']:.1f}/100")
        print(f"   📊 الحالة: {summary['status']}")
        
        print("\n📈 النقاط التفصيلية:")
        for name, score, weight in summary['individual_scores']:
            print(f"   {name}: {score:.1f}% (وزن: {weight}%)")
        
        if summary['recommendations']:
            print("\n💡 التوصيات:")
            for rec in summary['recommendations']:
                print(f"   {rec}")
        
        # Save detailed results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"final_system_test_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 تم حفظ النتائج التفصيلية في: {filename}")
        print("🏁 انتهى الاختبار النهائي!")
        
        return self.results

def main():
    """Main test function"""
    tester = FinalSystemTest()
    results = tester.run_complete_test()
    
    # Print key findings
    summary = results.get('summary', {})
    
    print(f"\n🎯 الخلاصة:")
    print(f"   النظام حصل على {summary.get('total_score', 0):.1f} نقطة من 100")
    
    if summary.get('total_score', 0) >= 75:
        print("   ✅ النظام جاهز للاستخدام!")
    else:
        print("   ⚠️ النظام يحتاج مزيد من الإصلاحات")

if __name__ == "__main__":
    main()
