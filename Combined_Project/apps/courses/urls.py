from django.urls import path, include

from . import views
from .views import home, test_view, quiz_view, quiz_done, quiz_failed, user_login, register, user_logout, \
    restricted_page, course, CourseDetailView, LessonDetailView

urlpatterns = [
    path("", home, name='home'),
    path('test/', test_view, name='test'),
    path('restricted/', views.restricted_area, name='restricted_area'),
    path("login/", user_login, name='login'),
    path("register/", register, name='register'),
    path("logout/", user_logout, name='logout'),
    path("private/", restricted_page, name='private'),
    path('quiz/',quiz_view, name='quiz'),
    path('quiz_done/', quiz_done, name ='quiz_done'),
    path('quiz_failed/', quiz_failed, name ='quiz_failed'),
    path('courses/', course, name='course'),
    path('courses/<slug:course_slug>/<slug:slug>/', LessonDetailView.as_view(), name='lesson_detail'),
    path('courses/<slug:slug>/', CourseDetailView.as_view(), name='course_detail'),
]
from django.conf import settings
from django.conf.urls.static import static
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)