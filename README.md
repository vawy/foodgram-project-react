# Описание
**Проект Foodgram - Продуктовый помощник**

![workflow](https://github.com/vawy/foodgram-project-react/actions/workflows/main.yml/badge.svg) 

### Технологии
- Python 3.10
- Django 4.1
- Django REST Framework 3.14
- Gunicorn
- Nginx
- PostgreSQL
- Docker
- GitHub Actions

[foodgram2023.hopto.org](foodgram2023.hopto.org)

### Развертка и запуск проекта локально

#### Клонирование репозитория
Клонировать репозиторий и перейти в него в командной строке:

```
git@github.com:vawy/foodgram-project-react.git
cd foodgram-project-react
```

#### Изменение файлов

- Добавить .env в корень проекта

#### Запуск проекта
```
cd infra/
docker-compose -d --build
```

#### Миграции проекта, добавление юзера, сбор статики
```
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
docker-compose exec backend python manage.py collectstatic --no-input
docker-compose exec backend python manage.py load_ingredients 
```

P.s. Добавить `winpty` при ошибке:
`
the input device is not a TTY.  If you are using mintty, try prefixing the command with 'winpty'
`
    
### API
Документация API доступна по следующему эндпоинту:

    http://<project_ip>/redoc

#### Регистрация
Для регистрации отправьте POST-запрос на эндпоит `api/v1/auth/signup/`, в теле запроса укажите:
```JSON
{
    "username": "your_username",
    "email": "your_email"
}
```
При успешной регистрации сервер вернет данные с кодом 200.
Далее ~~на указанный электронный адрес~~ в папке sent_emails директории проекта будет лог-файл эмитирующий электронное письмо. В нем указан верификационный ключ, его необходимо сохранить для дальнейшего получения JWT-токена
#### Получение JWT-токена
Для получения JWT-токена, отправьте POST-запрос на эндпоит `api/v1/auth/token/`, в теле запроса укажите:
```JSON
{
    "username": "your_username",
    "confirmation_code": "your_code"
}
```
на энипоинт:

В ответ API вернёт JWT-токен
~~~JSON
{
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjIwODU1Mzc3LCJqdGkiOiJkY2EwNmRiYTEzNWQ0ZjNiODdiZmQ3YzU2Y2ZjNGE0YiIsInVzZXJfaWQiOjF9.eZfkpeNVfKLzBY7U0h5gMdTwUnGP3LjRn5g8EIvWlVg"
}
~~~

`token` - Сам JWT-токен
Токен используется в заголовке запроса под ключом `Bearer`


## Автор

### Василий Вигилянский 

##### IP
`178.154.224.46`
