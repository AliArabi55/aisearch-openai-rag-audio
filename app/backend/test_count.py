import asyncio
import os
from dotenv import load_dotenv
from azure.search.documents.aio import SearchClient
from azure.core.credentials import AzureKeyCredential

# تحميل متغيرات البيئة
load_dotenv('.env')

async def count_all_items():
    """حساب إجمالي العناصر في فهرس Azure Search"""
    
    # إعداد العميل
    client = SearchClient(
        endpoint=os.getenv('AZURE_SEARCH_ENDPOINT'),
        index_name=os.getenv('AZURE_SEARCH_INDEX'),
        credential=AzureKeyCredential(os.getenv('AZURE_SEARCH_API_KEY'))
    )
    
    try:
        # البحث عن جميع العناصر مع العد الكلي
        results = await client.search(
            search_text="*",
            include_total_count=True,
            top=1  # نحتاج فقط للعد، لا للنتائج
        )
        
        total_count = await results.get_count()
        print(f"🔢 العدد الكلي للعناصر في Azure Search: {total_count}")
        
        # عرض عينة من العناصر للتأكد
        print("\n📋 عينة من العناصر:")
        count = 0
        sample_results = await client.search(search_text="*", top=10)
        async for result in sample_results:
            count += 1
            print(f"  {count}. [ID:{result.get('ID')}] {result.get('Name')} - {result.get('Price')} جنيه")
            
    except Exception as e:
        print(f"❌ خطأ: {e}")
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(count_all_items())
