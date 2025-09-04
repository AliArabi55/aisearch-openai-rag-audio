"""
🔧 نسخة مؤقتة من التطبيق مع محاكي Real-time
=============================================
"""
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
from dotenv import load_dotenv

# استيراد المحاكي المؤقت
from rtmt_mockup import add_mockup_to_app

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
    # تحميل إعدادات .env
    load_dotenv(Path(__file__).parent / "app" / "backend" / ".env")
    
    app = web.Application()
    
    # إضافة الملفات الثابتة
    current_directory = Path(__file__).parent / "app" / "backend"
    app.router.add_static("/", path=current_directory / "static", name="ui")
    app.router.add_static('/assets', path=current_directory / "static/assets", name='assets')
    
    # إضافة المحاكي المؤقت
    mockup = add_mockup_to_app(app)
    
    logger.info("🚀 التطبيق جاهز مع المحاكي المؤقت")
    logger.info("🌐 الصفحة الرئيسية: http://localhost:8765")
    logger.info("🔧 صفحة الاختبار: http://localhost:8765/test")
    
    return app

if __name__ == "__main__":
    import aiohttp.web as web
    
    host = os.environ.get("HOST", "localhost")
    port = int(os.environ.get("PORT", 8765))
    
    logger.info(f"🌐 بدء تشغيل الخادم على {host}:{port}")
    web.run_app(create_app(), host=host, port=port)
