# Foodrgam

 Продуктовый помощник - дипломный проект части курса на Яндекс.Практикум по Django и DRF.

 Это онлайн-сервис и API для него. 

 Здесь пользователи могут публиковать рецепты,

 Подписываться на публикации других пользователей,

 Перед походом в магазин Можно будет скачать список продуктов :grinning:

## О проекте 

- Проект завернут в Docker-контейнерах;
- Проект был развернут на сервере: <http://158.160.80.191/>
  
## Стек технологий
- Python
- Django
- Django REST Framework
- PostgreSQL
- Docker

## Зависимости
- Перечислены в файле backend/requirements.txt


## Для запуска на локальной машине

1. Слонируйте репозиторий к себе на гитхаб
2. Из директории `/infra/` выполните команду `docker-compose up -d --build`
3. Выполните миграции `python manage.py makemigrations`, `python manage.py migrate`
4. Создайте Администратора `python manage.py createsuperuser`
5. Соберите статику `python manage.py collectstatic`
6. Загрузите фикстуры в базу данных `python recipes/utils.py`

Креды:
  Log: admin
  Pass: admin12345
