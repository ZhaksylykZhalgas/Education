from decimal import Decimal
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Avg
from django.utils.text import slugify
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _


class Feedback(models.Model):
    TOPIC_CHOICES = [
        ('complaint', 'Жалоба'),
        ('idea', 'Идея'),
        ('other', 'Другое'),
    ]

    name = models.CharField(max_length=100, verbose_name="Имя")
    email = models.EmailField(verbose_name="Почта")
    message = models.TextField(verbose_name="Сообщение")
    topic = models.CharField(max_length=20, choices=TOPIC_CHOICES, verbose_name="Выберите пункт", default='other')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return f"{self.name} - {self.topic}"


class Instructor(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='instructors/')
    experience = models.CharField(max_length=200)  # Example: "5 years"

    def __str__(self):
        return self.name


class Course(models.Model):
    title = models.CharField(max_length=200, verbose_name="Названия курса")
    slug = models.SlugField(unique=True, max_length=200, blank=True)
    image = models.ImageField(upload_to='courses/', verbose_name="Фото курса")
    short_description = models.TextField(max_length=500, verbose_name="Краткое описание")
    detailed_description = models.TextField(verbose_name="Подробнее описание")
    average_rating = models.FloatField(default=0.0, verbose_name="Средний рейтинг")
    completed_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='CourseCompletion',
        related_name='completed_courses_via_course',
        blank=True
    )

    duration = models.CharField(max_length=50, verbose_name="Срок обучения")
    topics_count = models.PositiveIntegerField(verbose_name="Количество тем", default=0)
    yearly_salary = models.CharField(max_length=50, verbose_name="Средняя зарплата в год")
    demand_percentage = models.PositiveIntegerField(verbose_name="Потребность (в процентах)")
    jobs_available = models.CharField(max_length=100, verbose_name="Доступные занятия")

    instructors = models.ManyToManyField('Instructor', related_name='courses')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    is_published = models.BooleanField(default=False, verbose_name=_("Опубликован"))

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Course.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        self.topics_count = self.lessons.filter(lesson_type='lecture').count()
        super().save(*args, **kwargs)

    def update_rating(self):
        ratings = self.ratings.aggregate(avg_score=Avg('score'))
        self.average_rating = Decimal(ratings['avg_score'] or 0).quantize(Decimal('0.00'))
        self.save()


class Lesson(models.Model):
    LESSON_TYPES = [
        ('lecture', 'Лекция'),
        ('exercise', 'Упражнение'),
        ('solution', 'Ответ'),
    ]

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons', verbose_name="Курс")
    title = models.CharField(max_length=200, verbose_name="Название урока")
    video = models.FileField(upload_to='lessons/videos/', verbose_name="Видео урок", blank=True, null=True)
    lesson_type = models.CharField(max_length=20, choices=LESSON_TYPES, verbose_name="Тип урока")
    description = models.TextField(blank=True, verbose_name="Описание урока")
    additional_materials = models.FileField(
        upload_to='lessons/materials/',
        verbose_name="Дополнительные материалы",
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Rating(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ratings')
    course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name='ratings')
    score = models.PositiveIntegerField(
        verbose_name="Оценка",
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    def __str__(self):
        return f"{self.user.username} - {self.course.title} - {self.score}"


class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField(verbose_name="Комментарий", max_length=500)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies'
    )

    avatar = models.CharField(max_length=255, null=True, blank=True)


    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата изменения")

    FORBIDDEN_WORDS = ['тупой', 'мал', 'ишак']
    # likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_comments', blank=True)
    # dislikes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='disliked_comments', blank=True)
    #
    # @property
    # def like_count(self):
    #     return self.likes.count()
    #
    # @property
    # def dislike_count(self):
    #     return self.dislikes.count()

    @property
    def is_edited(self):
        """Возвращает True, если комментарий был изменен."""
        return self.updated_at is not None and self.updated_at > self.created_at

    def save(self, *args, **kwargs):
        # for word in self.FORBIDDEN_WORDS:
        #     if word.lower() in self.text.lower():
        #         raise ValueError(f"Комментарий содержит запрещенное слово: {word}")
        # """Сохраняет старую версию комментария в истории и обновляет updated_at."""
        if self.pk:  # Если объект уже существует
            original = Comment.objects.get(pk=self.pk)
            if original.text != self.text:  # Проверяем, изменился ли текст
                # Сохраняем старую версию в истории
                CommentRepliesHistory.objects.create(
                    comment=self,
                    text=original.text,
                    updated_at=now()
                )
                # Обновляем поле updated_at
                self.updated_at = now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.course.title} - {self.created_at.strftime('%Y-%m-%d')}"


class CommentLike(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Пользователь"
    )
    comment = models.ForeignKey('Comment', on_delete=models.CASCADE, related_name="likes")
    like_type = models.CharField(max_length=10, choices=[('like', 'Лайк'), ('dislike', 'Дизлайк')])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'comment')

    def __str__(self):
        return f"{self.user} -> {self.comment.id} ({self.like_type})"


class CommentRepliesHistory(models.Model):
    comment = models.ForeignKey(
        'Comment',
        on_delete=models.CASCADE,
        related_name="reply_history",
        verbose_name="Комментарий"
    )
    text = models.TextField(default='')
    old_text = models.TextField(verbose_name="Старый текст")  # Хранит старую версию текста комментария
    new_text = models.TextField(verbose_name="Новый текст", blank=True, null=True)  # Хранит новую версию текста
    updated_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата сохранения версии")

    def __str__(self):
        return f"История комментария {self.comment.id} от {self.updated_at.strftime('%Y-%m-%d %H:%M')}"



class CommentsHistory(models.Model):
    comment = models.ForeignKey(
        Comment, on_delete=models.CASCADE, related_name="history_comments", verbose_name="Комментарий"
    )
    text = models.TextField(verbose_name="Старый текст")
    updated_at = models.DateTimeField(verbose_name="Дата изменения")

    def __str__(self):
        return f"История {self.comment.id} ({self.updated_at.strftime('%Y-%m-%d %H:%M:%S')})"



class CourseCompletion(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='completed_courses'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='completions'
    )
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'course')


class Section(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='sections')
    title = models.CharField(max_length=200, verbose_name="Название раздела")
    description = models.TextField(blank=True, verbose_name="Описание раздела")

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class CustomUser(AbstractUser):
    is_email_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.username
