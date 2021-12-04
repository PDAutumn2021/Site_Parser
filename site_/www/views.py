from django.views.generic import TemplateView
from django.shortcuts import render
from django.http import HttpResponse

class Test(TemplateView):

    template_name = "test/test_tmp.html"


def index(request):
    return render(request, 'www/index.html')


def about(request):
    return render(request, 'www/about.html')


def product(request):
    return render(request, 'www/product.html')


def search(request):
    return render(request, 'www/search.html')


def avtorization(request):
    return render(request, 'www/avtorization.html')


def registration(request):
    return render(request, 'www/registration.html')