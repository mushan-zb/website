"""
    Author: mushan
    Date: 2019/2/27 13:30
    Version: 1.0
    Describe: 博客的路由分发
"""

from django.urls import path
from .views import index, search, article, category

urlpatterns = [
    path('', index, name='index'),
    path('page/<int:page>', index, name='page'),
    path('article/<int:pk>', article, name='article'),
    path('category/<slug:slug>', category, name='category'),
    path('category/<slug:slug>/<int:pk>', category, name='category'),
    path('search/', search, name='search'),
    path('search/<int:page>', search, name='search')
]
