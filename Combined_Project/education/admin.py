from django.contrib import admin
from .models import *


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'topic', 'created_at')
    list_filter = ('topic', 'created_at')
    search_fields = ('name', 'email', 'message')
    ordering = ('-created_at',)


@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ('name', 'experience')


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'average_rating', 'created_at', 'completed_users_count')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [LessonInline]

    actions = ['publish_courses', 'unpublish_courses']

    @admin.action(description="Опубликовать выбранные курсы")
    def publish_courses(self, request, queryset):
        queryset.update(is_published=True)
        self.message_user(request, "Выбранные курсы успешно опубликованы.")

    @admin.action(description="Скрыть выбранные курсы")
    def unpublish_courses(self, request, queryset):
        queryset.update(is_published=False)
        self.message_user(request, "Выбранные курсы успешно скрыты.")

    def completed_users_count(self, obj):
        return obj.completed_users.count()

    completed_users_count.short_description = "Завершившие пользователи"


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'lesson_type', 'course')
    list_filter = ('lesson_type', 'course')
    search_fields = ('title',)


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'score')
    list_filter = ('course',)
    search_fields = ('user__username', 'course__title')


class CommentHistoryInline(admin.TabularInline):
    model = CommentRepliesHistory
    fields = ('old_text', 'new_text', 'updated_at')
    readonly_fields = ('old_text', 'new_text', 'updated_at')
    extra = 0  # Убираем пустые строки для добавления новых записей

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'course', 'text', 'parent', 'is_edited', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at', 'course', 'parent')
    search_fields = ('user__username', 'text', 'course__title', 'parent')
    inlines = [CommentHistoryInline]  # Inline для отображения истории комментариев

    def is_edited(self, obj):
        return obj.is_edited

    is_edited.boolean = True
    is_edited.short_description = "Изменен?"


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_email_verified', 'is_staff', 'date_joined')
    list_filter = ('is_email_verified', 'is_staff')
    search_fields = ('username', 'email')
    ordering = ('date_joined',)


class CommentLikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'comment', 'like_type', 'created_at')
    list_filter = ('like_type', 'created_at')
    search_fields = ('user__username', 'comment__text')


admin.site.register(CommentLike, CommentLikeAdmin)
