import http.server
import socketserver
import json
import os
from urllib.parse import parse_qs

# --- 1. الاتصال بقاعدة البيانات MongoDB ---
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

    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(200)

    def do_GET(self):
        # 1. جلب الأسئلة للمنصة ولوحة المشرف
        if self.path in ['/questions', '/get_questions']:
            questions = []
            if questions_col is not None:
                try:
                    questions = list(questions_col.find({}, {'_id': 0}))
                except Exception as e:
                    print("خطأ قراءة الأسئلة:", e)

            self._set_headers(200)
            self.wfile.write(json.dumps(questions, ensure_ascii=False).encode('utf-8'))

        # 2. جلب إجابات ونتائج الطلاب للمشرف
        elif self.path in ['/submissions', '/get_submissions', '/results', '/api/submissions']:
            results = []
            if results_col is not None:
                try:
                    results = list(results_col.find({}, {'_id': 0}))
                except Exception as e:
                    print("خطأ قراءة النتائج:", e)

            self._set_headers(200)
            self.wfile.write(json.dumps(results, ensure_ascii=False).encode('utf-8'))

        # 3. عرض الصفحات العادية
        else:
            super().do_GET()

    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            raw_body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else ""

            # قراءة البيانات سواء كانت JSON أو Form Data
            data = {}
            if raw_body:
                try:
                    data = json.loads(raw_body)
                except Exception:
                    parsed = parse_qs(raw_body)
                    data = {k: v[0] if len(v) == 1 else v for k, v in parsed.items()}

            # إضافة سؤال جديد
            if self.path in ['/add_question', '/questions']:
                if data and questions_col is not None:
                    if isinstance(data, dict):
                        data.pop('_id', None)
                        questions_col.insert_one(data)

                self._set_headers(200)
                self.wfile.write(json.dumps({"status": "success"}).encode('utf-8'))

            # حفظ نتيجة/إجابة طالب
            elif self.path in ['/submit', '/submit_answer', '/submit_exam', '/submissions', '/api/submit']:
                if data and results_col is not None:
                    if isinstance(data, dict):
                        data.pop('_id', None)
                        results_col.insert_one(data)

                self._set_headers(200)
                self.wfile.write(json.dumps({"status": "success"}).encode('utf-8'))

            else:
                self._set_headers(404)
                self.wfile.write(json.dumps({"error": "Not found"}).encode('utf-8'))

        except Exception as e:
            print("خطأ أثناء استقبال الطلب:", e)
            self._set_headers(500)
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))

socketserver.TCPServer.allow_reuse_address = True

with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
    print(f"السيرفر يعمل الآن بنجاح على المنفذ {PORT}")
    httpd.serve_forever()
    
