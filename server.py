import http.server
import socketserver
import json
import os

PORT = 8080
QUESTIONS_FILE = 'questions.json'
SUBMISSIONS_FILE = 'submissions.json'

# دالة تحميل البيانات من الملفات
def load_data(filename):
    if not os.path.exists(filename):
        return []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

# دالة حفظ البيانات في الملفات
def save_data(filename, data):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

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
