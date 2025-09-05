#!/usr/bin/env python3
"""
أداة تشخيص شاملة لمشاكل الأداء والموديل الريل تايم
Comprehensive diagnostic tool for performance and realtime model issues
"""

import asyncio
import time
import json
import sys
import os
from datetime import datetime
from typing import Dict, List

# إضافة مسار backend للاستيراد
sys.path.append(os.path.join(os.path.dirname(__file__), 'app', 'backend'))

class RTDiagnostics:
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'environment_check': {},
            'azure_search_performance': {},
            'openai_realtime_check': {},
            'system_resources': {},
            'recommendations': []
        }

    def check_environment_variables(self):
        """فحص متغيرات البيئة المطلوبة"""
        print("🔍 فحص متغيرات البيئة...")
        
        required_vars = [
            'AZURE_SEARCH_SERVICE_ENDPOINT',
            'AZURE_SEARCH_INDEX_NAME', 
            'AZURE_SEARCH_API_KEY',
            'AZURE_OPENAI_ENDPOINT',
            'AZURE_OPENAI_API_KEY',
            'AZURE_OPENAI_DEPLOYMENT_NAME'
        ]
        
        missing_vars = []
        present_vars = []
        
        for var in required_vars:
            value = os.getenv(var)
            if value:
                present_vars.append(var)
                print(f"  ✅ {var}: متوفر")
            else:
                missing_vars.append(var)
                print(f"  ❌ {var}: مفقود")
        
        self.results['environment_check'] = {
            'present_vars': present_vars,
            'missing_vars': missing_vars,
            'status': 'OK' if not missing_vars else 'ERROR'
        }
        
        return len(missing_vars) == 0

    async def test_azure_search_performance(self):
        """اختبار أداء Azure Search"""
        print("🔍 اختبار أداء Azure Search...")
        
        try:
            from azure.search.documents import SearchClient
            from azure.core.credentials import AzureKeyCredential
            
            endpoint = os.getenv('AZURE_SEARCH_SERVICE_ENDPOINT')
            key = os.getenv('AZURE_SEARCH_API_KEY')
            index_name = os.getenv('AZURE_SEARCH_INDEX_NAME')
            
            if not all([endpoint, key, index_name]):
                print("  ❌ متغيرات Azure Search مفقودة")
                self.results['azure_search_performance']['status'] = 'ERROR'
                return False
            
            search_client = SearchClient(
                endpoint=endpoint,
                index_name=index_name,
                credential=AzureKeyCredential(key)
            )
            
            # اختبار استعلامات متعددة وقياس الوقت
            test_queries = ["بيتزا", "برجر", "شاورما", "chicken", "pizza"]
            performance_data = []
            
            for query in test_queries:
                start_time = time.time()
                try:
                    results = search_client.search(
                        search_text=query,
                        top=5,
                        select="ID,Name,ingredients,Price"
                    )
                    result_count = len(list(results))
                    end_time = time.time()
                    response_time = (end_time - start_time) * 1000  # milliseconds
                    
                    performance_data.append({
                        'query': query,
                        'response_time_ms': response_time,
                        'result_count': result_count,
                        'status': 'SUCCESS'
                    })
                    print(f"  ✅ {query}: {response_time:.1f}ms, {result_count} نتائج")
                    
                except Exception as e:
                    performance_data.append({
                        'query': query,
                        'error': str(e),
                        'status': 'ERROR'
                    })
                    print(f"  ❌ {query}: خطأ - {e}")
            
            # حساب متوسط زمن الاستجابة
            successful_queries = [p for p in performance_data if p['status'] == 'SUCCESS']
            if successful_queries:
                avg_response_time = sum(p['response_time_ms'] for p in successful_queries) / len(successful_queries)
                max_response_time = max(p['response_time_ms'] for p in successful_queries)
                
                self.results['azure_search_performance'] = {
                    'status': 'OK',
                    'average_response_time_ms': avg_response_time,
                    'max_response_time_ms': max_response_time,
                    'successful_queries': len(successful_queries),
                    'failed_queries': len(performance_data) - len(successful_queries),
                    'details': performance_data
                }
                
                # إضافة توصيات للأداء
                if avg_response_time > 1000:
                    self.results['recommendations'].append("⚠️ زمن استجابة Azure Search بطيء (>1 ثانية)")
                if max_response_time > 2000:
                    self.results['recommendations'].append("⚠️ بعض الاستعلامات بطيئة جداً (>2 ثانية)")
                    
                print(f"  📊 متوسط زمن الاستجابة: {avg_response_time:.1f}ms")
                return True
            else:
                self.results['azure_search_performance']['status'] = 'ERROR'
                return False
                
        except Exception as e:
            print(f"  ❌ خطأ في اختبار Azure Search: {e}")
            self.results['azure_search_performance'] = {
                'status': 'ERROR',
                'error': str(e)
            }
            return False

    def check_openai_realtime_config(self):
        """فحص إعدادات OpenAI Realtime"""
        print("🔍 فحص إعدادات OpenAI Realtime...")
        
        try:
            # فحص ملف app.py للإعدادات
            app_path = os.path.join('app', 'backend', 'app.py')
            if os.path.exists(app_path):
                with open(app_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # البحث عن إعدادات مهمة
                config_checks = {
                    'realtime_model': 'gpt-4o-realtime' in content,
                    'websocket_setup': 'websocket' in content.lower(),
                    'voice_settings': 'voice' in content.lower(),
                    'rtmt_setup': 'RTMiddleTier' in content
                }
                
                self.results['openai_realtime_check'] = config_checks
                
                for check, status in config_checks.items():
                    print(f"  {'✅' if status else '❌'} {check}: {'موجود' if status else 'مفقود'}")
                    
                return all(config_checks.values())
            else:
                print("  ❌ ملف app.py غير موجود")
                return False
                
        except Exception as e:
            print(f"  ❌ خطأ في فحص إعدادات Realtime: {e}")
            return False

    def check_system_resources(self):
        """فحص موارد النظام"""
        print("🔍 فحص موارد النظام...")
        
        try:
            import psutil
            
            # معلومات CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # معلومات الذاكرة
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available_gb = memory.available / (1024**3)
            
            # معلومات القرص
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            self.results['system_resources'] = {
                'cpu_percent': cpu_percent,
                'cpu_count': cpu_count,
                'memory_percent': memory_percent,
                'memory_available_gb': memory_available_gb,
                'disk_percent': disk_percent
            }
            
            print(f"  💻 استخدام CPU: {cpu_percent}%")
            print(f"  💾 استخدام الذاكرة: {memory_percent}%")
            print(f"  💾 الذاكرة المتاحة: {memory_available_gb:.1f} GB")
            print(f"  💿 استخدام القرص: {disk_percent:.1f}%")
            
            # إضافة توصيات للموارد
            if cpu_percent > 80:
                self.results['recommendations'].append("⚠️ استخدام CPU مرتفع")
            if memory_percent > 80:
                self.results['recommendations'].append("⚠️ استخدام الذاكرة مرتفع")
            if memory_available_gb < 1:
                self.results['recommendations'].append("⚠️ ذاكرة متاحة قليلة")
                
            return True
            
        except ImportError:
            print("  ⚠️ مكتبة psutil غير مثبتة")
            return False
        except Exception as e:
            print(f"  ❌ خطأ في فحص الموارد: {e}")
            return False

    async def run_full_diagnosis(self):
        """تشغيل التشخيص الشامل"""
        print("🔧 بدء التشخيص الشامل للنظام...")
        print("=" * 60)
        
        # فحص متغيرات البيئة
        env_ok = self.check_environment_variables()
        print()
        
        # فحص أداء Azure Search
        search_ok = await self.test_azure_search_performance()
        print()
        
        # فحص إعدادات Realtime
        realtime_ok = self.check_openai_realtime_config()
        print()
        
        # فحص موارد النظام
        resources_ok = self.check_system_resources()
        print()
        
        # تحليل النتائج وإضافة توصيات
        print("📋 ملخص التشخيص:")
        print("=" * 60)
        
        overall_status = "OK" if all([env_ok, search_ok, realtime_ok]) else "ISSUES_FOUND"
        
        print(f"🔧 متغيرات البيئة: {'✅ OK' if env_ok else '❌ ISSUES'}")
        print(f"🔍 أداء Azure Search: {'✅ OK' if search_ok else '❌ ISSUES'}")
        print(f"🎙️ إعدادات Realtime: {'✅ OK' if realtime_ok else '❌ ISSUES'}")
        print(f"💻 موارد النظام: {'✅ OK' if resources_ok else '❌ ISSUES'}")
        
        print(f"\n🎯 الحالة العامة: {'✅ النظام جاهز' if overall_status == 'OK' else '⚠️ يحتاج إصلاح'}")
        
        # طباعة التوصيات
        if self.results['recommendations']:
            print("\n💡 التوصيات:")
            for recommendation in self.results['recommendations']:
                print(f"  {recommendation}")
        
        # حفظ التقرير
        report_filename = f"rt_diagnostics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 تم حفظ التقرير في: {report_filename}")
        
        return overall_status == "OK"

async def main():
    """الدالة الرئيسية"""
    diagnostics = RTDiagnostics()
    success = await diagnostics.run_full_diagnosis()
    
    if not success:
        print("\n🔧 يُنصح بحل المشاكل المذكورة قبل تشغيل التطبيق")
    else:
        print("\n✅ النظام جاهز للتشغيل!")
    
    return success

if __name__ == "__main__":
    asyncio.run(main())
