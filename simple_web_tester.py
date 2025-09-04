#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
واجهة ويب بسيطة ومستقرة لاختبار Azure AI Search
Stable Simple Web Interface for Testing Azure AI Search
"""

import os
import json
import threading
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
import time

class AISearchHandler(BaseHTTPRequestHandler):
    def __init__(self, search_client, *args, **kwargs):
        self.search_client = search_client
        super().__init__(*args, **kwargs)

    def do_GET(self):
        """معالج طلبات GET"""
        if self.path == '/':
            self.send_html_page()
        else:
            self.send_error(404)

    def do_POST(self):
        """معالج طلبات POST"""
        if self.path == '/search':
            self.handle_search_request()
        else:
            self.send_error(404)

    def send_html_page(self):
        """إرسال صفحة HTML الرئيسية"""
        html_content = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>مختبر Azure AI Search - مطعم سيركلز</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Arial', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            direction: rtl;
        }
        
        .container {
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(45deg, #ff6b6b, #ee5a24);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.2em;
            margin-bottom: 10px;
        }
        
        .search-section {
            padding: 30px;
        }
        
        .search-box {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        
        .search-input {
            flex: 1;
            min-width: 250px;
            padding: 12px 15px;
            font-size: 1.1em;
            border: 2px solid #ddd;
            border-radius: 8px;
            outline: none;
        }
        
        .search-input:focus {
            border-color: #667eea;
        }
        
        .btn {
            padding: 12px 20px;
            font-size: 1em;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s;
        }
        
        .btn-basic {
            background: #74b9ff;
            color: white;
        }
        
        .btn-basic:hover {
            background: #0984e3;
        }
        
        .btn-semantic {
            background: #a29bfe;
            color: white;
        }
        
        .btn-semantic:hover {
            background: #6c5ce7;
        }
        
        .examples {
            margin: 20px 0;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
        }
        
        .example-item {
            display: inline-block;
            background: #74b9ff;
            color: white;
            padding: 5px 12px;
            margin: 3px;
            border-radius: 15px;
            cursor: pointer;
            font-size: 0.9em;
        }
        
        .example-item:hover {
            background: #0984e3;
        }
        
        .results {
            margin-top: 20px;
        }
        
        .results-header {
            background: #f1f2f6;
            padding: 10px 15px;
            border-radius: 6px;
            margin-bottom: 15px;
            font-weight: bold;
        }
        
        .result-item {
            background: white;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 10px;
        }
        
        .result-name {
            font-size: 1.2em;
            font-weight: bold;
            color: #2d3436;
            margin-bottom: 5px;
        }
        
        .result-price {
            background: #00b894;
            color: white;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 0.9em;
            display: inline-block;
            margin-bottom: 8px;
        }
        
        .result-ingredients {
            color: #636e72;
            margin-bottom: 8px;
        }
        
        .result-meta {
            font-size: 0.8em;
            color: #636e72;
        }
        
        .loading {
            text-align: center;
            padding: 30px;
            color: #636e72;
        }
        
        .error {
            background: #ff7675;
            color: white;
            padding: 10px;
            border-radius: 6px;
            margin: 10px 0;
        }
        
        .status-bar {
            background: #e17055;
            color: white;
            padding: 10px;
            text-align: center;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 مختبر Azure AI Search</h1>
            <p>اختبار البحث في قائمة طعام مطعم سيركلز</p>
        </div>
        
        <div class="status-bar">
            <strong>الاتصال:</strong> نشط ✅ 
            <strong>الفهرس:</strong> english22-index ✅
            <strong>البحث الدلالي:</strong> متاح جزئياً ⚠️
        </div>
        
        <div class="search-section">
            <div class="search-box">
                <input type="text" class="search-input" id="searchInput" placeholder="ابحث عن طعام... مثل: pizza, burger, chicken">
                <button class="btn btn-basic" onclick="search('basic')">🔍 بحث أساسي</button>
                <button class="btn btn-semantic" onclick="search('semantic')">🧠 بحث دلالي</button>
            </div>
            
            <div class="examples">
                <strong>أمثلة:</strong>
                <span class="example-item" onclick="setQuery('pizza tuna')">pizza tuna</span>
                <span class="example-item" onclick="setQuery('chicken burger')">chicken burger</span>
                <span class="example-item" onclick="setQuery('seafood')">seafood</span>
                <span class="example-item" onclick="setQuery('calzone')">calzone</span>
                <span class="example-item" onclick="setQuery('beef')">beef</span>
                <span class="example-item" onclick="setQuery('crispy')">crispy</span>
            </div>
            
            <div class="results" id="results">
                <div style="text-align: center; padding: 30px; color: #636e72;">
                    👆 اختر مثالاً أو اكتب استعلامك
                </div>
            </div>
        </div>
    </div>

    <script>
        function setQuery(query) {
            document.getElementById('searchInput').value = query;
        }

        function search(type) {
            const query = document.getElementById('searchInput').value.trim();
            if (!query) {
                alert('يرجى إدخال نص للبحث');
                return;
            }

            const resultsDiv = document.getElementById('results');
            resultsDiv.innerHTML = '<div class="loading">🔍 جاري البحث...</div>';

            fetch('/search', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({query: query, type: type})
            })
            .then(response => response.json())
            .then(data => {
                displayResults(data, query, type);
            })
            .catch(error => {
                resultsDiv.innerHTML = '<div class="error">❌ خطأ في الاتصال</div>';
            });
        }

        function displayResults(data, query, type) {
            const resultsDiv = document.getElementById('results');
            
            if (!data.success) {
                resultsDiv.innerHTML = `<div class="error">❌ ${data.error}</div>`;
                return;
            }

            const typeLabel = type === 'semantic' ? '🧠 بحث دلالي' : '🔍 بحث أساسي';
            let html = `<div class="results-header">${typeLabel}: ${data.count} نتيجة لـ "${query}"</div>`;

            if (data.results.length === 0) {
                html += '<div style="text-align: center; padding: 20px;">😔 لا توجد نتائج</div>';
            } else {
                data.results.forEach(item => {
                    html += `
                        <div class="result-item">
                            <div class="result-name">${item.name || 'غير محدد'}</div>
                            <div class="result-price">${item.price || '0'} جنيه</div>
                            <div class="result-ingredients">🥘 ${item.ingredients || 'غير محدد'}</div>
                            <div class="result-meta">
                                ID: ${item.id} | النقاط: ${item.score ? item.score.toFixed(2) : 'N/A'}
                                ${item.reranker_score ? ` | دلالي: ${item.reranker_score.toFixed(2)}` : ''}
                            </div>
                        </div>
                    `;
                });
            }

            resultsDiv.innerHTML = html;
        }

        // البحث بالضغط على Enter
        document.getElementById('searchInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') search('basic');
        });
    </script>
</body>
</html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))

    def handle_search_request(self):
        """معالج طلب البحث"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            query = data.get('query', '')
            search_type = data.get('type', 'basic')
            
            if search_type == 'semantic':
                result = self.semantic_search(query)
            else:
                result = self.basic_search(query)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            error_result = {"success": False, "error": str(e), "results": []}
            self.send_response(500)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(error_result, ensure_ascii=False).encode('utf-8'))

    def basic_search(self, query):
        """البحث الأساسي"""
        try:
            results = self.search_client.search(
                search_text=query,
                top=8,
                select=["ID", "Name", "ingredients", "Price"]
            )
            
            items = []
            for result in results:
                items.append({
                    "id": result.get("ID"),
                    "name": result.get("Name"),
                    "ingredients": result.get("ingredients"),
                    "price": result.get("Price"),
                    "score": getattr(result, "@search.score", None)
                })
            
            return {"success": True, "results": items, "count": len(items)}
            
        except Exception as e:
            return {"success": False, "error": str(e), "results": []}

    def semantic_search(self, query):
        """البحث الدلالي (سيحاول ويعود للأساسي في حالة الخطأ)"""
        try:
            # محاولة البحث الدلالي
            results = self.search_client.search(
                search_text=query,
                top=8,
                select=["ID", "Name", "ingredients", "Price"],
                query_type="semantic",
                semantic_configuration_name="english22-semantic-configuration"
            )
            
            items = []
            for result in results:
                items.append({
                    "id": result.get("ID"),
                    "name": result.get("Name"),
                    "ingredients": result.get("ingredients"),
                    "price": result.get("Price"),
                    "score": getattr(result, "@search.score", None),
                    "reranker_score": getattr(result, "@search.reranker_score", None)
                })
            
            return {"success": True, "results": items, "count": len(items), "note": "semantic"}
            
        except Exception as e:
            # في حالة فشل البحث الدلالي، نعود للبحث الأساسي
            basic_result = self.basic_search(query)
            if basic_result["success"]:
                basic_result["note"] = f"البحث الدلالي فشل، تم استخدام البحث الأساسي: {str(e)[:50]}"
            return basic_result

def create_handler_class(search_client):
    """إنشاء فئة المعالج مع search_client"""
    class Handler(AISearchHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(search_client, *args, **kwargs)
    return Handler

def main():
    """الدالة الرئيسية"""
    print("🚀 تهيئة مختبر Azure AI Search...")
    
    # تحميل متغيرات البيئة
    load_dotenv("app/backend/.env")
    
    search_endpoint = os.environ.get("AZURE_SEARCH_ENDPOINT")
    search_key = os.environ.get("AZURE_SEARCH_API_KEY")
    search_index = os.environ.get("AZURE_SEARCH_INDEX")
    
    if not all([search_endpoint, search_key, search_index]):
        print("❌ خطأ: متغيرات البيئة مفقودة")
        return
    
    # إنشاء عميل البحث
    credential = AzureKeyCredential(search_key)
    search_client = SearchClient(
        endpoint=search_endpoint,
        index_name=search_index,
        credential=credential
    )
    
    print(f"✅ تم الاتصال بـ: {search_endpoint}")
    print(f"📋 الفهرس: {search_index}")
    
    # إنشاء الخادم
    handler_class = create_handler_class(search_client)
    server = HTTPServer(('localhost', 8080), handler_class)
    
    print("\n🌟 مختبر AI Search جاهز!")
    print("🔗 افتح المتصفح على: http://localhost:8080")
    print("⏹️  اضغط Ctrl+C للإيقاف\n")
    
    # فتح المتصفح تلقائياً
    def open_browser():
        time.sleep(1)
        webbrowser.open('http://localhost:8080')
    
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n⏹️  تم إيقاف الخادم بنجاح")
        server.shutdown()

if __name__ == "__main__":
    main()
