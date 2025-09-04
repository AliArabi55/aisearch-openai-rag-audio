#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبار سريع للتطبيق مع النظام الجديد
"""

import requests
import json

def test_live_app():
    """اختبار التطبيق المباشر مع نظام الترجمة الهجين"""
    
    print("🚀 اختبار التطبيق المباشر مع نظام الترجمة الهجين")
    print("=" * 70)
    
    base_url = "http://localhost:8765"
    
    # اختبار الاتصال أولاً
    try:
        response = requests.get(base_url, timeout=5)
        print(f"✅ التطبيق متصل (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ التطبيق غير متاح: {e}")
        return
    
    # اختبار البحث مع الترجمة
    search_url = f"{base_url}/search"
    
    test_queries = [
        "أريد بيتزا تونة وسط",
        "عايز كباب دجاج كبير", 
        "هات عصير برتقال طازج"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. 🗣️ طلب: '{query}'")
        print("-" * 50)
        
        try:
            payload = {"query": query}
            headers = {"Content-Type": "application/json"}
            
            response = requests.post(search_url, 
                                   json=payload, 
                                   headers=headers, 
                                   timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ نجح البحث!")
                print(f"📊 عدد النتائج: {len(result.get('results', []))}")
                
                # عرض أول نتيجة
                if result.get('results'):
                    first_result = result['results'][0]
                    name = first_result.get('Name', 'غير محدد')
                    print(f"🍕 أول نتيجة: {name}")
                
            else:
                print(f"❌ خطأ في البحث: {response.status_code}")
                print(f"📄 الرسالة: {response.text}")
                
        except Exception as e:
            print(f"❌ خطأ في الطلب: {e}")
        
        print("-" * 50)
    
    print(f"\n🎉 انتهى اختبار التطبيق المباشر")
    print("=" * 70)

if __name__ == "__main__":
    test_live_app()
