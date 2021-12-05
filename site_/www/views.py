from django.views.generic import TemplateView, DetailView
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.generic.base import ContextMixin

from parsers.loader import load
from api.models import Category, Product


class BaseContextMixin(ContextMixin):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all().values_list('name', flat=True)
        return context


class HomeView (TemplateView, BaseContextMixin):

    template_name = 'www/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = self.get_products()
        return context

    def get_products(self):
        products_list = []
        products_objs = Product.objects.filter()[:3]

        for i, product_obj in enumerate(products_objs):
            product_dict = {}
            product_dict['id'] = product_obj.id
            product_dict['name'] = product_obj.name
            product_dict['price'] = product_obj.price
            product_dict['img'] = product_obj.img
            product_dict['description'] = product_obj.description
            product_dict['properties'] = ( dict(zip(('name', 'value'), item)) for item in product_obj.productsproperties_set.values_list('property__name', 'value') ) # список вида [{'name': 'Страна', 'value': 'Китай'}, {'name': 'Цвет', 'value': None}...], который содрежит все возможные для данной категории свойства
            products_list.append(product_dict)

        return products_list


class CategoryListView (TemplateView, BaseContextMixin):

    template_name = 'www/search.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # self.request.GET - тут лежат передаваемые get-параметры
        # kwargs['category_name'] - тут лежит название текущей категории

        context['products'] = self.get_products()
        context['total_count'] = Product.objects.filter(category__name=kwargs['category_name']).count()
        return context

    def get_products(self):
        products_list = []
        products_objs = Product.objects.filter()[:20]

        for i, product_obj in enumerate(products_objs):
            product_dict = {}
            product_dict['id'] = product_obj.id
            product_dict['name'] = product_obj.name
            product_dict['price'] = product_obj.price
            product_dict['img'] = product_obj.img
            product_dict['description'] = product_obj.description
            product_dict['properties'] = ( dict(zip(('name', 'value'), item)) for item in product_obj.productsproperties_set.values_list('property__name', 'value') ) # список вида [{'name': 'Страна', 'value': 'Китай'}, {'name': 'Цвет', 'value': None}...], который содрежит все возможные для данной категории свойства
            products_list.append(product_dict)

        return products_list


class ProductDetailView (TemplateView, BaseContextMixin):

    template_name = 'www/product.html'
    model = Product

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        obj = Product.objects.filter(pk=kwargs['pk'])
        context['object'] = list(obj.values())[0]
        context['object'].update({'price': obj.first().price})
        context['object'].update({'site': obj.first().site.name})
        context['object'].update({'properties': (dict(zip(('name', 'value'), item))
                                                 for item in obj.first().productsproperties_set
                                                                        .values_list('property__name', 'value')
                                                 )
                                  })

        context['category_name'] = obj.first().category.name
        context['recommendations'] = self.get_recommendations()
        return context

    def get_recommendations(self):
        products_list = []
        products_objs = Product.objects.filter()[:6]

        for i, product_obj in enumerate(products_objs):
            product_dict = {}
            product_dict['num'] = i
            product_dict['id'] = product_obj.id
            product_dict['img'] = product_obj.img
            product_dict['name'] = product_obj.name
            product_dict['price'] = product_obj.price
            products_list.append(product_dict)

        return products_list


def about(request):
    return render(request, 'www/about.html')


def search(request):
    return render(request, 'www/search.html')


def avtorization(request):
    return render(request, 'www/avtorization.html')


def registration(request):
    return render(request, 'www/registration.html')


def loader(request):
    result = load()
    return JsonResponse(result, safe=False)
