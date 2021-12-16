import datetime
import json
import time

from django.db.models import Max
from django.views.generic import TemplateView, DetailView
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.generic.base import ContextMixin

from parsers.loader import load
from api.models import Category, Product
from api.models import ProductsProperties
from api.models import Pricing


class BaseContextMixin(ContextMixin):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all().values('name', 'eng_name')
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
    translate = {
        'tiles': {
            'Shade': 'Оттенок',
            'Form': 'Форма',
            'TypeRoom': 'Тип помещений',
            'minWidth': 'Ширина',
            'minThickness': 'Толщина',
            'maxWidth': 'Ширина',
            'TypeWork': 'Вид работ',
            'minSquare': 'Площадь элемента',
            'Material': 'Материал',
            'minLength': 'Длина',
            'maxLength': 'Длина',
            'Room': 'Помещение',
            'Design': 'Дизайн',
            'Surface': 'Поверхность',
            'Country': 'Страна производства',
            'maxSquare': 'Площадь элемента',
            'LayingSurface': 'Поверхность укладки',
            'maxThickness': 'Толщина'
        },
        'wallpapers': {
            'BaseMaterial': 'Материал основы',
            'TextureWall': 'Фактура',
            'maxLengthWall': 'Длина рулона',
            'CountryWall': 'Страна производства',
            'DockinCanvases': 'Стыковка полотен',
            'CoverMaterial': 'Материал покрытия',
            'minLengthWall': 'Длина рулона',
            'RoomWall': 'Помещение',
            'minWeight': 'Вес штуки',
            'maxWeight': 'Вес штуки',
            'maxWidthWall': 'Ширина рулона',
            'minWidthWall': 'Ширина рулона',
            'DesignWall': 'Дизайн / Рисунок'
        }
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        filtered_products = self.get_products(kwargs['category_name'])
        context['products'] = self.get_product_list(filtered_products)
        context['total_count'] = len(filtered_products)
        context['itemPerPage'] = 9
        return context

    def get_product_dict(self, product_obj):
        product_dict = {}
        product_dict['id'] = product_obj.id
        product_dict['name'] = product_obj.name
        product_dict['price'] = product_obj.price

        product_dict['img'] = product_obj.img
        product_dict['description'] = product_obj.description
        product_dict['properties'] = (dict(zip(('name', 'value'), item)) for item in
                                      product_obj.productsproperties_set.values_list('property__name',
                                                                                             'value'))
        return product_dict

    def get_product_list(self, filtered_products):
        products_list = []
        if 'page' not in self.request.GET or 'itemPerPage' not in self.request.GET:
            beg = 0
            end = 20
        else:
            beg = int(self.request.GET['itemPerPage']) * (int(self.request.GET['page']) - 1)
            end = int(self.request.GET['itemPerPage']) * int(self.request.GET['page'])

        if beg > len(filtered_products):
            return []
        filtered_products = Product.objects.filter(id__in=filtered_products[beg:end])
        for product_obj in filtered_products:
            products_list.append(self.get_product_dict(product_obj))
        return products_list

    def get_products(self, category_name):
        filtered_products = ProductsProperties.objects.filter(product__category__eng_name=category_name)
        types = []

        for key, value in self.request.GET.items():
            if value == '':
                continue
            if 'type' in key:
                types.append(value)
            elif 'minPrice' == key:
                prices = [i['product'] for i in Pricing.objects.values('product')
                                             .filter(price__gte=float(value))
                                             .annotate(total=Max('date'))]
                filtered_products = filtered_products.filter(product__in=prices)
            elif 'maxPrice' == key:
                prices = [i['product'] for i in Pricing.objects.values('product')
                                             .filter(price__lte=float(value))
                                             .annotate(total=Max('date'))]
                filtered_products = filtered_products.filter(product__in=prices)
            elif 'min' in key:
                filtered_products = filtered_products.filter(value__gte=float(value),
                                                             property__name=self.translate[category_name][key])
            elif 'max' in key:
                filtered_products = filtered_products.filter(value__lte=float(value),
                                                             property__name=self.translate[category_name][key])
            elif 'page' in key.lower():
                continue
            else:
                filtered_products = filtered_products.filter(value=value,
                                                             property__name=self.translate[category_name][key])
        if len(types) > 0:
            filtered_products = filtered_products.filter(product__subcategory__in=types)

        filtered_products = filtered_products.values_list('product', flat=True).distinct()

        return filtered_products


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

        context['category_name'] = obj.first().category.eng_name
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


class LoaderView (TemplateView, BaseContextMixin):

    template_name = 'www/loader.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        start = time.time()

        context['errors'] = load()

        end = time.time()
        t = end - start

        context['time'] = f'{int(t // 60 // 60 % 60)} : {int(t // 60 % 60)} : {int(t % 60)}'

        return context


def about(request):
    return render(request, 'www/about.html')


def search(request):
    return render(request, 'www/search.html')


def avtorization(request):
    return render(request, 'www/avtorization.html')


def registration(request):
    return render(request, 'www/registration.html')
