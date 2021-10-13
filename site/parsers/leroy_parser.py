import json
import requests
from typing import List, Dict, Any

from utils import parse_category


def get_data(depth: List[int] = [0, 0, 0, 0]) -> Dict[str, List[Any]]:
    '''
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
    for cat in to_parse[:depth[0]]:
        result.append(parse_category(s, cat, depth[1:]))

    return result

