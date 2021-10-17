import time
import random
import re
import json
import bs4.element
import requests
from bs4 import BeautifulSoup
from typing import Tuple, Dict, Any, List


def get_data(depth: List[Any] = [0, 0, 0, 0]) -> List[Dict[str, Any]]:
    '''
        Returns the parsed data from the Leroy Merlin site

        Args:
            depth: List[int] - list of depths where:
                depth[0] - depth of categrories
                depth[1] - depth of subcategories
                depth[2] - depth of classes
                depth[3] - depth of goods

        returns: Dict[str, List[Any]]
    '''
    result = []

    s = requests.Session()
    categories_data = s.get('https://leroymerlin.ru/content/elbrus/moscow/ru/displayedCatalogue.json')
    to_parse = json.loads(categories_data.text)

    if depth[0] == 0:
        depth[0] = len(to_parse)
    for ind, cat in enumerate(to_parse):
        if isinstance(depth[0], dict):
            if cat['name'] in depth[0]:
                result.append(parse_category(cat, depth))
        elif isinstance(depth[0], int):
            if ind > depth[0]:
                break
        result.append(parse_category(s, cat, depth[1:]))

    return result

api_key = None
request_id = None
main_href = 'https://leroymerlin.ru'


def get_response(s: requests.Session, href: str, timeout_range: Tuple = (5, 10)) -> bs4.element.Tag:
  '''
        Returns response to parse

        Args:
            s: requests.Session - session object
            href: str - html reference string
            timeout_range: Tuple - range of random timeout
                timeout_range[0] - lower
                timeout_range[1] - upper

        returns: bs4.element.Tag
  '''

  header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4174.0 Safari/537.36',
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
  }
  time.sleep(random.randint(timeout_range[0], timeout_range[1]))
  response = s.get(href, headers=header)
  html = BeautifulSoup(response.text)
  return html


def parse_good(s: requests.Session, good: Dict[str, Any]) -> Dict[str, Any]:
    '''
        Returns a parsed good object

        Args:
            s: requests.Session - session object
            good: Dict[str, Any] - object defining good

        return: Dict[str, Any]
    '''

    dict_go = dict(
        name=good['displayedName'],
        photo=good['mediaMainPhoto']['desktop'],
        href=main_href + good['productLink'],
        properties=[]
    )
    dict_go['properties'].append(dict(name='Цена', value=good['price']['main_price']))
    good_html = get_response(s, dict_go['href'])
    for term, definition in zip(
            good_html.find_all('dt', {'class': 'def-list__term'}),
            good_html.find_all('dd', {'class': 'def-list__definition'})
    ):
        dict_go['properties'].append(dict(name=term.text.strip(), value=definition.text.strip()))
    return dict_go


def parse_class(s: requests.Session, cl: Dict[str, Any], depths: List[int] = [0]) -> Dict[str, Any]:
    '''
        Returns a parsed class object

        Args:
            s: requests.Session - session object
            cl: Dict[str, Any] - object defining class
            depths: List[int] - object defining depth

        return: Dict[str, Any]
    '''

    global api_key
    global request_id
    dict_cl = dict(
        name=cl['name'],
        href=main_href + cl['sitePath'],
        goods=[]
    )

    if api_key is None:
        header = get_headers('get-api-key', cl['sitePath'])
        get_api_key = s.get(dict_cl['href'], headers=header).text
        api_key = re.search('"apiKey":"(.*?)"', get_api_key).group(1)
        request_id = re.search('"requestID":"(.*?)"', get_api_key).group(1)
    header = get_headers('get-data-model', api_key, 'a', request_id)
    model = json.loads(
        s.get('https://api.leroymerlin.ru/hybrid/v1/getModel', params=(('pathname', cl['sitePath']), ('region', '')),
              headers=header).text)
    data = {
        "customerId": "GA1.2.1317799358.1634020624",
        "facets": [],
        "familyIds": [model['properties']['familyId']],
        "limit": 80,
        "offset": 0,
        "regionId": model['properties']['regionId'],
        "searchMethod": "DEFAULT",
        "suggest": "true"
    }
    max_len = int(model['properties']['productsCount'])
    offset = 0
    if depths[0] == 0:
        depths[0] = max_len
    while offset < max_len and offset < depths[0]:
        data['offset'] = offset
        resp = s.post('https://api.leroymerlin.ru/hybrid/v1/getProducts', data=json.dumps(data), headers=header).text
        goods = json.loads(resp)
        for good in goods['content']:
            if offset >= depths[0]:
                break
            offset += 1
            dict_cl['goods'].append(parse_good(good))
    return dict_cl


def parse_subcategory(s: requests.Session, sub: Dict[str, Any], depths: List[int] =[0, 0]) -> Dict[str, Any]:
    '''
        Returns a parsed subcategory object

        Args:
            s: requests.Session - session object
            sub: Dict[str, Any] - object defining subcategory
            depths: List[int] - object defining depth

        return: Dict[str, Any]
    '''

    dict_sub = dict(
        name=sub['name'],
        href=main_href + sub['sitePath'],
        classes=[]
    )
    if depths[0] == 0:
        depths[0] = len(sub['childs'])
    for cl in sub['childs'][:depths[0]]:
        dict_sub['classes'].append(parse_class(s, cl, depths[1:]))
    return dict_sub


def parse_category(s: requests.Session, cat: Dict[str, Any], depths: List[Any] = [0, 0, 0]) -> Dict[str, Any]:
    '''
        Returns a parsed category object

        Args:
            s: requests.Session - session object
            cat: Dict[str, Any] - object defining category
            depths: List[int] - object defining depth

        return: Dict[str, Any]
    '''

    dict_cat = dict(
        name=cat['name'],
        href=main_href + cat['sitePath'],
        subcategories=[]
    )
    if depths[0] == 0:
        depths[0] = len(cat['childs'])
    for ind, sub in enumerate(cat['childs']):
        if isinstance(depths[0], dict):
            if sub['name'] in depths[0][cat['name']]:
                dict_cat['subcategories'].append(parse_subcategory(sub, depths[1:]))
        elif isinstance(depths[0], int):
            if ind > depths[0]:
                break
            dict_cat['subcategories'].append(parse_subcategory(sub, depths[1:]))
    return dict_cat


def get_headers(event: str, *args) -> Dict[str, str]:
  '''
        Returns headers based on the event

        Args:
            event: str - name of event

        return: Dict[str, str]
  '''

  if event == 'get-api-key':
    return {
        'authority': 'leroymerlin.ru',
        'method': 'GET',
        'path': args[0],
        'scheme': 'https',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'cache-control': 'max-age=0',
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
  elif event == 'get-data-model':
    header = {
      'Accept': 'application/json, text/plain, */*',
      'Accept-Encoding': 'gzip, deflate, br',
      'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
      'Connection': 'keep-alive',
      'Content-Type': 'application/json;charset=UTF-8',
      'Host': 'api.leroymerlin.ru',
      'Origin': 'https://leroymerlin.ru',
      'Referer': 'https://leroymerlin.ru/',
      'sec-ch-ua': '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
      'sec-ch-ua-mobile': '?0',
      'sec-ch-ua-platform': "Windows",
      'Sec-Fetch-Dest': 'empty',
      'Sec-Fetch-Mode': 'cors',
      'Sec-Fetch-Site': 'same-site',
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36',
      'x-api-key': args[0],
      'x-api-option': args[1],
      'x-request-id': args[2]
    }
  return header