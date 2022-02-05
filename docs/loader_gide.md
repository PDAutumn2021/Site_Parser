# Запуск и остановка демона для развертывания на проде
```
uwsgi --stop /tmp/site_parser_master.pid # это путь из uwsgi.ini
uwsgi --ini uwsgi.ini # запусткать из директории в которой находится manage.py
```
# Запуск загрузчика
```
ssh std-1548.ist.mospolytech.ru -l std

cd Site_Parser/
source venv/bin/activate
cd site_/
python manage.py shell

from parsers.loader import load
load()
```
