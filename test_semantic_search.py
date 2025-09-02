#!/usr/bin/env python3
"""
اختبار البحث الدلالي في Azure AI Search
"""

import asyncio
import os
import sys
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.aio import SearchClient
from dotenv import load_dotenv

# تحميل متغيرات البيئة
env_path = os.path.join(os.path.dirname(__file__), "app", "backend", ".env")
print(f"📂 مسار ملف .env: {env_path}")
print(f"📂 هل الملف موجود: {os.path.exists(env_path)}")

# قراءة ملف .env مباشرة للتشخيص
if os.path.exists(env_path):
    with open(env_path, 'r', encoding='utf-8') as f:
        content = f.read()
        print(f"📝 محتوى ملف .env:")
        for i, line in enumerate(content.splitlines(), 1):
            if "SEMANTIC" in line:
                print(f"   السطر {i}: {repr(line)}")  # استخدام repr لإظهار المحتوى الخام

# تجربة تحميل dotenv مع خيارات مختلفة
from dotenv import load_dotenv
result = load_dotenv(env_path, override=True)
print(f"📥 نتيجة تحميل dotenv: {result}")

# قراءة المتغير مباشرة من الملف كبديل
semantic_config_from_file = None
if os.path.exists(env_path):
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip().startswith('AZURE_SEARCH_SEMANTIC_CONFIGURATION='):
                semantic_config_from_file = line.split('=', 1)[1].strip()
                break
                
print(f"🔧 قراءة مباشرة من الملف: {semantic_config_from_file}")

async def test_semantic_search():
    """اختبار البحث الدلالي"""
    
    # إعداد العميل
    search_endpoint = os.environ.get("AZURE_SEARCH_ENDPOINT")
    search_index = os.environ.get("AZURE_SEARCH_INDEX")  
    search_key = os.environ.get("AZURE_SEARCH_API_KEY")
    semantic_config = os.environ.get("AZURE_SEARCH_SEMANTIC_CONFIGURATION") or semantic_config_from_file or "334455"  # استخدام القيمة المحددة مباشرة
    
    print(f"🔍 معلومات البحث:")
    print(f"   النقطة: {search_endpoint}")
    print(f"   الفهرس: {search_index}")
    print(f"   التكوين الدلالي: {semantic_config}")
    print(f"   المفتاح: {'موجود' if search_key else 'غير موجود'}")
    
    # طباعة جميع متغيرات البيئة للتشخيص
    print(f"🔧 تشخيص متغيرات البيئة:")
    for key in ["AZURE_SEARCH_ENDPOINT", "AZURE_SEARCH_INDEX", "AZURE_SEARCH_API_KEY", "AZURE_SEARCH_SEMANTIC_CONFIGURATION"]:
        value = os.environ.get(key)
        print(f"   {key}: {'موجود' if value else 'غير موجود'} = {value}")
    
    print("-" * 50)
    
    if not all([search_endpoint, search_index, search_key, semantic_config]):
        print("❌ خطأ: بيانات البحث غير مكتملة!")
        return False
    
    # إنشاء العميل
    credential = AzureKeyCredential(search_key)
    search_client = SearchClient(search_endpoint, search_index, credential)
    
    # اختبار البحث العادي أولاً
    print("🔍 اختبار البحث العادي:")
    try:
        search_results = await search_client.search(
            search_text="Pizza",
            query_type="simple",
            top=3,
            select="ID,Name,ingredients,Price",
            search_fields="Name,ingredients"
        )
        
        count = 0
        async for result in search_results:
            count += 1
            print(f"   نتيجة {count}: {result.get('Name')} (ID: {result.get('ID')})")
            
        if count > 0:
            print(f"✅ البحث العادي يعمل: وجدت {count} نتيجة")
        else:
            print("❌ البحث العادي لا يجد نتائج")
            
    except Exception as e:
        print(f"❌ خطأ في البحث العادي: {e}")
        return False
    
    print("-" * 50)
    
    # اختبار البحث الدلالي
    print("🧠 اختبار البحث الدلالي:")
    try:
        search_results = await search_client.search(
            search_text="Pizza",
            query_type="semantic",
            semantic_configuration_name=semantic_config,
            top=3,
            select="ID,Name,ingredients,Price",
            search_fields="Name,ingredients"
        )
        
        count = 0
        async for result in search_results:
            count += 1
            reranker_score = result.get('@search.reranker_score')
            print(f"   نتيجة {count}: {result.get('Name')} (ID: {result.get('ID')})")
            if reranker_score:
                print(f"      درجة دلالية: {reranker_score:.3f}")
            
        if count > 0:
            print(f"✅ البحث الدلالي يعمل: وجدت {count} نتيجة")
            return True
        else:
            print("❌ البحث الدلالي لا يجد نتائج")
            return False
            
    except Exception as e:
        print(f"❌ خطأ في البحث الدلالي: {e}")
        print("   قد يكون التكوين الدلالي غير صحيح أو غير مفعل")
        return False
    
    finally:
        await search_client.close()

async def main():
    """الدالة الرئيسية"""
    print("🧪 اختبار البحث الدلالي في Azure AI Search")
    print("=" * 50)
    
    success = await test_semantic_search()
    
    print("=" * 50)
    if success:
        print("🎉 البحث الدلالي يعمل بشكل صحيح!")
    else:
        print("💥 هناك مشكلة في البحث الدلالي")
    
    return success

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n⏹️ تم إلغاء الاختبار")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 خطأ غير متوقع: {e}")
        sys.exit(1)
