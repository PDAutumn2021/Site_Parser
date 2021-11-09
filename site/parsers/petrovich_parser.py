import re
import bs4.element
import requests
import html5lib
from bs4 import BeautifulSoup
from typing import Tuple, Dict, Any, List

ITEMS_PER_PAGE = 20
URL_SORT_PART = '?sort=title_asc'
MAIN_URL = 'https://moscow.petrovich.ru/'
result =[]
s = requests.Session()
'''
Примеры заполнения аргументов
    get_data(['Интерьер и отделка',['Обои','Керамическая плитка и затирки'],['Мозаика','Фотообои']])
    get_data() - поиск всех данных вне зависимости от категорий
'''
def get_data(depth: List[Any] = [None, None, None, None]): #получаем значение и URL категорий, переходим на страницу выбранной категории
    soup = find_soup(MAIN_URL)
    categories_ul = soup.find('ul', class_='pt-list___2KAzV sections-list-item')
    categories=categories_ul.find_all('li')

    for category in categories:
        category_href =MAIN_URL+ category.find('a').attrs['href']
        category_name=category.find('span')
        d={'name':category_name.text, 'href':category_href}
        if (depth[0]==None) or ((d['name']==depth[0])): #выбор категории
                d['subcategory']=parce_subcategory(d['href'],depth)
                result.append(d)
    return result

def parce_item(href: str): #Поиск товаров в выбранном классе по страницам
    d_arr=[]
    soup = find_soup(href)
    items_div = soup.find('header', class_='product-list-header')
    items = items_div.find('p')
    item_number=items.text
    number=re.findall('\d+', item_number)
    number=int(number[0]) #количество товаров в данном классе
    page=number//ITEMS_PER_PAGE # номер страницы при отображении товаров

    k=0
    while (k<=page):
        items_data=None
        if (k==0):
            href_1=href+URL_SORT_PART
        else:
            href_1=href+URL_SORT_PART+'p='+str(k)
        soup = find_soup(href_1)
        items = soup.find_all('a', class_='title')
        for item in items:
            d={}
            d=add_name_and_url(item)
            d['photo']=item_img(d['href'])
            d['properties']=item_properties(d['href'])
            d_arr.append(d)
        k=k+1
    return d_arr

    
def item_img(href: str):# поиск изображения товара со страницы описания товара
    soup = find_soup(href)
    img = soup.find('div', class_='content-slide')
    img = img.find('img').attrs['data-src']
    return (img)


def item_properties(href: str):# поиск свойств товара со страницы описания товара
    d=[]
    soup = find_soup(href)
    price_div = soup.find('div', class_='price-details')
    price_array = price_div.find_all('p')
    del price_array[0]
    #price_array[0].text - цена по скидке (по карте клуба)
    #price_array[1].text - цена без скидки
    price = price_array[1].text
    d_prop={}
    d_prop['name']='Цена'
    d_prop['value']=price

    item_properties_div = soup.find('ul', class_='product-properties-list listing-data')
    item_properties = item_properties_div.find_all('li')
    for property in item_properties:
        d_prop={}
        property_name=property.find('div', class_='title').text
        property_value=property.find('div', class_='value').text
        d_prop['name']=property_name
        d_prop['value']=property_value
        d.append(d_prop)
    return (d)


def parce_subcategory(href: str, depth :List[Any]):#получаем значение и URL субкатегорий, переходим на страницу выбранной субкатегории
    d=[]
    
    soup = find_soup(href)
    subcategories = soup.find_all('a', class_='catalog-subsection')
    for subcategory in subcategories:
        d_sub=add_name_and_url(subcategory)
        if (depth[1]==None) or ((d_sub['name']==depth[1])):# выбор субкатегории
            d_sub['classes']=parce_classes(d_sub['href'],depth)
            d.append(d_sub)
        else:
            for dep in depth[1]:
                if (d_sub['name']==dep):# выбор субкатегории
                    d_sub['classes']=parce_classes(d_sub['href'], depth)
                    d.append(d_sub)        
    return (d)


def parce_classes(href: str, depth: List[Any]):#получаем значение и URL классов, переходим на страницу выбранного класса
    d=[]
    soup = find_soup(href)
    classes = soup.find_all('a', class_='catalog-subsection')
    for clas in classes:
        d_class=add_name_and_url(clas)
        if (depth[2]==None) or ((d_class['name']==depth[2])):# выбор класса, если аргумент для класса задан типами None и Str
            d_class['goods']=parce_item(d_class['href'])
            d.append(d_class)
        else:
            for dep in depth[2]:
                if (d_class['name']==dep):# выбор класса, если аргумент для класса задан типом List
                    d_class['goods']=parce_item(d_class['href'])
                    d.append(d_class) 
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
