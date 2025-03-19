from django import forms
from .models import *
import  re

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['name', 'email', 'message', 'topic']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите ваше имя'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Введите вашу почту'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Напишите ваше сообщение', 'rows': 5}),
            'topic': forms.RadioSelect(attrs={'class': 'radio-group'}),
        }
        labels = {
            'name': 'Ваше имя',
            'email': 'Ваша почта',
            'message': 'Ваше сообщение',
            'topic': 'Выберите пункт',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['topic'].empty_label = None


class CommentForm(forms.ModelForm):
    FORBIDDEN_WORDS = ['тупой', 'мал', 'ишак']

    class Meta:
        model = Comment
        fields = ['text', 'parent']  # Добавляем поле для родительского комментария
        widgets = {
            'text': forms.Textarea(attrs={
                'placeholder': 'Напишите ваш комментарий...',
                'rows': 4,
                'class': 'form-control',
            }),
        }

    def clean_text(self):
        text = self.cleaned_data.get('text', '').strip()
        max_words = 50  # Установите максимальное количество слов
        word_count = len(text.split())  # Подсчет слов
        forbidden_found = []

        # Проверяем запрещенные слова
        for word in self.FORBIDDEN_WORDS:
            pattern = r'\b' + re.escape(word) + r'\b'
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                forbidden_found.extend(matches)
                text = re.sub(pattern, lambda m: '*' * len(m.group()), text, flags=re.IGNORECASE)
        self.data = self.data.copy()
        self.data['text'] = text
        print(text)
        # Проверяем длину текста
        if word_count > max_words:
            raise forms.ValidationError(
                f"Ваш текст слишком длинный. Максимум {max_words} слов, но вы написали {word_count} слов."
            )

        # Если найдены запрещенные слова
        if forbidden_found:
            self.cleaned_data['text'] = text  # Сохраняем измененный текст
            raise forms.ValidationError(
                f"Ваш комментарий содержал запрещенные слова: {', '.join(forbidden_found)}. "
                f"Они были автоматически заменены на звездочки. Проверьте и отправьте снова."
            )

        return text



