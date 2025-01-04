from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('estoqueview/', views.estoqueview, name='estoqueview')
]
 