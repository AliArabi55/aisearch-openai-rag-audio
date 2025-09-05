#!/usr/bin/env python3
"""
Script to remove hardcoded secrets from all Python files
"""

import os
import re
import glob

def remove_secrets_from_file(file_path):
    """Remove hardcoded secrets from a Python file"""
    changes_made = False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Pattern to find Azure Search keys (typical format)
        azure_key_pattern = r'["\']H8m1E7AhfXDBPQPXU0EV5pSjOqRBHRZzcd85rjJckdAzSeA6xr0d["\']'
        if re.search(azure_key_pattern, content):
            content = re.sub(azure_key_pattern, 'os.getenv("AZURE_SEARCH_KEY")', content)
            changes_made = True
            print(f"🔧 Removed Azure Search key from: {file_path}")
        
        # Pattern to find other common secret patterns
        patterns_to_check = [
            (r'api_key\s*=\s*["\'][A-Za-z0-9+/=]{30,}["\']', 'api_key = os.getenv("AZURE_SEARCH_KEY")'),
            (r'search_key\s*=\s*["\'][A-Za-z0-9+/=]{30,}["\']', 'search_key = os.getenv("AZURE_SEARCH_KEY")'),
            (r'subscription_key\s*=\s*["\'][A-Za-z0-9+/=]{30,}["\']', 'subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY")'),
        ]
        
        for pattern, replacement in patterns_to_check:
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                changes_made = True
                print(f"🔧 Replaced hardcoded key in: {file_path}")
        
        if changes_made:
            # Add necessary imports if not present
            if 'import os' not in content and 'os.getenv' in content:
                content = 'import os\n' + content
            
            if 'from dotenv import load_dotenv' not in content and 'os.getenv' in content:
                content = content.replace('import os\n', 'import os\nfrom dotenv import load_dotenv\n\nload_dotenv()\n')
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ Updated: {file_path}")
        
        return changes_made
        
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False

def main():
    """Main function to process all Python files"""
    print("🔍 Scanning for hardcoded secrets...")
    
    # Find all Python files in the project
    python_files = []
    for root, dirs, files in os.walk('.'):
        # Skip hidden directories and virtual environments
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['venv', '.venv', '__pycache__', 'node_modules']]
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    total_changed = 0
    for file_path in python_files:
        if remove_secrets_from_file(file_path):
            total_changed += 1
    
    print(f"\n📊 Summary:")
    print(f"   Files scanned: {len(python_files)}")
    print(f"   Files modified: {total_changed}")
    
    if total_changed > 0:
        print(f"\n⚠️  Next steps:")
        print(f"   1. Verify your .env file contains: AZURE_SEARCH_KEY=your_actual_key")
        print(f"   2. Add .env to .gitignore if not already present")
        print(f"   3. Test your application to ensure it still works")
        print(f"   4. Commit these changes to remove secrets from git history")

if __name__ == "__main__":
    main()
