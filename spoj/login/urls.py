from django.conf.urls import url
from . import views

app_name = 'login'

urlpatterns = [

    #url(r'profile/(?P<username>[a-z]+)', views.profile, name='profile'),
    url(r'^$', views.index, name='index'),
]