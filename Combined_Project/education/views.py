import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseRedirect, HttpResponseForbidden, HttpResponse
from django.contrib import messages
from django.urls import reverse
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
import random
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db.models import Count, Q
from .forms import *
from .models import *

import logging

logger = logging.getLogger(__name__)


# Create your views here.

def main_page(request):
    random_courses = Course.objects.order_by('?')[:3]
    return render(request, 'main/main_page.html', {'random_courses': random_courses})


def contact(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            form.save()  # Сохраняем данные в базу
            return redirect('contact_success')  # Перенаправляем на страницу успеха
    else:
        form = FeedbackForm()
    return render(request, 'main/contact.html', {'form': form})


def success_view(request):
    return render(request, 'main/success.html')


def about(request):
    return render(request, 'main/about_us.html')


def contact_success(request):
    return render(request, 'main/success.html', {'message': "Спасибо за ваш отзыв!"})


def courses(request):
    query = request.GET.get('query', '').strip()
    instructor_id = request.GET.get('instructor', '')
    completion_status = request.GET.get('completion', '')

    courses = Course.objects.filter(is_published=True)
    if query:
        courses = courses.filter(title__icontains=query)

    if instructor_id:
        courses = courses.filter(instructors__id=instructor_id)

    completed_courses = []
    if request.user.is_authenticated:
        completed_courses = CourseCompletion.objects.filter(user=request.user).values_list('course_id', flat=True)
        if completion_status == "completed":
            courses = courses.filter(id__in=completed_courses)
        elif completion_status == "not_completed":
            courses = courses.exclude(id__in=completed_courses)

    filter_rating = request.GET.get('filter_rating', '')  # Совпадает с name="filter_rating"
    if request.user.is_authenticated:
        if filter_rating == "5":
            courses = courses.filter(average_rating__gte=5)
        elif filter_rating == "4":
            courses = courses.filter(average_rating__gte=4, average_rating__lt=5)
        elif filter_rating == "3":
            courses = courses.filter(average_rating__gte=3, average_rating__lt=4)
        elif filter_rating == "2":
            courses = courses.filter(average_rating__gte=2, average_rating__lt=3)
        elif filter_rating == "1":
            courses = courses.filter(average_rating__gte=1, average_rating__lt=2)
        elif filter_rating == "0":
            courses = courses.filter(average_rating__gte=0)
    instructors = Instructor.objects.all()
    message = None
    if not courses.exists():
        message = 'Курсы не найдены.'

    return render(request, 'main/course.html', {
        'courses': courses,
        'query': query,
        'instructors': instructors,
        'completed_courses': completed_courses,
        'message': message,
        'filter_rating': filter_rating,
    })


def course_list(request):
    query = request.GET.get('query', '').strip()  # Получаем запрос пользователя
    message = None  # Инициализируем сообщение

    if query:  # Если запрос есть
        courses = Course.objects.filter(title__icontains=query)  # Фильтруем курсы
        if not courses.exists():  # Если курсы не найдены
            message = 'Пока у нас нет этот курс :(.'
    else:  # Если запрос пустой
        if 'query' in request.GET:  # Если запрос отправлен, но пуст
            message = 'Пожалуйста, введите текст для поиска!'
        courses = Course.objects.all()  # Показываем все курсы, если запрос пуст

    return render(request, 'main/course_list.html', {
        'courses': courses,
        'query': query,
        'message': message,  # Передаем сообщение в шаблон
    })


@login_required
def course_detail(request, slug):
    course = get_object_or_404(Course, slug=slug)
    lessons = course.lessons.all()  # Получить уроки курса
    return render(request, 'main/course_detail.html', {'course': course, 'lessons': lessons})


def lesson_detail(request, slug, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id, course__slug=slug)
    return render(request, 'main/lesson_detail.html', {'lesson': lesson})


@login_required
def add_rating(request, slug):
    course = get_object_or_404(Course, slug=slug)
    message = None  # Сообщение для отображения
    if request.method == 'POST':
        score = request.POST.get('score', '5')  # Если оценка не передана, используем значение по умолчанию
        try:
            score = int(score)
            if score < 1 or score > 5:
                raise ValueError("Оценка должна быть от 1 до 5.")
        except ValueError:
            messages.error(request, 'Некорректное значение оценки.')
            return redirect('add_rating', slug=slug)

        # Сохраняем оценку пользователя
        rating, created = Rating.objects.get_or_create(user=request.user, course=course)
        rating.score = score
        rating.save()

        # Обновляем средний рейтинг
        course.update_rating()
        message = "Спасибо за ваш отзыв!"  # Сообщение благодарности

    return render(request, 'main/add_rating.html', {'courses': courses, 'message': message})


@login_required
def start_course(request, slug):
    courses = get_object_or_404(Course, slug=slug)
    lessons = Lesson.objects.filter(course=courses)
    lectures = lessons.filter(lesson_type='lecture')
    exercises = lessons.filter(lesson_type='exercise')
    solutions = lessons.filter(lesson_type='solution')

    message = None
    existing_rating = None

    # Fetch user's existing rating if it exists
    try:
        existing_rating = Rating.objects.get(user=request.user, course=courses).score
    except Rating.DoesNotExist:
        existing_rating = None

    if request.method == 'POST':
        # Handle the submitted rating
        rating_value = request.POST.get('rating')
        if rating_value:
            try:
                rating_value = int(rating_value)
                if not (1 <= rating_value <= 5):
                    raise ValueError("Недопустимое значение рейтинга.")
            except (TypeError, ValueError):
                return HttpResponse('Недопустимое значение рейтинга.', status=400)

            # Create or update the rating
            rating, created = Rating.objects.get_or_create(
                user=request.user, course=courses, defaults={'score': rating_value}
            )
            if not created:
                rating.score = rating_value
                rating.save()

            # Update course average rating
            courses.update_rating()
            message = "Ваша оценка успешно обновлена!" if not created else "Спасибо за ваш отзыв!"

    context = {
        'course': courses,
        'lectures': lectures,
        'exercises': exercises,
        'solutions': solutions,
        'lessons': lessons,
        'message': message,
        'existing_rating': existing_rating,
    }
    return render(request, 'main/start_course.html', context)


@login_required
def delete_comment(request, id):
    comment = get_object_or_404(Comment, id=id)
    if comment.user == request.user:  # Убедитесь, что пользователь может удалять только свои комментарии
        comment.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def complete_course(request, slug):
    course = get_object_or_404(Course, slug=slug)

    if request.method == "POST":
        # Добавляем текущего пользователя в список завершивших, если его там нет
        if request.user not in course.completed_users.all():
            course.completed_users.add(request.user)
            course.save()
            return JsonResponse({"message": "Курс успешно завершен!"}, status=200)
        return JsonResponse({"message": "Вы уже завершили этот курс."}, status=400)
    return JsonResponse({"message": "Метод не поддерживается."}, status=405)


@never_cache
@login_required
def more(request, slug):
    courses = get_object_or_404(Course, slug=slug)
    instructors = courses.instructors.all()

    for course in Course.objects.all():
        course.topics_count = course.lessons.filter(lesson_type='lecture').count()
        course.save()

    # Аннотируем комментарии с количеством лайков и дизлайков
    comments = courses.comments.filter(parent__isnull=True).annotate(
        like_count=Count('likes', filter=Q(likes__like_type='like')),
        dislike_count=Count('likes', filter=Q(likes__like_type='dislike'))
    ).order_by('-created_at')

    # Пагинация
    paginator = Paginator(comments, 5)
    page_number = request.GET.get('page')
    page_comments = paginator.get_page(page_number)

    # Обработка реакций текущего пользователя
    user_reactions = {}
    if request.user.is_authenticated:
        user_reactions = {
            like.comment.id: like.like_type
            for like in CommentLike.objects.filter(user=request.user, comment__in=page_comments)
        }

    # Список доступных аватаров
    avatars = ['1.png', '2.png', '3.png', '4.png']

    if request.method == 'POST':
        form = CommentForm(request.POST)
        parent_id = request.POST.get('parent_id')  # ID родительского комментария, если это ответ

        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.course = courses
            comment.avatar = random.choice(avatars)

            if form.cleaned_data['parent']:
                comment.parent = form.cleaned_data['parent']
            # Привязываем ответ к родительскому комментарию
            if parent_id:
                forbidden_words = ['тупой', 'мал', 'ишак']
                for word in forbidden_words:
                    if word.lower() in comment.text.lower():
                        messages.error(request, "Ваш ответ содержит запрещенные слова и был автоматически удален.")
                        return redirect('more', slug=slug)

                comment.parent = Comment.objects.get(id=parent_id)
            comment.save()
            return redirect('more', slug=slug)
        else:
            form.fields['text'].initial = form.cleaned_data.get('text', '')

            # if comment.parent and comment.parent.user_id == request.user.id:
            #     # Additional logic can go here, if needed
            #     comment.parent.delete()
            # return redirect('more', slug=slug)

    else:
        form = CommentForm()

    return render(request, 'main/more.html', {
        "courses": courses,
        "instructors": instructors,
        "page_comment": page_comments,
        "form": form,
        "average_rating": courses.average_rating,
        "user_reactions": user_reactions,
    })


@login_required
def add_comment(request):
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.avatar = 'default.png'  # Укажите или настройте аватар
            comment.save()
            return JsonResponse({"success": True, "message": "Комментарий успешно добавлен!"})
        else:
            return JsonResponse({"success": False, "errors": form.errors}, status=400)

    return JsonResponse({"success": False, "message": "Некорректный метод запроса"}, status=405)


@login_required
def delete_reply(request, reply_id):
    reply = get_object_or_404(Comment, id=reply_id)
    if reply.user != request.user:
        return HttpResponseForbidden("Вы не можете удалить этот ответ.")
    course_slug = reply.course.slug
    parent_id = reply.parent.id if reply.parent else None
    reply.delete()
    return redirect('more', slug=course_slug)
    # return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def edit_reply(request, reply_id):
    if request.method == "POST":
        reply = get_object_or_404(Comment, id=reply_id, parent__isnull=False)

        # Проверяем, является ли пользователь автором
        if reply.user != request.user:
            return JsonResponse({"success": False, "error": "Вы не можете редактировать этот ответ."}, status=403)

        data = json.loads(request.body)
        new_text = data.get("text", "").strip()

        if not new_text:
            return JsonResponse({"success": False, "error": "Текст ответа не может быть пустым."}, status=400)

        reply.text = new_text
        reply.save()

        return JsonResponse({"success": True, "text": new_text})

    return JsonResponse({"success": False, "error": "Некорректный метод запроса."}, status=405)


@login_required
@require_POST
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    # Проверка на право редактирования
    if request.user != comment.user:
        return JsonResponse({'error': 'Вы не можете редактировать этот комментарий'}, status=403)

    # Получаем новый текст комментария
    data = json.loads(request.body)
    new_text = data.get('text', '').strip()

    if not new_text:
        return JsonResponse({'error': 'Текст комментария не может быть пустым'}, status=400)

    # Обновляем комментарий только если текст изменился
    if comment.text != new_text:
        comment.text = new_text
        comment.updated_at = now()
        comment.save()
        return JsonResponse({
            'success': True,
            'text': new_text,
            'updated_at': comment.updated_at.strftime('%d.%m.%Y %H:%M')
        })

    # Если текст не изменился
    return JsonResponse({'success': False, 'message': 'Комментарий не изменился.'})


@login_required
@require_POST
def like_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    # Удаляем текущую реакцию, если она есть
    existing_like = CommentLike.objects.filter(user=request.user, comment=comment, like_type='like').first()
    if existing_like:
        existing_like.delete()
        user_reacted = None  # Пользователь удалил лайк
    else:
        # Удаляем дизлайк, если он есть
        CommentLike.objects.filter(user=request.user, comment=comment, like_type='dislike').delete()
        # Добавляем лайк
        CommentLike.objects.create(user=request.user, comment=comment, like_type='like')
        user_reacted = 'like'

    # Возвращаем обновленные данные
    like_count = CommentLike.objects.filter(comment=comment, like_type='like').count()
    dislike_count = CommentLike.objects.filter(comment=comment, like_type='dislike').count()

    return JsonResponse({
        "success": True,
        "like_count": like_count,
        "dislike_count": dislike_count,
        "user_reacted": user_reacted,
    })


@login_required
@require_POST
def dislike_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    # Удаляем текущую реакцию, если она есть
    existing_dislike = CommentLike.objects.filter(user=request.user, comment=comment, like_type='dislike').first()
    if existing_dislike:
        existing_dislike.delete()
        user_reacted = None  # Пользователь удалил дизлайк
    else:
        # Удаляем лайк, если он есть
        CommentLike.objects.filter(user=request.user, comment=comment, like_type='like').delete()
        # Добавляем дизлайк
        CommentLike.objects.create(user=request.user, comment=comment, like_type='dislike')
        user_reacted = 'dislike'

    # Возвращаем обновленные данные
    like_count = CommentLike.objects.filter(comment=comment, like_type='like').count()
    dislike_count = CommentLike.objects.filter(comment=comment, like_type='dislike').count()

    return JsonResponse({
        "success": True,
        "like_count": like_count,
        "dislike_count": dislike_count,
        "user_reacted": user_reacted,
    })


def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username').strip()
        email = request.POST.get('email').strip()
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "Пароли не совпадают")
            return redirect('register')

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Имя пользователя уже занято")
            return redirect('register')

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Этот email уже используется")
            return redirect('register')

        try:
            user = CustomUser.objects.create_user(username=username, email=email, password=password)
            user.is_email_verified = False  # По умолчанию email не подтверждён
            user.save()

            # Автоматический вход
            login(request, user)

            # Отправка письма с подтверждением
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            confirm_url = request.build_absolute_uri(reverse('email_confirm', kwargs={'uidb64': uid, 'token': token}))

            send_mail(
                'Подтверждение почты',
                f'Здравствуйте, {username}. Подтвердите вашу почту по ссылке: {confirm_url}',
                'noreply@example.com',
                [email],
                fail_silently=False,
            )

            messages.info(request, "Пожалуйста, подтвердите вашу почту. Уведомление отображается в шапке.")
            return redirect('main_page')
        except Exception as e:
            messages.error(request, f"Произошла ошибка: {str(e)}")
            return redirect('register')

    return render(request, 'main/register.html')


def email_confirmation_view(request):
    return render(request, 'main/email_confirmation.html')


# Подтверждение почты

def confirm_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_email_verified = True  # Устанавливаем подтверждение
        user.save()
        messages.success(request, "Ваш email подтверждён! Теперь вы можете использовать все функции.")
        return redirect('main_page')
    else:
        return render(request, 'main/invalid_token.html', {"message": "Ссылка для подтверждения недействительна."})


@login_required
def resend_email_confirmation(request):
    # Проверяем, авторизован ли пользователь и не подтверждён ли его email
    if not request.user.is_email_verified:
        user = request.user
        # Генерация токена и ссылки для подтверждения
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        confirm_url = request.build_absolute_uri(
            reverse('email_confirm', kwargs={'uidb64': uid, 'token': token})
        )
        # Отправка письма
        send_mail(
            'Подтверждение почты',
            f'Здравствуйте, {user.username}. Подтвердите ваш email по ссылке: {confirm_url}',
            'your-email@example.com',
            [user.email],
            fail_silently=False,
        )
        # Добавляем сообщение об успешной отправке
        messages.success(request, 'Письмо с подтверждением отправлено ещё раз на вашу почту.')
    else:
        # Если email уже подтверждён
        messages.info(request, 'Ваш email уже подтверждён.')

    # Перенаправление обратно на главную страницу
    return redirect('main_page')


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Вы успешно вошли!")
            return redirect('main_page')  # Replace with your main page
        else:
            messages.error(request, "Неверное имя пользователя или пароль")
            return redirect('login')

    return render(request, 'main/login.html')


def logout_view(request):
    logout(request)
    messages.success(request, "Вы вышли из системы!")
    return redirect('main_page')
