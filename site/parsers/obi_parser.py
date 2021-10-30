import requests
import bs4.element
import html5lib
from bs4 import BeautifulSoup
from typing import Any, List, Dict

main_href = 'https://www.obi.ru'
category_href = 'https://www.obi.ru/header-service/navigation/ru/ru/categories/'

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
        'accept-encoding': 'gzip, deflate, br',
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
        header: Dict[str, Any]
) -> bs4.element.Tag:
    '''
        Returns result of get request
        Args:
            s: requests.Session - session object,
            hr: str - html reference,
            header: Dict[str, Any] - request header dict
        Returns bs4.element.Tag
    '''

    html = s.get(hr, headers=header)
    if len(html.links) > 0:
        html = BeautifulSoup(html.content, 'html5lib')
    else:
        html = BeautifulSoup(html.text, 'html5lib')
    return html


def get_properties(properties: bs4.element.Tag) -> List[Dict[str, str]]:
    '''
        Returns properties of a good
        Args:
            properties: bs4.element.Tag - list of properties in html
        Returns List[Dict[str, str]]
    '''

    result = []
    for prop in properties:
        text = prop.text.replace('  ', '').replace('\n', '')
        if ':' in text:
            key, value = text.split(':')
            result.append(dict(name=key, value=value))
    return result


def get_good(
        s: requests.Session,
        hr: str,
        good: bs4.element.Tag,
        header: Dict[str, Any]
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

    header['path'] = hr.split(main_href)[-1]
    html = get_response(s, hr, header)

    return dict(
        name=good.text.replace('  ', '').replace('\n', ''),
        href=hr,
        photo='https:' + html.find('a', {'class': 'ads-slider__link js-ads-slider__zoom'}).get('href'),
        properties=get_properties(html.find_all('tr'))
    )


def get_goods(
        s: requests.Session,
        html: bs4.element.Tag,
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
            result.append(get_good(s, goods.find('a').get('href'), good, header))
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

    header['path'] = cl.find('a').get('href')
    header[
        'accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
    html = get_response(s, main_href + header['path'], header)
    return dict(
        name=cl.text.replace('  ', '').replace('\n', ''),
        href=main_href + header['path'],
        goods=get_goods(s, html, header, depth)
    )


def get_classes(
        s: requests.Session,
        html: bs4.element.Tag,
        header: Dict[str, Any],
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
        if ind >= depth[0]:
            break
        result.append(get_class(s, cl, header, depth[1:]))
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

    num_href = subcategory.find('a').get('href').split('/')[-1]
    header['path'] = '/header-service/navigation/ru/ru/categories/' + num_href
    html = get_response(s, category_href + num_href, header)

    return dict(
        name=subcategory.text.replace('  ', '').replace('\n', ''),
        href=category_href + num_href,
        classes=get_classes(s, html, header, depth)
    )


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
            result.append(get_subcategory(s, subcategory, header, depth[1:]))
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

    num_href = category.find('a').get('href').split('/')[-1]
    header['path'] = '/header-service/navigation/ru/ru/categories/' + num_href
    header['accept'] = '*/*'
    header['x-instana-l'] = '1,correlationType=web;correlationId=60c5a76ec670b450'
    header['x-instana-s'] = '60c5a76ec670b450'
    header['x-instana-t'] = '60c5a76ec670b450'
    html = get_response(s, category_href + num_href, header)

    return dict(
        name=category.text.replace('  ', '').replace('\n', ''),
        href=category_href + num_href,
        subcategories=get_subcategories(s, html, header, category.text.replace('  ', '').replace('\n', ''), depth)
    )


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
            result.append(get_category(s, category, header, depth[1:]))
    return result
