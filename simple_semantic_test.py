import asyncio
import os
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.aio import SearchClient

# تحميل متغيرات البيئة
load_dotenv(dotenv_path="./app/backend/.env")

async def simple_semantic_test():
    """اختبار البحث الدلالي المبسط"""
    
    search_endpoint = os.environ.get("AZURE_SEARCH_ENDPOINT")
    search_index = os.environ.get("AZURE_SEARCH_INDEX")  
    search_key = os.environ.get("AZURE_SEARCH_API_KEY")
    semantic_config = os.environ.get("AZURE_SEARCH_SEMANTIC_CONFIGURATION", "334455")
    
    print(f"🔍 اختبار البحث الدلالي:")
    print(f"   النقطة: {search_endpoint}")
    print(f"   الفهرس: {search_index}")
    print(f"   التكوين الدلالي: {semantic_config}")
    
    # إنشاء العميل
    credential = AzureKeyCredential(search_key)
    search_client = SearchClient(search_endpoint, search_index, credential)
    
    # اختبار البحث العادي أولاً
    print("\n1️⃣ اختبار البحث العادي:")
    try:
        search_results = await search_client.search(
            search_text="burger",
            query_type="simple",
            top=2
        )
        
        results_count = 0
        async for result in search_results:
            results_count += 1
            print(f"   نتيجة {results_count}: {result.get('Name')} - السعر: {result.get('Price')} جنيه")
            
        print(f"✅ البحث العادي نجح - وجدت {results_count} نتيجة")
        
    except Exception as e:
        print(f"❌ خطأ في البحث العادي: {e}")
        await search_client.close()
        return False
    
    # اختبار البحث الدلالي
    print("\n2️⃣ اختبار البحث الدلالي:")
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
            
            print(f"   نتيجة {results_count}: {name}")
            print(f"      النتيجة العادية: {score:.2f}")
            print(f"      النتيجة الدلالية: {reranker_score}")
            
            # طباعة التعليقات إن وجدت
            captions = result.get('@search.captions', [])
            if captions:
                print(f"      عدد التعليقات: {len(captions)}")
                for i, caption in enumerate(captions):
                    caption_text = caption.text if hasattr(caption, 'text') else str(caption)
                    print(f"      تعليق {i+1}: {caption_text[:100]}...")
                    
        if results_count > 0:
            print(f"✅ البحث الدلالي نجح - وجدت {results_count} نتيجة")
        else:
            print("⚠️ البحث الدلالي لم يجد نتائج")
            
    except Exception as e:
        print(f"❌ خطأ في البحث الدلالي: {e}")
        await search_client.close()
        return False
    
    await search_client.close()
    print("\n🎉 الاختبار اكتمل بنجاح!")
    return True

if __name__ == "__main__":
    asyncio.run(simple_semantic_test())
