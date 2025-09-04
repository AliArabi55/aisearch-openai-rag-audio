#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
محلل العمليات النهائي
Final Operations Analyzer
تتبع كامل لجميع العمليات من الترجمة إلى البحث إلى النموذج
"""

import requests
import json
import time

def test_real_translation_flow():
    """اختبار تدفق الترجمة الحقيقي مع عرض العمليات"""
    
    print("=" * 80)
    print("🎯 اختبار نظام الترجمة الحقيقي والبحث")
    print("=" * 80)
    
    # عنوان التطبيق
    base_url = "http://localhost:8765"
    
    # جمل تجريبية
    test_queries = [
        "أريد بيتزا تونة وسط",
        "عايز كباب دجاج كبير",
        "طلب سلطة خضراء صغيرة"
    ]
    
    for i, arabic_query in enumerate(test_queries, 1):
        print(f"\n{i}. 🗣️  النص العربي: '{arabic_query}'")
        print("-" * 60)
        
        try:
            # طلب البحث
            search_url = f"{base_url}/search"
            
            headers = {
                'Content-Type': 'application/json'
            }
            
            payload = {
                'query': arabic_query
            }
            
            print(f"📤 إرسال طلب البحث إلى: {search_url}")
            
            # إرسال الطلب
            response = requests.post(search_url, 
                                   headers=headers, 
                                   json=payload, 
                                   timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"✅ استجابة ناجحة (Status: {response.status_code})")
                print(f"📊 النتائج: {len(result.get('results', []))} عنصر")
                
                # عرض النتائج
                for j, item in enumerate(result.get('results', [])[:3], 1):
                    name = item.get('Name', 'غير محدد')
                    ingredients = item.get('ingredients', 'غير محدد')
                    print(f"   {j}. 🍕 {name}")
                    print(f"      📝 المكونات: {ingredients}")
                
                # عرض معلومات إضافية
                if 'translation_info' in result:
                    trans_info = result['translation_info']
                    print(f"🌍 الترجمة: '{trans_info.get('original')}' → '{trans_info.get('translated')}'")
                
                if 'search_info' in result:
                    search_info = result['search_info']
                    print(f"🔍 البحث: {search_info.get('query')} في الحقول {search_info.get('fields')}")
                
            else:
                print(f"❌ خطأ في الطلب: {response.status_code}")
                print(f"📄 الرسالة: {response.text}")
                
        except Exception as e:
            print(f"❌ خطأ في الاتصال: {e}")
        
        print("-" * 60)
        time.sleep(2)  # فترة انتظار بين الطلبات
    
    print("\n" + "=" * 80)
    print("✅ انتهى اختبار نظام الترجمة والبحث")
    print("=" * 80)

def test_ragtools_endpoint():
    """اختبار endpoint RAG tools"""
    
    print("\n" + "=" * 80)
    print("🛠️  اختبار RAG Tools")
    print("=" * 80)
    
    base_url = "http://localhost:8765"
    
    try:
        # طلب قائمة الأدوات
        tools_url = f"{base_url}/tools"
        
        response = requests.get(tools_url, timeout=10)
        
        if response.status_code == 200:
            tools = response.json()
            print(f"✅ تم العثور على {len(tools)} أداة:")
            
            for tool in tools:
                name = tool.get('function', {}).get('name', 'غير محدد')
                description = tool.get('function', {}).get('description', 'لا يوجد وصف')
                print(f"   🔧 {name}: {description}")
        else:
            print(f"❌ خطأ في طلب الأدوات: {response.status_code}")
            
    except Exception as e:
        print(f"❌ خطأ في اختبار الأدوات: {e}")

def main():
    """الدالة الرئيسية"""
    
    print("🚀 بدء تحليل العمليات النهائي")
    print("🔗 الاتصال بـ localhost:8765")
    print("👁️  سيتم عرض جميع العمليات بالتفصيل")
    
    # اختبار الاتصال أولاً
    try:
        response = requests.get("http://localhost:8765", timeout=5)
        print(f"✅ التطبيق متاح (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ التطبيق غير متاح: {e}")
        return
    
    # تشغيل الاختبارات
    test_real_translation_flow()
    test_ragtools_endpoint()
    
    print("\n🎉 انتهى تحليل العمليات النهائي")

if __name__ == "__main__":
    main()
