from django import forms
from .models import Quote, Source


class SourceForm(forms.ModelForm):
    class Meta:
        model = Source
        fields = ['title', 'source_type', 'year']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название фильма или книги'}),
            'source_type': forms.Select(attrs={'class': 'form-control'}),
            'year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Год выпуска'}),
        }
        labels = {
            'title': 'Название',
            'source_type': 'Тип источника',
            'year': 'Год',
        }


class QuoteForm(forms.ModelForm):
    class Meta:
        model = Quote
        fields = ['text', 'source', 'weight']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Введите текст цитаты'
            }),
            'source': forms.Select(attrs={
                'class': 'form-control'
            }),
            'weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 10,
                'value': 1
            }),
        }
        labels = {
            'text': 'Текст цитаты',
            'source': 'Источник',
            'weight': 'Вес',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Если база данных не готова, не загружаем источники
        try:
            self.fields['source'].queryset = Source.objects.all()
        except:
            self.fields['source'].queryset = Source.objects.none()