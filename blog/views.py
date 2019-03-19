from django.shortcuts import render, redirect
from django.shortcuts import HttpResponse, Http404
from django.core.paginator import Paginator

from .models import ArticleModel

# Create your views here.


def index(request, page=1):
    article_list = ArticleModel.objects.filter(status=True)
    paginator = Paginator(article_list, 20)
    context = paginator.get_page(page)

    return render(request, 'blog/index.html', {'context': context})


def article(request, pk):
    try:
        article_info = ArticleModel.objects.get(pk=pk, status=True)
        article_info.view += 1
        article_info.save()
    except ArticleModel.DoesNotExist:
        raise Http404('页面找不到')
    return render(request, 'blog/article.html', {'article': article_info})


def search(request):
    key = request.GET.get('key')
    return HttpResponse(key)