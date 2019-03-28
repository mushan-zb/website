import markdown

from django.shortcuts import render, redirect, Http404, HttpResponse
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q

from .models import ArticleModel, LabelModel, CommentModel
from .forms import CommentForm

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
        article_info.viewed()
        label_list = LabelModel.objects.filter(status=True)
        hot_news = ArticleModel.objects.filter(status=True)[:10]
        comment_form = CommentForm()
    except ArticleModel.DoesNotExist:
        raise Http404('页面找不到')

    comment_list = []
    sub_level = {}

    def comment_sort():
        top_level = []
        for comment in CommentModel.objects.filter(article=article_info, status=True):
            if comment.reply is None:
                top_level.append(comment)
            else:
                sub_level.setdefault(comment.reply.pk, []).append(comment)
        for top_comment in top_level:
            comment_format(top_comment)

    def comment_format(top_comment):
        comment_list.append(top_comment)
        if top_comment.pk in sub_level:
            for comment in sub_level[top_comment.pk]:
                comment_format(comment)

    comment_sort()

    session = {
        'name': request.session.get('name', ''),
        'email': request.session.get('email', ''),
        'content': request.session.get('content', ''),
    }
    article_info.content = markdown.markdown(
        article_info.content,
        extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
            'markdown.extensions.toc',
        ]
    )
    print(comment_list)
    previous_article = article_info.previous_article()
    next_article = article_info.next_article()

    return render(request, 'blog/article.html', locals())


def category(request, slug, page=1):
    try:
        label = LabelModel.objects.filter(status=True, slug=slug)[0]
    except IndexError:
        raise Http404("页面找不到")
    article_list = ArticleModel.objects.filter(status=True, label=label.pk)
    paginator = Paginator(article_list, 20)
    context = paginator.get_page(page)
    label_list = LabelModel.objects.filter(status=True)
    hot_news = ArticleModel.objects.filter(status=True)[:10]

    return render(request, 'blog/category.html', locals())


def publish_comment(request):
    """ 100 错误 200 成功 300 警告"""
    result = {
        'status': 200,
        'explain': '评论已添加'
    }

    if request.method == 'POST':
        request.session['name'] = request.POST.get('name').strip()
        request.session['email'] = request.POST.get('email')
        request.session['content'] = request.POST.get('content')

        if request.POST.get('name').strip() in ['木杉', 'mushan']:
            result['status'] = 301
            result['explain'] = '不能使用博客主的昵称'
            return JsonResponse(result)

        comment = CommentModel()
        comment.article = ArticleModel.objects.get(pk=request.POST.get('article'))
        if request.POST.get('reply'):
            comment.reply = CommentModel.objects.get(pk=request.POST.get('reply'))
        form = CommentForm(request.POST, instance=comment)

        if form.is_valid():
            try:
                form.save()
                request.session['content'] = ''
            except:
                result['status'] = 100
                result['explain'] = '评论失败'
        else:
            result['status'] = 303
            result['explain'] = '数据格式有误'
        return JsonResponse(result)
    else:
        result['status'] = 101
        result['explain'] = '非法请求'
        return JsonResponse(result)


def search(request, page=1):
    key = request.GET.get('key')
    if not key:
        return redirect('/blog')
    result = ArticleModel.objects.filter(Q(status=True) & (Q(title__contains=key) | Q(content__contains=key)))

    paginator = Paginator(result, 20)
    context = paginator.get_page(page)
    label_list = LabelModel.objects.filter(status=True)
    hot_news = ArticleModel.objects.filter(status=True)[:10]
    count = len(result)

    return render(request, 'blog/search.html', locals())
