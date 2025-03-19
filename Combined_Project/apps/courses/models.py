from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Rating(models.Model):
    Ratename = models.CharField('Название Рейтинга', max_length=30)
    min_r = models.PositiveSmallIntegerField("Минимум Рейтинга", default=0)
    max_r = models.PositiveSmallIntegerField("Максимум Рейтинг", default=1)
    image = models.ImageField("Название", upload_to='rating/')
    def __str__(self):
        return self.Ratename
    class Meta:
        verbose_name = "Звание"
        verbose_name_plural = ("Звания")

class Language(models.Model):
    name = models.CharField("Название", max_length=30)
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Язык Программирования"
        verbose_name_plural = ( "Языки программирования")

class Course(models.Model):

    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    title = models.CharField("Название", max_length=30)
    description = models.TextField("Описание")
    point_w = models.PositiveSmallIntegerField("Рейтинг при победе",default=10)
    point_m = models.PositiveSmallIntegerField("Рейтинг при поражении", default=10)
    image = models.ImageField('Фото', upload_to='course/',default='course/default.jpeg')
    draft = models.BooleanField("Черновик", default=False)
    url = models.SlugField(max_length=130, unique=True)
    def  __str__(self):
        return self.title

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = ("Курсы")


    def get_absolute_url(self):
        return reverse("course_detail", kwargs={'slug': self.url})

from django.db import models
from django.urls import reverse

class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons", verbose_name="Курс")
    title = models.CharField("Название", max_length=30)
    description = models.TextField("Описание")
    video = models.FileField("Видео", upload_to='lessons/', default='lessons/default.mp4')
    url = models.SlugField(max_length=130, unique=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Тема"
        verbose_name_plural = "Темы"

    def get_absolute_url(self):
        return reverse('lesson_detail', kwargs={'course_slug': self.course.url, 'slug': self.url})


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    total_points = models.PositiveSmallIntegerField("Очко рейтинга", default=1000)
    course = models.ManyToManyField(Course, verbose_name='Тест', related_name='course')
    logo = models.ImageField('Аватар', upload_to='user_logo/', default='user_logo/default.jpeg')
    # Другие поля профиля пользователя, такие как изучаемые языки и т.д.

    def __str__(self):
        return self.user.username

class Question(models.Model):
    question_text = models.CharField(max_length=255)
    lesson = models.ForeignKey(Lesson, verbose_name='Урок', on_delete=models.CASCADE, default=1)

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)


from django.db import models


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)

# models.py

from django.db import models
from django.contrib.auth.models import User

class Response(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)

class ExampleModel(models.Model):
    name = models.CharField(max_length=100)