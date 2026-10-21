from django import forms
from django.core.exceptions import ValidationError
# https://docs.djangoproject.com/en/6.1/ref/forms/validation/

class FeedbackForm(forms.Form):
    rating = forms.TypedChoiceField(
        choices=[
            ('', 'Select a rating'),
            *[(value, f'{value} star{"s" if value != 1 else ""}')
              for value in range(1,6)],
        ],
        coerce=int,
        empty_value=None,
        required=False,
        label='Rating',
        widget=forms.Select(attrs={'class': 'forms-select'}),
    )
    comment = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        label='Review',
    )

    def clean(self):
        cleaned_data = super().clean()
        rating = cleaned_data.get('rating')
        comment = cleaned_data.get('comment', '').strip()
        if rating is None and not comment:
            raise ValidationError('Choose a rating or write a review!')
        cleaned_data['comment'] = comment
        return cleaned_data