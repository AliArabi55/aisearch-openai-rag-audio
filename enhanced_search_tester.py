#!/usr/bin/env python3
"""
واجهة ويب محسنة لاختبار Azure AI Search
تعرض مقارنة بين البحث العادي والدلالي
"""

import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs
from dotenv import load_dotenv
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

# تحميل متغيرات البيئة
load_dotenv("app/backend/.env")

class SearchTestHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        """صفحة الاختبار الرئيسية"""
        
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            html = self.get_test_page()
            self.wfile.write(html.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        """معالجة طلبات البحث"""
        
        if self.path == '/search':
            # قراءة البيانات
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                query = data.get('query', '')
                search_type = data.get('type', 'basic')
                
                # تنفيذ البحث
                results = self.perform_search(query, search_type)
                
                # إرسال النتائج
                self.send_response(200)
                self.send_header('Content-type', 'application/json; charset=utf-8')
                self.end_headers()
                
                response = json.dumps(results, ensure_ascii=False, indent=2)
                self.wfile.write(response.encode('utf-8'))
                
            except Exception as e:
                self.send_error_response(str(e))
        else:
            self.send_response(404)
            self.end_headers()
    
    def perform_search(self, query, search_type):
        """تنفيذ البحث"""
        
        # إعداد العميل
        search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
        search_key = os.getenv("AZURE_SEARCH_API_KEY")
        search_index = os.getenv("AZURE_SEARCH_INDEX")
        semantic_config = os.getenv("AZURE_SEARCH_SEMANTIC_CONFIGURATION")
        
        search_client = SearchClient(
            endpoint=search_endpoint,
            index_name=search_index,
            credential=AzureKeyCredential(search_key)
        )
        
        try:
            if search_type == 'semantic':
                # البحث الدلالي
                results = search_client.search(
                    search_text=query,
                    query_type="semantic",
                    semantic_configuration_name=semantic_config,
                    top=5,
                    include_total_count=True
                )
                
                search_results = []
                for result in results:
                    item = {
                        'title': result.get('Name', 'بلا عنوان'),
                        'content': result.get('ingredients', 'لا يوجد محتوى'),
                        'score': result.get('@search.score', 0),
                        'semantic_score': result.get('@search.reranker_score', 'غير متوفر'),
                        'id': result.get('ID', 'بلا معرف')
                    }
                    search_results.append(item)
                
                return {
                    'success': True,
                    'type': 'semantic',
                    'query': query,
                    'total_count': getattr(results, 'get_count', lambda: len(search_results))(),
                    'results': search_results,
                    'message': f'تم العثور على نتائج باستخدام البحث الدلالي'
                }
                
            else:
                # البحث العادي
                results = search_client.search(
                    search_text=query,
                    top=5,
                    include_total_count=True
                )
                
                search_results = []
                for result in results:
                    item = {
                        'title': result.get('Name', 'بلا عنوان'),
                        'content': result.get('ingredients', 'لا يوجد محتوى'),
                        'score': result.get('@search.score', 0),
                        'semantic_score': 'غير متوفر (بحث عادي)',
                        'id': result.get('ID', 'بلا معرف')
                    }
                    search_results.append(item)
                
                return {
                    'success': True,
                    'type': 'basic',
                    'query': query,
                    'total_count': getattr(results, 'get_count', lambda: len(search_results))(),
                    'results': search_results,
                    'message': f'تم العثور على نتائج باستخدام البحث العادي'
                }
                
        except Exception as e:
            return {
                'success': False,
                'type': search_type,
                'query': query,
                'error': str(e),
                'message': f'فشل البحث: {str(e)}'
            }
    
    def send_error_response(self, error_msg):
        """إرسال رد خطأ"""
        self.send_response(500)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()
        
        error_response = {
            'success': False,
            'error': error_msg
        }
        
        response = json.dumps(error_response, ensure_ascii=False)
        self.wfile.write(response.encode('utf-8'))
    
    def get_test_page(self):
        """صفحة اختبار البحث"""
        
        return '''<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>مختبر Azure AI Search المحسن</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 20px;
            min-height: 100vh;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #2c3e50, #34495e);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }
        
        .header p {
            margin: 10px 0 0 0;
            opacity: 0.8;
            font-size: 1.1em;
        }
        
        .search-section {
            padding: 40px;
        }
        
        .search-box {
            display: flex;
            gap: 15px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }
        
        .search-input {
            flex: 1;
            padding: 15px 20px;
            border: 2px solid #ddd;
            border-radius: 50px;
            font-size: 16px;
            min-width: 300px;
            transition: all 0.3s ease;
        }
        
        .search-input:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        .search-button {
            padding: 15px 30px;
            border: none;
            border-radius: 50px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            min-width: 150px;
        }
        
        .basic-search {
            background: #3498db;
            color: white;
        }
        
        .basic-search:hover {
            background: #2980b9;
            transform: translateY(-2px);
        }
        
        .semantic-search {
            background: #e74c3c;
            color: white;
        }
        
        .semantic-search:hover {
            background: #c0392b;
            transform: translateY(-2px);
        }
        
        .results-container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-top: 30px;
        }
        
        .result-section {
            border: 2px solid #eee;
            border-radius: 15px;
            overflow: hidden;
        }
        
        .result-header {
            padding: 15px 20px;
            font-weight: bold;
            font-size: 1.2em;
        }
        
        .basic-header {
            background: #3498db;
            color: white;
        }
        
        .semantic-header {
            background: #e74c3c;
            color: white;
        }
        
        .result-content {
            padding: 20px;
        }
        
        .result-item {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 15px;
            border-right: 4px solid #ddd;
        }
        
        .result-title {
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 8px;
            font-size: 1.1em;
        }
        
        .result-text {
            color: #666;
            line-height: 1.5;
            margin-bottom: 10px;
        }
        
        .result-scores {
            display: flex;
            gap: 15px;
            font-size: 0.9em;
        }
        
        .score {
            background: #ecf0f1;
            padding: 4px 8px;
            border-radius: 12px;
            font-weight: bold;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            color: #666;
            font-size: 1.1em;
        }
        
        .error {
            background: #ffebee;
            color: #c62828;
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
            border-right: 4px solid #c62828;
        }
        
        .success {
            background: #e8f5e8;
            color: #2e7d32;
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
            border-right: 4px solid #2e7d32;
        }
        
        .info-box {
            background: #e3f2fd;
            border: 1px solid #90caf9;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 30px;
        }
        
        .info-title {
            font-weight: bold;
            color: #1565c0;
            margin-bottom: 10px;
        }
        
        @media (max-width: 768px) {
            .results-container {
                grid-template-columns: 1fr;
            }
            
            .search-box {
                flex-direction: column;
            }
            
            .search-input {
                min-width: auto;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 مختبر Azure AI Search المحسن</h1>
            <p>مقارنة شاملة بين البحث العادي والبحث الدلالي</p>
        </div>
        
        <div class="search-section">
            <div class="info-box">
                <div class="info-title">📊 معلومات الاختبار:</div>
                <p><strong>الخادم:</strong> https://neslst11mune.search.windows.net</p>
                <p><strong>الفهرس:</strong> english22-index</p>
                <p><strong>المشكلة:</strong> البحث الدلالي لا يعمل لأن الإعداد غير موجود</p>
            </div>
            
            <div class="search-box">
                <input type="text" class="search-input" id="searchQuery" 
                       placeholder="أدخل كلمة البحث (مثل: pizza, burger, chicken)..."
                       value="pizza">
                
                <button class="search-button basic-search" onclick="performSearch('basic')">
                    🔍 بحث عادي
                </button>
                
                <button class="search-button semantic-search" onclick="performSearch('semantic')">
                    🧠 بحث دلالي
                </button>
            </div>
            
            <div class="results-container">
                <div class="result-section">
                    <div class="result-header basic-header">
                        🔍 نتائج البحث العادي
                    </div>
                    <div class="result-content" id="basicResults">
                        <div class="loading">اضغط "بحث عادي" لبدء البحث</div>
                    </div>
                </div>
                
                <div class="result-section">
                    <div class="result-header semantic-header">
                        🧠 نتائج البحث الدلالي
                    </div>
                    <div class="result-content" id="semanticResults">
                        <div class="loading">اضغط "بحث دلالي" لبدء البحث</div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        function performSearch(type) {
            const query = document.getElementById('searchQuery').value;
            const targetDiv = type === 'basic' ? 'basicResults' : 'semanticResults';
            
            if (!query.trim()) {
                alert('يرجى إدخال كلمة للبحث');
                return;
            }
            
            // عرض تحميل
            document.getElementById(targetDiv).innerHTML = '<div class="loading">🔄 جاري البحث...</div>';
            
            // تنفيذ البحث
            fetch('/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query: query,
                    type: type
                })
            })
            .then(response => response.json())
            .then(data => {
                displayResults(data, targetDiv);
            })
            .catch(error => {
                document.getElementById(targetDiv).innerHTML = 
                    `<div class="error">خطأ في الشبكة: ${error.message}</div>`;
            });
        }
        
        function displayResults(data, targetDiv) {
            let html = '';
            
            if (data.success) {
                html += `<div class="success">✅ ${data.message}</div>`;
                html += `<div style="margin: 10px 0; font-weight: bold;">إجمالي النتائج: ${data.total_count || data.results.length}</div>`;
                
                if (data.results && data.results.length > 0) {
                    data.results.forEach((result, index) => {
                        html += `
                            <div class="result-item">
                                <div class="result-title">${index + 1}. ${result.title}</div>
                                <div class="result-text">${result.content.substring(0, 200)}...</div>
                                <div class="result-scores">
                                    <span class="score">📊 نقاط البحث: ${result.score.toFixed(2)}</span>
                                    <span class="score">🧠 نقاط دلالية: ${result.semantic_score}</span>
                                </div>
                            </div>
                        `;
                    });
                } else {
                    html += '<div class="error">لم يتم العثور على نتائج</div>';
                }
            } else {
                html += `<div class="error">❌ فشل البحث: ${data.message || data.error}</div>`;
                
                if (data.type === 'semantic' && data.error.includes('Unknown semantic configuration')) {
                    html += `
                        <div style="margin-top: 15px; padding: 15px; background: #fff3cd; border-radius: 10px; border-right: 4px solid #ffc107;">
                            <strong>💡 المشكلة:</strong> إعداد البحث الدلالي غير موجود<br>
                            <strong>🔧 الحل:</strong> يجب إنشاء البحث الدلالي في Azure Portal<br>
                            <strong>📋 اسم الإعداد المطلوب:</strong> english22-semantic-configuration
                        </div>
                    `;
                }
            }
            
            document.getElementById(targetDiv).innerHTML = html;
        }
        
        // السماح بالبحث عند الضغط على Enter
        document.getElementById('searchQuery').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                performSearch('basic');
            }
        });
    </script>
</body>
</html>'''

def start_server():
    """تشغيل الخادم"""
    
    print("🚀 تهيئة مختبر Azure AI Search المحسن...")
    
    # التحقق من الإعدادات
    search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
    search_index = os.getenv("AZURE_SEARCH_INDEX")
    
    if not search_endpoint or not search_index:
        print("❌ خطأ: متغيرات البيئة غير موجودة")
        print("💡 تأكد من وجود ملف app/backend/.env")
        return
    
    print(f"✅ تم الاتصال بـ: {search_endpoint}")
    print(f"📋 الفهرس: {search_index}")
    print()
    print("🌟 مختبر AI Search المحسن جاهز!")
    print("🔗 افتح المتصفح على: http://localhost:8080")
    print("⏹️  اضغط Ctrl+C للإيقاف")
    print()
    
    try:
        server = HTTPServer(('localhost', 8080), SearchTestHandler)
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n⏹️  تم إيقاف الخادم بنجاح")

if __name__ == "__main__":
    start_server()
