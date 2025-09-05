#!/usr/bin/env python3
"""
إنشاء إعدادات البحث الدلالي لتحسين الأداء
Create Semantic Search Configuration for Better Performance
"""

import requests
import json
import os
from dotenv import load_dotenv

def create_semantic_configuration():
    """Create semantic search configuration"""
    load_dotenv()
    
    search_endpoint = os.getenv('AZURE_SEARCH_ENDPOINT')
    index_name = os.getenv('AZURE_SEARCH_INDEX_NAME')
    api_key = os.getenv('AZURE_SEARCH_API_KEY')
    
    if not all([search_endpoint, index_name, api_key]):
        print("❌ خطأ: متغيرات البيئة مفقودة!")
        return False
    
    headers = {
        'Content-Type': 'application/json',
        'api-key': api_key
    }
    
    try:
        print("🔍 فحص الفهرس الحالي...")
        
        # Get current index configuration
        url = f'{search_endpoint}/indexes/{index_name}?api-version=2023-11-01'
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            print(f"❌ خطأ في الحصول على الفهرس: {response.status_code}")
            print(response.text)
            return False
        
        index_data = response.json()
        print("✅ تم الحصول على الفهرس بنجاح")
        
        # Add semantic search configuration
        semantic_config = {
            "name": "english22-index-semantic-configuration",
            "prioritizedFields": {
                "titleField": {
                    "fieldName": "Name"
                },
                "prioritizedContentFields": [
                    {
                        "fieldName": "ingredients"
                    }
                ]
            }
        }
        
        # Update index with semantic search
        if 'semanticSearch' not in index_data:
            index_data['semanticSearch'] = {
                "configurations": []
            }
        
        # Check if configuration already exists
        existing_configs = index_data['semanticSearch']['configurations']
        config_exists = any(config['name'] == semantic_config['name'] for config in existing_configs)
        
        if not config_exists:
            index_data['semanticSearch']['configurations'].append(semantic_config)
            
            print("🔧 إضافة إعدادات البحث الدلالي...")
            
            # Update the index
            update_response = requests.put(url, headers=headers, json=index_data)
            
            if update_response.status_code == 200:
                print("✅ تم إنشاء إعدادات البحث الدلالي بنجاح!")
                return True
            else:
                print(f"❌ خطأ في تحديث الفهرس: {update_response.status_code}")
                print(update_response.text)
                return False
        else:
            print("✅ إعدادات البحث الدلالي موجودة مسبقاً")
            return True
            
    except Exception as e:
        print(f"❌ خطأ في إنشاء البحث الدلالي: {e}")
        return False

def test_semantic_search():
    """Test semantic search performance"""
    load_dotenv()
    
    search_endpoint = os.getenv('AZURE_SEARCH_ENDPOINT')
    index_name = os.getenv('AZURE_SEARCH_INDEX_NAME')
    api_key = os.getenv('AZURE_SEARCH_API_KEY')
    
    headers = {
        'Content-Type': 'application/json',
        'api-key': api_key
    }
    
    # Test semantic search query
    semantic_query = {
        "search": "chicken",
        "queryType": "semantic",
        "semanticConfiguration": "english22-index-semantic-configuration",
        "top": 5,
        "select": "ID,Name,ingredients,Price",
        "queryCaption": "extractive",
        "queryAnswer": "extractive"
    }
    
    try:
        print("🔍 اختبار البحث الدلالي...")
        
        url = f'{search_endpoint}/indexes/{index_name}/docs/search?api-version=2023-11-01'
        response = requests.post(url, headers=headers, json=semantic_query)
        
        if response.status_code == 200:
            results = response.json()
            print(f"✅ البحث الدلالي يعمل! عدد النتائج: {len(results.get('value', []))}")
            
            for result in results.get('value', [])[:3]:
                name = result.get('Name', 'بدون اسم')
                price = result.get('Price', 'غير محدد')
                print(f"   🍽️ {name} - {price} ريال")
                
            return True
        else:
            print(f"❌ خطأ في البحث الدلالي: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ خطأ في اختبار البحث الدلالي: {e}")
        return False

def main():
    """Main function"""
    print("🚀 إعداد البحث الدلالي لتحسين الأداء...")
    print("=" * 50)
    
    # Create semantic configuration
    if create_semantic_configuration():
        print("\n🧪 اختبار البحث الدلالي...")
        test_semantic_search()
    
    print("\n" + "=" * 50)
    print("🏁 انتهى إعداد البحث الدلالي!")

if __name__ == "__main__":
    main()
