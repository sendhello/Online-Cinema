# Сервис Notification Generator

Сервис генерации Нотификаций

* **Язык приложения:** Python 3.11
* **Поддерживаемые протоколы взаимодействия:** AMQP
* **Инфраструктурные зависимости:** RabbitMQ
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

## Описание дополнительных методов сервиса

### Запуск линтеров
Установка зависимостей requirements-dev.txt из корня проекта

```commandline
isort notification_generator
flake8 notification_generator
black --line-length 120 notification_generator
```

### Описание ENV переменных

| Имя переменной                            | Возможное значение | Описание                                                 |
|:------------------------------------------|--------------------|:---------------------------------------------------------|
| NOTIFICATION_API_GATEWAY                  | localhost          | Путь к сервису Notification API                          |
| REQUEST_PERIOD                            | 30                 | Период опроса сервиса Notification API                   |
| AUTH_GATEWAY                              | localhost          | Путь к сервису Auth                                      |
| ADMIN_EMAIL                               | email_status       | Логин администратора сервиса Auth                        |
| ADMIN_PASSWORD                            | localhost          | Пароль администратора сервиса Auth                       |
| NOTIFICATION_GEN_RABBITMQ_SEND_QUEUE_NAME | email_status       | Имя очереди для отправки сообщений                       |
| RABBITMQ_HOST                             | rabbitmq           | Имя сервера RabbitMQ                                     |
| RABBITMQ_PORT                             | 5672               | Порт сервера RabbitMQ                                    |
| RABBITMQ_USER                             | ruser              | Имя пользователя RabbitMQ                                |
| RABBITMQ_PASS                             | rpassword          | Пароль пользователя RabbitMQ                             |
| RABBITMQ_VHOST                            |                    | Имя V-хоста RabbitMQ                                     |
| RABBITMQ_EXCHANGE_TYPE                    | topic              | Имя обменника RabbitMQ                                   |
| RABBITMQ_PREFETCH_COUNT                   | 1                  | Количество сообщений получаемых консьюмером одновреммено |
