# Натройка и запуск проекта

1. Устанавливаете локально проект `git clone https://github.com/PDAutumn2021/Site_Parser.git`

2. Создаете виртуальную среду для python (в проекте используется Python 3.9) в коре проекта `python -m venv venv`

3. Активируете витруальную среду win:`source venv/Scripts/activate` linux:`source venv/bin/activate` (после успешной активации появиться `(venv)` в начале строки консоли)

4. Скачиваете пакеты `pip install -r requirements.txt`

5. Добавляете в проект файл `site/site_parser/protected.py` со следующм содержанием:
```python
# секретный ключ проекта (для разработки не важно что тут будет)
SECRET_KEY = 'some_key'
# список разрешенных хостов с которыми можно взамодействовать
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
# ваша БД
DB = {
        # возможно использование других СУБД см. https://docs.djangoproject.com/en/3.2/ref/settings/#engine
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'name',
        'USER': 'user',
        'PASSWORD': 'password',
        'HOST': 'example.com',
        'PORT': '3306',
}
```

6. Перейдите в каталог `site`

7. Выполните миграции БД `python manage.py migrate`

8. Можно запускать проект `python manage.py runserver`

9. Заполните БД, перейдя на страницу http://127.0.0.1:8000/loader/ (процедура не быстрая, ничего происходить не будет, как только прцедура закончится, откроется JSON с ошибками, которые возникли при выполнении)

10. Если работете в PyCharm, то для того, чтобы он не ругался на импорты нужно отметить каталог `site_` как `Sources Root` (правый клик `Mark Directory as -> Sources Root`) 