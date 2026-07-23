let quizData = []; // قاعدة بيانات الأسئلة
let currentQuestion = 0;
let selectedOption = null;
let username = "";
let whatsappNumber = "";
let userAnswers = [];

let isQuizActive = false;
let warningCount = 0;
let leaveTime = null;
let countdownInterval = null;

// حماية الصفحة ومنع اللصق والنسخ
document.addEventListener('contextmenu', e => e.preventDefault());
document.addEventListener('copy', e => e.preventDefault());
document.addEventListener('paste', e => e.preventDefault());

// 1. جلب الأسئلة مع حماية كاملة ضد التجميد (حتى لو فاضية)
function fetchQuestions() {
    fetch('/get_questions')
    .then(res => {
        if (!res.ok) return [];
        return res.json();
    })
    .then(data => { 
        quizData = Array.isArray(data) ? data : []; 
        console.log("تم تحميل الأسئلة بنجاح عددهم:", quizData.length);
    })
    .catch(err => {
        console.log("السيرفر لسة فاضي أو يحتاج إضافة أسئلة.");
        quizData = [];
    });
}
fetchQuestions();

// 👑 2. دالة الدخول للوحة التحكم (معزولة وشغالة دائماً)
function goToAdmin() {
    const pass = prompt("الرجاء إدخال الرمز السري للأستاذ الخضر:");
    if (pass === "906748343") {
        document.getElementById('start-screen').classList.remove('active');
        document.getElementById('admin-screen').classList.add('active');
        loadStudentsSubmissions();
        loadAdminQuestions();
    } else if (pass !== null) {
        alert("❌ الرمز السري غير صحيح، حاول مرة أخرى.");
    }
}

function startQuiz() {
    username = document.getElementById('username').value.trim();
    whatsappNumber = document.getElementById('whatsapp').value.trim();
    
    if(username === "" || whatsappNumber === "") { alert("الرجاء إدخال الاسم ورقم الواتساب أولاً."); return; }
    if(!quizData || quizData.length === 0) { alert("⚠️ الاختبار فارغ حالياً! اطلب من الأستاذ الخضر الدخول للوحة التحكم وإضافة أسئلة أولاً."); return; }
    
    document.getElementById('user-display').innerText = "الممتحن: " + username;
    document.getElementById('start-screen').classList.remove('active');
    document.getElementById('quiz-screen').classList.add('active');
    
    isQuizActive = true;
    loadQuestion();
}

function loadQuestion() {
    selectedOption = null;
    if(document.getElementById('code-answer')) document.getElementById('code-answer').value = "";
    
    const currentQuiz = quizData[currentQuestion];
    document.getElementById('question-number').innerText = `السؤال ${currentQuestion + 1} من ${quizData.length}`;
    document.getElementById('question-text').innerText = currentQuiz.text;
    
    const progressPercent = (currentQuestion / quizData.length) * 100;
    document.getElementById('progress').style.width = progressPercent + "%";

    if(currentQuiz.type === "mcq") {
        document.getElementById('options-container').style.display = "block";
        document.getElementById('code-container').style.display = "none";
        
        const optionsContainer = document.getElementById('options-container');
        optionsContainer.innerHTML = "";
        currentQuiz.options.forEach((option, index) => {
            const button = document.createElement('button');
            button.innerText = option;
            button.classList.add('option-btn');
            button.onclick = () => {
                document.querySelectorAll('.option-btn').forEach(btn => btn.classList.remove('selected'));
                button.classList.add('selected');
                selectedOption = index;
            };
            optionsContainer.appendChild(button);
        });
    } else {
        document.getElementById('options-container').style.display = "none";
        document.getElementById('code-container').style.display = "block";
    }
}

function nextQuestion() {
    const currentQuiz = quizData[currentQuestion];
    let studentAnswer = "";
    
    if(currentQuiz.type === "mcq") {
        if(selectedOption === null) { alert("الرجاء اختيار إجابة!"); return; }
        studentAnswer = currentQuiz.options[selectedOption];
    } else {
        studentAnswer = document.getElementById('code-answer').value.trim();
        if(studentAnswer === "") { alert("الرجاء كتابة أو تصحيح الكود أولاً!"); return; }
    }
    
    userAnswers.push({ question: currentQuiz.text, type: currentQuiz.type, answer: studentAnswer });
    
    currentQuestion++;
    if(currentQuestion < quizData.length) {
        loadQuestion();
    } else {
        submitExam();
    }
}

function submitExam() {
    isQuizActive = false;
    document.getElementById('quiz-screen').classList.remove('active');
    document.getElementById('result-screen').classList.add('active');
    
    const payload = { username: username, whatsapp: whatsappNumber, answers: userAnswers };

    fetch('/submit_exam', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    }).then(res => console.log("تم تسليم الإجابات بنجاح."));
}

function exitAdmin() {
    document.getElementById('admin-screen').classList.remove('active');
    document.getElementById('start-screen').classList.add('active');
    fetchQuestions();
}

function toggleAdminOptions() {
    const type = document.getElementById('new-q-type').value;
    document.getElementById('admin-mcq-inputs').style.display = type === "mcq" ? "block" : "none";
}

function addQuestion() {
    const text = document.getElementById('new-q-text').value.trim();
    const type = document.getElementById('new-q-type').value;
    let options = [];
    let correct = null;
    
    if(text === "") { alert("اكتب نص السؤال!"); return; }
    if(type === "mcq") {
        const optRaw = document.getElementById('new-q-options').value;
        options = optRaw.split(',').map(s => s.trim());
        correct = parseInt(document.getElementById('new-q-correct').value);
    }
    
    const payload = { text: text, type: type, options: options, correct: correct };
    
    fetch('/add_question', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    }).then(() => {
        alert("🎉 تم حفظ ونشر السؤال بنجاح!");
        loadAdminQuestions();
        document.getElementById('new-q-text').value = "";
    });
}

function loadStudentsSubmissions() {
    fetch('/get_submissions')
    .then(res => res.json())
    .then(data => {
        const tbody = document.getElementById('admin-tbody');
        tbody.innerHTML = "";
        data.forEach(sub => {
            let details = "";
            sub.answers.forEach((ans, idx) => {
                details += `<div><strong>س${idx+1}: ${ans.question}</strong></div>`;
                if(ans.type === 'code') {
                    details += `<pre>${ans.answer}</pre><br>`;
                } else {
                    details += `<div style="color:var(--neon-blue); margin-bottom:10px;">إجابة الطالب: ${ans.answer}</div>`;
                }
            });
            
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><strong>${sub.username}</strong></td>
                <td><a href="https://wa.me/${sub.whatsapp}" target="_blank" style="color:var(--neon-green); font-weight:bold;">${sub.whatsapp}</a></td>
                <td>${details}</td>
            `;
            tbody.appendChild(tr);
        });
    });
}

// نظام الأمان ضد مغادرة الصفحة
function userLeftWindow() { if (!isQuizActive || leaveTime !== null) return; if (warningCount === 0) { warningCount++; leaveTime = Date.now(); document.getElementById('warning-modal').style.display = 'flex'; countdownInterval = setInterval(() => { let left = 20 - Math.floor((Date.now() - leaveTime) / 1000); if (left <= 0) { disqualifyUser(); } else { document.getElementById('countdown-text').innerText = left; } }, 500); } else { disqualifyUser(); } }
function userReturnedToWindow() { if (!isQuizActive || leaveTime === null) return; clearInterval(countdownInterval); if ((Date.now() - leaveTime) / 1000 >= 20) { disqualifyUser(); } else { document.getElementById('warning-modal').style.display = 'none'; leaveTime = null; alert("تحذير أخير من الأستاذ الخضر!"); } }
function disqualifyUser() { isQuizActive = false; clearInterval(countdownInterval); document.getElementById('warning-modal').style.display = 'none'; document.getElementById('quiz-screen').classList.remove('active'); document.getElementById('disqualified-screen').classList.add('active'); }
window.addEventListener('blur', userLeftWindow); window.addEventListener('focus', userReturnedToWindow);
// دالة إعادة الطالب لشاشة البداية بعد تسليم الامتحان
function goToHome() {
    // تصفير البيانات والعدادات لإعادة الاختبار من جديد
    currentQuestion = 0;
    selectedOption = null;
    userAnswers = [];
    warningCount = 0;
    leaveTime = null;
    
    // تفريغ خانات الاسم والواتساب
    if(document.getElementById('username')) document.getElementById('username').value = "";
    if(document.getElementById('whatsapp')) document.getElementById('whatsapp').value = "";
    
    // إخفاء شاشة النتيجة وإظهار شاشة البداية
    document.getElementById('result-screen').classList.remove('active');
    document.getElementById('start-screen').classList.add('active');
    
    // تحديث الأسئلة مجدداً من السيرفر
    fetchQuestions();
}
// عرض جميع الأسئلة داخل لوحة تحكم الأستاذ
function loadAdminQuestions() {
    fetch('/get_questions')
    .then(res => res.json())
    .then(data => {
        const tbody = document.getElementById('admin-questions-tbody');
        tbody.innerHTML = "";
        data.forEach((q, index) => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${q.text}</td>
                <td><span style="color:var(--neon-blue);">${q.type === 'mcq' ? 'اختياري' : 'كود / نصي'}</span></td>
                <td>
                    <button onclick="deleteQuestion(${index})" style="background:#ff3333; color:white; border:none; padding:6px 12px; border-radius:4px; cursor:pointer; font-weight:bold;">❌ حذف</button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    });
}

// دالة حذف سؤال معين وإعادة تحديث الجدول
function deleteQuestion(index) {
    if(confirm("هل أنت متأكد من رغبتك في حذف هذا السؤال نهائياً؟")) {
        fetch('/delete_question', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ index: index })
        })
        .then(res => res.json())
        .then(data => {
            alert("🗑️ تم حذف السؤال بنجاح!");
            loadAdminQuestions(); // إعادة تحديث جدول الأسئلة
            fetchQuestions();     // تحديث قاعدة البيانات في الخلفية
        });
    }
}
