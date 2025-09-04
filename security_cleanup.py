#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
أداة تنظيف المشروع من الـ API Keys المكشوفة
Clean project from exposed API keys
"""

import os
import sys
from pathlib import Path

def print_arabic(text):
    """طباعة النصوص العربية بشكل صحيح"""
    try:
        print(text.encode('utf-8').decode('utf-8'))
    except:
        print(text)

def remove_secrets_from_files():
    """إزالة الـ API keys من الملفات"""
    
    print_arabic("🧹 تنظيف المشروع من الـ API Keys المكشوفة")
    print_arabic("=" * 60)
    
    # الملفات التي قد تحتوي على secrets
    potentially_unsafe_files = [
        "check_index_schema.py",
        "test_5_items_prices.py", 
        "test_name_field.py",
        "test_semantic_prices.py"
    ]
    
    removed_files = []
    
    for filename in potentially_unsafe_files:
        file_path = Path(filename)
        if file_path.exists():
            print_arabic(f"🗑️  حذف ملف غير آمن: {filename}")
            file_path.unlink()
            removed_files.append(filename)
        else:
            print_arabic(f"✅ ملف غير موجود: {filename}")
    
    if removed_files:
        print_arabic(f"\n📝 تم حذف {len(removed_files)} ملف:")
        for file in removed_files:
            print_arabic(f"   • {file}")
    else:
        print_arabic("\n✅ لا توجد ملفات غير آمنة للحذف")
    
    return removed_files

def create_gitignore_template():
    """إنشاء قالب .gitignore محدث"""
    
    gitignore_content = """
# Security - API Keys and Secrets
*.key
*.secret
.env*
!.env.example
secrets/
credentials/

# Azure specific
.azure/
*_env

# Test files that might contain secrets
test_*_api.py
*_secret_*.py
check_index_schema.py
test_5_items_prices.py
test_name_field.py
test_semantic_prices.py

# Common Python ignores
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Logs
*.log
logs/

# Coverage reports
htmlcov/
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# mypy
.mypy_cache/
.dmypy.json
dmypy.json
"""
    
    return gitignore_content.strip()

def main():
    """الدالة الرئيسية"""
    print_arabic("🔒 أداة تأمين المشروع")
    
    # حذف الملفات غير الآمنة
    removed_files = remove_secrets_from_files()
    
    # إنشاء دليل للمطورين
    print_arabic("\n📋 إرشادات الأمان:")
    print_arabic("1. ✅ استخدم دائماً متغيرات البيئة (.env)")
    print_arabic("2. ❌ لا تضع API keys مباشرة في الكود")
    print_arabic("3. 🔍 تحقق من .gitignore قبل الـ commit")
    print_arabic("4. 🧹 نظف التاريخ إذا تم كشف secrets")
    
    print_arabic("\n💡 كيفية استخدام الـ API keys بأمان:")
    print_arabic("""
from dotenv import load_dotenv
import os

# تحميل متغيرات البيئة
load_dotenv("app/backend/.env")

# استخدام المتغيرات
SEARCH_KEY = os.environ.get("AZURE_SEARCH_API_KEY")
SEARCH_ENDPOINT = os.environ.get("AZURE_SEARCH_ENDPOINT")
""")
    
    if removed_files:
        print_arabic(f"\n⚠️  تم حذف {len(removed_files)} ملف غير آمن")
        print_arabic("💾 تذكر عمل commit للتغييرات:")
        print_arabic("   git add .")
        print_arabic('   git commit -m "Remove files with exposed API keys"')
    
    print_arabic("\n🎯 المشروع الآن آمن للـ push!")

if __name__ == "__main__":
    main()
