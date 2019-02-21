from django.db import models

# Create your models here.


class BaseModel(models.Model):
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now=True)
    modify_time = models.DateTimeField(verbose_name='最近修改时间', auto_now_add=True)
    display = models.BooleanField(verbose_name='显示', default=True)

    class Meta:
        abstract = True


class LabelModel(BaseModel):
    slug = models.SlugField(verbose_name='地址', max_length=30)
    name = models.CharField(verbose_name='标签名', max_length=30)
    article = models.ManyToManyField(verbose_name='文章', to='ArticleModel', blank=True)

    class Meta:
        verbose_name = verbose_name_plural = '标签'

    def __str__(self):
        return self.name


class ArticleModel(BaseModel):
    title = models.CharField(verbose_name='标题', max_length=100, unique=True)
    content = models.TextField(verbose_name='内容')
    label = models.ManyToManyField(verbose_name='标签', to='LabelModel')


class CommentModel(BaseModel):
    pass
