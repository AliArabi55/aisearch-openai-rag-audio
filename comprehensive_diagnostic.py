#!/usr/bin/env python3
"""
اختبار شامل للتطبيق والملفات الصوتية
Comprehensive test for app and audio files
"""
import os
import sys
from pathlib import Path

def check_audio_files():
    """فحص الملفات الصوتية"""
    print("🎵 فحص الملفات الصوتية...")
    
    audio_dir = Path(r"c:\Users\aliar\OneDrive\Documents\GitHub\aisearch-openai-rag-audio\app\backend\static\audio")
    
    required_files = ["Ran.mp3", "between.wav", "Nancy.wav"]
    
    print(f"📁 مجلد الصوت: {audio_dir}")
    print(f"📍 هل المجلد موجود؟ {audio_dir.exists()}")
    
    if audio_dir.exists():
        files = list(audio_dir.glob("*"))
        print(f"📋 الملفات الموجودة: {[f.name for f in files]}")
        
        for req_file in required_files:
            file_path = audio_dir / req_file
            if file_path.exists():
                size = file_path.stat().st_size
                print(f"✅ {req_file}: موجود ({size} بايت)")
            else:
                print(f"❌ {req_file}: غير موجود")
    else:
        print("❌ مجلد الصوت غير موجود")

def check_environment():
    """فحص متغيرات البيئة"""
    print("\n🔧 فحص متغيرات البيئة...")
    
    env_file = Path(r"c:\Users\aliar\OneDrive\Documents\GitHub\aisearch-openai-rag-audio\app\backend\.env")
    
    if env_file.exists():
        print("✅ ملف .env موجود")
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if "PORT=8766" in content:
                print("✅ المنفذ 8766 مُعرّف")
            else:
                print("❌ المنفذ غير مُعرّف أو خاطئ")
                
            if "AZURE_OPENAI_REALTIME_DEPLOYMENT=gpt-4o-mini-realtime-preview" in content:
                print("✅ Real-time deployment مُعرّف")
            else:
                print("❌ Real-time deployment غير مُعرّف")
    else:
        print("❌ ملف .env غير موجود")

def test_audio_creation():
    """اختبار إنشاء الملفات الصوتية"""
    print("\n🎵 اختبار إنشاء الملفات الصوتية...")
    
    try:
        # تشغيل سكريبت الإنشاء
        exec_path = Path(r"c:\Users\aliar\OneDrive\Documents\GitHub\aisearch-openai-rag-audio")
        os.chdir(exec_path)
        
        # استيراد وتشغيل الدالة
        sys.path.append(str(exec_path))
        
        # تنفيذ إنشاء الملفات
        exec(open("create_audio_files.py").read())
        
        print("✅ تم إنشاء الملفات الصوتية بنجاح")
        
    except Exception as e:
        print(f"❌ خطأ في إنشاء الملفات الصوتية: {e}")

def test_app_startup():
    """اختبار بدء التطبيق"""
    print("\n🚀 اختبار بدء التطبيق...")
    
    app_path = Path(r"c:\Users\aliar\OneDrive\Documents\GitHub\aisearch-openai-rag-audio\app\backend")
    
    if (app_path / "app.py").exists():
        print("✅ ملف app.py موجود")
        
        # فحص المكونات المطلوبة
        required_files = ["ragtools.py", "order_tools.py", "rtmt.py"]
        for req_file in required_files:
            if (app_path / req_file).exists():
                print(f"✅ {req_file}: موجود")
            else:
                print(f"❌ {req_file}: غير موجود")
    else:
        print("❌ ملف app.py غير موجود")

if __name__ == "__main__":
    print("="*60)
    print("🔍 تشخيص شامل للتطبيق والملفات الصوتية")
    print("="*60)
    
    check_environment()
    check_audio_files()
    test_audio_creation()
    check_audio_files()  # فحص مجدد بعد الإنشاء
    test_app_startup()
    
    print("\n"+"="*60)
    print("✅ انتهى التشخيص")
    print("="*60)
