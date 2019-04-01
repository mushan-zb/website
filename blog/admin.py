from django.contrib import admin
from .models import ArticleModel, LabelModel, CommentModel

# Register your models here.

# admin.site.site_header = '木杉网站管理系统'
# admin.site.site_title = '木杉网站后台'


def display(model_admin, request, queryset):
    queryset.update(status=True)


def hide(model_admin, request, queryset):
    queryset.update(status=False)


display.short_description = '将选中数据隐藏'
hide.short_description = '将选中数据显示'


@admin.register(ArticleModel)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'modify_time', 'view', 'address']
    list_per_page = 20
    search_fields = ['title', 'label', 'content']
    actions = [display, hide]
    filter_horizontal = ['label']
    fieldsets = (
        (None, {
            'fields': ('title', 'content', 'label'),
        }),
        (None, {
            'fields': ('view', 'status')
        })
    )


@admin.register(LabelModel)
class LabelAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'modify_time', 'address']
    list_per_page = 20
    search_fields = ['name', 'slug']
    actions = [display, hide]


@admin.register(CommentModel)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'article', 'reply', 'address']
    list_per_page = 20
    search_fields = ['name', 'content', 'article', 'reply']
    actions = [display, hide]
