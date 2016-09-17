from django import forms
from django.contrib.auth.models import User

def valid_user(username, password):
    return True


class NameForm(forms.Form):
    error_css_class = 'error1'
    required_css_class = "required1"
    username = forms.CharField(label='Username', max_length=50)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    def clean(self):
        if valid_user(self['username'].value(), self['password'].value()):
            user = User.objects.create_user(username=self['username'].value(), password=self['password'].value())
            user.save()
        else:
            raise forms.ValidationError("Wrong credentials")
