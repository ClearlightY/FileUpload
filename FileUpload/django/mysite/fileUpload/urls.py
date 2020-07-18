from django.urls import path

from . import views

urlpatterns = [
    path('textCheck', views.textCheck, name='textCheck'),
    path('check', views.check, name='check'),
    path('check_result', views.check_result, name='check_result'),
    path('globalUpload', views.globalUpload, name='globalUpload'),
    path('fileMerge', views.fileMerge, name='fileMerge'),
    path('file_download', views.file_download, name='file_download'),
]
