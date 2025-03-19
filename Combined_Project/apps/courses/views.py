from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.db.models import F
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView
from django.contrib.auth.decorators import login_required
from .models import Rating, Course, Lesson


# Регистрация нового пользователя
def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        # Дополнительные действия после регистрации, например, автоматический вход
        login(request, user)  # Автоматический вход после регистрации
        return redirect('home')  # Перенаправление на главную страницу

    return render(request, 'registration/register.html')  # Отображение страницы регистрации

# Вход пользователя
def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            # Перенаправление на главную страницу или другую страницу после входа
            return redirect('home')  # Пример перенаправления на главную страницу
        else:
            # Обработка ошибки входа
            return render(request, 'registration/login.html', {'error_message': 'Invalid credentials.'})

    return render(request, 'registration/login.html')

# Выход пользователя
def user_logout(request):
    logout(request)
    # Перенаправление на главную страницу или другую страницу после выхода
    return redirect('home')  # Пример перенаправления на главную страницу

def home(request):
    course = Course.objects.all()
    i = 0
    if request.user.is_authenticated:
        user_profile = UserProfile.objects.get(user=request.user)
        rates = Rating.objects.all()
        username = request.user.username
        rate = None
        for r in rates:
            if r.min_r <= user_profile.total_points < r.max_r:
                rate = r
                break
        print(rate)
        return render(request, 'courses/main_page.html', {'rate': rate, 'user_profile': user_profile, 'username': username, 'courses': course, 'i':i})
    else:
        return render(request, 'courses/main_page.html',{'courses': course, 'i': i})


@login_required
def restricted_area(request):
    return render(request, 'courses/resrticted.html')

from django.contrib.auth.decorators import login_required, permission_required

def course(request):
    courses = Course.objects.all()
    username = request.user.username
    return render(request, 'courses/course.html', {'courses': courses,'username': username})

@permission_required('myapp.can_view_page')
def restricted_page(request):
    # Ваше представление
    return render(request, 'courses/test.html', {})

# views.py
from .models import Question, UserProfile, Answer, Response, Choice
from .forms import TestForm, QuizForm


def test_view(request):
    questions = Question.objects.all()
    if request.method == 'POST':
        form = TestForm(request.POST, questions=questions)
        if form.is_valid():
            user_profile = UserProfile.objects.get(user=request.user)
            total_points = 0
            for question in questions:
                answer_id = form.cleaned_data.get(str(question.id))
                answer = Answer.objects.get(id=answer_id)
                if answer.is_correct:
                    total_points += 10
            user_profile.total_points = F('total_points') + total_points
            user_profile.save()
            return render(request, 'courses/test_completed.html')
    else:
        form = TestForm(questions=questions)
    return render(request, 'chatbot/test.html', {'form': form})

from .models import Question, Answer  # Импортируем модели

def quiz_view(request):
    questions_with_answers = []  # Создаем пустой список для хранения вопросов и ответов

    # Получаем список всех вопросов
    questions = Question.objects.all()

    # Для каждого вопроса получаем связанные с ним ответы и добавляем их в список вместе с вопросом
    for question in questions:
        answers = Answer.objects.filter(question=question)
        questions_with_answers.append({'question': question, 'answers': answers})

    # Весь остальной код оставляем без измененийя
    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            user = request.user  # Assuming user is authenticated
            user_profile = UserProfile.objects.get(user=request.user)
            total_points = 0

            for field_name, value in form.cleaned_data.items():
                question_id = int(field_name.split('_')[1])
                response = Response(user=user, question_id=question_id, choice_id=value)
                response.save()
                choice = Choice.objects.get(id=value)
                if choice.is_correct:
                    total_points += 10
                else:
                    total_points -= 10

            user_profile.total_points = F('total_points') + total_points
            user_profile.save()
            if total_points >= 0:
                return redirect('quiz_done')
            else:
                return redirect(('quiz_failed'))
            messages.success(request, 'Your responses have been submitted successfully.')
            return redirect('quiz_result')  # Redirect to view results
    else:
        form = QuizForm()
    username = request.user.username
    return render(request, 'courses/test.html', {'form': form, 'username': username, 'questions_with_answers': questions_with_answers})

def quiz_done(request):
    username = request.user.username
    return render(request,'courses/done.html',{'username':username})

def quiz_failed(request):
    username = request.user.username
    return render(request,'courses/failed.html', {'username': username})

from django.views.generic.detail import DetailView

from django.views.generic.detail import DetailView
from .models import Course, Lesson

class CourseDetailView(DetailView):
    model = Course
    slug_field = "url"
    template_name = 'courses/course_detail.html'
    context_object_name = 'course'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Получите объект курса
        course = self.get_object()
        # Получите все уроки, связанные с этим курсом
        lessons = Lesson.objects.filter(course=course)
        # Добавьте уроки в контекст
        context['lessons'] = lessons
        return context

from django.shortcuts import get_object_or_404

from django.views.generic import DetailView
from django.shortcuts import redirect
from django.contrib import messages
from .forms import QuizForm
from .models import Lesson, Course, Question, Response, Choice, UserProfile  # Подставьте правильные пути к вашим моделям





class LessonDetailView(DetailView):
    model = Lesson
    slug_field = "url"
    template_name = 'courses/lesson_detail.html'
    context_object_name = 'lesson'

    def get_queryset(self):
        course_slug = self.kwargs.get('course_slug')
        lesson_slug = self.kwargs.get('slug')
        course = get_object_or_404(Course, url=course_slug)
        return Lesson.objects.filter(course=course, url=lesson_slug)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lesson = self.get_object()
        questions = Question.objects.filter(lesson=lesson)
        context['questions'] = questions
        context['form'] = QuizForm()
        context['username'] = self.request.user.username
        return context

    def post(self, request, *args, **kwargs):
        form = QuizForm(request.POST)
        if form.is_valid():
            user = self.request.user
            user_profile = UserProfile.objects.get(user=user)
            total_points = 0

            for field_name, value in form.cleaned_data.items():
                question_id = int(field_name.split('_')[1])
                response = Response(user=user, question_id=question_id, choice_id=value)
                response.save()
                choice = Choice.objects.get(id=value)
                if choice.is_correct:
                    total_points += 10
                else:
                    total_points -= 10

            user_profile.total_points = F('total_points') + total_points
            user_profile.save()

            if total_points >= 0:
                messages.success(request, 'Your responses have been submitted successfully.')
                return redirect('quiz_done')
            else:
                return redirect('quiz_failed')
        else:
            # Если форма недействительна, возвращаем обратно на страницу урока
            return self.get(request, *args, **kwargs)







    # Можно добавить дополнительные методы или переопределить уже существующие

# def about(request):
#     return render(request, 'gasyrlab/about.html')
#
# class show_post(DetailView):
#     slug_field = "url"
#     template_name = "gasyrlab/post.html"



from django.shortcuts import render
from django.http import JsonResponse



from django.http import JsonResponse

# Словарь с готовыми ответами
PREDEFINED_ANSWERS = {
    "Привет": "Привет, какие вопросы вас волнует?",
    "привет": "Привет, какие вопросы вас волнует?",
    "Сәлем": "Сәлем, немен көмектесе аламын?",
    "сәлем": "Сәлем, немен көмектесе аламын?",
    "Какие курсы программирования вы предлагаете?": "Мы предлагаем курсы по Python, Java, JavaScript, C++, HTML/CSS, и другим языкам программирования.",
    "Как записаться на курсы?": "Вы можете записаться через наш сайт или связаться с нами по телефону.",
    "Есть ли у вас пробные занятия?": "Да, у нас есть бесплатные пробные занятия, чтобы вы могли оценить нашу программу.",
    "Сколько длится курс программирования?": "Длительность курсов варьируется от 1 до 6 месяцев, в зависимости от уровня и программы.",
    "Какие курсы подходят для начинающих?": "Для новичков мы рекомендуем курсы по Python, HTML/CSS или JavaScript.",
    "Можно ли обучаться онлайн?": "Да, все наши курсы проходят в онлайн-формате с интерактивными заданиями.",
    "Какой график занятий?": "Мы предлагаем занятия в утреннее, дневное и вечернее время. Выберите удобное для себя расписание.",
    "Предоставляете ли вы сертификат после окончания курса?": "Да, после завершения курса вы получите сертификат.",
    "Какая стоимость курсов?": "Стоимость зависит от программы курса. Подробную информацию вы можете найти на нашем сайте.",
    "Какие технологии изучаются на курсе?": "Мы изучаем базовые и продвинутые технологии, такие как Flask, Django, React, Node.js, SQL и другие.",
    "Какой возрастной лимит для курсов?": "Наши курсы подходят для всех, начиная с 12 лет.",
    "Есть ли проекты в ходе обучения?": "Да, в каждом курсе есть практические проекты, которые вы сможете добавить в своё портфолио.",
    "Можно ли учиться без опыта?": "Конечно! У нас есть программы для тех, кто начинает с нуля.",
    "Какие инструменты мне понадобятся?": "Вам понадобится компьютер с доступом в интернет и установленный редактор кода (например, Visual Studio Code).",
    "Есть ли у вас курсы по разработке игр?": "Да, мы предлагаем курсы по созданию игр на Unity и Unreal Engine.",
    "Как проходит обучение?": "Обучение проходит в формате онлайн-вебинаров, интерактивных заданий и видеолекций.",
    "Есть ли у вас поддержка студентов?": "Да, наши преподаватели и наставники всегда готовы помочь вам с вопросами.",
    "Как проходят экзамены и тесты?": "Мы проводим онлайн-тесты и проверяем практические проекты.",
    "Какие перспективы после курса?": "Вы сможете начать карьеру в IT, работать фрилансером или продолжить обучение на более продвинутом уровне.",
    "Как оплатить курс?": "Вы можете оплатить курс картой, через банковский перевод или воспользоваться рассрочкой.",
    "Как проверить свой уровень знаний?": "Мы предлагаем бесплатное тестирование для определения вашего уровня.",
    "Есть ли у вас индивидуальные занятия?": "Да, вы можете выбрать индивидуальный формат обучения.",
    "Какие языки программирования самые популярные?": "Сейчас самые востребованные языки — Python, JavaScript и Java.",
    "Есть ли у вас курсы по искусственному интеллекту?": "Да, у нас есть курсы по машинному обучению, Data Science и искусственному интеллекту.",
    "Как вы помогаете с трудоустройством?": "Мы помогаем составить резюме, готовим к собеседованиям и предоставляем вакансии от наших партнёров.",
    "Какие курсы для школьников?": "У нас есть программы по основам программирования и созданию игр для школьников.",
    "Можно ли начать в любое время?": "Да, вы можете присоединиться к курсу в удобное для вас время.",
    "Есть ли у вас русскоязычные преподаватели?": "Да, все наши преподаватели говорят на русском языке.",
    "Что изучается на курсе Python?": "На курсе Python вы изучите основы языка, работу с данными, создание приложений и веб-разработку.",
    "Как связаться с вами?": "Вы можете написать нам в чат на сайте или позвонить по указанному номеру.",
    "Есть ли у вас проекты по командной разработке?": "Да, мы организуем командные проекты для отработки навыков работы в группе.",
    "Какая у вас программа для начинающих?": "Мы начинаем с основ программирования, изучения синтаксиса и написания простых программ.",
    "Какие навыки получу после курса?": "Вы научитесь писать код, разрабатывать приложения и решать задачи программирования.",
    "Есть ли у вас вечерние занятия?": "Да, у нас есть вечерние группы для тех, кто работает или учится днём.",
    "Какие курсы для веб-разработки?": "Мы предлагаем курсы по HTML/CSS, JavaScript, React и Node.js для создания сайтов.",
    "Можно ли обучаться с телефона?": "Да, вы можете просматривать лекции и решать задачи с телефона, но для программирования лучше использовать компьютер.",
    "Как устроены домашние задания?": "Домашние задания включают практические задачи и проекты с обратной связью от преподавателя.",
    "Есть ли у вас курсы для продвинутых пользователей?": "Да, мы предлагаем курсы по backend-разработке, DevOps, и созданию микросервисов.",
    "Какие есть курсы для Data Science?": "У нас есть курсы по Python для анализа данных, SQL, Pandas, NumPy и машинному обучению.",
    "Можно ли задавать вопросы во время занятий?": "Да, наши преподаватели отвечают на вопросы в реальном времени.",
    "Как часто проходят занятия?": "Обычно занятия проходят 2-3 раза в неделю, в зависимости от курса.",
    "Что нужно для записи на курс?": "Достаточно оставить заявку на сайте и выбрать удобное время.",
    "Есть ли у вас тестовые задания?": "Да, мы даём тестовые задания для проверки ваших знаний.",
    "Можно ли пересмотреть лекции?": "Да, все записи лекций доступны в вашем личном кабинете.",
    "Как вы оцениваете проекты студентов?": "Преподаватели оценивают проекты по критериям качества кода, функциональности и дизайна.",
    "Какие курсы подходят для начинающих фрилансеров?": "Курсы по веб-разработке, Python и разработке мобильных приложений отлично подходят для фриланса.",
    "Есть ли у вас марафоны или хакатоны?": "Да, мы регулярно проводим образовательные марафоны и хакатоны для студентов.",
    "Сіздер қандай бағдарламалау курстарын ұсынасыздар?": "Біз Python, Java, JavaScript, C++, HTML/CSS және басқа бағдарламалау тілдері бойынша курстар ұсынамыз.",
    "Курстарға қалай жазылуға болады?": "Сіз біздің сайт арқылы немесе телефон арқылы хабарласып жазыла аласыз.",
    "Тегін сынақ сабақтары бар ма?": "Иә, бізде тегін сынақ сабақтары бар, олар арқылы біздің бағдарламамен таныса аласыз.",
    "Бағдарламалау курсы қанша уақытқа созылады?": "Курстардың ұзақтығы деңгейге және бағдарламаға байланысты 1-6 айды құрайды.",
    "Бастапқы деңгей үшін қандай курстар қолайлы?": "Жаңадан бастаушылар үшін Python, HTML/CSS немесе JavaScript курстарын ұсынамыз.",
    "Онлайн оқуға бола ма?": "Иә, біздің барлық курстарымыз онлайн форматта интерактивті тапсырмалармен өтеді.",
    "Сабақтар кестесі қандай?": "Біз таңғы, түскі және кешкі уақытта сабақтар ұсынамыз. Өзіңізге қолайлы уақытты таңдаңыз.",
    "Курс аяқталған соң сертификат беріледі ме?": "Иә, курсты аяқтағаннан кейін сіз сертификат аласыз.",
    "Курстардың бағасы қандай?": "Бағасы курс бағдарламасына байланысты. Толық ақпаратты біздің сайттан таба аласыз.",
    "Курс барысында қандай технологиялар оқытылады?": "Біз Flask, Django, React, Node.js, SQL және басқа заманауи технологияларды үйретеміз.",
    "Курстарға жас шектеуі бар ма?": "Біздің курстарымыз 12 жастан бастап кез келген адамға қолайлы.",
    "Оқу барысында жобалар бар ма?": "Иә, әр курста сіз өз портфолиоңызға қосуға болатын практикалық жобалар бар.",
    "Тәжірибесіз оқуға бола ма?": "Әрине! Біздің бағдарламаларымыз жаңадан бастаушылар үшін арналған.",
    "Маған қандай құралдар қажет?": "Компьютер, интернетке қолжетімділік және код редакторы (мысалы, Visual Studio Code) қажет.",
    "Ойын әзірлеу курстары бар ма?": "Иә, бізде Unity және Unreal Engine платформаларында ойын жасауды үйрететін курстар бар.",
    "Оқу қалай өтеді?": "Оқу онлайн вебинарлар, интерактивті тапсырмалар және бейнелекциялар форматында өтеді.",
    "Студенттерге қолдау көрсетіле ме?": "Иә, біздің оқытушылар мен менторлар сіздің барлық сұрақтарыңызға жауап беруге дайын.",
    "Емтихан мен тесттер қалай өтеді?": "Біз онлайн тесттер өткіземіз және практикалық жобаларды тексереміз.",
    "Курс аяқталған соң қандай мүмкіндіктер бар?": "Сіз IT саласында мансап бастауыңызға, фрилансер болып жұмыс істеуіңізге немесе оқуын жалғастыруыңызға болады.",
    "Курсты қалай төлеуге болады?": "Курсты карта арқылы, банк аударымы арқылы немесе бөліп төлеу арқылы төлеуге болады.",
    "Білім деңгейімді қалай тексеремін?": "Біз сіздің деңгейіңізді анықтау үшін тегін тестілеу ұсынамыз.",
    "Жеке сабақтар бар ма?": "Иә, сіз жеке оқу форматын таңдай аласыз.",
    "Қай бағдарламалау тілдері ең танымал?": "Қазіргі кезде ең танымал тілдер — Python, JavaScript және Java.",
    "Жасанды интеллект бойынша курстар бар ма?": "Иә, бізде машиналық оқыту, деректер ғылымы және жасанды интеллект бойынша курстар бар.",
    "Сіздер жұмысқа орналасуға көмектесесіздер ме?": "Иә, біз түйіндеме құруға, сұхбаттарға дайындалуға және серіктестерімізден вакансиялар ұсынуға көмектесеміз.",
    "Мектеп оқушыларына арналған курстар бар ма?": "Бізде бағдарламалау негіздері мен ойын жасауға арналған бағдарламалар бар.",
    "Кез келген уақытта оқуды бастауға бола ма?": "Иә, сіз өзіңізге қолайлы уақытта курстарға қосыла аласыз.",
    "Сіздерде қазақ тілінде сөйлейтін оқытушылар бар ма?": "Иә, біздің барлық оқытушылар қазақ тілінде сөйлейді.",
    "Python курсында не оқытылады?": "Python курсында сіз бағдарламалау негіздерін, деректермен жұмысты, қосымша жасауды және веб-әзірлеуді үйренесіз.",
    "Сіздермен қалай байланысуға болады?": "Бізге сайттағы чат арқылы немесе көрсетілген телефон нөмірі арқылы хабарласа аласыз.",
    "Командалық жоба жасау мүмкіндігі бар ма?": "Иә, біз топтық жобаларды ұйымдастырамыз, бұл топпен жұмыс істеу дағдыларын жетілдіруге көмектеседі.",
    "Бастапқы деңгей бағдарламасы қандай?": "Біз бағдарламалаудың негіздерінен, синтаксистен және қарапайым бағдарламаларды жазудан бастаймыз.",
    "Курсты аяқтаған соң қандай дағдылар аласыз?": "Сіз код жазуды, қосымшалар әзірлеуді және бағдарламалау тапсырмаларын шешуді үйренесіз.",
    "Кешкі сабақтар бар ма?": "Иә, біз күндізгі немесе жұмыс істейтін адамдар үшін кешкі топтар ұсынамыз.",
    "Веб-әзірлеу курстары қандай?": "HTML/CSS, JavaScript, React және Node.js арқылы сайт жасау курстарын ұсынамыз.",
    "Ұялы телефоннан оқуға бола ма?": "Иә, лекцияларды қарау және тапсырмаларды орындау үшін ұялы телефонды қолдануға болады, бірақ бағдарламалау үшін компьютер жақсырақ.",
    "Үй тапсырмалары қалай беріледі?": "Үй тапсырмалары практикалық тапсырмалар мен оқытушыдан кері байланыс алуды қамтиды.",
    "Ілгері деңгей пайдаланушыларына арналған курстар бар ма?": "Иә, біз backend-әзірлеу, DevOps және микросервистерді жасау курстарын ұсынамыз.",
    "Data Science үшін қандай курстар бар?": "Бізде Python арқылы деректерді талдау, SQL, Pandas, NumPy және машиналық оқыту курстары бар.",
    "Сабақ барысында сұрақ қоюға бола ма?": "Иә, біздің оқытушылар нақты уақытта сұрақтарға жауап береді.",
    "Сабақтар қаншалықты жиі өтеді?": "Әдетте сабақтар аптасына 2-3 рет өтеді, курсқа байланысты.",
    "Курсқа жазылу үшін не қажет?": "Сайтта өтінім қалдырып, өзіңізге ыңғайлы уақытты таңдасаңыз жеткілікті.",
    "Сынақ тапсырмалар бар ма?": "Иә, біз сіздің біліміңізді тексеру үшін сынақ тапсырмалар береміз.",
    "Лекцияларды қайта көруге бола ма?": "Иә, барлық лекция жазбалары жеке кабинетте қолжетімді.",
    "Студенттердің жобалары қалай бағаланады?": "Оқытушылар жобаларды код сапасы, функционалдылық және дизайн бойынша бағалайды.",
    "Фрилансерлерге арналған қандай курстар бар?": "Веб-әзірлеу, Python және мобильді қосымша жасау курстары фрилансқа өте қолайлы.",
    "Марафондар немесе хакатондар өткізіледі ме?": "Иә, біз студенттер үшін оқу марафондары мен хакатондар ұйымдастырамыз."
}



def chatbot_view(request):
    if request.method == 'POST':
        user_message = request.POST.get('message')
        print(f"Сообщение от пользователя: {user_message}")
        response = PREDEFINED_ANSWERS.get(user_message, "Извините, я не понял ваш вопрос.")
        return JsonResponse({'response': response})
    return render(request, "chatbot/chat.html")


