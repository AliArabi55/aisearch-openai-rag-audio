#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
واجهة ويب بسيطة لاختبار Azure AI Search
Simple Web Interface for Testing Azure AI Search
"""

import asyncio
import os
import sys
import json
from aiohttp import web, web_runner
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

# إعداد الترميز للنصوص العربية
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

class AISearchWebTester:
    def __init__(self):
        # تحميل متغيرات البيئة
        load_dotenv("app/backend/.env")
        
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
        
        print(f"✅ AI Search Tester initialized")
        print(f"🔗 Endpoint: {self.search_endpoint}")
        print(f"📋 Index: {self.search_index}")
        print(f"🧠 Semantic Config: {self.semantic_config}")

    async def basic_search(self, query):
        """البحث الأساسي"""
        try:
            results = self.search_client.search(
                search_text=query,
                top=10,
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

    async def semantic_search(self, query):
        """البحث الدلالي"""
        try:
            results = self.search_client.search(
                search_text=query,
                top=10,
                select=["ID", "Name", "ingredients", "Price"],
                query_type="semantic",
                semantic_configuration_name=self.semantic_config,
                query_caption="extractive"
            )
            
            items = []
            for result in results:
                # استخراج الـ captions
                captions = []
                if hasattr(result, "@search.captions") and result.get("@search.captions"):
                    for caption in result["@search.captions"]:
                        captions.append(caption.get("text", "") or caption.get("highlights", ""))
                
                items.append({
                    "id": result.get("ID"),
                    "name": result.get("Name"),
                    "ingredients": result.get("ingredients"),
                    "price": result.get("Price"),
                    "score": getattr(result, "@search.score", None),
                    "reranker_score": getattr(result, "@search.reranker_score", None),
                    "captions": captions
                })
            
            return {"success": True, "results": items, "count": len(items)}
            
        except Exception as e:
            return {"success": False, "error": str(e), "results": []}

    async def search_handler(self, request):
        """معالج طلبات البحث"""
        try:
            data = await request.json()
            query = data.get("query", "")
            search_type = data.get("type", "basic")  # basic or semantic
            
            if not query.strip():
                return web.json_response({
                    "success": False,
                    "error": "Query cannot be empty"
                })
            
            if search_type == "semantic":
                result = await self.semantic_search(query)
            else:
                result = await self.basic_search(query)
            
            return web.json_response(result)
            
        except Exception as e:
            return web.json_response({
                "success": False,
                "error": str(e)
            })

    def create_app(self):
        """إنشاء تطبيق الويب"""
        app = web.Application()
        
        # إعداد المسارات
        app.router.add_post('/search', self.search_handler)
        app.router.add_get('/', self.home_handler)
        
        return app
    
    async def home_handler(self, request):
        """صفحة الرئيسية"""
        html_content = f"""
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>مختبر Azure AI Search</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Arial', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            direction: rtl;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(45deg, #ff6b6b, #ee5a24);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header p {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        
        .search-section {{
            padding: 40px;
        }}
        
        .search-container {{
            display: flex;
            gap: 15px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }}
        
        .search-input {{
            flex: 1;
            min-width: 300px;
            padding: 15px 20px;
            font-size: 1.1em;
            border: 2px solid #ddd;
            border-radius: 10px;
            outline: none;
            transition: all 0.3s;
        }}
        
        .search-input:focus {{
            border-color: #667eea;
            box-shadow: 0 0 10px rgba(102, 126, 234, 0.3);
        }}
        
        .search-buttons {{
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }}
        
        .btn {{
            padding: 15px 25px;
            font-size: 1em;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s;
            font-weight: bold;
        }}
        
        .btn-basic {{
            background: #74b9ff;
            color: white;
        }}
        
        .btn-basic:hover {{
            background: #0984e3;
            transform: translateY(-2px);
        }}
        
        .btn-semantic {{
            background: #a29bfe;
            color: white;
        }}
        
        .btn-semantic:hover {{
            background: #6c5ce7;
            transform: translateY(-2px);
        }}
        
        .examples {{
            margin: 30px 0;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
        }}
        
        .examples h3 {{
            color: #2d3436;
            margin-bottom: 15px;
        }}
        
        .example-tags {{
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }}
        
        .example-tag {{
            background: #74b9ff;
            color: white;
            padding: 8px 15px;
            border-radius: 20px;
            cursor: pointer;
            transition: all 0.3s;
            font-size: 0.9em;
        }}
        
        .example-tag:hover {{
            background: #0984e3;
            transform: scale(1.05);
        }}
        
        .results-container {{
            margin-top: 30px;
        }}
        
        .results-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding: 15px;
            background: #f1f2f6;
            border-radius: 8px;
        }}
        
        .results-count {{
            font-weight: bold;
            color: #2d3436;
        }}
        
        .search-type {{
            background: #00b894;
            color: white;
            padding: 5px 15px;
            border-radius: 15px;
            font-size: 0.9em;
        }}
        
        .result-item {{
            background: white;
            border: 1px solid #ddd;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 15px;
            transition: all 0.3s;
            position: relative;
        }}
        
        .result-item:hover {{
            transform: translateY(-3px);
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }}
        
        .result-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }}
        
        .result-name {{
            font-size: 1.3em;
            font-weight: bold;
            color: #2d3436;
        }}
        
        .result-price {{
            background: #00b894;
            color: white;
            padding: 8px 15px;
            border-radius: 20px;
            font-weight: bold;
        }}
        
        .result-ingredients {{
            color: #636e72;
            margin: 10px 0;
            line-height: 1.5;
        }}
        
        .result-meta {{
            display: flex;
            gap: 15px;
            margin-top: 15px;
            font-size: 0.9em;
        }}
        
        .meta-item {{
            background: #f8f9fa;
            padding: 5px 10px;
            border-radius: 5px;
            color: #636e72;
        }}
        
        .semantic-score {{
            background: #a29bfe;
            color: white;
        }}
        
        .captions {{
            background: #fdcb6e;
            color: #2d3436;
            margin-top: 10px;
            padding: 10px;
            border-radius: 5px;
            font-style: italic;
        }}
        
        .loading {{
            text-align: center;
            padding: 40px;
            color: #636e72;
        }}
        
        .spinner {{
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }}
        
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        
        .error {{
            background: #ff7675;
            color: white;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
        }}
        
        .info-panel {{
            background: #e17055;
            color: white;
            padding: 20px;
            text-align: center;
        }}
        
        .status-indicator {{
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-left: 10px;
        }}
        
        .status-working {{
            background: #00b894;
        }}
        
        .status-error {{
            background: #ff7675;
        }}
        
        @media (max-width: 768px) {{
            .search-container {{
                flex-direction: column;
            }}
            
            .search-buttons {{
                justify-content: center;
            }}
            
            .example-tags {{
                justify-content: center;
            }}
            
            .results-header {{
                flex-direction: column;
                gap: 10px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 مختبر Azure AI Search</h1>
            <p>اختبر البحث الأساسي والدلالي في مطعم سيركلز</p>
        </div>
        
        <div class="info-panel">
            <strong>الاتصال:</strong> {self.search_endpoint}
            <span class="status-indicator status-working"></span>
            <strong>الفهرس:</strong> {self.search_index}
            <span class="status-indicator status-working"></span>
            <strong>البحث الدلالي:</strong> {self.semantic_config or "غير متاح"}
            <span class="status-indicator {'status-working' if self.semantic_config else 'status-error'}"></span>
        </div>
        
        <div class="search-section">
            <div class="search-container">
                <input type="text" class="search-input" id="searchInput" placeholder="ابحث عن طعام... مثل: بيتزا تونة، برجر لحمة، فراخ">
                <div class="search-buttons">
                    <button class="btn btn-basic" onclick="search('basic')">
                        🔍 بحث أساسي
                    </button>
                    <button class="btn btn-semantic" onclick="search('semantic')">
                        🧠 بحث دلالي
                    </button>
                </div>
            </div>
            
            <div class="examples">
                <h3>🍽️ أمثلة للبحث:</h3>
                <div class="example-tags">
                    <span class="example-tag" onclick="setQuery('pizza tuna')">pizza tuna</span>
                    <span class="example-tag" onclick="setQuery('بيتزا تونة')">بيتزا تونة</span>
                    <span class="example-tag" onclick="setQuery('chicken burger')">chicken burger</span>
                    <span class="example-tag" onclick="setQuery('برجر لحمة')">برجر لحمة</span>
                    <span class="example-tag" onclick="setQuery('seafood')">seafood</span>
                    <span class="example-tag" onclick="setQuery('calzone')">calzone</span>
                    <span class="example-tag" onclick="setQuery('كالزونى')">كالزونى</span>
                    <span class="example-tag" onclick="setQuery('crispy chicken')">crispy chicken</span>
                </div>
            </div>
            
            <div class="results-container" id="resultsContainer">
                <div style="text-align: center; padding: 40px; color: #636e72;">
                    👆 اختر كلمة من الأمثلة أو اكتب استعلامك الخاص
                </div>
            </div>
        </div>
    </div>

    <script>
        let currentSearchType = 'basic';

        function setQuery(query) {{
            document.getElementById('searchInput').value = query;
        }}

        function search(type) {{
            currentSearchType = type;
            const query = document.getElementById('searchInput').value.trim();
            
            if (!query) {{
                alert('يرجى إدخال نص للبحث');
                return;
            }}

            const resultsContainer = document.getElementById('resultsContainer');
            
            // عرض مؤشر التحميل
            resultsContainer.innerHTML = `
                <div class="loading">
                    <div class="spinner"></div>
                    <p>جاري البحث عن "${{query}}"...</p>
                </div>
            `;

            // إرسال طلب البحث
            fetch('/search', {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/json',
                }},
                body: JSON.stringify({{
                    query: query,
                    type: type
                }})
            }})
            .then(response => response.json())
            .then(data => {{
                displayResults(data, query, type);
            }})
            .catch(error => {{
                console.error('Error:', error);
                resultsContainer.innerHTML = `
                    <div class="error">
                        ❌ خطأ في الاتصال: ${{error.message}}
                    </div>
                `;
            }});
        }}

        function displayResults(data, query, searchType) {{
            const resultsContainer = document.getElementById('resultsContainer');
            
            if (!data.success) {{
                resultsContainer.innerHTML = `
                    <div class="error">
                        ❌ خطأ في البحث: ${{data.error}}
                    </div>
                `;
                return;
            }}

            const searchTypeLabel = searchType === 'semantic' ? '🧠 بحث دلالي' : '🔍 بحث أساسي';
            
            let html = `
                <div class="results-header">
                    <div class="results-count">
                        تم العثور على ${{data.count}} نتيجة لـ "${{query}}"
                    </div>
                    <div class="search-type">${{searchTypeLabel}}</div>
                </div>
            `;

            if (data.results.length === 0) {{
                html += `
                    <div style="text-align: center; padding: 40px; color: #636e72;">
                        😔 لم يتم العثور على نتائج لهذا البحث
                    </div>
                `;
            }} else {{
                data.results.forEach((item, index) => {{
                    html += `
                        <div class="result-item">
                            <div class="result-header">
                                <div class="result-name">${{item.name || 'غير محدد'}}</div>
                                <div class="result-price">${{item.price || 'غير محدد'}} جنيه</div>
                            </div>
                            <div class="result-ingredients">
                                🥘 المكونات: ${{item.ingredients || 'غير محدد'}}
                            </div>
                            <div class="result-meta">
                                <span class="meta-item">ID: ${{item.id}}</span>
                                <span class="meta-item">النقاط: ${{item.score ? item.score.toFixed(3) : 'N/A'}}</span>
                                ${{item.reranker_score ? `<span class="meta-item semantic-score">دلالي: ${{item.reranker_score.toFixed(3)}}</span>` : ''}}
                            </div>
                            ${{item.captions && item.captions.length > 0 ? `
                                <div class="captions">
                                    📝 مقاطع مطابقة: ${{item.captions.join(', ')}}
                                </div>
                            ` : ''}}
                        </div>
                    `;
                }});
            }}

            resultsContainer.innerHTML = html;
        }}

        // البحث عند الضغط على Enter
        document.getElementById('searchInput').addEventListener('keypress', function(e) {{
            if (e.key === 'Enter') {{
                search(currentSearchType);
            }}
        }});

        // تركيز على حقل البحث عند تحميل الصفحة
        window.onload = function() {{
            document.getElementById('searchInput').focus();
        }};
    </script>
</body>
</html>
        """
        
        return web.Response(text=html_content, content_type='text/html')

async def main():
    """الدالة الرئيسية"""
    try:
        tester = AISearchWebTester()
        app = tester.create_app()
        
        # إعداد الخادم
        runner = web_runner.AppRunner(app)
        await runner.setup()
        
        site = web_runner.TCPSite(runner, 'localhost', 8080)
        await site.start()
        
        print("🚀 مختبر AI Search يعمل على:")
        print("🔗 http://localhost:8080")
        print("⏹️  اضغط Ctrl+C للإيقاف")
        
        # الانتظار إلى الأبد
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n⏹️  تم إيقاف الخادم")
        finally:
            await runner.cleanup()
            
    except Exception as e:
        print(f"❌ خطأ: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
