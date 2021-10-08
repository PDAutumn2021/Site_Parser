from django.urls import path
from . import views

name = 'www'

urlpatterns = [
    path('', views.Test.as_view(), name="test_name"),
]