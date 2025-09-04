#!/usr/bin/env python3

"""اختبار ترجمة OpenAI مباشرة"""

import sys
import os
import asyncio

backend_path = os.path.join(os.path.dirname(__file__), 'app', 'backend')
sys.path.insert(0, backend_path)

async def test_openai_translation():
    print("🤖 اختبار ترجمة OpenAI...")
    
    try:
        from translation_utils import translate_with_openai
        
        arabic_text = "أريد بيتزا تونة وسط"
        print(f"النص العربي: {arabic_text}")
        
        translated = await translate_with_openai(arabic_text)
        print(f"ترجمة OpenAI: {translated}")
        
    except Exception as e:
        print(f"خطأ: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_openai_translation())
