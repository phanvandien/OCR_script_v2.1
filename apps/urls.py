# my_ocr_app/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_file, name='upload_file'),
    path('result/', views.result_page, name='result_page'),
    path('download_excel/', views.download_excel, name='download_excel'),
]