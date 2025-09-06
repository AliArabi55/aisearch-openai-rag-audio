import logging
import os
import sys
from pathlib import Path

# إعداد الترميز للنصوص العربية
import locale
locale.setlocale(locale.LC_ALL, '')

# تعيين ترميز UTF-8 للتيرمينال
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

from aiohttp import web
from azure.core.credentials import AzureKeyCredential
from azure.identity import AzureDeveloperCliCredential, DefaultAzureCredential
from dotenv import load_dotenv

from simple_ragtools import attach_simple_rag_tools
from rtmt import RTMiddleTier

# إعداد الـ logging مع دعم UTF-8
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("simple_voicerag")

async def create_app():
    print("🚀 بدء تطبيق مطعم سيركلز المبسط...")
    
    # تحميل المتغيرات
    load_dotenv()
    
    # إعداد البيانات
    llm_key = os.environ.get("AZURE_OPENAI_API_KEY")
    search_key = os.environ.get("AZURE_SEARCH_API_KEY")
    
    print(f"🔑 مفتاح OpenAI: {'✅ موجود' if llm_key else '❌ مفقود'}")
    print(f"🔍 مفتاح Search: {'✅ موجود' if search_key else '❌ مفقود'}")

    # إنشاء التطبيق
    app = web.Application()
    
    # إعداد RT Middle Tier
    llm_credential = AzureKeyCredential(llm_key)
    search_credential = AzureKeyCredential(search_key)
    
    print("🤖 إعداد Real-time Model...")
    rtmt = RTMiddleTier(
        credentials=llm_credential,
        endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        deployment=os.environ["AZURE_OPENAI_REALTIME_DEPLOYMENT"],
        voice_choice=os.environ.get("AZURE_OPENAI_REALTIME_VOICE_CHOICE") or "alloy"
    )
    
    # رسالة النظام المبسطة والواضحة
    rtmt.system_message = """
أنت موظف طلبات في مطعم سيركلز. 

قواعد مهمة جداً:
1. عندما تحصل على نتائج البحث، ستجد السعر موجود بوضوح
2. اذكر السعر دائماً للعميل: "البيتزا دي سعرها X جنيه"
3. لا تقل أبداً "السعر غير متاح" - السعر موجود دائماً في النتائج
4. استخدم search tool للبحث عن الأطعمة
5. اتكلم عامية مصرية بسيطة

مثال للرد:
عميل: "عايز بيتزا تونة وسط"
أنت: تستخدم search مع "tuna pizza medium"
النتيجة: "الاسم: Medium Tuna Pizza, السعر: 150 جنيه"
ردك: "بيتزا التونة الوسط عندنا بـ 150 جنيه. تحب تطلبها؟"

مهم جداً: استخدم السعر الموجود في نتائج البحث ولا تقل "غير متاح"
""".strip()

    print("🔧 ربط أدوات البحث...")
    attach_simple_rag_tools(
        rtmt,
        credentials=search_credential,
        search_endpoint=os.environ.get("AZURE_SEARCH_ENDPOINT"),
        search_index=os.environ.get("AZURE_SEARCH_INDEX")
    )

    # ربط الـ middleware
    rtmt.attach_to_app(app, "/realtime")

    # إعداد الملفات الثابتة
    current_directory = Path(__file__).parent
    
    # إنشاء صفحة HTML بسيطة
    html_content = """
<!DOCTYPE html>
<html dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>مطعم سيركلز - اختبار مبسط</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-align: center;
            padding: 50px;
            min-height: 100vh;
            margin: 0;
        }
        h1 {
            font-size: 3em;
            margin-bottom: 30px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .info {
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 15px;
            margin: 20px auto;
            max-width: 600px;
            backdrop-filter: blur(10px);
        }
        .status {
            font-size: 1.2em;
            margin: 10px 0;
        }
        .success { color: #4CAF50; }
        .error { color: #f44336; }
    </style>
</head>
<body>
    <h1>🍕 مطعم سيركلز - تطبيق مبسط</h1>
    
    <div class="info">
        <h2>معلومات التطبيق</h2>
        <div class="status">✅ Real-time Model: نشط</div>
        <div class="status">✅ Azure AI Search: متصل</div>
        <div class="status">✅ أدوات البحث: جاهزة</div>
    </div>
    
    <div class="info">
        <h2>اختبار المحادثة</h2>
        <p>استخدم تطبيق الهاتف أو أي RT client للاتصال بـ:</p>
        <p><strong>ws://localhost:8767/realtime</strong></p>
    </div>
    
    <div class="info">
        <h2>أمثلة للاختبار</h2>
        <p>"عايز بيتزا تونة وسط"</p>
        <p>"إيه عندكم في البيتزا؟"</p>
        <p>"عايز برجر دبل"</p>
    </div>
</body>
</html>
"""
    
    # إنشاء مجلد static
    static_dir = current_directory / 'static'
    static_dir.mkdir(exist_ok=True)
    
    # كتابة ملف HTML
    with open(static_dir / 'index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    app.add_routes([web.get('/', lambda _: web.FileResponse(static_dir / 'index.html'))])
    app.router.add_static('/', path=static_dir, name='static')
    
    print("✅ التطبيق جاهز!")
    return app

if __name__ == "__main__":
    host = os.environ.get("HOST", "localhost")
    port = int(os.environ.get("PORT", 8767))
    print(f"🌟 تشغيل التطبيق على: http://{host}:{port}")
    web.run_app(create_app(), host=host, port=port)
