#!/usr/bin/env python3
"""
أداة بحث محسنة للتعامل مع النصوص العربية والإنجليزية
Enhanced Search Tool for Arabic and English Text
"""

import requests
import json
import os
import time
from dotenv import load_dotenv
from typing import List, Dict, Any

class EnhancedSearchTester:
    def __init__(self):
        load_dotenv()
        self.search_endpoint = os.getenv('AZURE_SEARCH_ENDPOINT')
        self.index_name = os.getenv('AZURE_SEARCH_INDEX_NAME')
        self.api_key = os.getenv('AZURE_SEARCH_API_KEY')
        
        self.headers = {
            'Content-Type': 'application/json',
            'api-key': self.api_key
        }
        
    def search_with_timing(self, query: str, search_mode: str = "any") -> Dict[str, Any]:
        """Execute search with performance timing"""
        
        search_payload = {
            "search": query,
            "searchMode": search_mode,
            "top": 10,
            "select": "ID,Name,ingredients,Price",
            "searchFields": "Name,ingredients",
            "highlight": "Name,ingredients",
            "highlightPreTag": "<b>",
            "highlightPostTag": "</b>"
        }
        
        url = f'{self.search_endpoint}/indexes/{self.index_name}/docs/search?api-version=2023-11-01'
        
        start_time = time.time()
        
        try:
            response = requests.post(url, headers=self.headers, json=search_payload)
            search_time = time.time() - start_time
            
            if response.status_code == 200:
                results = response.json()
                return {
                    'success': True,
                    'results': results.get('value', []),
                    'count': len(results.get('value', [])),
                    'time_seconds': search_time,
                    'query': query,
                    'search_mode': search_mode
                }
            else:
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}",
                    'time_seconds': search_time,
                    'query': query,
                    'search_mode': search_mode
                }
                
        except Exception as e:
            search_time = time.time() - start_time
            return {
                'success': False,
                'error': str(e),
                'time_seconds': search_time,
                'query': query,
                'search_mode': search_mode
            }
    
    def test_multiple_search_strategies(self, query: str) -> List[Dict[str, Any]]:
        """Test different search strategies for the same query"""
        
        strategies = [
            {"mode": "any", "description": "البحث العام"},
            {"mode": "all", "description": "البحث الدقيق"}
        ]
        
        results = []
        
        for strategy in strategies:
            print(f"  🔍 {strategy['description']} لـ '{query}'...")
            result = self.search_with_timing(query, strategy['mode'])
            result['strategy'] = strategy['description']
            results.append(result)
            
            if result['success']:
                print(f"    ✅ {result['count']} نتائج في {result['time_seconds']:.3f}s")
            else:
                print(f"    ❌ فشل: {result['error']}")
        
        return results
    
    def run_comprehensive_search_test(self) -> Dict[str, Any]:
        """Run comprehensive search testing"""
        
        print("🔍 اختبار البحث الشامل المحسن...")
        print("=" * 60)
        
        # Test queries in both Arabic and English
        test_queries = [
            # Arabic queries
            "دجاج",
            "بيتزا", 
            "برجر",
            "سلطة",
            "شاورما",
            # English queries
            "chicken",
            "pizza",
            "burger", 
            "salad",
            "beef",
            # Mixed content
            "chicken pizza",
            "beef burger"
        ]
        
        all_results = []
        total_time = 0
        successful_searches = 0
        
        for query in test_queries:
            print(f"\n🎯 اختبار البحث عن: '{query}'")
            query_results = self.test_multiple_search_strategies(query)
            
            for result in query_results:
                all_results.append(result)
                if result['success']:
                    total_time += result['time_seconds']
                    successful_searches += 1
                    
                    # Show top results
                    if result['results']:
                        print(f"    📋 أفضل النتائج:")
                        for i, item in enumerate(result['results'][:3], 1):
                            name = item.get('Name', 'بدون اسم')
                            price = item.get('Price', 'غير محدد')
                            print(f"      {i}. {name} - {price} ريال")
        
        # Calculate performance metrics
        avg_time = total_time / successful_searches if successful_searches > 0 else 0
        success_rate = (successful_searches / len(all_results)) * 100
        
        summary = {
            'total_queries': len(all_results),
            'successful_queries': successful_searches,
            'success_rate_percent': success_rate,
            'average_time_seconds': avg_time,
            'total_time_seconds': total_time,
            'performance_rating': 'fast' if avg_time < 0.5 else 'slow' if avg_time > 2 else 'medium',
            'all_results': all_results
        }
        
        print("\n" + "=" * 60)
        print("📊 ملخص نتائج الاختبار:")
        print(f"   🎯 إجمالي الاستعلامات: {summary['total_queries']}")
        print(f"   ✅ الاستعلامات الناجحة: {summary['successful_queries']}")
        print(f"   📈 معدل النجاح: {summary['success_rate_percent']:.1f}%")
        print(f"   ⏱️ متوسط الوقت: {summary['average_time_seconds']:.3f}s")
        print(f"   🏃 تقييم الأداء: {summary['performance_rating']}")
        
        # Save detailed results
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"enhanced_search_test_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        print(f"💾 تم حفظ النتائج التفصيلية في: {filename}")
        
        return summary

def main():
    """Main testing function"""
    tester = EnhancedSearchTester()
    
    if not all([tester.search_endpoint, tester.index_name, tester.api_key]):
        print("❌ خطأ: متغيرات البيئة مفقودة!")
        print("تأكد من وجود AZURE_SEARCH_ENDPOINT, AZURE_SEARCH_INDEX_NAME, AZURE_SEARCH_API_KEY")
        return
    
    print("🚀 بدء اختبار البحث المحسن...")
    results = tester.run_comprehensive_search_test()
    
    # Provide recommendations based on results
    print("\n💡 توصيات التحسين:")
    
    if results['success_rate_percent'] < 80:
        print("   📝 تحسين فهرسة المحتوى العربي")
        print("   🔤 إضافة محلل نصوص عربي")
    
    if results['average_time_seconds'] > 1:
        print("   ⚡ تحسين استعلامات البحث")
        print("   🎯 تقليل عدد الحقول المطلوبة")
    
    if results['performance_rating'] == 'slow':
        print("   🚀 اعتبار تفعيل الـ caching")
        print("   📊 مراجعة إعدادات الفهرس")
    
    print("\n🏁 انتهى اختبار البحث المحسن!")

if __name__ == "__main__":
    main()
