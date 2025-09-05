#!/usr/bin/env python3
"""
أداة تشخيص بسيطة جداً لنظام الـ Real-time Model
===============================================
"""

import os
import sys
import json
from datetime import datetime

# إضافة مسار backend
backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app', 'backend')
sys.path.append(backend_path)

print("🚀 بدء تشخيص نظام Real-time Model")
print("="*60)

def check_environment():
    """فحص متغيرات البيئة"""
    print("\n🔧 الخطوة 1: فحص متغيرات البيئة")
    
    env_vars = [
        'AZURE_OPENAI_ENDPOINT',
        'AZURE_OPENAI_REALTIME_DEPLOYMENT_NAME',
        'AZURE_OPENAI_API_VERSION',
        'AZURE_OPENAI_API_KEY',
        'AZURE_SEARCH_ENDPOINT',
        'AZURE_SEARCH_KEY',
        'AZURE_SEARCH_INDEX'
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        status = "✅ مُعرف" if value else "❌ غير مُعرف"
        length = f" ({len(value)} حرف)" if value else ""
        print(f"   {var}: {status}{length}")
    
    return len([v for v in env_vars if os.getenv(v)])

def check_app_py():
    """فحص ملف app.py والـ system message"""
    print("\n📄 الخطوة 2: فحص ملف app.py")
    
    app_file = os.path.join(backend_path, 'app.py')
    
    if not os.path.exists(app_file):
        print("   ❌ ملف app.py غير موجود")
        return False
    
    try:
        with open(app_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"   📊 حجم الملف: {len(content)} حرف")
        print(f"   📊 عدد الأسطر: {len(content.split('\\n'))}")
        
        # البحث عن system message patterns
        system_patterns = [
            'system_message',
            'instructions', 
            '"role": "system"',
            "'role': 'system'"
        ]
        
        found_patterns = []
        for pattern in system_patterns:
            if pattern in content:
                found_patterns.append(pattern)
        
        print(f"   🤖 أنماط system message: {found_patterns}")
        
        # البحث عن كلمات السعر
        price_keywords = ['سعر', 'price', 'متاح', 'available', 'غير متاح', 'unavailable']
        found_keywords = []
        
        for keyword in price_keywords:
            count = content.count(keyword)
            if count > 0:
                found_keywords.append(f"{keyword}({count})")
        
        print(f"   💰 كلمات السعر: {found_keywords}")
        
        # البحث عن الجمل المشكوك فيها
        suspicious_phrases = [
            'السعر مش متاح',
            'السعر غير متاح',
            'price not available',
            'لو مافيش سعر'
        ]
        
        found_suspicious = []
        for phrase in suspicious_phrases:
            if phrase in content:
                found_suspicious.append(phrase)
        
        if found_suspicious:
            print(f"   🚨 جمل مشكوك فيها: {found_suspicious}")
        else:
            print("   ✅ لا توجد جمل مشكوك فيها")
        
        return True, found_suspicious
        
    except Exception as e:
        print(f"   ❌ خطأ في قراءة الملف: {e}")
        return False, []

def test_basic_search():
    """اختبار أساسي للبحث"""
    print("\n🔍 الخطوة 3: اختبار البحث الأساسي")
    
    try:
        from azure.search.documents import SearchClient
        from azure.core.credentials import AzureKeyCredential
        
        search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
        search_key = os.getenv("AZURE_SEARCH_KEY") 
        search_index = os.getenv("AZURE_SEARCH_INDEX", "english22-index")
        
        if not search_endpoint or not search_key:
            print("   ❌ إعدادات البحث غير مكتملة")
            return False
        
        search_client = SearchClient(
            endpoint=search_endpoint,
            index_name=search_index,
            credential=AzureKeyCredential(search_key)
        )
        
        # بحث بسيط
        results = search_client.search(
            search_text="Pizza Tuna Medium",
            top=3,
            select="ID,Name,Price"
        )
        
        results_list = list(results)
        print(f"   📦 وُجدت {len(results_list)} نتائج")
        
        prices_found = 0
        for i, result in enumerate(results_list):
            name = result.get('Name', 'Unknown')
            price = result.get('Price', 'N/A')
            price_type = type(price).__name__
            
            if price != 'N/A' and price is not None:
                prices_found += 1
            
            print(f"      {i+1}. {name} - السعر: {price} ({price_type})")
        
        print(f"   💰 العناصر التي لها أسعار: {prices_found}/{len(results_list)}")
        
        return True, prices_found > 0
        
    except Exception as e:
        print(f"   ❌ خطأ في البحث: {e}")
        return False, False

def main():
    """الدالة الرئيسية"""
    
    # تجميع النتائج
    results = {
        "timestamp": datetime.now().isoformat(),
        "environment_vars_count": 0,
        "app_py_exists": False,
        "suspicious_phrases": [],
        "search_works": False,
        "prices_available": False
    }
    
    # فحص البيئة
    results["environment_vars_count"] = check_environment()
    
    # فحص app.py
    app_check = check_app_py()
    if isinstance(app_check, tuple):
        results["app_py_exists"] = app_check[0]
        results["suspicious_phrases"] = app_check[1]
    else:
        results["app_py_exists"] = app_check
    
    # فحص البحث
    search_check = test_basic_search()
    if isinstance(search_check, tuple):
        results["search_works"] = search_check[0]
        results["prices_available"] = search_check[1]
    else:
        results["search_works"] = search_check
    
    # تحليل المشكلة
    print("\n🎯 تحليل المشكلة:")
    print("="*40)
    
    if results["search_works"] and results["prices_available"]:
        print("✅ البحث يعمل والأسعار متوفرة في قاعدة البيانات")
    else:
        print("❌ مشكلة في البحث أو قاعدة البيانات")
    
    if results["app_py_exists"]:
        if results["suspicious_phrases"]:
            print(f"🚨 توجد جمل مشكوك فيها في app.py: {results['suspicious_phrases']}")
            print("💡 المشكلة المحتملة: الـ system message يطلب من الموديل قول 'السعر غير متاح'")
        else:
            print("✅ ملف app.py يبدو طبيعياً")
    else:
        print("❌ ملف app.py غير موجود")
    
    if results["environment_vars_count"] < 7:
        print(f"⚠️ بعض متغيرات البيئة غير مُعرفة ({results['environment_vars_count']}/7)")
    
    # توصيات
    print("\n💡 التوصيات:")
    print("="*40)
    
    if results["suspicious_phrases"]:
        print("1. 🔧 راجع system message في app.py وأزل التعليمات التي تطلب قول 'السعر غير متاح'")
        print("2. 🔄 أعد تشغيل التطبيق بعد التعديل")
    
    if not results["prices_available"]:
        print("1. 🔍 تحقق من فهرس البحث وتأكد أن حقل Price يحتوي على بيانات")
    
    if results["environment_vars_count"] < 7:
        print("1. ⚙️ راجع ملف .env وتأكد من إعداد جميع المتغيرات")
    
    # حفظ التقرير
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"quick_debug_report_{timestamp}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"\n💾 تم حفظ التقرير في: {filename}")

if __name__ == "__main__":
    main()
