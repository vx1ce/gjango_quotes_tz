from django.contrib import admin
from .models import Source, Quote, QuoteView


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ['title', 'source_type', 'year', 'created_at']
    list_filter = ['source_type', 'year']
    search_fields = ['title']


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ['text_short', 'source', 'weight', 'likes', 'dislikes', 'views', 'created_at']
    list_filter = ['source', 'created_at']
    search_fields = ['text', 'source__title']
    list_editable = ['weight']

    def text_short(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text

    text_short.short_description = 'Текст'


@admin.register(QuoteView)
class QuoteViewAdmin(admin.ModelAdmin):
    list_display = ['quote', 'ip_address', 'viewed_at']
    list_filter = ['viewed_at']