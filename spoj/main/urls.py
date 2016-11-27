from django.conf.urls import url
from . import views

app_name = 'main'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^all/', views.all, name='all'),
    url(r'^logout/', views.logout_view, name='logout'),
    url(r'^profile/(?P<user_id>[a-zA-Z0-9_]+)', views.profile, name='profile'),
    url(r'^code/(?P<search_id>[a-zA-Z0-9]+)', views.code, name='code'),
    url(r'^follow/(?P<user_id>[a-zA-Z0-9_]+)/(?P<val>[0-1])', views.follow, name='follow'),
]