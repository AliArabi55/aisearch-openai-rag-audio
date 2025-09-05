#!/usr/bin/env python3
"""
أداة تشخيص شاملة لأداء موديل الريل تايم
Comprehensive Performance Diagnostic Tool for Real-time Model
"""

import asyncio
import time
import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Any

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'app', 'backend'))

try:
    from azure.search.documents import SearchClient
    from azure.core.credentials import AzureKeyCredential
    from dotenv import load_dotenv
    print("✅ تم تحميل المكتبات المطلوبة")
except ImportError as e:
    print(f"❌ خطأ في تحميل المكتبات: {e}")
    exit(1)

class RealtimePerformanceDiagnostic:
    def __init__(self):
        """Initialize diagnostic tool"""
        load_dotenv()
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'environment_check': {},
            'search_performance': {},
            'model_input_performance': {},
            'memory_performance': {},
            'recommendations': []
        }
        
    def check_environment_variables(self) -> Dict:
        """Check if all required environment variables are set"""
        print("🔍 فحص متغيرات البيئة...")
        
        required_vars = [
            'AZURE_SEARCH_ENDPOINT',
            'AZURE_SEARCH_INDEX_NAME', 
            'AZURE_SEARCH_API_KEY',
            'AZURE_OPENAI_ENDPOINT',
            'AZURE_OPENAI_API_KEY'
        ]
        
        env_status = {}
        missing_vars = []
        
        for var in required_vars:
            value = os.getenv(var)
            if value and value != "YOUR_AZURE_OPENAI_ENDPOINT_HERE":
                env_status[var] = "✅ متوفر"
            else:
                env_status[var] = "❌ مفقود"
                missing_vars.append(var)
        
        self.results['environment_check'] = {
            'status': env_status,
            'missing_variables': missing_vars,
            'all_present': len(missing_vars) == 0
        }
        
        for var, status in env_status.items():
            print(f"   {var}: {status}")
            
        return self.results['environment_check']
    
    def test_search_performance(self) -> Dict:
        """Test Azure Search performance"""
        print("🔍 اختبار أداء Azure Search...")
        
        try:
            search_endpoint = os.getenv('AZURE_SEARCH_ENDPOINT')
            index_name = os.getenv('AZURE_SEARCH_INDEX_NAME')
            api_key = os.getenv('AZURE_SEARCH_API_KEY')
            
            if not all([search_endpoint, index_name, api_key]):
                raise Exception("متغيرات Azure Search مفقودة")
            
            search_client = SearchClient(
                endpoint=search_endpoint,
                index_name=index_name,
                credential=AzureKeyCredential(api_key)
            )
            
            # Test queries with performance timing
            test_queries = ["بيتزا", "برجر", "دجاج", "سلطة", "chicken"]
            query_times = []
            
            for query in test_queries:
                start_time = time.time()
                
                try:
                    results = search_client.search(
                        search_text=query,
                        top=5,
                        select="ID,Name,ingredients,Price"
                    )
                    
                    # Convert to list to measure actual search time
                    results_list = list(results)
                    search_time = time.time() - start_time
                    
                    query_times.append({
                        'query': query,
                        'time_seconds': search_time,
                        'results_count': len(results_list),
                        'status': 'success'
                    })
                    
                    print(f"   🔍 '{query}': {search_time:.3f}s ({len(results_list)} نتائج)")
                    
                except Exception as e:
                    query_times.append({
                        'query': query,
                        'time_seconds': 0,
                        'results_count': 0,
                        'status': f'error: {str(e)}'
                    })
                    print(f"   ❌ '{query}': خطأ - {e}")
            
            avg_time = sum(q['time_seconds'] for q in query_times if q['status'] == 'success') / len([q for q in query_times if q['status'] == 'success'])
            
            self.results['search_performance'] = {
                'queries': query_times,
                'average_time_seconds': avg_time,
                'performance_rating': 'fast' if avg_time < 1 else 'slow' if avg_time > 3 else 'medium'
            }
            
            print(f"   📊 متوسط وقت البحث: {avg_time:.3f} ثانية")
            
            if avg_time > 2:
                self.results['recommendations'].append("🐌 البحث بطيء - قد تحتاج لتحسين الاستعلامات")
            
        except Exception as e:
            self.results['search_performance'] = {'error': str(e)}
            print(f"   ❌ خطأ في اختبار البحث: {e}")
            
        return self.results['search_performance']
    
    def test_model_input_performance(self) -> Dict:
        """Test model input formatting performance"""
        print("🔍 اختبار أداء تنسيق إدخال الموديل...")
        
        try:
            from model_input_settings import generate_model_input
            
            # Sample data for testing
            sample_docs = [
                {
                    'ID': '1',
                    'Name': 'بيتزا مارجريتا',
                    'ingredients': 'جبن موتزاريلا، طماطم، ريحان',
                    'Price': 220
                },
                {
                    'ID': '2', 
                    'Name': 'برجر كلاسيك',
                    'ingredients': 'لحم بقري، خس، طماطم، بصل',
                    'Price': 145
                },
                {
                    'ID': '3',
                    'Name': 'سلطة يونانية', 
                    'ingredients': 'خس، طماطم، زيتون، جبن فيتا، خيار',
                    'Price': 85
                }
            ]
            
            # Test formatting performance
            format_times = []
            
            for i in range(5):  # Test 5 times
                start_time = time.time()
                result = generate_model_input(sample_docs, "test", "test")
                format_time = time.time() - start_time
                format_times.append(format_time)
                
            avg_format_time = sum(format_times) / len(format_times)
            
            self.results['model_input_performance'] = {
                'times': format_times,
                'average_time_seconds': avg_format_time,
                'performance_rating': 'fast' if avg_format_time < 0.1 else 'slow' if avg_format_time > 0.5 else 'medium'
            }
            
            print(f"   📊 متوسط وقت التنسيق: {avg_format_time:.4f} ثانية")
            
            if avg_format_time > 0.2:
                self.results['recommendations'].append("🐌 تنسيق البيانات بطيء - قد تحتاج للتحسين")
                
        except Exception as e:
            self.results['model_input_performance'] = {'error': str(e)}
            print(f"   ❌ خطأ في اختبار التنسيق: {e}")
            
        return self.results['model_input_performance']
    
    def test_cache_performance(self) -> Dict:
        """Test cache performance"""
        print("🔍 اختبار أداء الذاكرة المؤقتة...")
        
        try:
            import ragtools
            
            # Test cache operations
            start_time = time.time()
            
            # Clear cache
            ragtools.clear_cache()
            clear_time = time.time() - start_time
            
            # Test cache storage and retrieval
            test_data = {'test': 'data', 'timestamp': time.time()}
            
            start_time = time.time()
            ragtools.save_to_cache("test_query", test_data)
            save_time = time.time() - start_time
            
            start_time = time.time()
            cached_data = ragtools.get_from_cache("test_query")
            retrieve_time = time.time() - start_time
            
            self.results['memory_performance'] = {
                'clear_time': clear_time,
                'save_time': save_time,
                'retrieve_time': retrieve_time,
                'cache_working': cached_data is not None
            }
            
            print(f"   🗑️ مسح الذاكرة: {clear_time:.4f}s")
            print(f"   💾 حفظ البيانات: {save_time:.4f}s")  
            print(f"   📖 استرجاع البيانات: {retrieve_time:.4f}s")
            print(f"   🧠 الذاكرة تعمل: {'✅' if cached_data else '❌'}")
            
        except Exception as e:
            self.results['memory_performance'] = {'error': str(e)}
            print(f"   ❌ خطأ في اختبار الذاكرة: {e}")
            
        return self.results['memory_performance']
    
    def generate_recommendations(self) -> List[str]:
        """Generate performance improvement recommendations"""
        print("💡 توليد التوصيات...")
        
        recommendations = []
        
        # Environment recommendations
        env_check = self.results.get('environment_check', {})
        if not env_check.get('all_present', False):
            recommendations.append("🔧 تأكد من إعداد جميع متغيرات البيئة المطلوبة")
        
        # Search performance recommendations
        search_perf = self.results.get('search_performance', {})
        if search_perf.get('performance_rating') == 'slow':
            recommendations.append("🔍 فحص اتصال Azure Search - قد يكون هناك مشكلة في الشبكة")
            recommendations.append("📊 استخدام البحث الدلالي لتحسين الأداء")
        
        # Model input recommendations  
        model_perf = self.results.get('model_input_performance', {})
        if model_perf.get('performance_rating') == 'slow':
            recommendations.append("⚡ تحسين تنسيق البيانات للموديل")
        
        # Cache recommendations
        cache_perf = self.results.get('memory_performance', {})
        if not cache_perf.get('cache_working', False):
            recommendations.append("🧠 إصلاح مشكلة الذاكرة المؤقتة")
        
        # General recommendations
        recommendations.extend([
            "🚀 استخدام البحث الدلالي لنتائج أسرع وأدق",
            "📝 تحديد عدد النتائج لتقليل البيانات المرسلة",
            "⚡ تفعيل الضغط للاستجابات الكبيرة",
            "🧠 استخدام الذاكرة المؤقتة للاستعلامات المتكررة"
        ])
        
        self.results['recommendations'] = recommendations
        
        for rec in recommendations:
            print(f"   {rec}")
            
        return recommendations
    
    def run_full_diagnostic(self) -> Dict:
        """Run complete performance diagnostic"""
        print("🚀 بدء التشخيص الشامل للأداء...")
        print("=" * 60)
        
        self.check_environment_variables()
        print()
        
        self.test_search_performance() 
        print()
        
        self.test_model_input_performance()
        print()
        
        self.test_cache_performance()
        print()
        
        self.generate_recommendations()
        print()
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"performance_diagnostic_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        print("=" * 60)
        print(f"✅ تم حفظ نتائج التشخيص في: {filename}")
        print("🏁 انتهى التشخيص الشامل!")
        
        return self.results

def main():
    """Main diagnostic function"""
    diagnostic = RealtimePerformanceDiagnostic()
    results = diagnostic.run_full_diagnostic()
    
    # Print summary
    print("\n📋 ملخص النتائج:")
    
    env_ok = results['environment_check'].get('all_present', False)
    print(f"   🔧 متغيرات البيئة: {'✅ جميعها موجودة' if env_ok else '❌ متغيرات مفقودة'}")
    
    search_rating = results['search_performance'].get('performance_rating', 'unknown')
    print(f"   🔍 أداء البحث: {search_rating}")
    
    model_rating = results['model_input_performance'].get('performance_rating', 'unknown')  
    print(f"   🎯 أداء الموديل: {model_rating}")
    
    cache_ok = results['memory_performance'].get('cache_working', False)
    print(f"   🧠 الذاكرة المؤقتة: {'✅ تعمل' if cache_ok else '❌ لا تعمل'}")

if __name__ == "__main__":
    main()
