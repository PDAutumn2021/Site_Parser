import time
import random
import re
import bs4.element
import requests
from bs4 import BeautifulSoup
from typing import Tuple, Dict, Any, List

result =[]
s = requests.Session()


def get_dataset():
    main_data= s.get('https://moscow.petrovich.ru/')
    soup = BeautifulSoup(main_data.text)
    categories_ul = soup.find('ul', class_='pt-list___2KAzV sections-list-item')
    categories=categories_ul.find_all('li')

    for category in categories:
        category_href ='https://moscow.petrovich.ru/'+ category.find('a').attrs['href']
        category_name=category.find('span')
        d={'name':category_name.text, 'href':category_href}
        if (d['href']=='https://moscow.petrovich.ru//catalog/1533/'): #выбор категории "Интерьер и отделка"
            #print('обработка субкатегории ',category_name.text)
            d['subcategory']=parce_subcategory(d['href'])
        result.append(d)
    return result

def parce_item(href):
    d_arr=[]
    i=0
    items_data = s.get(href)
    items_soup = BeautifulSoup(items_data.text)
    items_div = items_soup.find('header', class_='product-list-header')
    items = items_div.find('p')
    item_number=items.text
    number=re.findall('\d+', item_number)
    number=int(number[0]) #количество товаров в данном классе

    page=number//20 # количество страниц, на которых располагаются товары данного класса

    k=0
    while (k<=page):
        try:
            items_data=None
            if (k==0):
                href_1=href+'?sort=title_asc'
            else:
                    href_1=href+'?sort=title_asc&p='+str(k)
            items_data = s.get(href_1)
            items_soup = BeautifulSoup(items_data.text)
            items = items_soup.find_all('a', class_='title')
            
            for item in items:
                i=i+1
                #if (i>3): break      -для более быстрой проверки работы программы (удалить при полной уверенности в работоспособности программы)
                d={}
                item_href=item.attrs['href']
                item_text = item.text
                d['name']= item_text
                d['href']='https://moscow.petrovich.ru/'+item_href
                d['photo']=item_img(d['href'])
                #print('№',i,' ',d['name'])
                d['properties']=item_properties(d['href'])
                d_arr.append(d)
        except requests.exceptions.ConnectionError as e:
            pass
        except Exception as e:
            logger.error(e)
            randomtime = random.randint(1,5)
            logger.warn('ERROR - Retrying again website %s, retrying in %d secs' % (url, randomtime))
            time.sleep(randomtime)
            continue
        k=k+1
    return d_arr
    
def item_img(href):
    item_data = s.get (href)
    item_soup = BeautifulSoup(item_data.text, "html.parser")
    img = item_soup.find('div', class_='content-slide')
    img = img.find('img').attrs['data-src']
    return (img)



def item_properties(href):
    d=[]
    item_data = s.get (href)
    item_soup = BeautifulSoup(item_data.text)
    price_div = item_soup.find('div', class_='price-details')
    price_array = price_div.find_all('p')
    del price_array[0]
    #price_array[0].text - цена по скидке (по карте клуба)
    #price_array[1].text - цена без скидки
    price = price_array[1].text
    d_prop={}
    d_prop['name']='Цена'
    d_prop['value']=price

    item_properties_div = item_soup.find('ul', class_='product-properties-list listing-data')
    item_properties = item_properties_div.find_all('li')
    for property in item_properties:
        d_prop={}
        property_name=property.find('div', class_='title').text
        property_value=property.find('div', class_='value').text
        d_prop['name']=property_name
        d_prop['value']=property_value
        d.append(d_prop)
    return (d)

def parce_subcategory(href):
    d=[]
    subcategory_data=s.get (href)
    soup = BeautifulSoup(subcategory_data.text)
    subcategories = soup.find_all('a', class_='catalog-subsection')
    for subcategory in subcategories:
        subcategory_href ='https://moscow.petrovich.ru/'+ subcategory.attrs['href']
        subcategory_name =subcategory.text
        d_sub={'name':subcategory_name, 'href':subcategory_href}
        if (d_sub['href']=='https://moscow.petrovich.ru//catalog/1351/') or (d_sub['href']=='https://moscow.petrovich.ru//catalog/12102/'):# парсинг только плитки  и обоев
            d_sub['classes']=parce_classes(d_sub['href'])
        d.append(d_sub)
    return (d)

def parce_classes(href):
    d=[]
    classes_data=s.get (href)
    soup = BeautifulSoup(classes_data.text)
    classes = soup.find_all('a', class_='catalog-subsection')
    for clas in classes:
        class_href ='https://moscow.petrovich.ru/'+ clas.attrs['href']
        class_name =clas.text
        d={'name':class_name, 'href':class_href}
        #print('обработка  класса ',class_name)
        d['goods']=parce_item(d['href'])
    return (d)
