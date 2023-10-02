# Subscribe Service

Сервис подписок

* **Язык приложения:** Python 3.11
* **Поддерживаемые протоколы взаимодействия:** REST API
* **Инфраструктурные зависимости:** Postgres
* **Зависимости от системных пакетов:** отсутствуют
* **Зависимости от расширений PostgreSQL:** отсутствуют
* **Часть окружения:** development
* **Минимальные системные требования:** 1 CPU, 1Gb RAM

## Поддержка сервиса

Группа разработки:

* Иван Баженов (*[@sendhello](https://github.com/sendhello)*)

## Описание обязательных методов для запуска сервиса

### Запуск сервиса
```commandline
# Из корня проекта
docker compose up --build
```

### Документация
* http://127.0.0.1/api/subscribe/openapi (Swagger)
* http://127.0.0.1/api/subscribe/openapi.json (openapi)

## Описание дополнительных методов сервиса

### Запуск functional-тестов
Установка зависимостей requirements-dev.txt из корня проекта

```commandline
pytest -vv subscribe_service
```

### Запуск линтеров
Установка зависимостей requirements-dev.txt из корня проекта

```commandline
isort subscribe_service
flake8 subscribe_service
black --skip-string-normalization subscribe_service
```

### Описание ENV переменных

| Имя переменной          | Возможное значение             | Описание                                  |
|:------------------------|--------------------------------|:------------------------------------------|
| DEBUG                   | False                          | Режим отладки                             |
| PROJECT_NAME            | Auth                           | Название сервиса (отображается в Swagger) |
| ENVIRONMENT             | dev                            | Имя окружения                             |
| SHOW_TRACEBACK          | true                           | Показывать трейсбек в http-ответе         |
| SUBSCRIBE_POSTGRES_HOST | subscribe-postgres             | Путь к БД Postgres                        |
| SUBSCRIBE_POSTGRES_PORT | 5432                           | Порт БД Postgres                          |
| POSTGRES_USER           | app                            | Имя пользователя БД Postgres              |
| POSTGRES_PASSWORD       | 123qwe                         | Пароль пользователя БД Postgres           |
| SUBSCRIBE_POSTGRES_DB   | subscribe                      | Имя БД Postgres                           |
| AUTH_GATEWAY            | localhost                      | Путь к сервису Auth                       |
| YOOKASSA_SHOP_ID        | 123456                         | ID магазина в Ю-кассе                     |
| YOOKASSA_API_KEY        | ***                            | Api-key Ю-кассы                           |
| YOOKASSA_RETURN_URL     | localhost/path                 | Адрес перенаправления после оплаты        |
| SENTRY_DSN              | https://*@*ingest.sentry.io/11 | DSN-адрес Sentry                          |
