from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User



from .models import UserProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from .models import UserProfile  # Предполагая, что ваша модель UserProfile находится в файле models.py

# Определяем группу, к которой хотим добавить разрешение
group, created = Group.objects.get_or_create(name='My Group')

# Получаем ContentType для модели UserProfile
content_type = ContentType.objects.get_for_model(UserProfile)

# Получаем или создаем разрешение "Can view page" для модели UserProfile
permission, created = Permission.objects.get_or_create(name='Can view page', content_type=content_type)

# Добавляем разрешение к группе
group.permissions.add(permission)

