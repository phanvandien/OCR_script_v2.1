# apps/urls.py
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.upload_file, name='home'),
    path('upload/', views.upload_file, name='upload_file'),
    path('result/', views.result_page, name='result_page'),
    path('get_progress/', views.get_progress_status, name='get_progress_status'),
    path('edit_record/', views.edit_record, name='edit_record'),
    path('replace_image/', views.replace_image, name='replace_image'),
    path('download_excel/', views.download_excel, name='download_excel'),
    #path('mark_viewed/', views.mark_viewed, name='mark_viewed'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)