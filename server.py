import http.server
import socketserver
import json
import os
from pymongo import MongoClient

# --- الاتصال بقاعدة البيانات السحابية MongoDB ---
MONGO_URI = "mongodb+srv://glofr12gdf_db_user:iqZibU7xeVESsJTo@store.yovmlnq.mongodb.net/?appName=store"

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client['quiz_platform']
    questions_col = db['questions']
    results_col = db['results']
    print("تم الاتصال بـ MongoDB بنجاح!")
except Exception as e:
    print("خطأ في الاتصال بـ MongoDB:", e)

PORT = int(os.environ.get("PORT", 8080))

class MyHandler(http.server.SimpleHTTPRequestHandler):

    def do_GET(self):
        # 1. جلب الأسئلة من MongoDB
        if self.path in ['/questions', '/get_questions']:
            try:
                questions = list(questions_col.find({}, {'_id': 0}))
            except Exception as e:
                print("خطأ قراءة الأسئلة:", e)
                questions = []

            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(questions, ensure_ascii=False).encode('utf-8'))

        # 2. جلب إجابات ونتائج الطلاب للمشرف
        elif self.path in ['/submissions', '/get_submissions', '/results']:
            try:
                results = list(results_col.find({}, {'_id': 0}))
            except Exception as e:
                print("خطأ قراءة النتائج:", e)
                results = []

            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(results, ensure_ascii=False).encode('utf-8'))

        # 3. عرض الصفحات العادية (index.html, style.css, script.js)
        else:
            super().do_GET()

    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            # حفظ سؤال جديد
            if self.path in ['/add_question', '/questions']:
                if isinstance(data, dict):
                    data.pop('_id', None)
                    questions_col.insert_one(data)
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success"}).encode('utf-8'))

            # حفظ إجابة/نتيجة طالب جديدة
            elif self.path in ['/submit', '/submit_answer', '/submit_exam', '/submissions']:
                if isinstance(data, dict):
                    data.pop('_id', None)
                    results_col.insert_one(data)
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success"}).encode('utf-8'))

            else:
                self.send_response(404)
                self.end_headers()

        except Exception as e:
            print("خطأ في معالجة طلب POST:", e)
            self.send_response(500)
            self.end_headers()

# تشغيل السيرفر
with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
    print(f"السيرفر يعمل على المنفذ {PORT}")
    httpd.serve_forever()
