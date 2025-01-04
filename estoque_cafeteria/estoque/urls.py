from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.login, name='login'),
    path('produtoview/', views.produtoview, name='produtoview'),
    path('estoqueview/', views.estoqueview, name='estoqueview'),
    path('offline/', views.offline, name='offline')  # Nova rota offline

]
 