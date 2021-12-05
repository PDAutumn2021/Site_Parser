from django.urls import path
from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

name = 'www'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('category/<str:category_name>/', views.CategoryListView.as_view(), name='category'),
    path('product/<int:pk>', views.ProductDetailView.as_view(), name='product'),

    path('about', views.about, name='aboutPage'),
    path('search', views.search, name='searchPage'),
    path('avtorization', views.avtorization, name='avtorizationPage'),
    path('registration', views.registration, name='registrationPage'),

    path('loader', views.loader, name='loader'),
]
urlpatterns += staticfiles_urlpatterns()
