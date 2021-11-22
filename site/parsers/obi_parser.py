import requests
import bs4.element
import html5lib
from bs4 import BeautifulSoup
from typing import Any, List, Dict

main_href = 'https://www.obi.ru'
category_href = 'https://www.obi.ru/header-service/navigation/ru/ru/categories/'
MAX_ATTEMPT_NUMBER = 5

def get_data(depth: List[Any]=[0,0,0,0]) -> List[Dict[str, Any]]:
  '''
        Returns the parsed data from the Leroy Merlin site
        Args:
            depth: List[int] - list of depths where:
                if you want all depths as int:
                    depth[0] - depth of categories
                    depth[1] - depth of subcategories
                    depth[2] - depth of classes
                    depth[3] - depth of goods
                Example: [0, 0, 0, 0]
                if you want get some special categories and subcategories:
                    depth[0] - names of special categories as keys and
                               names of special subcategories as values
                    depth[1] - depth of classes
                    depth[2] - depth of goods
                Example: [{'Техника':['Электротовары'], 'Стройка':['Плитка', 'Окна']}, 1, 1]
        returns: Dict[str, Any]
  '''

  header = {
        'authority': 'www.obi.ru',
        'method': 'GET',
        'path': '/',
        'scheme': 'https',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'http',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'cache-control': 'max-age=0',
        'referer': 'https://www.obi.ru/',
        'sec-ch-ua': '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': "Windows",
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36'
  }
  s = requests.Session()
  html = get_response(s, main_href, header)
  return get_categories(s, html, header, depth)


def get_response(
        s: requests.Session,
        hr: str,
        header: Dict[str, Any],
        attempt: int = 1
) -> bs4.element.Tag:
    '''
        Returns result of get request
        Args:
            s: requests.Session - session object,
            hr: str - html reference,
            header: Dict[str, Any] - request header dict
            attempt: int - номер попытки запросить данные
        Returns bs4.element.Tag
    '''

    html = s.get(hr, headers=header)
    if len(html.links) > 0:
        html = BeautifulSoup(html.content, 'html5lib')
    else:
        html = BeautifulSoup(html.text, 'html5lib')

    # если нас забанили, то ждем 15 секунд и отправляем запрос снова (пока не пустят)
    if html.text.find('Ð£Ð²Ð°Ð¶Ð°ÐµÐ¼ÑÐµ Ð¿Ð¾ÑÐµÑÐ¸ÑÐµÐ»Ð¸!') > 0 and attempt <= MAX_ATTEMPT_NUMBER:
        time.sleep(15.)
        html = get_response(s, hr, header, attempt+1)
    elif attempt > MAX_ATTEMPT_NUMBER:
        raise Exception('Поздравляю, нас забанили! ')

    return html


def get_properties(properties: bs4.element.Tag, subcategory_name: str) -> List[Dict[str, str]]:
    '''
        Returns properties of a good
        Args:
            properties: bs4.element.Tag - list of properties in html
        Returns List[Dict[str, str]]
    '''
    countries=['Россия', 'Белоруссия', 'Украина', 'Китай', 'Турция', 'Испания', 'Индия', 'Италия', 'Вьетнам', 'Словакия', 'Бельгия', 'Германия', 'Великобритания', 'Республика Корея']
    result = []
    for prop in properties:
        text = prop.text.replace('  ', '').replace('\n', '')
        if ':' in text:
            text = text.partition(':')
            key = text[0]
            value = text[2]
            if subcategory_name == "Обои":
                if "Материал основы" in key:
                    val_names = ['Флизелин', 'Бумага', 'Винил', 'Стеклоткань']
                    if value in val_names:
                        result.append(dict(name=key, value=value))
                    else:
                        result.append(dict(name=key, value="Другое"))
                
                elif "Длина рулона" in key:
                    value = value.split(" ")
                    value_num = value[0].split(',')
                    value_num = '.'.join(value_num)
                    val = float(value_num)
                    result.append(dict(name=key, value=val))
                    
                elif "Ширина рулона" in key:
                    value = value.split(" ")
                    value_num = value[0].split(',')
                    value_num = '.'.join(value_num)
                    val = float(value_num)
                    result.append(dict(name=key, value=val))
                
                elif "Материал покрытия" in key:
                    val_names = ['Флизелин', 'Бумага', 'Винил', 'Стеклоткань']
                    if value in val_names:
                        result.append(dict(name=key, value=value))
                    else:
                        result.append(dict(name=key, value="Другое"))
                
                elif "Помещение" in key:
                    val_names = ['Производственное помещение', 'Жилая комната', 'Кухня', 'Детская']
                    if value == "Офис":
                        value = "Производственное помещение"
                    if value in val_names:
                        result.append(dict(name=key, value=value))
                    else:
                        result.append(dict(name=key, value="Жилая комната"))
                
                elif "Дизайн" in key:
                    key = "Дизайн / Рисунок"
                    val_names = ['Орнамент', 'Однотонный', 'Полосы', 'Фотопринт', 'Имитация материала', 'Надписи', 'Рисунок']
                    if value in val_names:
                        if value == "Орнамент":
                            value = "Узор"
                        result.append(dict(name=key, value=value))
                    else:
                        result.append(dict(name=key, value="Другое"))
                
                elif "Фактура" in key:
                    val_names = ['Гладкая', 'Рельефная']
                    if value in val_names:
                        result.append(dict(name=key, value=value))
                    else:
                        result.append(dict(name=key, value="Другое"))
                
                elif "Стыковка полотен" in key:
                    val_names = ['С подбором рисунка', 'Без подбора рисунка']
                    if value in val_names:
                        result.append(dict(name=key, value=value))
                    elif value == "Смещенное наложение рисунка":
                        result.append(dict(name=key, value="С подбором рисунка"))
                    else:
                        result.append(dict(name=key, value="Без подбора рисунка"))
                    
                elif "Вес" in key:
                    key = "Вес упаковки"
                    value = value.split(" ")
                    value_num = value[0].split(',')
                    value_num = '.'.join(value_num)
                    val = float(value_num)
                    if value[1] == "г":
                        val = val/1000
                    result.append(dict(name=key, value=val))
                
                elif "Страна производства" in key:
                    if value in countries:
                       result.append(dict(name=key, value=value))
                    else: 
                        result.append(dict(name=key, value="Другое"))
            
            
            if subcategory_name == "Плитка":   
                if "Оттенок" in key:
                    val_names = ['Светлый','Темный','Комбинированный']
                    if value in val_names:
                       result.append(dict(name=key, value=value))
                    else: 
                        result.append(dict(name=key, value="Другое"))
                
                elif "Поверхность" in key:
                    val_names = ['Глянцевая','Рельефная','Матовая']
                    if value in val_names:
                       result.append(dict(name=key, value=value))
                    else: 
                        result.append(dict(name=key, value="Другое"))
                
                elif "Материал" in key:
                    val_names = ['Керамика','Глина','Натуральный камень', 'Гипс', 'Керамогранит', 'Клинкер', 'Цемент', 'Бетон', 'Пластик', 'Стекло', 'Металл', 'Мрамор', 'Дерево', 'Резина']
                    if value in val_names:
                       result.append(dict(name=key, value=value))
                    else: 
                        result.append(dict(name=key, value="Другое"))
                
                elif "Форма" in key:
                    val_names = ['Прямоугольник','Квадрат','Шестигранник', 'Угол', 'Треугольник', 'Произвольная', 'Восьмигранник']
                    if value in val_names:
                       result.append(dict(name=key, value=value))
                    else: 
                        result.append(dict(name=key, value="Произвольная"))
                    
                elif "Ширина" in key:
                    for result_part in result:
                        if "Ширина" in result_part.values():
                            break
                    else:
                        value = value.split(" ")
                        value_num = value[0].split(',')
                        value_num = '.'.join(value_num)
                        val = float(value_num)
                        result.append(dict(name=key, value=val))
                
                elif "Вид работ" in key:
                    val_names = ['Внутренние','Наружные']
                    if value in val_names:
                       result.append(dict(name=key, value=value))
                    else: 
                        result.append(dict(name=key, value="Внутренние"))
                
                elif "Поверхность укладки" in key:
                    val_names = ['Стена','Пол', 'Фасад','Цоколь','Лестница']
                    if value in val_names:
                       result.append(dict(name=key, value=value))
                    else: 
                        result.append(dict(name=key, value="Другое"))
                
                elif "Тип помещений" in key:
                    val_names = ['Сухие','Влажные']
                    if value in val_names:
                       result.append(dict(name=key, value=value))
                    else: 
                        result.append(dict(name=key, value="Сухие"))
                
                elif "Помещение" in key:
                    val_names = ['Кухня','Ванная комната','Производственное помещение','Жилая комната']
                    if value == "Офис":
                        value = "Производственное помещение"
                    if value in val_names:
                       result.append(dict(name=key, value=value))
                    else: 
                        result.append(dict(name=key, value="Жилая комната"))
                
                elif "Дизайн" in key:
                    val_names = ['Однотонный','Имитация материала','Орнамент','Авторский', 'Мозаика']
                    if value in val_names:
                       result.append(dict(name=key, value=value))
                    else: 
                        result.append(dict(name=key, value="Другое"))
                
                elif "Количество в упаковке" in key:
                    value = value.split(" ")
                    val = int(value[0])
                    result.append(dict(name="Кол-во в упаковке", value=val))
                
                elif "Площадь элемента" in key:
                    value = value.split(" ")
                    value_num = value[0].split(',')
                    value_num = '.'.join(value_num)
                    val = float(value_num)
                    result.append(dict(name=key, value=val))
                
                elif "Длина" in key:
                    value = value.split(" ")
                    value_num = value[0].split(',')
                    value_num = '.'.join(value_num)
                    val = float(value_num)
                    result.append(dict(name=key, value=val))
                
                elif "Вес штуки" in key:
                    value = value.split(" ")
                    value_num = value[0].split(',')
                    value_num = '.'.join(value_num)
                    val = float(value_num)
                    if value[1] == "г":
                        val = val/1000
                    result.append(dict(name=key, value=val))
                
                elif "Толщина" in key:
                    value = value.split(" ")
                    value_num = value[0].split(',')
                    value_num = '.'.join(value_num)
                    val = float(value_num)
                    result.append(dict(name=key, value=val))
                
                elif "Страна производства" in key:
                    if value == "КНР":
                        value = "Китай"
                    if value in countries:
                       result.append(dict(name=key, value=value))
                    else: 
                        result.append(dict(name=key, value="Другое"))
                    
    return result


def get_good(
        s: requests.Session,
        hr: str,
        good: bs4.element.Tag,
        header: Dict[str, Any],
        cl: str,
        subcategory_name: str
) -> Dict[str, Any]:
    '''
        Returns dict defining good
        Args:
            s: requests.Session - session object,
            hr: str - html reference,
            good: bs4.element.Tag - html defining good,
            header: Dict[str, Any] - request header dict
        Returns Dict[str, Any]
    '''
    class_name = cl.text.replace("\n","")
    header['path'] = hr.split(main_href)[-1]
    html = get_response(s, hr, header)
    photo_href = html.find('img', {'class': 'ads-slider__image'})
    if photo_href is None:
        photo_href=""
    else:
        photo_href = 'https:' + photo_href.get('src')
    
    article_text = html.find('span',{'class': 'article-number'})
    if article_text is None:
        article_text = ""
        article_number = ''
    else:
        article_text = article_text.text
        article_number = ''
        for word in article_text:
            if word.isdigit():
                article_number = article_number + word
        article_number = int(article_number)

    price_text = html.find('strong',{'data-ui-name': 'ads.price.strong'})
    if price_text is None:
        price_text = ""
    else:
        price_text = price_text.text
        price_text = price_text.replace(',', '.').replace(' ', '')
        price_text = float(price_text)

    description_text = []
    descriptions = html.find('div',{'class': 'description-text js-toggle-additional-content toggle-additional-content toggle-additional-content--text-centered clearfix'})
    if descriptions is None:
        descriptions = ""
    else:
        descriptions = descriptions.find_all('p')
        if descriptions is None:
            descriptions = ""
            description_text = ''
        else:
            for p in descriptions:
                p=p.text
                description_text.append(p)
            description_text[0]=''

    return dict(
        category=subcategory_name,
        subcategory=class_name,
        site_name="OBI",
        url=hr,
        name=good.text.replace('  ', '').replace('\n', ''),
        img= photo_href,
        description = description_to_str(description_text),
        price = price_text,
        article = article_number,
        properties=get_properties(html.find_all('tr'), subcategory_name)
    )


def description_to_str(description: (list or str), joiner: str='\n'):
    """Конвертирует описание из списока в строку
    :param description: описание для объекта
    :param joiner: строка, вставляемая между двумя элементами массива
    :return: описание в формате строки
    """
    if isinstance(description, list):
        answer = ''
        for item in description:
            if item:
                answer += item + joiner
        return answer
    elif isinstance(description, str):
        return description
    return ''


def get_goods(
        s: requests.Session,
        subcategory_name: str,
        html: bs4.element.Tag,
        cl: str,
        header: Dict[str, Any],
        depth: List[Any] = [0]
) -> List[Dict[str, Any]]:
    '''
        Returns list of goods
        Args:
            s: requests.Session - session object,
            html: bs4.element.Tag - html defining goods,
            header: Dict[str, Any] - request header dict,
            depth: List[Any] - depth object
        Returns List[Dict[str, Any]]
    '''

    result = []
    p = 0
    n = 0
    ma = depth[0]
    while True:
        goods_ = html.find_all('li', {'class': 'product large'})
        if depth[0] == 0:
            ma += len(goods_)
        for goods in goods_:
            if n >= ma:
                return result
            good = goods.find('p')
            if good is None or good.text.replace('  ', '').replace('\n', '') == '':
                continue
            result.append(get_good(s, goods.find('a').get('href'), good, header, cl, subcategory_name))
            n += 1

        if p != 0 and len(html.find_all('a', {'class': 'pagination-bar__btn js-queryLink scrollup disabled'})) != 0:
            break
        elif len(html.find_all('a', {'class': 'pagination-bar__btn js-queryLink scrollup'})) == 0:
            break
        hr = html.find_all('a', {'class': 'pagination-bar__btn js-queryLink scrollup'})[-1].get('href')
        header['accept'] = '*/*'
        header['path'] = hr.split(main_href)[-1]
        html = get_response(s, hr, header)
        p += 1
    return result


def get_class(
        s: requests.Session,
        subcategory_name: str,
        cl: bs4.element.Tag,
        header: Dict[str, Any],
        depth: List[Any] = [0]
) -> Dict[str, Any]:
    '''
        Returns dict defining class
        Args:
            s: requests.Session - session object,
            cl: bs4.element.Tag - html defining class,
            header: Dict[str, Any] - request header dict,
            depth: List[Any] - depth object
        Returns Dict[str, Any]
    '''
    result=[]
    header['path'] = cl.find('a').get('href')
    header[
        'accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
    html = get_response(s, main_href + header['path'], header)
    goods=get_goods(s, subcategory_name, html, cl, header, depth)
    result=result+goods
    return result


def get_classes(
        s: requests.Session,
        html: bs4.element.Tag,
        header: Dict[str, Any],
        subcategory_name: str,
        depth: List[Any] = [0, 0]
) -> List[Dict[str, Any]]:
    '''
        Returns list of classes
        Args:
            s: requests.Session - session object,
            html: bs4.element.Tag - html defining classes,
            header: Dict[str, Any] - request header dict,
            depth: List[Any] - depth object
        Returns List[Dict[str, Any]]
    '''

    result = []
    classes = html.find_all('div', {'class': 'headr__nav-cat-row'})
    if depth[0] == 0:
        depth[0] = len(classes)
    for ind, cl in enumerate(classes):
        if subcategory_name == "Обои":
            cl_name = cl_name_wp
        if subcategory_name == "Плитка":
            cl_name = cl_name_tile
        if 'cl_name' in locals():
            if cl.text.replace('  ', '').replace('\n', '') in cl_name:
                result = result + get_class(s, subcategory_name, cl, header, depth[1:])
        else:
            if ind >= depth[0]:
                break
            result = result + get_class(s subcategory_name,, cl, header, depth[1:])
    return result


def get_subcategory(
        s: requests.Session,
        subcategory: bs4.element.Tag,
        header: Dict[str, Any],
        depth: List[Any] = [0, 0]
) -> Dict[str, Any]:
    '''
        Returns dict defining subcategory
        Args:
            s: requests.Session - session object,
            subcategory: bs4.element.Tag - html defining subcategory,
            header: Dict[str, Any] - request header dict,
            depth: List[Any] - depth object
        Returns Dict[str, Any]
    '''
    result=[]
    num_href = subcategory.find('a').get('href').split('/')[-1]
    header['path'] = '/header-service/navigation/ru/ru/categories/' + num_href
    html = get_response(s, category_href + num_href, header)
    subcategory_name = subcategory.text.replace("\n","")
    classes = get_classes(s, html, header, subcategory_name, depth)
    result = result + classes
    return result


def get_subcategories(
        s: requests.Session,
        html: bs4.element.Tag,
        header: Dict[str, Any],
        cat_name: str,
        depth: List[Any] = [0, 0, 0]
) -> List[Dict[str, Any]]:
    '''
        Returns list of subcategories
        Args:
            s: requests.Session - session object,
            html: bs4.element.Tag - html object defining subcategories,
            header: Dict[str, Any] - request header dict,
            cat_name: str - parent category name,
            depth: List[Any] - depth object
        Returns List[Dict[str, Any]]
    '''

    result = []
    subcategories = html.find_all('div', {'class': 'headr__nav-cat-row'})

    if depth[0] == 0:
        depth[0] = len(subcategories)
    for ind, subcategory in enumerate(subcategories):
        if isinstance(depth[0], dict):
            if subcategory.text.replace('  ', '').replace('\n', '') in depth[0][cat_name]:
                result.append(get_subcategory(s, subcategory, header, depth[1:]))
        elif isinstance(depth[0], int):
            if ind >= depth[0]:
                break
            result = result + get_subcategory(s, subcategory, header, depth[1:])
    return result


def get_category(
        s: requests.Session,
        category: bs4.element.Tag,
        header: Dict[str, Any],
        depth: List[Any] = [0, 0, 0]
) -> Dict[str, Any]:
    '''
        Returns object defining category
        Args:
            s: requests.Session - session object,
            category: bs4.element.Tag - object defining category,
            header: Dict[str, Any] - request header dict,
            depth: List[Any] - depth object
        Returns Dict[str, Any]
    '''
    result=[]
    num_href = category.find('a').get('href').split('/')[-1]
    header['path'] = '/header-service/navigation/ru/ru/categories/' + num_href
    header['accept'] = '*/*'
    header['x-instana-l'] = '1,correlationType=web;correlationId=60c5a76ec670b450'
    header['x-instana-s'] = '60c5a76ec670b450'
    header['x-instana-t'] = '60c5a76ec670b450'
    html = get_response(s, category_href + num_href, header)
    result = result + get_subcategories(s, html, header, category.text.replace('  ', '').replace('\n', ''), depth)
    
    return result


def get_categories(
        s: requests.Session,
        html: bs4.element.Tag,
        header: Dict[str, Any],
        depth: List[Any] = [0, 0, 0, 0]
) -> List[Dict[str, Any]]:
    '''
        Returns list of categories
        Args:
            s: requests.Session - session object,
            html: bs4.element.Tag - object defining categories,
            header: Dict[str, Any] - request header dict,
            depth: List[Any] - depth object
        Returns List[Dict[str, Any]]
    '''

    result = []
    categories = html.find_all('div', {"class": "headr__nav-cat-row"})

    if depth[0] == 0:
        depth[0] = len(categories)
    for ind, category in enumerate(categories):
        if 'Доставка' in category.text:
            break
        if isinstance(depth[0], dict):
            if category.text.replace('  ', '').replace('\n', '') in depth[0]:
                result.append(get_category(s, category, header, depth))
        elif isinstance(depth[0], int):
            if ind >= depth[0]:
                break
            result = result + get_category(s, category, header, depth[1:])
    return result
