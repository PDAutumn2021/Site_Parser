# Формат данных, возвращаемых парсерами

```python
[
    # Категория
    {
        'href': 'https://leroymerlin.ru/catalogue/hranenie/',
        'name': 'Хранение',
        # Подкатегория
        'subcategories': [{
            'href': 'https://leroymerlin.ru/catalogue/mebel/',
            'name': 'Мебель',
            # Подклассы
            'classes': [{
                'href': 'https://leroymerlin.ru/catalogue/shkafy-kupe/',
                'name': 'Шкафы-купе',
                # Товары
                'goods': [{
                    'href': 'https://leroymerlin.ru/product/shkaf-kupe-princessa-melaniya-turin-2502m1-90012642/',
                    'name': 'Шкаф-купе Принцесса Мелания Турин 2502.М1, 200х171х45.8 см',
                    'photo': 'https://res.cloudinary.com/lmru/image/upload/f_auto,q_auto,w_150,h_150,c_pad,b_white,d_photoiscoming.png/LMCode/90012642.jpg',
                    # Свойства
                    'properties': [
                        {
                            'name': 'Цена',
                            'value': 29700
                        },
                        {
                            'name': 'Ширина (см)',
                            'value': '171'
                        },
                        {
                            'name': 'Цвет',
                            'value': 'Темное дерево'
                        }
                    ]
                }]
            }],
        }]
    }
]
```