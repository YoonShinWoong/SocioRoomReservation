from django import forms
from .models import Blog

# 만약 모델 기반이 아니라면 forms.Form
class BlogPost(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ['title' , 'description']