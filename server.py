import http.server
import socketserver
import json
import os
from urllib.parse import parse_qs

# --- الاتصال بقاعدة البيانات السحابية ---
MONGO_URI = "mongodb+srv://glofr12gdf_db_user:iqZibU7xeVESsJTo@store.yovmlnq.mongodb.net/?appName=store"

questions_col = None
results_col = None

try:
    from pymongo import MongoClient
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client['quiz_platform']
    questions_col = db['questions']
    results_col = db['results']
    print(">>> تم الاتصال بـ MongoDB بنجاح! <<<")
except Exception as e:
    print(">>> خطأ في الاتصال بقاعدة البيانات:", e)

PORT = int(os.environ.get("PORT", 8080))

class MyHandler(http.server.SimpleHTTPRequestHandler):

    def _set_cors_headers(self, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, DELETE')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()

    def do_OPTIONS(self):
        self._set_cors_headers(200)

    def do_GET(self):
        clean_path = self.path.split('?')[0].rstrip('/')

        # 1. اعتراض طلبات الأسئلة (حتى لو طلب ملف questions.json)
        if clean_path in ['/questions', '/get_questions', '/questions.json']:
            questions = []
            if questions_col is not None:
                try:
                    questions = list(questions_col.find({}, {'_id': 0}))
                except Exception as e:
                    print("خطأ قراءة الأسئلة:", e)
            self._set_cors_headers(200)
            self.wfile.write(json.dumps(questions, ensure_ascii=False).encode('utf-8'))

        # 2. اعتراض طلبات الإجابات (حتى لو طلب ملف submissions.json)
        elif clean_path in ['/submissions', '/get_submissions', '/results', '/submissions.json', '/answers.json', '/results.json']:
            results = []
            if results_col is not None:
                try:
                    results = list(results_col.find({}, {'_id': 0}))
                except Exception as e:
                    print("خطأ قراءة النتائج:", e)
            self._set_cors_headers(200)
            self.wfile.write(json.dumps(results, ensure_ascii=False).encode('utf-8'))

        # 3. عرض الموقع العادي
        else:
            super().do_GET()

    def do_POST(self):
        clean_path = self.path.split('?')[0].rstrip('/')
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            raw_body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else ""

            data = {}
            if raw_body:
                try:
                    data = json.loads(raw_body)
                except Exception:
                    parsed = parse_qs(raw_body)
                    data = {k: v[0] if len(v) == 1 else v for k, v in parsed.items()}

            # أ. إضافة سؤال جديد
            if clean_path in ['/add_question', '/questions', '/questions.json']:
                if questions_col is not None and data:
                    if isinstance(data, list):
                        questions_col.delete_many({})
                        clean_data = [{k:v for k,v in d.items() if k != '_id'} for d in data if isinstance(d, dict)]
                        if clean_data: questions_col.insert_many(clean_data)
                    elif isinstance(data, dict):
                        data.pop('_id', None)
                        questions_col.insert_one(data)
                self._set_cors_headers(200)
                self.wfile.write(json.dumps({"status": "success"}).encode('utf-8'))

            # ب. حذف سؤال
            elif 'delete' in clean_path:
                if questions_col is not None and isinstance(data, dict):
                    q_id = data.get('id') or data.get('text') or data.get('question')
                    if q_id:
                        questions_col.delete_one({"$or": [{"id": q_id}, {"text": q_id}, {"question": q_id}]})
                self._set_cors_headers(200)
                self.wfile.write(json.dumps({"status": "success"}).encode('utf-8'))

            # ج. الالتقاط الشامل والذكي لإجابات الطلاب
            else:
                if results_col is not None and data:
                    if isinstance(data, list):
                        # لو المتصفح أرسل قائمة كاملة
                        results_col.delete_many({})
                        clean_data = [{k:v for k,v in d.items() if k != '_id'} for d in data if isinstance(d, dict)]
                        if clean_data: results_col.insert_many(clean_data)
                    elif isinstance(data, dict):
                        # لو المتصفح أرسل إجابة واحدة
                        data.pop('_id', None)
                        results_col.insert_one(data)

                self._set_cors_headers(200)
                self.wfile.write(json.dumps({"status": "success"}).encode('utf-8'))

        except Exception as e:
            print("خطأ POST:", e)
            self._set_cors_headers(500)
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))

socketserver.TCPServer.allow_reuse_address = True

with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
    print(f"السيرفر يعمل بنجاح على المنفذ {PORT}")
    httpd.serve_forever()
