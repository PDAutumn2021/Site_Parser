from django.urls import path
from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

name = 'www'

urlpatterns = [
    path('', views.index, name='homePage'),
    path('about', views.about, name='aboutPage'),
    path('product', views.product, name='productPage'),
    path('search', views.search, name='searchPage'),
    path('avtorization', views.avtorization, name='avtorizationPage'),
    path('registration', views.registration, name='registrationPage'),
    path('loader', views.loader, name='loader'),
]
urlpatterns += staticfiles_urlpatterns()
