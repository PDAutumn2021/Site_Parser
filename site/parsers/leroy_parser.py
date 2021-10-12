import json
import requests

from site.parsers.utils import parse_category


def get_data(depth=[0, 0, 0, 0]):
    result = []

    s = requests.Session()
    categories_data = s.get('https://leroymerlin.ru/content/elbrus/moscow/ru/displayedCatalogue.json')
    to_parse = json.loads(categories_data.text)

    if depth[0] == 0:
        depth[0] = len(to_parse)
    for cat in to_parse[:depth[0]]:
        result.append(parse_category(s, cat, depth[1:]))

    return result

