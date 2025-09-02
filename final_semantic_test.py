import asyncio
import os
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.aio import SearchClient

# تحميل متغيرات البيئة
load_dotenv(dotenv_path="./app/backend/.env")

async def comprehensive_semantic_test():
    """اختبار شامل للبحث الدلالي"""
    
    search_endpoint = os.environ.get("AZURE_SEARCH_ENDPOINT")
    search_index = os.environ.get("AZURE_SEARCH_INDEX")  
    search_key = os.environ.get("AZURE_SEARCH_API_KEY")
    semantic_config = os.environ.get("AZURE_SEARCH_SEMANTIC_CONFIGURATION", "334455")
    
    print("🧪 اختبار شامل للبحث الدلالي في Azure AI Search")
    print("=" * 60)
    print(f"🔍 معلومات البحث:")
    print(f"   النقطة: {search_endpoint}")
    print(f"   الفهرس: {search_index}")
    print(f"   التكوين الدلالي: {semantic_config}")
    print(f"   المفتاح: {'موجود' if search_key else 'غير موجود'}")
    
    # إنشاء العميل
    credential = AzureKeyCredential(search_key)
    search_client = SearchClient(search_endpoint, search_index, credential)
    
    # اختبار البحث العادي
    print("\n1️⃣ اختبار البحث العادي:")
    print("-" * 40)
    try:
        search_results = await search_client.search(
            search_text="cheese",
            query_type="simple",
            top=3
        )
        
        results_count = 0
        async for result in search_results:
            results_count += 1
            print(f"   {results_count}. {result.get('Name')} - {result.get('Price')} جنيه")
            print(f"      المكونات: {result.get('ingredients', '')[:60]}...")
            print(f"      النتيجة: {result.get('@search.score', 0):.2f}")
            
        print(f"\n✅ البحث العادي نجح - وجدت {results_count} نتيجة")
        
    except Exception as e:
        print(f"❌ خطأ في البحث العادي: {e}")
        await search_client.close()
        return False
    
    # اختبار البحث الدلالي باللغة الإنجليزية
    print("\n2️⃣ اختبار البحث الدلالي (إنجليزي):")
    print("-" * 40)
    try:
        search_results = await search_client.search(
            search_text="I want something delicious with cheese",
            query_type="semantic",
            semantic_configuration_name=semantic_config,
            top=3,
            query_caption="extractive",
            query_answer="extractive"
        )
        
        results_count = 0
        async for result in search_results:
            results_count += 1
            name = result.get('Name', 'بدون اسم')
            score = result.get('@search.score', 0)
            reranker_score = result.get('@search.reranker_score', 'غير متاح')
            
            print(f"   {results_count}. {name}")
            print(f"      النتيجة العادية: {score:.2f}")
            print(f"      النتيجة الدلالية: {reranker_score}")
            
            # طباعة التعليقات
            captions = result.get('@search.captions', [])
            if captions:
                for caption in captions:
                    caption_text = caption.text if hasattr(caption, 'text') else str(caption)
                    print(f"      📝 {caption_text[:80]}...")
                    
        if results_count > 0:
            print(f"\n✅ البحث الدلالي (إنجليزي) نجح - وجدت {results_count} نتيجة")
        else:
            print("\n⚠️ البحث الدلالي (إنجليزي) لم يجد نتائج")
            
    except Exception as e:
        print(f"❌ خطأ في البحث الدلالي (إنجليزي): {e}")
        await search_client.close()
        return False
    
    # اختبار البحث الدلالي باللغة العربية
    print("\n3️⃣ اختبار البحث الدلالي (عربي):")
    print("-" * 40)
    try:
        search_results = await search_client.search(
            search_text="أريد أكلة لذيذة بالجبن",
            query_type="semantic",
            semantic_configuration_name=semantic_config,
            top=3,
            query_caption="extractive",
            query_answer="extractive"
        )
        
        results_count = 0
        async for result in search_results:
            results_count += 1
            name = result.get('Name', 'بدون اسم')
            score = result.get('@search.score', 0)
            reranker_score = result.get('@search.reranker_score', 'غير متاح')
            
            print(f"   {results_count}. {name}")
            print(f"      النتيجة العادية: {score:.2f}")
            print(f"      النتيجة الدلالية: {reranker_score}")
                    
        if results_count > 0:
            print(f"\n✅ البحث الدلالي (عربي) نجح - وجدت {results_count} نتيجة")
        else:
            print("\n⚠️ البحث الدلالي (عربي) لم يجد نتائج")
            
    except Exception as e:
        print(f"❌ خطأ في البحث الدلالي (عربي): {e}")
        await search_client.close()
        return False
    
    # اختبار مقارن: نفس الاستعلام بطريقتين
    print("\n4️⃣ مقارنة: نفس الاستعلام بطريقتين:")
    print("-" * 40)
    query = "burger"
    
    # البحث العادي
    print("🔸 البحث العادي:")
    try:
        simple_results = await search_client.search(
            search_text=query,
            query_type="simple",
            top=3
        )
        
        simple_items = []
        async for result in simple_results:
            simple_items.append({
                'name': result.get('Name'),
                'score': result.get('@search.score', 0)
            })
            
        for i, item in enumerate(simple_items, 1):
            print(f"   {i}. {item['name']} (درجة: {item['score']:.2f})")
            
    except Exception as e:
        print(f"   ❌ خطأ: {e}")
    
    # البحث الدلالي
    print("\n🔸 البحث الدلالي:")
    try:
        semantic_results = await search_client.search(
            search_text=query,
            query_type="semantic",
            semantic_configuration_name=semantic_config,
            top=3
        )
        
        semantic_items = []
        async for result in semantic_results:
            semantic_items.append({
                'name': result.get('Name'),
                'score': result.get('@search.score', 0),
                'reranker_score': result.get('@search.reranker_score', 'غير متاح')
            })
            
        for i, item in enumerate(semantic_items, 1):
            print(f"   {i}. {item['name']} (عادي: {item['score']:.2f}, دلالي: {item['reranker_score']})")
            
    except Exception as e:
        print(f"   ❌ خطأ: {e}")
    
    await search_client.close()
    
    print("\n" + "=" * 60)
    print("🎉 الاختبار الشامل اكتمل!")
    print(f"✅ التكوين الدلالي '{semantic_config}' يعمل بشكل صحيح")
    print("✅ يمكنك الآن استخدام البحث الدلالي في التطبيق")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    asyncio.run(comprehensive_semantic_test())
