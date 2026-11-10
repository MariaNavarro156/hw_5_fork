from django.urls import path
from . import views

urlpatterns = [
    # HW2
    path('time', views.time_view, name='time'),
    path('sum', views.sum_view, name='sum'),
    # HW4
    path('', views.index, name='home'),
    path('index.html', views.index, name='index_html'),
    path('new', views.new, name='new'),
    path('createUser', views.createUser, name='createUser'),
    path('new_course', views.new_course, name='newCourse'),
    path('createCourse', views.create_course, name='createCourse'),
    path('new_lecture', views.new_lecture, name='newLecture'),
    path('createLecture', views.create_lecture, name='createLecture'),
    path('new_qr_upload', views.new_qr_upload, name='newQRUpload'),
    path('createQRCodeUpload', views.create_qr_upload, name='createQRUpload'),
    path('dumpUploads', views.dump_uploads, name='dumpUploads'),
]
