
# forms.py
from django import forms
from .models import Answer
# forms.py

from django import forms
from .models import Question

class QuizForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(QuizForm, self).__init__(*args, **kwargs)
        questions = Question.objects.all()
        for question in questions:
            choices = [(choice.id, choice.choice_text) for choice in question.choice_set.all()]
            self.fields['question_{}'.format(question.id)] = forms.ChoiceField(
                label=question.question_text,
                widget=forms.RadioSelect,
                choices=choices,
                required=True
            )


class TestForm(forms.Form):
    def __init__(self, *args, **kwargs):
        questions = kwargs.pop('questions')
        super(TestForm, self).__init__(*args, **kwargs)
        for question in questions:
            self.fields["question_{0}".format(question.id)] = forms.ChoiceField(
                label=question.text,
                choices=[(answer.id, answer.text) for answer in question.answer_set.all()],
                widget=forms.RadioSelect
            )

    def clean(self):
        cleaned_data = super().clean()
        for name, value in cleaned_data.items():
            if value is None:
                raise forms.ValidationError("Please answer all questions.")
        return cleaned_data
