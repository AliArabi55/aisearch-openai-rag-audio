#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
واجهة اختبار AI Search البسيطة
Simple AI Search Testing Interface
"""

from aiohttp import web
import aiohttp
import json
import os
import sys
from pathlib import Path
import asyncio

# إعداد الترميز للنصوص العربية
import locale
locale.setlocale(locale.LC_ALL, '')

if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv("app/backend/.env")

class AISearchTester:
    def __init__(self):
        self.search_endpoint = os.environ.get("AZURE_SEARCH_ENDPOINT")
        self.search_key = os.environ.get("AZURE_SEARCH_API_KEY")
        self.search_index = os.environ.get("AZURE_SEARCH_INDEX")
        self.semantic_config = os.environ.get("AZURE_SEARCH_SEMANTIC_CONFIGURATION")
        
        if not all([self.search_endpoint, self.search_key, self.search_index]):
            raise ValueError("Missing required Azure Search configuration")
        
        self.credential = AzureKeyCredential(self.search_key)
        self.search_client = SearchClient(
            endpoint=self.search_endpoint,
            index_name=self.search_index,
            credential=self.credential
        )
    
    async def search_basic(self, query, top=5):
        """بحث أساسي"""
        try:
            results = self.search_client.search(
                search_text=query,
                top=top,
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
            
            return {
                "type": "basic",
                "query": query,
                "results": items,
                "count": len(items)
            }
            
        except Exception as e:
            return {"error": str(e), "type": "basic"}
    
    async def search_semantic(self, query, top=5):
        """بحث دلالي"""
        try:
            if not self.semantic_config:
                return {"error": "Semantic configuration not found", "type": "semantic"}
            
            results = self.search_client.search(
                search_text=query,
                top=top,
                select=["ID", "Name", "ingredients", "Price"],
                query_type="semantic",
                semantic_configuration_name=self.semantic_config,
                query_caption="extractive",
                query_answer="extractive"
            )
            
            items = []
            for result in results:
                # استخراج الـ captions
                captions = []
                if hasattr(result, "@search.captions"):
                    for caption in result["@search.captions"]:
                        captions.append({
                            "text": caption.get("text", ""),
                            "highlights": caption.get("highlights", "")
                        })
                
                items.append({
                    "id": result.get("ID"),
                    "name": result.get("Name"),
                    "ingredients": result.get("ingredients"), 
                    "price": result.get("Price"),
                    "score": getattr(result, "@search.score", None),
                    "reranker_score": getattr(result, "@search.reranker_score", None),
                    "captions": captions
                })
            
            return {
                "type": "semantic",
                "query": query,
                "results": items,
                "count": len(items)
            }
            
        except Exception as e:
            return {"error": str(e), "type": "semantic"}
    
    async def search_comparison(self, query, top=5):
        """مقارنة بين البحث الأساسي والدلالي"""
        basic_results = await self.search_basic(query, top)
        semantic_results = await self.search_semantic(query, top)
        
        return {
            "query": query,
            "basic": basic_results,
            "semantic": semantic_results
        }

# إنشاء متغير عام للـ tester
search_tester = None

async def init_search():
    """تهيئة AI Search"""
    global search_tester
    try:
        search_tester = AISearchTester()
        print("✅ تم تهيئة AI Search بنجاح")
        return True
    except Exception as e:
        print(f"❌ خطأ في تهيئة AI Search: {str(e)}")
        return False

async def handle_search(request):
    """معالج البحث"""
    if not search_tester:
        return web.json_response({"error": "AI Search not initialized"}, status=500)
    
    data = await request.json()
    query = data.get("query", "").strip()
    search_type = data.get("type", "basic")
    top = data.get("top", 5)
    
    if not query:
        return web.json_response({"error": "Query is required"}, status=400)
    
    try:
        if search_type == "basic":
            results = await search_tester.search_basic(query, top)
        elif search_type == "semantic":
            results = await search_tester.search_semantic(query, top)
        elif search_type == "comparison":
            results = await search_tester.search_comparison(query, top)
        else:
            return web.json_response({"error": "Invalid search type"}, status=400)
        
        return web.json_response(results)
        
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

async def handle_config(request):
    """عرض إعدادات AI Search"""
    config = {
        "endpoint": os.environ.get("AZURE_SEARCH_ENDPOINT"),
        "index": os.environ.get("AZURE_SEARCH_INDEX"),
        "semantic_config": os.environ.get("AZURE_SEARCH_SEMANTIC_CONFIGURATION"),
        "has_api_key": bool(os.environ.get("AZURE_SEARCH_API_KEY"))
    }
    return web.json_response(config)

def create_html_interface():
    """إنشاء واجهة HTML"""
    return """
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>اختبار AI Search</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        
        h1 {
            text-align: center;
            color: #667eea;
            margin-bottom: 30px;
            font-size: 2.5em;
        }
        
        .search-section {
            background: #f8f9fa;
            padding: 25px;
            border-radius: 10px;
            margin-bottom: 30px;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
            color: #555;
        }
        
        input[type="text"], select {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        
        input[type="text"]:focus, select:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .button-group {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        
        button {
            padding: 12px 25px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            cursor: pointer;
            transition: all 0.3s;
            font-weight: bold;
        }
        
        .btn-primary {
            background: #667eea;
            color: white;
        }
        
        .btn-secondary {
            background: #6c757d;
            color: white;
        }
        
        .btn-success {
            background: #28a745;
            color: white;
        }
        
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        
        .results {
            margin-top: 30px;
        }
        
        .result-type {
            margin-bottom: 30px;
            padding: 20px;
            border-radius: 10px;
            border-left: 5px solid #667eea;
        }
        
        .result-type h3 {
            margin-top: 0;
            color: #667eea;
        }
        
        .result-item {
            background: white;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 8px;
            border: 1px solid #eee;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        
        .result-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        
        .result-name {
            font-weight: bold;
            color: #333;
            font-size: 1.1em;
        }
        
        .result-score {
            background: #667eea;
            color: white;
            padding: 4px 8px;
            border-radius: 15px;
            font-size: 0.9em;
        }
        
        .result-details {
            color: #666;
            line-height: 1.6;
        }
        
        .captions {
            background: #fff3cd;
            padding: 10px;
            border-radius: 5px;
            margin-top: 10px;
            border-left: 3px solid #ffc107;
        }
        
        .error {
            background: #f8d7da;
            color: #721c24;
            padding: 15px;
            border-radius: 8px;
            margin-top: 20px;
        }
        
        .loading {
            text-align: center;
            padding: 20px;
            color: #667eea;
        }
        
        .config-info {
            background: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        
        .comparison {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-top: 20px;
        }
        
        @media (max-width: 768px) {
            .comparison {
                grid-template-columns: 1fr;
            }
            
            .button-group {
                flex-direction: column;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 اختبار AI Search</h1>
        
        <div id="config-info" class="config-info">
            <strong>📋 إعدادات الاتصال:</strong>
            <div id="config-details">جاري تحميل الإعدادات...</div>
        </div>
        
        <div class="search-section">
            <div class="form-group">
                <label for="query">🔤 استعلام البحث:</label>
                <input type="text" id="query" placeholder="مثال: بيتزا تونة، برجر، حلويات..." value="بيتزا تونة">
            </div>
            
            <div class="form-group">
                <label for="top">📊 عدد النتائج:</label>
                <select id="top">
                    <option value="3">3 نتائج</option>
                    <option value="5" selected>5 نتائج</option>
                    <option value="10">10 نتائج</option>
                </select>
            </div>
            
            <div class="button-group">
                <button class="btn-primary" onclick="searchBasic()">🔍 بحث أساسي</button>
                <button class="btn-secondary" onclick="searchSemantic()">🧠 بحث دلالي</button>
                <button class="btn-success" onclick="searchComparison()">⚖️ مقارنة</button>
            </div>
        </div>
        
        <div id="results" class="results"></div>
    </div>

    <script>
        // تحميل إعدادات الاتصال
        async function loadConfig() {
            try {
                const response = await fetch('/config');
                const config = await response.json();
                
                document.getElementById('config-details').innerHTML = `
                    <div><strong>Endpoint:</strong> ${config.endpoint || 'غير محدد'}</div>
                    <div><strong>Index:</strong> ${config.index || 'غير محدد'}</div>
                    <div><strong>Semantic Config:</strong> ${config.semantic_config || 'غير محدد'}</div>
                    <div><strong>API Key:</strong> ${config.has_api_key ? '✅ موجود' : '❌ مفقود'}</div>
                `;
            } catch (error) {
                document.getElementById('config-details').innerHTML = '❌ خطأ في تحميل الإعدادات';
            }
        }
        
        async function search(type) {
            const query = document.getElementById('query').value.trim();
            const top = parseInt(document.getElementById('top').value);
            
            if (!query) {
                alert('يرجى إدخال استعلام البحث');
                return;
            }
            
            const resultsDiv = document.getElementById('results');
            resultsDiv.innerHTML = '<div class="loading">🔄 جاري البحث...</div>';
            
            try {
                const response = await fetch('/search', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ query, type, top })
                });
                
                const data = await response.json();
                
                if (data.error) {
                    resultsDiv.innerHTML = `<div class="error">❌ ${data.error}</div>`;
                    return;
                }
                
                displayResults(data, type);
                
            } catch (error) {
                resultsDiv.innerHTML = `<div class="error">❌ خطأ في الاتصال: ${error.message}</div>`;
            }
        }
        
        function searchBasic() {
            search('basic');
        }
        
        function searchSemantic() {
            search('semantic');
        }
        
        function searchComparison() {
            search('comparison');
        }
        
        function displayResults(data, type) {
            const resultsDiv = document.getElementById('results');
            
            if (type === 'comparison') {
                displayComparisonResults(data);
            } else {
                displaySingleResults(data);
            }
        }
        
        function displaySingleResults(data) {
            const resultsDiv = document.getElementById('results');
            
            if (data.results.length === 0) {
                resultsDiv.innerHTML = '<div class="error">😔 لم يتم العثور على نتائج</div>';
                return;
            }
            
            const typeTitle = data.type === 'semantic' ? '🧠 نتائج البحث الدلالي' : '🔍 نتائج البحث الأساسي';
            
            let html = `
                <div class="result-type">
                    <h3>${typeTitle}</h3>
                    <p><strong>الاستعلام:</strong> "${data.query}" | <strong>عدد النتائج:</strong> ${data.count}</p>
                    ${data.results.map(result => formatResult(result)).join('')}
                </div>
            `;
            
            resultsDiv.innerHTML = html;
        }
        
        function displayComparisonResults(data) {
            const resultsDiv = document.getElementById('results');
            
            let html = `
                <h3>⚖️ مقارنة نتائج البحث</h3>
                <p><strong>الاستعلام:</strong> "${data.query}"</p>
                <div class="comparison">
                    <div class="result-type">
                        <h3>🔍 البحث الأساسي</h3>
                        ${data.basic.error ? `<div class="error">${data.basic.error}</div>` : 
                          data.basic.results.map(result => formatResult(result)).join('')}
                    </div>
                    <div class="result-type">
                        <h3>🧠 البحث الدلالي</h3>
                        ${data.semantic.error ? `<div class="error">${data.semantic.error}</div>` : 
                          data.semantic.results.map(result => formatResult(result)).join('')}
                    </div>
                </div>
            `;
            
            resultsDiv.innerHTML = html;
        }
        
        function formatResult(result) {
            const scoreInfo = result.reranker_score 
                ? `دلالي: ${result.reranker_score.toFixed(2)} | أساسي: ${result.score.toFixed(2)}`
                : result.score 
                ? result.score.toFixed(2)
                : 'غير متاح';
                
            const captions = result.captions && result.captions.length > 0
                ? `<div class="captions">
                     <strong>📝 مقاطع مطابقة:</strong><br>
                     ${result.captions.map(c => c.text || c.highlights).join('<br>')}
                   </div>`
                : '';
            
            return `
                <div class="result-item">
                    <div class="result-header">
                        <div class="result-name">${result.name || 'غير محدد'}</div>
                        <div class="result-score">${scoreInfo}</div>
                    </div>
                    <div class="result-details">
                        <div><strong>المكونات:</strong> ${result.ingredients || 'غير محدد'}</div>
                        <div><strong>السعر:</strong> ${result.price || 'غير محدد'} جنيه</div>
                        <div><strong>ID:</strong> ${result.id || 'غير محدد'}</div>
                    </div>
                    ${captions}
                </div>
            `;
        }
        
        // تحميل الإعدادات عند تحميل الصفحة
        window.onload = function() {
            loadConfig();
        };
        
        // Enter key support
        document.getElementById('query').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                searchBasic();
            }
        });
    </script>
</body>
</html>
    """

async def create_app():
    """إنشاء التطبيق"""
    # تهيئة AI Search
    search_ready = await init_search()
    
    if not search_ready:
        print("❌ فشل في تهيئة AI Search - تحقق من إعدادات .env")
        return None
    
    app = web.Application()
    
    # الروابط
    app.router.add_get('/', lambda request: web.Response(text=create_html_interface(), content_type='text/html'))
    app.router.add_post('/search', handle_search)
    app.router.add_get('/config', handle_config)
    
    return app

if __name__ == "__main__":
    def main():
        print("🚀 تشغيل واجهة اختبار AI Search...")
        print("🌐 افتح المتصفح على: http://localhost:9000")
        print("⏹️  اضغط Ctrl+C للإيقاف")
        
        async def init_and_run():
            app = await create_app()
            if app:
                return app
            else:
                print("❌ فشل في تشغيل التطبيق")
                return None
        
        # إنشاء event loop جديد
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            app = loop.run_until_complete(init_and_run())
            if app:
                web.run_app(app, host='localhost', port=9000)
        finally:
            loop.close()
    
    main()
