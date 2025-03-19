from django.contrib import admin

from .models import *
# Register your models here.
admin.site.register(Course)
admin.site.register(Language)
admin.site.register(Lesson)
admin.site.register(Rating)
admin.site.register(UserProfile)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Choice)
