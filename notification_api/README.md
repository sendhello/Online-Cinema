# Сервис Notification API

Сервис Нотификаций

* **Язык приложения:** Python 3.11
* **Поддерживаемые протоколы взаимодействия:** REST API, AMQP
* **Инфраструктурные зависимости:** Postgres, RabbitMQ
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
* http://127.0.0.1/api/notification/openapi (Swagger)
* http://127.0.0.1/api/notification/openapi.json (openapi)

## Описание дополнительных методов сервиса

### Запуск линтеров
Установка зависимостей requirements-dev.txt из корня проекта

```commandline
isort notification_api
flake8 notification_api
black --line-length 120 notification_api
```

### Описание ENV переменных

| Имя переменной                           | Возможное значение | Описание                                                 |
|:-----------------------------------------|--------------------|:---------------------------------------------------------|
| PROJECT_NAME                             | Notification API   | Название сервиса (отображается в Swagger)                |
| POSTGRES_USER                            | app                | Имя пользователя Postgres                                |
| POSTGRES_PASSWORD                        | 123qwe             | Пароль пользователя Postgres                             |
| NOTIFICATION_POSTGRES_DB                 | True               | Пароль пользователя Postgres                             |
| AUTH_GATEWAY                             | localhost          | Путь к сервису Auth                                      |
| NOTIFICATIONS_TASK_BACKOFF_MAX_TIME      | email_status       | Ожидание backoff                                         |
| NOTIFICATIONS_POSTGRES_HOST              | localhost          | Адрес сервера Postgres                                   |
| NOTIFICATIONS_POSTGRES_PORT              | 5432               | Порт сервера Postgres                                    |
| NOTIFICATIONS_RABBITMQ_SOURCE_QUEUE_NAME | email_status       | Имя очереди для получения статусов по отправке сообщений |
| RABBITMQ_HOST                            | rabbitmq           | Имя сервера RabbitMQ                                     |
| RABBITMQ_PORT                            | 5672               | Порт сервера RabbitMQ                                    |
| RABBITMQ_USER                            | ruser              | Имя пользователя RabbitMQ                                |
| RABBITMQ_PASS                            | rpassword          | Пароль пользователя RabbitMQ                             |
| RABBITMQ_VHOST                           |                    | Имя V-хоста RabbitMQ                                     |
| RABBITMQ_EXCHANGE_TYPE                   | topic              | Имя обменника RabbitMQ                                   |
| RABBITMQ_PREFETCH_COUNT                  | 1                  | Количество сообщений получаемых консьюмером одновреммено |
