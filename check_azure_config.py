import requests
import json

search_endpoint = 'https://neslst11mune.search.windows.net'
index_name = 'english22-index'
api_key = 'H8m1E7AhfXDBPQPXU0EV5pSjOqRBHRZzcd85rjJckdAzSeA6xr0d'

headers = {
    'Content-Type': 'application/json',
    'api-key': api_key
}

try:
    # Get index schema
    url = f'{search_endpoint}/indexes/{index_name}?api-version=2023-11-01'
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        index_data = response.json()
        semantic_configs = index_data.get('semanticSearch', {}).get('configurations', [])
        print('🔍 Semantic Configurations المتاحة:')
        for config in semantic_configs:
            print(f'   ✅ {config["name"]}')
        
        if not semantic_configs:
            print('❌ لا توجد Semantic Configurations')
            
        # Print all available fields
        fields = index_data.get('fields', [])
        print('\n📋 الحقول المتاحة:')
        for field in fields:
            print(f'   📄 {field["name"]} ({field["type"]})')
            
    else:
        print(f'❌ خطأ في الاستعلام: {response.status_code} - {response.text}')
        
except Exception as e:
    print(f'❌ خطأ في الاتصال: {e}')
