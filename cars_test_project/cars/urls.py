"""URL-конфигурация приложения cars."""
from django.urls import path

from . import views

app_name = 'cars'

urlpatterns = [
    path('', views.index, name='index'),
    path('update_autoru_catalog', views.update_catalog, name='update_catalog'),
]
