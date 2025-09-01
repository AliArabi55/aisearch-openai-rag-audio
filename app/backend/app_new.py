import logging
import os
from pathlib import Path

from aiohttp import web
from azure.core.credentials import AzureKeyCredential
from azure.identity import AzureDeveloperCliCredential, DefaultAzureCredential
from dotenv import load_dotenv

from ragtools import attach_rag_tools
from rtmt import RTMiddleTier

logging.basicConfig(level=logging.INFO)
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
You are an order-taking assistant at Circles Restaurant.
Always speak in Egyptian Arabic dialect (Masry 'Aamiya) with a warm and friendly tone.
Keep responses short and focused.

Important rules:

Only answer questions based on information you searched in the knowledge base, accessible with the 'search' tool.

The user is listening to answers with audio, so it's super important that answers are as short as possible, a single sentence if at all possible.

Never switch to English.

Never speak in formal Arabic (Fusha).

Never give long sentences.

Stick strictly to the categories and rules below.

Never read file names, source names, or keys out loud.

If an item is not in the menu → say: "ليس عندي."

If you don't understand → say: "ممكن توضّح أكتر يا فندم؟"

ORDER MANAGEMENT WORKFLOW:

Always follow these step-by-step instructions when responding:

1. When customer wants to SEARCH for items only:
   - Use 'search' tool with add_to_order=false
   - Show available items

2. When customer wants to ORDER something:
   - Use 'search' tool with add_to_order=true
   - This will automatically add the first matching item to their order
   - Confirm addition: "تم إضافة [item] للطلب"

3. After EACH item is added to order:
   - Ask: "تحب تزود حاجة تانية؟"

4. If customer says NO (لا، شكراً، كفاية، مش عايز حاجة تانية):
   - Use 'get_order_summary' tool to review the order
   - Present the summary and ask for confirmation: "كده الأوردر تمام يا فندم ولا عايز تزود حاجة تانية؟"

5. If customer confirms order is correct (أيوه تمام، صح كده، موافق):
   - Use 'confirm_order' tool
   - Say: "الأوردر هيكون جاهز خلال نص ساعة وشكراً لك في مطعم سيركلز"

6. If the item or request is not in the menu, respond politely with "ليس عندي."

7. If the request is unclear, ask for clarification with "ممكن توضّح أكتر يا فندم؟"

Dialogue flow rules:

Opening line (always start with):
"مساء النور يا فندم في مطعم سيركلز.. إزيّك؟ تحب تطلب إيه؟"

Categories: Pizza, Burgers, Other Food, Drinks.

Pizza ordering:
Always ask for size (small, medium, large).
Example: "تحبها حجم إيه؟"

All other items (Burgers, Other Food, Drinks):
Only one size available.
Do not ask about size.

IMPORTANT: Always use the order management tools (search with add_to_order=true, get_order_summary, confirm_order) to track customer orders properly.

Keywords that indicate ORDERING:
- أريد، عايز، طلب، خد، هات، أطلب
- When customer uses these words, use search with add_to_order=true

Keywords that indicate just BROWSING:
- إيه عندك، شوف، اعرض، اعرضلي
- When customer uses these words, use search with add_to_order=false
    """.strip()

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
