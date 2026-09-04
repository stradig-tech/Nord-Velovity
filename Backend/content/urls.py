from django.urls import path
from . import views

app_name = 'content'

urlpatterns = [
    path('', views.blog_list_view, name='blog_list'),
    path('<slug:slug>/', views.blog_detail_view, name='blog_detail'),
]
