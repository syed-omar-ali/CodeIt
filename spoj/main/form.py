from django import forms
from django.contrib.auth.models import User


class Userform(forms.Form):
    class Meta:
        model= User
        fields = ('username', 'password')
    username = forms.CharField(max_length=20,widget=forms.TextInput(attrs={'id': 'my_field',
                                                             'class': 'form-control', 'placeholder':'SPOJ Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'id': 'my_field',
                                                             'class': 'form-control', 'placeholder':'SPOJ Password'}))
