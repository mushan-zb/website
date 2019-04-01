import time
import markdown

from smtplib import SMTPException
from django.shortcuts import render, redirect, Http404, HttpResponse
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.core.mail import send_mail
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
        try:
            ip = request.META['HTTP_X_FORWARDED_FOR']
        except KeyError:
            ip = request.META['REMOTE_ADDR']
        comment.address = ip
        if request.POST.get('reply'):
            comment.reply = CommentModel.objects.get(pk=request.POST.get('reply'))
        form = CommentForm(request.POST, instance=comment)

        url = 'https://' + request.get_host() + request.path
        from_email = 'mushan-blog@mail.mushan.top'

        if form.is_valid():
            try:
                # 设置每个用户，每天的评论次数，防爬虫恶意提交
                # comment_count = comment.objects.filter(
                #     status=True, address=ip,
                #     name=request.POST.get('name'),
                #     email=request.POST.get('email'),
                # ).count()

                form.save()
                request.session['content'] = ''
                subject = '【木杉博客】 - 消息通知'
                if comment.reply:
                    recipient_list = [comment.reply.email]
                    html_message = '{name} 你好\n你在木杉博客中发表的评论得到他人的回复\n评论：{comment}\n回复：{reply}\n快速查看：{url}'.format(name=comment.reply.name, comment=comment.reply.content, reply=comment.content, url=url)
                else:
                    admin_url = 'https://' + request.get_host() + '/admin'
                    recipient_list = ['zhenbin0212@163.com']
                    html_message = '博客收到一条新评论\n评论：{comment}\n快速查看：{url}\n后台管理：{admin_url}'.format(comment=comment.content, url=url, admin_url=admin_url)

                send_mail(
                    subject=subject,
                    message=html_message,
                    from_email=from_email,
                    recipient_list=recipient_list,
                    fail_silently=False
                )
            except SMTPException:
                result['status'] = 302
                result['explain'] = '评论成功，但邮件发送失败'
            except:
                result['status'] = 100
                result['explain'] = '评论失败'
        else:
            result['status'] = 300
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
