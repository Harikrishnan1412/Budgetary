from django.urls import path
from . import views



app_name = 'userperference'
urlpatterns = [
    path('', views.userinfo, name='preference'),
    path('userprofile', views.account_detail, name='userprofile')
]
