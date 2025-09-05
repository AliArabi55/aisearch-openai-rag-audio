#!/usr/bin/env python3
"""
أداة تتبع شاملة لمشكلة عدم ظهور الأسعار في موديل الريل تايم
Comprehensive Debugging Tool for Real-time Model Price Issue
"""

import json
import sys
import os
import time
from datetime import datetime
from typing import Dict, List, Any

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'app', 'backend'))

try:
    from dotenv import load_dotenv
    from azure.search.documents import SearchClient
    from azure.core.credentials import AzureKeyCredential
    print("✅ تم تحميل المكتبات المطلوبة")
except ImportError as e:
    print(f"❌ خطأ في تحميل المكتبات: {e}")
    exit(1)

class PriceFlowTracker:
    def __init__(self):
        """Initialize the price flow tracker"""
        load_dotenv()
        self.tracking_data = {
            'timestamp': datetime.now().isoformat(),
            'steps': [],
            'issues_found': [],
            'recommendations': []
        }
        
    def log_step(self, step_name: str, data: Any, success: bool = True):
        """Log a step in the price flow tracking"""
        step_data = {
            'step': step_name,
            'timestamp': datetime.now().isoformat(),
            'success': success,
            'data': data
        }
        self.tracking_data['steps'].append(step_data)
        
        status = "✅" if success else "❌"
        print(f"{status} {step_name}")
        if isinstance(data, dict) and 'details' in data:
            print(f"   📝 {data['details']}")
    
    def log_issue(self, issue: str):
        """Log an issue found during tracking"""
        self.tracking_data['issues_found'].append(issue)
        print(f"🚨 مشكلة: {issue}")
    
    def log_recommendation(self, recommendation: str):
        """Log a recommendation"""
        self.tracking_data['recommendations'].append(recommendation)
        print(f"💡 توصية: {recommendation}")
    
    def step1_test_azure_search_direct(self) -> Dict:
        """Step 1: Test Azure Search directly for Price field type"""
        print("\n🔍 الخطوة 1: اختبار Azure Search مباشرة...")
        
        try:
            search_endpoint = os.getenv('AZURE_SEARCH_ENDPOINT')
            index_name = os.getenv('AZURE_SEARCH_INDEX_NAME')
            api_key = os.getenv('AZURE_SEARCH_API_KEY')
            
            if not all([search_endpoint, index_name, api_key]):
                self.log_issue("متغيرات البيئة مفقودة")
                return {}
            
            search_client = SearchClient(
                endpoint=search_endpoint,
                index_name=index_name,
                credential=AzureKeyCredential(api_key)
            )
            
            # Search for tuna pizza specifically
            results = search_client.search(
                search_text="tuna pizza",
                top=3,
                select="ID,Name,ingredients,Price"
            )
            
            items = list(results)
            
            if items:
                sample_item = items[0]
                price_value = sample_item.get('Price')
                price_type = type(price_value).__name__
                
                step_data = {
                    'total_results': len(items),
                    'sample_item': dict(sample_item),
                    'price_value': price_value,
                    'price_type': price_type,
                    'details': f"وجدت {len(items)} نتائج، السعر: {price_value} (نوع: {price_type})"
                }
                
                self.log_step("Azure Search Direct Test", step_data, True)
                
                # Check if Price is Int32
                if price_type == 'int':
                    print(f"   🔢 السعر من نوع integer: {price_value}")
                elif price_type == 'str':
                    print(f"   📝 السعر من نوع string: '{price_value}'")
                else:
                    print(f"   ⚠️ السعر من نوع غير متوقع: {price_type}")
                    self.log_issue(f"نوع السعر غير متوقع: {price_type}")
                
                return step_data
            else:
                self.log_issue("لا توجد نتائج لـ 'tuna pizza'")
                return {'total_results': 0}
                
        except Exception as e:
            self.log_issue(f"خطأ في Azure Search: {str(e)}")
            return {}
    
    def step2_test_translation_flow(self) -> Dict:
        """Step 2: Test Arabic to English translation"""
        print("\n🌐 الخطوة 2: اختبار تدفق الترجمة...")
        
        try:
            from translation_utils import translate_and_extract_for_search
            
            test_queries = [
                "بيتزا تونه وسط",
                "بيتزا تونة وسط", 
                "تونة بيتزا",
                "tuna pizza medium"
            ]
            
            translation_results = []
            
            for query in test_queries:
                translated, mode = translate_and_extract_for_search(query)
                
                result = {
                    'original': query,
                    'translated': translated,
                    'mode': mode
                }
                translation_results.append(result)
                print(f"   '{query}' → '{translated}'")
            
            step_data = {
                'results': translation_results,
                'details': f"اختبار {len(test_queries)} استعلامات ترجمة"
            }
            
            self.log_step("Translation Flow Test", step_data, True)
            return step_data
            
        except Exception as e:
            self.log_issue(f"خطأ في الترجمة: {str(e)}")
            return {}
    
    def step3_test_search_through_ragtools(self) -> Dict:
        """Step 3: Test search through ragtools (the actual app flow)"""
        print("\n🔧 الخطوة 3: اختبار البحث عبر ragtools...")
        
        try:
            # Import ragtools components
            import ragtools
            from translation_utils import translate_and_extract_for_search
            
            # Test with Arabic query
            arabic_query = "بيتزا تونه وسط"
            print(f"   🔍 البحث الأصلي: '{arabic_query}'")
            
            # Translate query
            search_query, mode = translate_and_extract_for_search(arabic_query)
            print(f"   🎯 الاستعلام المترجم: '{search_query}'")
            
            # Setup search client
            search_endpoint = os.getenv('AZURE_SEARCH_ENDPOINT')
            index_name = os.getenv('AZURE_SEARCH_INDEX_NAME')
            api_key = os.getenv('AZURE_SEARCH_API_KEY')
            
            search_client = SearchClient(
                endpoint=search_endpoint,
                index_name=index_name,
                credential=AzureKeyCredential(api_key)
            )
            
            # Perform search
            search_results = search_client.search(
                search_text=search_query,
                top=5,
                select="ID,Name,ingredients,Price"
            )
            
            docs = []
            for r in list(search_results):
                doc = {
                    'ID': r.get('ID', 'غير محدد'),
                    'Name': r.get('Name', 'بدون اسم'),
                    'ingredients': r.get('ingredients', 'بدون وصف'),
                    'Price': r.get('Price', 'غير محدد')
                }
                docs.append(doc)
                
                # Log detailed price info
                price_val = r.get('Price')
                print(f"   📋 {doc['Name']}: السعر = {price_val} (نوع: {type(price_val).__name__})")
            
            step_data = {
                'arabic_query': arabic_query,
                'translated_query': search_query,
                'results_count': len(docs),
                'docs': docs,
                'details': f"العثور على {len(docs)} نتائج من ragtools"
            }
            
            self.log_step("Ragtools Search Flow", step_data, len(docs) > 0)
            return step_data
            
        except Exception as e:
            self.log_issue(f"خطأ في ragtools: {str(e)}")
            return {}
    
    def step4_test_model_input_generation(self, docs: List[Dict]) -> Dict:
        """Step 4: Test model input generation with price validation"""
        print("\n🎛️ الخطوة 4: اختبار توليد إدخال الموديل...")
        
        if not docs:
            self.log_issue("لا توجد بيانات لاختبار توليد إدخال الموديل")
            return {}
        
        try:
            from model_input_settings import generate_model_input
            
            # Test model input generation
            result = generate_model_input(docs, "بيتزا تونه وسط", "tuna pizza medium")
            
            # Check if prices are shown
            prices_shown = []
            price_not_available_count = result.count("السعر غير متاح")
            
            for doc in docs:
                price = doc.get('Price')
                if price is not None and str(price).strip() and str(price) != "غير محدد":
                    prices_shown.append(price)
            
            step_data = {
                'input_docs_count': len(docs),
                'generated_text': result,
                'prices_in_docs': [doc.get('Price') for doc in docs],
                'prices_shown_count': len(prices_shown),
                'price_not_available_count': price_not_available_count,
                'details': f"نولد نص للموديل مع {len(prices_shown)} أسعار ظاهرة و {price_not_available_count} أسعار غير متاحة"
            }
            
            print(f"   📝 النص المولد: {result}")
            print(f"   💰 الأسعار الموجودة: {prices_shown}")
            print(f"   ❌ عدد 'السعر غير متاح': {price_not_available_count}")
            
            success = price_not_available_count == 0 and len(prices_shown) > 0
            self.log_step("Model Input Generation", step_data, success)
            
            if not success:
                self.log_issue("الأسعار لا تظهر بشكل صحيح في إدخال الموديل")
            
            return step_data
            
        except Exception as e:
            self.log_issue(f"خطأ في توليد إدخال الموديل: {str(e)}")
            return {}
    
    def step5_deep_price_validation_analysis(self, docs: List[Dict]) -> Dict:
        """Step 5: Deep analysis of price validation logic"""
        print("\n🔬 الخطوة 5: تحليل عميق لمنطق التحقق من الأسعار...")
        
        if not docs:
            return {}
        
        try:
            validation_results = []
            
            for i, doc in enumerate(docs, 1):
                price = doc.get('Price')
                
                # Manual validation (same logic as in model_input_settings.py)
                is_price_available = (
                    price is not None and 
                    str(price).strip() and 
                    str(price) != "غير محدد" and 
                    str(price).strip() != ""
                )
                
                validation_result = {
                    'doc_index': i,
                    'name': doc.get('Name', 'Unknown'),
                    'raw_price': price,
                    'price_type': type(price).__name__,
                    'price_str': str(price),
                    'price_str_strip': str(price).strip(),
                    'checks': {
                        'not_none': price is not None,
                        'strip_not_empty': bool(str(price).strip()),
                        'not_غير_محدد': str(price) != "غير محدد",
                        'strip_not_empty_string': str(price).strip() != ""
                    },
                    'final_result': is_price_available
                }
                
                validation_results.append(validation_result)
                
                print(f"   🧮 التحليل {i}: {doc.get('Name', 'Unknown')}")
                print(f"      السعر الخام: {price} (نوع: {type(price).__name__})")
                print(f"      فحص None: {validation_result['checks']['not_none']}")
                print(f"      فحص strip: {validation_result['checks']['strip_not_empty']}")
                print(f"      فحص 'غير محدد': {validation_result['checks']['not_غير_محدد']}")
                print(f"      النتيجة النهائية: {'✅ متاح' if is_price_available else '❌ غير متاح'}")
            
            # Summary
            available_count = sum(1 for r in validation_results if r['final_result'])
            
            step_data = {
                'validation_results': validation_results,
                'total_docs': len(docs),
                'available_prices': available_count,
                'unavailable_prices': len(docs) - available_count,
                'details': f"تحليل {len(docs)} عناصر: {available_count} متاح، {len(docs) - available_count} غير متاح"
            }
            
            success = available_count > 0
            self.log_step("Deep Price Validation Analysis", step_data, success)
            
            if not success:
                self.log_issue("جميع الأسعار تظهر كغير متاحة في التحليل العميق")
            
            return step_data
            
        except Exception as e:
            self.log_issue(f"خطأ في التحليل العميق: {str(e)}")
            return {}
    
    def run_complete_tracking(self) -> Dict:
        """Run complete price flow tracking"""
        print("🚀 بدء التتبع الشامل لتدفق الأسعار...")
        print("=" * 70)
        
        # Step 1: Azure Search Direct
        azure_data = self.step1_test_azure_search_direct()
        
        # Step 2: Translation
        translation_data = self.step2_test_translation_flow()
        
        # Step 3: Ragtools Search
        ragtools_data = self.step3_test_search_through_ragtools()
        
        # Step 4: Model Input Generation
        docs = ragtools_data.get('docs', [])
        model_input_data = self.step4_test_model_input_generation(docs)
        
        # Step 5: Deep Price Validation
        validation_data = self.step5_deep_price_validation_analysis(docs)
        
        # Generate summary and recommendations
        self.generate_final_analysis()
        
        # Save detailed tracking data
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"price_flow_tracking_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.tracking_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 تم حفظ بيانات التتبع في: {filename}")
        print("🏁 انتهى التتبع الشامل!")
        
        return self.tracking_data
    
    def generate_final_analysis(self):
        """Generate final analysis and recommendations"""
        print("\n📊 التحليل النهائي...")
        
        # Analyze issues found
        if not self.tracking_data['issues_found']:
            print("✅ لم يتم العثور على مشاكل في تدفق الأسعار")
        else:
            print("🚨 المشاكل المكتشفة:")
            for issue in self.tracking_data['issues_found']:
                print(f"   • {issue}")
        
        # Generate recommendations based on findings
        steps = self.tracking_data['steps']
        
        # Check Azure Search step
        azure_step = next((s for s in steps if s['step'] == 'Azure Search Direct Test'), None)
        if azure_step and azure_step['success']:
            price_type = azure_step['data'].get('price_type', 'unknown')
            if price_type == 'int':
                self.log_recommendation("Azure Search يرجع أسعار من نوع integer - هذا صحيح")
            else:
                self.log_recommendation(f"فحص نوع البيانات في Azure Search: {price_type}")
        
        # Check model input step  
        model_step = next((s for s in steps if s['step'] == 'Model Input Generation'), None)
        if model_step and not model_step['success']:
            self.log_recommendation("مراجعة منطق التحقق من الأسعار في model_input_settings.py")
            
        # Check validation step
        validation_step = next((s for s in steps if s['step'] == 'Deep Price Validation Analysis'), None)
        if validation_step and not validation_step['success']:
            self.log_recommendation("إصلاح شروط التحقق من صحة الأسعار")
        
        # General recommendations
        self.log_recommendation("التأكد من أن Azure Search يرجع بيانات صحيحة")
        self.log_recommendation("اختبار التطبيق مع استعلامات مختلفة")
        self.log_recommendation("مراقبة logs التطبيق أثناء الاستخدام")

def main():
    """Main tracking function"""
    tracker = PriceFlowTracker()
    results = tracker.run_complete_tracking()
    
    # Print summary
    print(f"\n🎯 ملخص التتبع:")
    print(f"   📝 عدد الخطوات: {len(results['steps'])}")
    print(f"   🚨 عدد المشاكل: {len(results['issues_found'])}")
    print(f"   💡 عدد التوصيات: {len(results['recommendations'])}")
    
    successful_steps = sum(1 for s in results['steps'] if s['success'])
    print(f"   ✅ خطوات ناجحة: {successful_steps}/{len(results['steps'])}")

if __name__ == "__main__":
    main()
