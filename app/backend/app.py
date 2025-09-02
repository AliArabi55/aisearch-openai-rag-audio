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

from ragtools import attach_rag_tools
from rtmt import RTMiddleTier

# إعداد الـ logging مع دعم UTF-8
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("voicerag")

async def create_app():
    if not os.environ.get("RUNNING_IN_PRODUCTION"):
        logger.info("Running in development mode, loading from .env file")
        load_dotenv()

    llm_key = os.environ.get("AZURE_OPENAI_API_KEY")
    search_key = os.environ.get("AZURE_SEARCH_API_KEY")

    credential = None
    if not llm_key or not search_key:
        if tenant_id := os.environ.get("AZURE_TENANT_ID"):
            logger.info("Using AzureDeveloperCliCredential with tenant_id %s", tenant_id)
            credential = AzureDeveloperCliCredential(tenant_id=tenant_id, process_timeout=60)
        else:
            logger.info("Using DefaultAzureCredential")
            credential = DefaultAzureCredential()
    llm_credential = AzureKeyCredential(llm_key) if llm_key else credential
    search_credential = AzureKeyCredential(search_key) if search_key else credential
    
    app = web.Application()

    rtmt = RTMiddleTier(
        credentials=llm_credential,
        endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        deployment=os.environ["AZURE_OPENAI_REALTIME_DEPLOYMENT"],
        voice_choice=os.environ.get("AZURE_OPENAI_REALTIME_VOICE_CHOICE") or "alloy"
        )
    rtmt.system_message = """
أنت موظف طلبات في مطعم سيركلز. اتكلم عامية مصرية ودود.

قواعد:
- استخدم 'search' tool للبحث (يترجم تلقائياً)
- ردود قصيرة جداً (جملة واحدة)
- لا تتكلم إنجليزي أو فصحى مع العميل
- لو مش فاهم قول: "ممكن توضّح أكتر يا فندم؟"

الافتتاح: "مساء النور يا فندم في مطعم سيركلز.. تحب تطلب إيه؟"

سؤال عن المتاح: "عندنا بيتزا، كالزونى، برجر، وحاجات تانية حلوة. تحب إيه؟"

خطوات الطلب:
1. للبحث فقط: search مع add_to_order=false
2. للطلب: search مع add_to_order=true ثم قول "تم إضافة [item] بـ[price] جنيه للطلب"
3. بعد كل إضافة: "تحب تزود حاجة تانية؟"
4. لو قال لا: استخدم get_order_summary
5. لو وافق: استخدم confirm_order وقول "الأوردر جاهز خلال نص ساعة"

اسأل عن الحجم للبيتزا والكالزونى (كبير أو وسط)
اسأل عن النوع للبرجر (سنجل أو دبل)

كلمات الطلب: أريد، عايز، طلب، خد، هات
كلمات البحث: إيه عندك، شوف، اعرض
    """.strip()
    # 6. If the item or request is not in the menu, respond politely with "ليس عندي."


    attach_rag_tools(rtmt,
        credentials=search_credential,
        search_endpoint=os.environ.get("AZURE_SEARCH_ENDPOINT"),
        search_index=os.environ.get("AZURE_SEARCH_INDEX"),
        semantic_configuration=None,  # لا نستخدم البحث الدلالي
        identifier_field=os.environ.get("AZURE_SEARCH_IDENTIFIER_FIELD") or "ID",
        content_field=os.environ.get("AZURE_SEARCH_CONTENT_FIELD") or "ingredients",
        embedding_field="",  # لا نستخدم الـ embedding
        title_field=os.environ.get("AZURE_SEARCH_TITLE_FIELD") or "Name",
        use_vector_query=False  # إيقاف البحث الشعاعي
        )

    rtmt.attach_to_app(app, "/realtime")

    current_directory = Path(__file__).parent
    app.add_routes([web.get('/', lambda _: web.FileResponse(current_directory / 'static/index.html'))])
    app.router.add_static('/', path=current_directory / 'static', name='static')
    # إضافة route منفصل للملفات الصوتية
    app.router.add_static('/audio', path=current_directory / 'static/audio', name='audio')
    
    return app

if __name__ == "__main__":
    host = "localhost"
    port = 8765
    web.run_app(create_app(), host=host, port=port)
