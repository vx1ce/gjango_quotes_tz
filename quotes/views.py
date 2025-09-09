from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.db.models import Count, Sum
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db import OperationalError
import random

from .models import Quote, Source
from .forms import QuoteForm, SourceForm


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def random_quote(request):
    try:
        quotes_count = Quote.objects.count()
        if quotes_count == 0:
            return render(request, 'quotes/random_quote.html', {'quote': None})

        quotes = list(Quote.objects.all())
        weights = [quote.weight for quote in quotes]
        quote = random.choices(quotes, weights=weights, k=1)[0]

        quote.views += 1
        quote.save()

        return render(request, 'quotes/random_quote.html', {'quote': quote})

    except OperationalError:
        return render(request, 'quotes/random_quote.html', {'quote': None})


@require_POST
def vote(request, quote_id):
    try:
        quote = Quote.objects.get(id=quote_id)
        vote_type = request.POST.get('vote_type')

        if vote_type == 'like':
            quote.likes += 1
        elif vote_type == 'dislike':
            quote.dislikes += 1

        quote.save()
        return JsonResponse({
            'likes': quote.likes,
            'dislikes': quote.dislikes
        })
    except Quote.DoesNotExist:
        return JsonResponse({'error': 'Quote not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def add_quote(request):
    try:
        if request.method == 'POST':
            form = QuoteForm(request.POST)
            if form.is_valid():
                quote = form.save()
                messages.success(request, 'Цитата успешно добавлена!')
                return redirect('random_quote')
        else:
            form = QuoteForm()

        return render(request, 'quotes/add_quote.html', {'form': form})
    except OperationalError:
        messages.error(request, 'База данных не готова. Выполните миграции.')
        return redirect('random_quote')


def add_source(request):
    try:
        if request.method == 'POST':
            form = SourceForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Источник успешно добавлен!')
                return redirect('add_quote')
        else:
            form = SourceForm()
            sources = Source.objects.all()

        return render(request, 'quotes/add_source.html', {'form': form, 'sources': sources})
    except OperationalError:
        messages.error(request, 'База данных не готова. Выполните миграции.')
        return redirect('random_quote')


def popular_quotes(request):
    try:
        quotes = Quote.objects.annotate(
            total_votes=Count('likes') + Count('dislikes')
        ).order_by('-likes')[:10]

        return render(request, 'quotes/popular_quotes.html', {'quotes': quotes})
    except OperationalError:
        return render(request, 'quotes/popular_quotes.html', {'quotes': []})


def dashboard(request):
    try:
        total_quotes = Quote.objects.count()
        total_sources = Source.objects.count()
        total_views = Quote.objects.aggregate(total=Sum('views'))['total'] or 0
        total_likes = Quote.objects.aggregate(total=Sum('likes'))['total'] or 0

        popular_sources = Source.objects.annotate(
            quote_count=Count('quotes'),
            total_likes=Sum('quotes__likes')
        ).order_by('-total_likes')[:5]

        recent_quotes = Quote.objects.select_related('source').order_by('-created_at')[:5]

        context = {
            'total_quotes': total_quotes,
            'total_sources': total_sources,
            'total_views': total_views,
            'total_likes': total_likes,
            'popular_sources': popular_sources,
            'recent_quotes': recent_quotes,
        }

    except OperationalError:
        context = {
            'total_quotes': 0,
            'total_sources': 0,
            'total_views': 0,
            'total_likes': 0,
            'popular_sources': [],
            'recent_quotes': [],
        }

    return render(request, 'quotes/dashboard.html', context)