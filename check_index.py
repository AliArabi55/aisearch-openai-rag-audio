import asyncio
import os
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.aio import SearchClient

# تحميل متغيرات البيئة
load_dotenv(dotenv_path="./app/backend/.env")

async def check_index_fields():
    """فحص حقول الفهرس المتاحة"""
    
    search_endpoint = os.environ.get("AZURE_SEARCH_ENDPOINT")
    search_index = os.environ.get("AZURE_SEARCH_INDEX")  
    search_key = os.environ.get("AZURE_SEARCH_API_KEY")
    
    print(f"🔍 فحص بنية الفهرس: {search_index}")
    print(f"   النقطة: {search_endpoint}")
    
    # إنشاء العميل
    credential = AzureKeyCredential(search_key)
    search_client = SearchClient(search_endpoint, search_index, credential)
    
    try:
        # جلب عنصر واحد لرؤية الحقول المتاحة
        search_results = await search_client.search(
            search_text="*",
            top=1
        )
        
        async for result in search_results:
            print("📋 الحقول المتاحة في الفهرس:")
            for key, value in result.items():
                print(f"   - {key}: {type(value).__name__} = {str(value)[:50]}...")
            break
            
    except Exception as e:
        print(f"❌ خطأ في فحص الفهرس: {e}")
    
    await search_client.close()

if __name__ == "__main__":
    asyncio.run(check_index_fields())
