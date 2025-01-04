from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.login, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('estoqueview/', views.estoqueview, name='estoqueview'),
    path('offline/', views.offline, name='offline')  # Nova rota offline

]
 