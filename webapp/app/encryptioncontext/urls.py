from django.urls import path
  
from . import views

app_name = 'encryptioncontext'
urlpatterns = [
    path('', views.create, name='home'),
    path('create', views.create, name='create'),
    path('authenticate', views.authenticate, name='authenticate'),
]
