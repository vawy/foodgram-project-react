![workflow status](https://github.com/vawy/foodgram-project-react/actions/workflows/main.yml/badge.svg)

## Описание

#### Проект Foodgram – Продуктовый помощник
На этом сервисе пользователи смогут публиковать рецепты, подписываться 
на публикации других пользователей, добавлять понравившиеся рецепты в список
«Избранное», а перед походом в магазин скачивать сводный список 
продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

#### Что могут делать неавторизованные пользователи
- Создать аккаунт.
- Просматривать рецепты на главной.
- Просматривать отдельные страницы рецептов.
- Просматривать страницы пользователей.
- Фильтровать рецепты по тегам.
#### Что могут делать авторизованные пользователи
- Входить в систему под своим логином и паролем.
- Выходить из системы (разлогиниваться).
- Менять свой пароль.
- Создавать/редактировать/удалять собственные рецепты
- Просматривать рецепты на главной.
- Просматривать страницы пользователей.
- Просматривать отдельные страницы рецептов.
- Фильтровать рецепты по тегам.
- Работать с персональным списком избранного: добавлять в него рецепты или удалять их, просматривать свою страницу избранных рецептов.
- Работать с персональным списком покупок: добавлять/удалять любые рецепты, выгружать файл с количеством необходимых ингредиентов для рецептов из списка покупок.
- Подписываться на публикации авторов рецептов и отменять подписку, просматривать свою страницу подписок.
#### Что может делать администратор
Администратор обладает всеми правами авторизованного пользователя.
Плюс к этому он может:
- изменять пароль любого пользователя,
- создавать/блокировать/удалять аккаунты пользователей,
- редактировать/удалять любые рецепты,
- добавлять/удалять/редактировать ингредиенты.
- добавлять/удалять/редактировать теги.

Все эти функции реализованы в стандартной админ-панели Django.

### Технологии

- Python 3.10
- Django 4.1
- Django REST Framework 3.14
- Gunicorn
- Nginx
- PostgreSQL
- Docker

### Запуск проекта локально

- Клонирование удаленного репозитория
```bash
git clone git@github.com:vawy/foodgram-project-react.git
cd infra
```
- В директории /infra создайте файл .env, с переменными окружения:
```bash
SECRET_KEY=<Your_some_long_string>
DB_ENGINE='django.db.backends.postgresql'
DB_NAME='postgres'
POSTGRES_USER='postgres'
POSTGRES_PASSWORD=<Your_password>
DB_HOST='db'
DB_PORT=5432
```
- Сборка и развертывание контейнеров
```bash
docker-compose up -d --build
```
- Выполните миграции, соберите статику, создайте суперпользователя
```bash
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py collectstatic --no-input
docker-compose exec backend python manage.py createsuperuser
```
- Наполните базу данных ингредиентами
```bash
docker-compose exec backend python manage.py load_ingredients
```
- или наполните базу тестовыми данными (включают посты и пользователей)
```bash
docker-compose exec backend python manage.py loaddata data/data.json 
```
- Стандартная админ-панель Django доступна по адресу [`https://localhost/admin/`](https://localhost/admin/)
- Документация к проекту доступна по адресу [`https://localhost/api/docs/`](`https://localhost/api/docs/`)

### Запуск API проекта в dev-режиме

- Клонирование удаленного репозитория (см. выше)
- Создание виртуального окружения и установка зависимостей
```bash
cd backend
python -m venv venv
. venv/Scripts/activate (windows)
. venv/bin/activate (linux)
pip install -r -requirements.txt
```
- в foodgram/setting.py замените БД на встроенную SQLite
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
```
- Примените миграции и соберите статику
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput
```
- Наполнение базы данных ингредиентами
```bash
python manage.py load_ingredients
```
- Запуск сервера
```bash
python manage.py runserver 
```

Проект доступен по адресу: [foodgram2023.hopto.org](http://foodgram2023.hopto.org)

Документация к API проекта: [foodgram2023.hopto.org/api/docs/](http://foodgram2023.hopto.org/api/docs/)

Доступ в админку: admin@t.ru / 12345
