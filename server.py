from pymongo import MongoClient

# رابط الاتصال بقاعدة البيانات
MONGO_URI = "mongodb+srv://glofr12gdf_db_user:iqZibU7xeVESsJTo@store.yovmlnq.mongodb.net/?appName=store"

client = MongoClient(MONGO_URI)
db = client['quiz_platform']

# مجموعات البيانات للحفظ الدائم
questions_col = db['questions']  # حفظ الأسئلة
results_col = db['results']      # حفظ نتائج الطلاب
import http.server
import socketserver
import json
import os

PORT = 8080
QUESTIONS_FILE = 'questions.json'
SUBMISSIONS_FILE = 'submissions.json'

# --- حفظ وقراءة البيانات من قاعدة البيانات السحابية MongoDB ---

def load_data(filename):
    try:
        if filename == QUESTIONS_FILE:
            # جلب الأسئلة من MongoDB
            questions = list(questions_col.find({}, {'_id': 0}))
            return questions
        elif filename == SUBMISSIONS_FILE:
            # جلب إجابات الطلاب من MongoDB
            submissions = list(results_col.find({}, {'_id': 0}))
            return submissions
        return []
    except Exception as e:
        print("Error loading from MongoDB:", e)
        return []

def save_data(filename, data):
    try:
        if filename == QUESTIONS_FILE:
            # تحديث قائمة الأسئلة في MongoDB
            questions_col.delete_many({})  # تفريغ القديم
            if data:
                questions_col.insert_many(data)  # إضافة الأسئلة الجديدة
        elif filename == SUBMISSIONS_FILE:
            # تحديث قائمة الإجابات في MongoDB
            results_col.delete_many({})  # تفريغ القديم
            if data:
                results_col.insert_many(data)  # إضافة الإجابات الجديدة
    except Exception as e:
        print("Error saving to MongoDB:", e)
        
class NobleServer(socketserver.TCPServer):
    allow_reuse_address = True

class MyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        # عرض الصفحة الرئيسية
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            with open('index.html', 'rb') as f:
                self.wfile.write(f.read())
        # عرض ملف التصميم
        elif self.path.startswith('/style.css'):
            self.send_response(200)
            self.send_header('Content-Type', 'text/css')
            self.end_headers()
            with open('style.css', 'rb') as f:
                self.wfile.write(f.read())
        # عرض ملف الجافا سكريبت
        elif self.path.startswith('/script.js'):
            self.send_response(200)
            self.send_header('Content-Type', 'application/javascript')
            self.end_headers()
            with open('script.js', 'rb') as f:
                self.wfile.write(f.read())
        # جلب الأسئلة للمنصة وللأستاذ
        elif self.path == '/get_questions':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            questions = load_data(QUESTIONS_FILE)
            self.wfile.write(json.dumps(questions).encode('utf-8'))
        # جلب إجابات الطلاب للوحة التحكم
        elif self.path == '/get_submissions':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            submissions = load_data(SUBMISSIONS_FILE)
            self.wfile.write(json.dumps(submissions).encode('utf-8'))
        else:
            self.send_error(404, "File Not Found")

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        # 1. إضافة سؤال جديد
        if self.path == '/add_question':
            q = json.loads(post_data.decode('utf-8'))
            questions = load_data(QUESTIONS_FILE)
            questions.append(q)
            save_data(QUESTIONS_FILE, questions)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status":"success"}')
            
        # 2. تسليم إجابات الطالب
        elif self.path == '/submit_exam':
            submission = json.loads(post_data.decode('utf-8'))
            submissions = load_data(SUBMISSIONS_FILE)
            submissions.append(submission)
            save_data(SUBMISSIONS_FILE, submissions)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status":"success"}')
            
        # 3. حذف سؤال (الميزة الجديدة)
        elif self.path == '/delete_question':
            data = json.loads(post_data.decode('utf-8'))
            q_index = data.get('index')
            questions = load_data(QUESTIONS_FILE)
            
            if q_index is not None and 0 <= q_index < len(questions):
                questions.pop(q_index)
                save_data(QUESTIONS_FILE, questions)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status":"success"}')
        else:
            self.send_error(404, "Not Found")

print(f"🔥 منصة الأستاذ الخضر تعمل الآن على http://localhost:{PORT}")
with NobleServer(("", PORT), MyHandler) as httpd:
    httpd.serve_forever()
