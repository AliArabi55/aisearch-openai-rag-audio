"""
مسح الذاكرة المؤقتة لحل مشكلة الأسعار الخاطئة
"""
import sys
import os

# إضافة مسار backend
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app', 'backend'))

# import ragtools
import importlib.util
spec = importlib.util.spec_from_file_location("ragtools", os.path.join(os.path.dirname(__file__), 'app', 'backend', 'ragtools.py'))
ragtools = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ragtools)

print("🗑️ مسح الذاكرة المؤقتة...")
ragtools.clear_cache()
print("✅ تم مسح الذاكرة المؤقتة بنجاح")

# عرض حالة الذاكرة 
print(f"📊 حالة الذاكرة المؤقتة: {len(ragtools.SEARCH_CACHE)} عنصر")
print(f"⏰ مدة انتهاء الصلاحية: {ragtools.CACHE_EXPIRY_MINUTES} دقيقة")

print("\n🎯 الآن جرب البحث مرة أخرى في Real-time للحصول على الأسعار الصحيحة")
