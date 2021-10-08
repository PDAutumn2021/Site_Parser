# Натройка и запуск проекта

1. Устанавливаете лоально проект `git clone https://github.com/PDAutumn2021/Site_Parser.git`

2. Создаете вертуальную среду для python (в проекте используется Python 3.9) в коре проекта `python -m venv venv`

3. Активируете витруальную среду win:`source venv/Scripts/activate` linux:`source venv/bin/activate` (после успешной активации появиться `(venv)` в начале строки консоли)

4. Скачиваете пакеты ` pip install -r requirements.txt`

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