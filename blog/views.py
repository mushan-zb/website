from django.shortcuts import render, redirect
from django.shortcuts import HttpResponse, Http404
from django.core.paginator import Paginator
from django.db.models import Q

from .models import ArticleModel, LabelModel

# Create your views here.


def index(request, page=1):
    article_list = ArticleModel.objects.filter(status=True)
    paginator = Paginator(article_list, 20)
    context = paginator.get_page(page)
    label_list = LabelModel.objects.filter(status=True)
    hot_news = article_list[:10]

    return render(request, 'blog/index.html', locals())


def article(request, pk):
    try:
        article_info = ArticleModel.objects.get(pk=pk, status=True)
        article_info.view += 1
        article_info.save()
        label_list = LabelModel.objects.filter(status=True)
        hot_news = ArticleModel.objects.filter(status=True)[:10]
    except ArticleModel.DoesNotExist:
        raise Http404('页面找不到')

    content = {
        'article': article_info,
        'hot_news': hot_news,
        'label_list': label_list,
    }

    return render(request, 'blog/article.html', content)


def category(request, slug, page=1):
    labels = LabelModel.objects.filter(status=True, slug=slug)
    if labels is None:
        raise Http404("页面找不到")
    article_list = ArticleModel.objects.filter(status=True, label=labels[0].pk)
    paginator = Paginator(article_list, 20)
    context = paginator.get_page(page)
    label_list = LabelModel.objects.filter(status=True)
    hot_news = ArticleModel.objects.filter(status=True)[:10]

    content = {
        'label': labels[0],
        'context': context,
        'label_list': label_list,
        'hot_news': hot_news,
    }

    return render(request, 'blog/category.html', content)


def search(request, page=1):
    key = request.GET.get('key')
    if not key:
        return redirect('/blog')
    result = ArticleModel.objects.filter(Q(status=True) & (Q(title__contains=key) | Q(content__contains=key)))

    paginator = Paginator(result, 20)
    context = paginator.get_page(page)
    label_list = LabelModel.objects.filter(status=True)
    hot_news = ArticleModel.objects.filter(status=True)[:10]

    content = {
        'count': len(result),
        'context': context,
        'label_list': label_list,
        'hot_news': hot_news,
    }

    return render(request, 'blog/search.html', content)
