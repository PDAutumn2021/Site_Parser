from api.models import Site, Product, Property, ProductsProperties, Pricing, Category
from parsers.obi_parser import get_data as obi_parser


def load():
    errors = {}

    try:
        site = Site.objects.get(name='OBI')
        data = obi_parser([{'Стройка': ['Плитка'], 'Всё для дома': ['Обои']}, 0, 0])

        errors['OBI'] = save_data_from_parser(site, data)
    except Exception as e:
        errors['OBI'] = 'error during handling parser'

    return errors


def save_data_from_parser(site: Site, data: dict):
    errors = []

    for item in data:
        # получаем товар, если не получилось пропускаем его и записываем в ошибки
        try:
            product, source = get_product(site, item)
        except Exception as e:
            errors.append({'item': item, 'message': 'error in get_product', 'error': e})
            continue

        # перезаписываем измененные данные о товаре
        try:
            if source != 'new':
                update_field(product, item, 'url')
                update_field(product, item, 'article')
                update_field(product, item, 'name')
                update_field(product, item, 'img')
                update_field(product, item, 'name')
                update_field(product, item, 'description')
            product.save()
        except Exception as e:
            errors.append({'item': item, 'product': product, 'message': 'error during changing product', 'error': e})
            continue

        # заносим данные в историю цен
        try:
            Pricing.objects.create(product=product, price=item['price'])
        except Exception as e:
            errors.append({'item': item, 'product': product, 'message': 'error during adding price', 'error': e})
            continue

        # перезаписываем свойства товара
        try:
            prop = 'initial'
            ProductsProperties.objects.filter(product=product).delete()
            for prop in item['properties']:
                property_obj, _ = Property.objects.get_or_create(name=prop['name'])
                ProductsProperties.objects.create(product=product, property=property_obj, value=prop['value'])
        except Exception as e:
            errors.append({'item': item, 'product': product, 'current_property': prop,
                           'message': 'error during adding property', 'error': e})
            continue

    return errors

def update_field(product: Product, item: dict, product_attr: str):
    """Обновляет поле товра если оно не совпадает с новым значением"""
    if getattr(product, product_attr) != item[product_attr]:
        setattr(product, product_attr, item[product_attr])


def get_product(site:Site, item:dict) -> tuple[Product, str]:
    """
    Возвращает объект товара из БД на основании словаря от парсера
    @param site: текущий объект сайт
    @param item: товар в виде словаря
    @return: продкут в виде django model и ключ, сообщающий по каком соответсвию был найден товар
    """
    if product := Product.objects.filter(site=site, article=item['article']):
        if len(product) > 1:
            raise Product.MultipleObjectsReturned()
        return product.first(), 'article'
    if product := Product.objects.filter(site=site, name=item['name']):
        if len(product) > 1:
            raise Product.MultipleObjectsReturned()
        return product.first(), 'name'
    if product := Product.objects.filter(site=site, url=item['url']):
        if len(product) > 1:
            raise Product.MultipleObjectsReturned()
        return product.first(), 'url'

    # если не получилось найти товар по его "условно уникальным" полям, то создаем новый
    category = Category.objects.get(name=item['category'])
    product = Product.objects.create(name=item['name'],
                                     site=site,
                                     url=item['url'],
                                     img=item['img'],
                                     category=category,
                                     subcategory=item['subcategory'],
                                     description=item['description'],
                                     article=item['article'], )
    return product, 'new'
