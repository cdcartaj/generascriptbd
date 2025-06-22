
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('generar-pc9-pie-amount-descarga/', views.generar_sql_pc9_pie_amount_descarga, name='generar_pc9_pie_amount_descarga'),
    path('generar-pc9-pie-amount-preview/', views.generar_sql_pc9_pie_amount_preview, name='generar_pc9_pie_amount_preview'),
    
]
