"""URL-конфигурация проекта cars_test_project."""
from django.contrib import admin
from django.urls import path
from django.urls import include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('cars.urls', namespace='cars')),
]
