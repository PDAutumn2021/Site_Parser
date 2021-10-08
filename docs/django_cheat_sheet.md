# Шпаргалка по Django
## Миграции БД
В django есть встроенной класс для работы с БД. Этот класс спопобен интерприетировать python-код и самостоятельно выполнять запросы к БД, в том числе и изменять ее структуру.

Для храниения истории изменения в структуре БД django использует специальные файлы миграции, они расположены внутри каждого приложения в каталоге `migrations` и начинаются в 4-ех чисел.

Сами по себе эти фалы ничего не могут сделать, необходимо чтобы django проанализировал их (узнал какие уже выполнены, а какие новые) и сответственно примени нужные миграции. Выполнение миграций производится при помощи команды `python manage.py migrate`. Эту команду необходимо выполнять каждый раз когда меняется структура БД, т.е. добавляется новый файл миграции в каталог `migrations`.

## Примитивные Views
Одним из способов обработки запросов пользователя и отправления ему ответов в django является класcовый подход, где базовый класс родитель от которого наследуются другие классы называется View.

### Простейший пример
`urls.py` (далее в примерах этот файл бует осутствовать, но он подразумевается):
```python
from django.urls import path  
from . import views  
  
name = 'app'  
  
urlpatterns = [  
    path('page/', views.PageView.as_view(), name="page"),  
]
```
`views.py`:
```python
from django.http import HttpResponse
from django.views import View

class PageView(View):
    def get(self, request):
        # <view logic>
        # вернет result - как response с meme-type text и статусом 200
        return HttpResponse('result')
```
### Отправка JSON и метод POST
Кроме метода get можно принимать и обрабатывать post-зпросы, для этого соответственно нужно определить метод `post(self, request)`. Использоване методов можно совмещать в одном и том же классе. Привелем пример, используя теперь другой класс, используемый для отправки данных в формате json:
`views.py`:
```python
from django.http import HttpResponse, JsonResponse
from django.views import View

class PageView(View):
	def get(self, request):
		# при get-запросе верент result как text
        return HttpResponse('result')

    def post(self, request):
	    # при post-запросе верент словать как json
        return JsonResponse({'foo':'bar'}, safe=False)
```

### Ответ в виде шаблона
Для того чтобы отправть пользователю отрендеренный шаблон (html-страницу) можно использовать класс TemplateView:
`views.py`:
```python
from django.views.generic import TemplateView
  
class PageView(TemplateView):
	# вернет пользователю шаблон расположенный по пути */templates/path/page.html
    template_name = "path/page.html"
```

## Шаблонизатор
**Шаблоны обязательно  должны храниться в каталоге templates/<app_name>/**

В django есть собственный шаблонизатор, подробнее про него можно почитать на странице официальной документации:
- https://docs.djangoproject.com/en/3.2/ref/templates/language/
- https://docs.djangoproject.com/en/3.2/ref/templates/builtins/

### Команды
В шаблонизаторе django комады записываются в вснутри следующей последовательности симовлов `{% some_comand %}`

Комментарии можно определять следующим образом `{# comment #}`, тогда информация расположенная внутри е будет отправлена сервером пользователю после рендеринга. Но никто не запрещает использовать и `<!-- comment -->` в HTML и `// comment` в js

### Наследование
Предположим у нас есть сайт. В общем его структура +- одинакова, менятс только содержание. Тогда можно сделать какой-то базовай класс в который поместится скелет сайта с импортом всех стилей и скриптов, а также шапкой. подвалом и т.д. А всем остальным станицам сайта просто наследоваться от этого базовго шаблона. Таким образом если нужно будет применить изменения к скелету сайта у нас не будет необходимости делать изменения в десятках файлов.

Пример:
`base.html`:
```html
{% load static %}  
<!DOCTYPE html>  
<html lang="en">  
<head>  
 <meta charset="UTF-8">  
 <title>Base</title>  
 <link href="{% static '/bootstrap-5.1.2-dist/css/bootstrap.min.css' %}" rel="stylesheet">  
 <link href="{% static '/fontawesome-free/css/all.css' %}" rel="stylesheet">  
 <script src="{% static '/jquery-3.6.0-dist/jquery-3.6.0.min.js' %}"></script>  
</head>  
<body>
	<header>...</header>
	<nav>...</nav>
	{% block content %}
		Тут какой-то контент отображаемый на по дефолту
	{% endblock %}
	<footer>...</footer>
</body>  
</html>
``` 
`extended.html`:
```html
{% extends "base.html" %}
{% block content %}
	Тут мы перезаписыаем содержимое базого блока
{% endblock %}
```

### Статические файлы
Django имеет стандортный механизм для хранения статических фалов внутри проекта. Для того чтобы использовать эти фалы используется команда `{% load static %}` в паре с `{% static '/path/file.min.js' %}`. Первая позволяет использовать ключевое слово `static` в шаблоне. Вторая подставляет на свое место url до указанного файла.

### Динамическая генерация url
Для того чтобы не писать url вручную. Django шаблонизатор может подствалять их сам используя имя для url. Это становится особенно полезно когда менятся какой-либо url, в результате чего (если не использовать динамическую подстановку) приходится изменять все шаблоны использующие эту ссылку.

Объявить ссылку можно при помощи команды `{% url 'app_name:url_name' arg1 arg2 %}`. Где `app_name` - имя приложения, `url_name` - имя ссылки написанные в файле `urls.py`, `arg1 ...` - аргуманты.
Пример файла `urls.py`:
```python
name = 'main'  
  
urlpatterns = [  
    path('foo/<str:bar>/<int:id>', views.View.as_view(), name="foo_page"),  
]
```
Команда для даннго примера: `{% url 'main:foo_page' "cat" 13 %}`