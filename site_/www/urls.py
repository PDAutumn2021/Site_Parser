from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from www import views

name = 'www'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('category/<str:category_name>/', views.CategoryListView.as_view(), name='category'),
    path('product/<int:pk>', views.ProductDetailView.as_view(), name='product'),

    path('about', views.about, name='aboutPage'),
    path('search', views.search, name='searchPage'),
    path('avtorization', views.avtorization, name='avtorizationPage'),
    path('registration', views.registration, name='registrationPage'),

    path('landing', views.LandingView.as_view(), name='landing'),
    path('loader', views.LoaderView.as_view(), name='loader'),
]
urlpatterns += staticfiles_urlpatterns()
