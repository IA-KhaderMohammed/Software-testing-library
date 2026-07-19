// 1. بنك الأسئلة (يمكنك زيادة الأسئلة وتعديلها بسهولة هنا)
const quizData = [
    {
        question: "ما هي المخرجات الصحيحة للكود التالي؟\nprint(type(5.5))",
        options: ["<class 'int'>", "<class 'float'>", "<class 'str'>", "<class 'bool'>"],
        correct: 1
    },
    {
        question: "أي من التالي هو اسم متغير (Variable) صحيح في بايثون؟",
        options: ["2my_var", "my-var", "my_var", "my var"],
        correct: 2
    },
    {
        question: "كيف نكتب تعليقاً (Comment) في لغة بايثون؟",
        options: ["// هذا تعليق", "# هذا تعليق", "/* هذا تعليق */", ""],
        correct: 1
    },
    {
        question: "ما هي الدالة المستخدمة لطباعة النصوص على الشاشة؟",
        options: ["output()", "echo()", "print()", "input()"],
        correct: 2
    },
    {
        question: "ما هي نتيجة العملية التالية؟ 2 ** 3",
        options: ["6", "8", "9", "5"],
        correct: 1
    }
];

let currentQuestion = 0;
let score = 0;
let selectedOption = null;
let username = "";

// متغيرات نظام منع الغش والحماية
let isQuizActive = false;
let warningCount = 0;
let leaveTime = null;
let countdownInterval = null;

// تعطيل النسخ واللصق والزر الأيمن للفأرة
document.addEventListener('contextmenu', e => e.preventDefault());
document.addEventListener('copy', e => e.preventDefault());
document.addEventListener('paste', e => e.preventDefault());

// منع اختصارات لوحة المفاتيح الشهيرة للغش والتفتيش (F12, Ctrl+C, Ctrl+V, etc)
document.addEventListener('keydown', e => {
    if (e.ctrlKey && (e.key === 'c' || e.key === 'v' || e.key === 'u' || e.key === 'i' || e.key === 'j')) {
        e.preventDefault();
    }
    if (e.key === 'F12') e.preventDefault();
});

// بدء الاختبار
function startQuiz() {
    const inputName = document.getElementById('username').value.trim();
    if(inputName === "") {
        alert("الرجاء إدخال اسمك أولاً.");
        return;
    }
    username = inputName;
    document.getElementById('user-display').innerText = "الممتحن: " + username;
    
    document.getElementById('start-screen').classList.remove('active');
    document.getElementById('quiz-screen').classList.add('active');
    
    isQuizActive = true;
    loadQuestion();
}

// تحميل السؤال
function loadQuestion() {
    selectedOption = null;
    document.getElementById('next-btn').disabled = true;
    
    const currentQuiz = quizData[currentQuestion];
    document.getElementById('question-number').innerText = `السؤال ${currentQuestion + 1} من ${quizData.length}`;
    document.getElementById('question-text').innerText = currentQuiz.question;
    
    // تحديث شريط التقدم
    const progressPercent = ((currentQuestion) / quizData.length) * 100;
    document.getElementById('progress').style.width = progressPercent + "%";

    const optionsContainer = document.getElementById('options-container');
    optionsContainer.innerHTML = "";
    
    currentQuiz.options.forEach((option, index) => {
        const button = document.createElement('button');
        button.innerText = option;
        button.classList.add('option-btn');
        button.onclick = () => selectOption(button, index);
        optionsContainer.appendChild(button);
    });
}

// اختيار إجابة
function selectOption(button, index) {
    const buttons = document.querySelectorAll('.option-btn');
    buttons.forEach(btn => btn.classList.remove('selected'));
    
    button.classList.add('selected');
    selectedOption = index;
    document.getElementById('next-btn').disabled = false;
}

// الانتقال للسؤال التالي أو إنهاء الاختبار
function nextQuestion() {
    if(selectedOption === quizData[currentQuestion].correct) {
        score++;
    }
    
    currentQuestion++;
    if(currentQuestion < quizData.length) {
        loadQuestion();
    } else {
        endQuiz();
    }
}

// إنهاء الاختبار وعرض النتيجة
function endQuiz() {
    isQuizActive = false;
    document.getElementById('quiz-screen').classList.remove('active');
    document.getElementById('result-screen').classList.add('active');
    
    document.getElementById('result-user').innerText = `أحسنت يا ${username}، لقد أتممت الاختبار بنجاح.`;
    
    const percentage = Math.round((score / quizData.length) * 100);
    document.getElementById('score-percentage').innerText = percentage + "%";
    document.getElementById('score-details').innerText = `لقد أجبت بشكل صحيح على ${score} من أصل ${quizData.length} أسئلة.`;
    
    if(percentage >= 75) {
        document.getElementById('result-feedback').innerText = "تهانينا! أنت مؤهل تماماً للانتقال إلى المرحلة الثانية! سيتم التواصل معك عبر الواتساب.";
        document.getElementById('result-feedback').style.color = "#39ff14";
    } else {
        document.getElementById('result-feedback').innerText = "للأسف لم تحقق النسبة المطلوبة للانتقال (75%). راجع الدروس وحاول في الاختبار القادم.";
        document.getElementById('result-feedback').style.color = "#ff0055";
    }
}

// الاستبعاد التلقائي
function disqualifyUser(reason) {
    isQuizActive = false;
    clearInterval(countdownInterval);
    document.getElementById('warning-modal').style.display = 'none';
    document.getElementById('quiz-screen').classList.remove('active');
    document.getElementById('start-screen').classList.remove('active');
    document.getElementById('disqualified-screen').classList.add('active');
    document.getElementById('disqualify-reason').innerText = reason;
}

// ================= نظام الرصد الذكي لمغادرة الشاشة =================

function userLeftWindow() {
    if (!isQuizActive || leaveTime !== null) return;

    if (warningCount === 0) {
        // المرة الأولى: بدء عد تنازلي 20 ثانية
        warningCount++;
        leaveTime = Date.now();
        document.getElementById('warning-modal').style.display = 'flex';
        
        let visualTimeLeft = 20;
        document.getElementById('countdown-text').innerText = visualTimeLeft;
        
        countdownInterval = setInterval(() => {
            let actualTimeAway = Math.floor((Date.now() - leaveTime) / 1000);
            visualTimeLeft = 20 - actualTimeAway;
            
            if (visualTimeLeft <= 0) {
                disqualifyUser("انتهت مهلة الـ 20 ثانية وأنت خارج الاختبار! تم استبعادك رسمياً.");
            } else {
                document.getElementById('countdown-text').innerText = visualTimeLeft;
            }
        }, 500);
    } else {
        // المرة الثانية: استبعاد فوري مباشر دون مهلة
        disqualifyUser("تم استبعادك تلقائياً لمحاولتك مغادرة واجهة الاختبار للمرة الثانية!");
    }
}

function userReturnedToWindow() {
    if (!isQuizActive || leaveTime === null) return;
    
    let totalTimeAway = (Date.now() - leaveTime) / 1000;
    clearInterval(countdownInterval);
    
    if (totalTimeAway >= 20) {
        disqualifyUser("انتهت مهلة الـ 20 ثانية وأنت خارج الاختبار! تم استبعادك رسمياً.");
    } else {
        // عاد في الوقت المناسب
        document.getElementById('warning-modal').style.display = 'none';
        leaveTime = null;
        alert("⚠️ تحذير أخير: لقد غادرت الاختبار لمرة واحدة وتم العفو عنك. المرة القادمة ستعني الطرد الفوري المباشر!");
    }
}

// الاستماع لأحداث المتصفح (الخروج من التبويب أو فقدان التركيز الفأرة وعودتها)
window.addEventListener('blur', userLeftWindow);
window.addEventListener('focus', userReturnedToWindow);
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        userLeftWindow();
    } else {
        userReturnedToWindow();
    }
});
