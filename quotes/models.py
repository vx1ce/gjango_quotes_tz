from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone


class Source(models.Model):
    SOURCE_TYPES = [
        ('movie', 'Фильм'),
        ('book', 'Книга'),
        ('song', 'Песня'),
        ('other', 'Другое'),
    ]

    title = models.CharField(max_length=200, verbose_name="Название")
    source_type = models.CharField(max_length=10, choices=SOURCE_TYPES, verbose_name="Тип")
    year = models.IntegerField(null=True, blank=True, verbose_name="Год")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['title', 'source_type']
        ordering = ['title']

    def __str__(self):
        return f"{self.get_source_type_display()}: {self.title} ({self.year})"

    def quote_count(self):
        return self.quotes.count()


class Quote(models.Model):
    text = models.TextField(verbose_name="Текст цитаты")
    source = models.ForeignKey(Source, on_delete=models.CASCADE, related_name='quotes', verbose_name="Источник")
    weight = models.IntegerField(default=1, verbose_name="Вес (чем больше, тем чаще показывается)")
    likes = models.IntegerField(default=0, verbose_name="Лайки")
    dislikes = models.IntegerField(default=0, verbose_name="Дизлайки")
    views = models.IntegerField(default=0, verbose_name="Просмотры")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['text', 'source']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.text[:50]}... ({self.source})"

    def clean(self):
        # Проверка, что у источника не больше 3 цитат
        if self.pk is None:  # Новая цитата
            if Quote.objects.filter(source=self.source).count() >= 3:
                raise ValidationError("У одного источника не может быть больше 3 цитат")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def total_votes(self):
        return self.likes + self.dislikes

    def like_percentage(self):
        if self.total_votes() == 0:
            return 0
        return (self.likes / self.total_votes()) * 100


class QuoteView(models.Model):
    quote = models.ForeignKey(Quote, on_delete=models.CASCADE, related_name='quote_views')
    ip_address = models.GenericIPAddressField()
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-viewed_at']