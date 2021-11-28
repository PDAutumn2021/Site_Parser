import re
import bs4.element
import requests
import html5lib
from bs4 import BeautifulSoup
from typing import Tuple, Dict, Any, List

ITEMS_PER_PAGE = 20
URL_SORT_PART = '?sort=title_asc'
MAIN_URL = 'https://moscow.petrovich.ru'
CAT_URL = 'https://moscow.petrovich.ru/catalog/1533/'

result =[]
s = requests.Session()
'''
Примеры заполнения аргументов
    get_data(['Обои','Керамическая плитка и затирки'],['Мозаика','Фотообои']])
    get_data() - поиск всех данных вне зависимости от категорий
'''
def get_data(depth: List[Any] = [None, None, None]): #получаем значение и URL категорий, переходим на страницу выбранной категории
    d={'site-name':"Петрович"}
    parce_category(d, depth, CAT_URL)
    return result

def parce_item(d, href: str): #Поиск товаров в выбранном классе по страницам
    d_arr=[]
    soup = find_soup(href)
    items_div = soup.find('header', class_='product-list-header')
    items = items_div.find('p')
    item_number=items.text
    number=re.findall('\d+', item_number)
    number=int(number[0]) #количество товаров в данном классе
    page=number//ITEMS_PER_PAGE # количество страниц при отображении товаров
    i=0
    k=0
    while (k<=page):
        if (k==0):
            href_1=href+URL_SORT_PART
        else:
            href_1=href+URL_SORT_PART+'&p='+str(k)
        soup = find_soup(href_1)
        items = soup.find_all('a', class_='title')
        k=k+1
        for item in items:
            err_sum=0
            d_item=None
            while ((err_sum<3) and (d_item==None)):
                try:
                    d_item={}
                    d_item=add_name_and_url(item)
                    d_item['photo']=item_img(d_item['href'])
                    d['name']=d_item['name']
                    d['img']=d_item['photo']
                    d['url']=d_item['href']
                    item_properties(d,d_item['href'])
                except:
                    err_sum=err_sum+1
                    d_item=None
    return d


    
def item_img(href: str):# поиск изображения товара со страницы описания товара
    soup = find_soup(href)
    img = soup.find('div', class_='content-slide')
    img = img.find('img').attrs['data-src']
    return (img)


def item_properties(d, href: str):# поиск свойств товара со страницы описания товара
    soup = find_soup(href)
    price_div = soup.find('div', class_='price-details')
    price_array = price_div.find_all('p')
    del price_array[0]
    #price_array[0].text - цена по скидке (по карте клуба)
    #price_array[1].text - цена без скидки
    price = price_array[1].text
    d['price']=price
    description=soup.find('p', class_='product-description-text').text
    d['description']=description
    code_div=soup.find('div', class_='product-actions-panel')
    code=code_div.find('span', class_='pt-c-secondary').text # уникальный код товара
    d['article']=code
    item_properties_div = soup.find('ul', class_='product-properties-list listing-data')
    item_properties = item_properties_div.find_all('li')
    d['properties']=[]
    for property in item_properties:
        d_prop={}
        property_name=property.find('div', class_='title').text
        property_value=property.find('div', class_='value').text
        d_prop['name']=property_name
        d_prop['value']=property_value
        d['properties'].append(d_prop)
    rename_items(d)
    return (d)


def parce_category(d, depth :List[Any], href: str):#получаем значение и URL субкатегорий, переходим на страницу выбранной категории
    soup = find_soup(href)
    categories = soup.find_all('a', class_='catalog-subsection')
    for category in categories:
        d_cat=add_name_and_url(category)
        if (depth[1]==None) or ((d_cat['name']==depth[0])):# выбор субкатегории
            d['category']=d_cat['name']
            parce_subcategory(d ,depth, d_cat['href'])
        else:
            for dep in depth[1]:
                if (d_cat['name']==dep):# выбор субкатегории
                   d['category']=d_sub['name']
                   parce_subcategory(d ,depth, d_sub['href'])   
    return (d)


def parce_subcategory(d, depth: List[Any],href: str):#получаем значение и URL классов, переходим на страницу выбранного класса
    soup = find_soup(href)
    subcategories = soup.find_all('a', class_='catalog-subsection')
    for subcategory in subcategories:
        d_sub=add_name_and_url(subcategory)
        if (depth[1]==None) or ((d_sub['name']==depth[1])):# выбор класса, если аргумент для класса задан типами None и Str
            d['subcategory']=d_sub['name']
            d_sub['goods']=parce_item(d, d_sub['href'])
        else:
            for dep in depth[1]:
                if (d_sub['name']==dep): # выбор класса, если аргумент для класса задан типом List
                    d['subcategory']=d_sub['name']
                    d_sub['goods']=parce_item(d, d_sub['href']) 
    return (d)


def add_name_and_url(item: bs4.element.Tag):# функция для заполнения основных характеристик объекта (URL и имя)
    item_name=item.text
    item_href=MAIN_URL+ item.attrs['href']
    d={'name':item_name, 'href':item_href}
    return(d)


def find_soup(href: str):
    classes_data=s.get (href)
    soup = BeautifulSoup(classes_data.text, 'html5lib')
    return(soup)


def rename_items(d):
    if d['category']=='Керамическая плитка и затирки':
        d['category']=['Керамическая плитка']
    facture=False
    arr_price=re.findall('\d+', d['price'])
    d['price']=''
    for price in arr_price:
        d['price']=d['price']+price
    for prop in d['properties']:
        if (prop['name']=='Тип товара'):
            if prop['value']=='Малярный флизелин':
                d['subcategory']='Флизелиновые обои'
        if (prop['name']=='Страна-производитель'):
            prop['name']='Страна производства'
        if (d['category']=='Обои'):
            if (prop['name']=='Материал основы'):
                if (prop['value']=='Стеклохолст'):
                    prop['value']=='Стеклоткань'
            if (prop['name']=='Длина, м'):
                prop['name']='Длина рулона'
            if prop['name']=='Покрытие':
                prop['name']='Материал покрытия'
                if (prop['value']=='Вспененный винил'or'Винил горячего тиснения'):
                    prop['value']='Винил'
            if prop['name']=='Рисунок':
                prop['name']='Дизайн/Рисунок'
                if (prop['value']=='Полосы' or prop['value']=='Линии'):
                    prop['value']='Полосы'
                elif prop['value']=='Без рисунка':
                    prop['value']='Однотонный'
                elif (prop['value']=='Бетон' or prop['value']=='Дерево' or prop['value']=='Доски' or prop['value']=='Кирпич' or prop['value']=='Камень' or prop['value']=='Мрамор'or prop['value']=='Штукатурка'):
                    prop['value']='Имитация материала'
                elif (prop['value']=='Узор'):
                    prop['value']='Узор'
                elif (prop['value']=='Животные' or prop['value']=='Звезды' or prop['value']=='Карта' or prop['value']=='Космос' or prop['value']=='Листья' or prop['value']=='Круги' or prop['value']=='Перья' or prop['value']=='Фрукты' or prop['value']=='Цветы'):
                    prop['value']='Рисунок'
                elif (d['subcategory']=='Фотообои'):
                    prop['value']='Фотопринт'
                else:
                    prop['value']='Другое'
            if prop['name']=='Помещение':
                arr_room=[]
                prop['value']=prop['value'].split(', ')
                l_room=False
                for pr in prop['value']:
                    if pr=='Офис':
                        arr_room.append('Производственное помещение')
                    if pr=='Кухня':
                        arr_room.append('Кухня')
                    elif (pr=='Гардеробная' or pr=='Гостинная' or pr=='Прихожая' or pr=='Спальня')and(l_room==False):
                        l_room=True
                        arr_room.append('Жилое помещение')
                prop['value']=arr_room

            if (prop['name']=='Ширина, м'):
                prop['name']='Ширина рулона'
            if (prop['name']=='Фактура'):
                if prop['value']=='Тисненые':
                    prop['value']='Рильефная'
                if prop['value']=='Тисненые':
                    prop['value']='Рильефная'
                else:
                    prop['value']='Гладкая'
            if (prop['name']=='Положение рисунка'):
                prop['name']='Стыковка полотен'
                if prop['value']=='Без подгона':
                    prop['value']='Без подбора рисунка'
                else:
                    prop['value']='C подбором рисунка'
            if (prop['name']=='Вес, кг'):
                prop['name']='Вес упаковки'
        if d['subcategory']=='Фотообои':
            d['subcategory']='Фотообои/Декоративные'
            d['properties'].append({'name':'Дизайн/Рисунок', 'value':'Фотопринт'})
        if (d['category']=='Плитка'):
            square=1
            if d['subcategory']=='Мозаика':
                d['subcategory']='Плитка-мозаика'
            for prop in d['properties']:
                if (prop['name']=='Материал'):
                    if (prop['value']=='Натуральный камень' or prop['value']=='Камень'):
                        d['subcategory'] ='Натуральный камень'
                if (prop['name']=='Цвет'):
                    prop['name']=='Оттенок'
                    if (prop['value']=='Абсолютно белый' or prop['value']=='Багамы' or prop['value']=='Бежевый' or prop['value']=='Бежевый мрамор' or prop['value']=='Белая луна' or prop['value']=='Бело-бежевый' or prop['value']=='Бело-серый' or prop['value']=='Белый' or prop['value']=='Бирюзовый' or prop['value']=='Голубой' or prop['value']=='Желтый' or prop['value']=='Жемчуг' or prop['value']=='Зеленый' or prop['value']=='Кремовый' or prop['value']=='Песочный' or prop['value']=='Розовый' or prop['value']=='Светло-бежевый' or prop['value']=='Светло-голубой' or prop['value']=='Светло-зеленый' or prop['value']=='Светло-коричневый' or prop['value']=='Светло-розовый' or prop['value']=='Светло-серый' or prop['value']=='Светлый' or prop['value']=='Серый' or prop['value']=='Серебряный' or prop['value']=='Сиреневый' or prop['value']=='Слоновая кость'):
                        prop['value']='Светлый'
                    elif (prop['value']=='Антрацит' or prop['value']=='Бежево-коричневый' or prop['value']=='Бежево-серый' or prop['value']=='Бронзовый' or prop['value']=='Графитовый' or prop['value']=='Кофейный' or prop['value']=='Красный' or prop['value']=='Медно-коричневый' or prop['value']=='Коричнево-серый' or prop['value']=='Коричневый' or prop['value']=='Оранжевый' or prop['value']=='Охра' or prop['value']=='Серо-коричневый' or prop['value']=='Серый' or prop['value']=='Темно-зеленый' or prop['value']=='Синий' or prop['value']=='Темно-бежевый' or prop['value']=='Темно-коричневый' or prop['value']=='Темный' or prop['value']=='Терракотовый' or prop['value']=='Темно-серый' or prop['value']=='Фиолетовый' or prop['value']=='Черный'):
                        prop['value']='Темный'
                    else:
                        prop['value']='Комбинированный'
                facture=false
                if (prop['name']=='Фактура'):
                    if (prop['value']!='Гладкая'):
                        facture=True
                if (prop['name']=='Материал'):
                    if (prop['value']=='Керамическая плитка' or prop['value']=='Плитка керамическая под мозаику'):
                        prop['value']='Керамика'
                    if (prop['value']=='Камень'):
                        prop['value']='Натуральный камень'
                    if (prop['value']=='Красная глина' or prop['value']=='Огнеупорная глина, песок, известняк, пигменты'):
                        prop['value']='Глина'
                    if (prop['value']=='Стекло/Камень/Металл' or prop['value']=='Стекло/камень' or prop['value']=='Стекломасса'):
                        prop['value']='Стекло'
                    if (prop['value']=='Натуральный мрамор'):
                        prop['value']='Мрамор'
                if (prop['name']=='Форма'):
                    if (prop['value']=='Квадратная'):
                        prop['value']='Квадрат'
                    if (prop['value']=='Прямоугольная'):
                        prop['value']='Прямоугольник'
                if (prop['name']=='Ширина, мм'):
                    prop['name']=='Ширина'
                    prop['value']=float(prop['value'])/10
                if (prop['name']=='Применение'):
                    prop['name']=='Поверхность укладки'
                    if (prop['value']=='Напольная'):
                        prop['value']='Пол'
                    elif(prop['value']=='Настенная'):
                        prop['value']='Стена'
                    else:
                        prop['value']='Другое'
                if (prop['name']=='Стилистика'):
                   prop['name']='Дизайн'
                   if (prop['value']=='Без рисунка' or prop['value']=='Грес' or prop['value']=='Кабанчик моноколор' or prop['value']=='Моноколор'):
                        prop['value']='Однотонный'
                   if (prop['value']=='Бетон' or prop['value']=='Дерево' or prop['value']=='Камень' or prop['value']=='Кирпич' or prop['value']=='Металл' or prop['value']=='Мрамор' or prop['value']=='Мрамор строительный'):
                        prop['value']='Имитация материала'
                   if (prop['value']=='Геометрия' or prop['value']=='Кабанчик класика' or prop['value']=='Плитка белая'):
                        prop['value']='Орнамент'
                   if (prop['value']=='Арт-деко' or prop['value']=='Винтаж' or prop['value']=='Классика' or prop['value']=='Клинкер' or prop['value']=='Минимализм' or prop['value']=='Модерн' or prop['value']=='Минимализм' or prop['value']=='Прованс' or prop['value']=='Пэчворк'):
                        prop['value']='Авторский'
                   if (prop['value']=='Мозаика камень' or prop['value']=='Без рисунка' or prop['value']=='Без рисунка' or prop['value']=='Без рисунка'):
                        prop['value']='Мозаика'
                   if (prop['name']=='Количество штук в упаковке, шт'):
                        prop['name']='Кол-во в упаковке'   
                        number=prop['value']
                   if (prop['name']=='Длина, мм'):
                        square=square*float(prop['value'])*0.001
                        prop['name']='Длина'
                        prop['value']=float(prop['value'])*0.1
                   if (prop['name']=='Ширина, мм'):
                        square=square*float(prop['value']*0.001)
                        prop['name']='Ширина'
                        prop['value']=float(prop['value'])*0.1
                   if (prop['name']=='Вес, кг'):
                        prop['name']='Вес штуки'
                        prop['value']=float(prop['value'])/number
                   if (prop['name']=='Толщина, мм'):
                        prop['name']='Толщина'
        if facture==True:
            d['properties'].append({'name':'Поверхность', 'value':'Рельефная'})
    result.append(d.copy())
    return (result);
