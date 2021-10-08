from django.urls import path
from . import views

name = 'api'

urlpatterns = [
    path('swagger/', views.SwaggerView.as_view(), name="swagger"),
]