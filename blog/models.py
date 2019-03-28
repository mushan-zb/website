from django.db import models

from mdeditor.fields import MDTextField

# Create your models here.


class BaseModel(models.Model):
    STATUS = (
        (True, '显示'),
        (False, '隐藏'),
    )
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now=True)
    modify_time = models.DateTimeField(verbose_name='最近修改时间', auto_now_add=True)
    status = models.BooleanField(verbose_name='状态', default=True, choices=STATUS)

    class Meta:
        abstract = True


class ArticleModel(BaseModel):
    title = models.CharField(verbose_name='标题', max_length=100, unique=True)
    content = MDTextField(verbose_name='内容')
    label = models.ManyToManyField(verbose_name='标签', to='LabelModel')
    view = models.IntegerField(verbose_name='浏览量', default=0)

    class Meta:
        verbose_name = verbose_name_plural = '文章'
        ordering = ['-modify_time']     # 逆序排序

    def __str__(self):
        return self.title

    def viewed(self):
        self.view += 1
        self.save()

    def next_article(self):
        """获取下一篇文章"""
        return ArticleModel.objects.filter(pk__gt=self.pk, status=True).reverse().first()

    def previous_article(self):
        """获取上一篇文章"""
        return ArticleModel.objects.filter(pk__lt=self.pk, status=True).first()


class LabelModel(BaseModel):
    slug = models.SlugField(verbose_name='地址', max_length=30, unique=True)
    name = models.CharField(verbose_name='标签名', max_length=30, unique=True)

    class Meta:
        verbose_name = verbose_name_plural = '标签'

    def __str__(self):
        return self.name


class CommentModel(BaseModel):
    name = models.CharField(verbose_name='昵称', max_length=10)
    email = models.EmailField(verbose_name='邮箱', max_length=30)
    content = models.TextField(verbose_name='内容')
    article = models.ForeignKey(verbose_name='文章', to='ArticleModel', on_delete=models.CASCADE)
    reply = models.ForeignKey(verbose_name='回复', to='CommentModel', on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        verbose_name = verbose_name_plural = '评论'

    def __str__(self):
        return self.name
