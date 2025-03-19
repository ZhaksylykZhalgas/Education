from django.urls import path
from django.contrib.auth import views as auth_views

from apps.chatbot.views import *
from .views import *

urlpatterns = [
    path('', main_page, name='main_page'),
    path('about/', about, name='about'),
    path('contact/', contact, name='contact'),
    path('contact_success/', contact_success, name='contact_success'),
    path('course/', courses, name='kyrs'),
    path('courses/', course_list, name='course_list'),
    path('course/<slug:slug>', more, name='more'),
    path('register/', register_view, name='register'),
    path('confirm/<uidb64>/<token>/', confirm_email, name='email_confirm'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='main/password_reset.html'), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(template_name='main/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='main/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='main/password_reset_complete.html'), name='password_reset_complete'),
    path('email_confirmation/', email_confirmation_view, name='email_confirmation'),
    path('resend-email-confirmation/', resend_email_confirmation, name='resend_email_confirmation'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    # Страница с деталями курса
    path('course/<slug:slug>/', course_detail, name='course_detail'),

    # Уроки курса
    path('course/<slug:slug>/lesson/<int:lesson_id>/', lesson_detail, name='lesson_detail'),

    # Страница для добавления рейтинга курса
    path('course/<slug:slug>/rate/', add_rating, name='add_rating'),
    path('course/<slug:slug>/start/', start_course, name='start_course'),
    path('course/<slug:slug>/complete/', complete_course, name='complete_course'),
    path('delete_comment/<int:id>/', delete_comment, name='delete_comment'),
    path('delete_reply/<int:reply_id>/', delete_reply, name='delete_reply'),
    path('edit-comment/<int:comment_id>/', edit_comment, name='edit_comment'),
    path('add-comment/', add_comment, name='add_comment'),
    path('edit-reply/<int:reply_id>/', edit_reply, name='edit_reply'),
    path('like-comment/<int:comment_id>/', like_comment, name='like_comment'),
    path('dislike-comment/<int:comment_id>/', dislike_comment, name='dislike_comment'),
    path('chatbot', chatbot_view, name='chatbot')
]