from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


from main import views

urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    path('student/', views.guestStudent, name='guestStudent'),
    path('teacher/', views.guestFaculty, name='guestFaculty'),
    path('', include('main.urls')),
    path('', include('discussion.urls')),

    path('', include('exam.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

