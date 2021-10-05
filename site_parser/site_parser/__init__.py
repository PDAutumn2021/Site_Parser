import pymysql
pymysql.install_as_MySQLdb()

SECRET_KEY = 'django-insecure-pbi6=6%3as@kj2m)8_b2j%gav*rd0f%*u9&nl0&2h)m$z!*)08'

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

DB = {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'DB_NAME',
        'USER': 'DB_USER',
        'PASSWORD': 'DB_PASSWORD',
        'HOST': '127.0.0.1',
        'PORT': '5432',
     }
