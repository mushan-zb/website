"""
    Author: mushan
    Date: 2019/3/26 8:36
    Version: 1.0
    Describe: form 表单
"""

from django import forms

from .models import CommentModel


class CommentForm(forms.ModelForm):
    class Meta:
        model = CommentModel
        fields = ['name', 'email', 'content']
        widgets = {
            'name': forms.TextInput(attrs={
                'id': 'name',
                'class': 'form-control',
                'placeholder': '请输入昵称',
            }),
            'email': forms.EmailInput(attrs={
                'id': 'email',
                'class': 'form-control',
                'placeholder': '请输入邮箱（若他人回复，将会邮件通知）',
            }),
            'content': forms.Textarea(attrs={
                'id': 'content',
                'class': 'form-control',
                'placeholder': '请输入评论内容',
            }),
        }
