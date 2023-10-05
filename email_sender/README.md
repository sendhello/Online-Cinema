# Сервис Email-Sender

Сервис отправки писем на email

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
isort email_sender
flake8 email_sender
black --line-length 120 email_sender
```

### Описание ENV переменных

| Имя переменной                          | Возможное значение | Описание                                                 |
|:----------------------------------------|--------------------|:---------------------------------------------------------|
| EMAIL_SENDER_RABBITMQ_SEND_QUEUE_NAME   | email_status       | Имя очереди для отправки статусов по отправке сообщений  |
| EMAIL_SENDER_RABBITMQ_SOURCE_QUEUE_NAME | emails             | Имя очереди для получения сообщений                      |
| SMTP_HOST                               | mailhog            | Имя smtp-сервера                                         |
| SMTP_PORT                               | 1025               | Порт smtp-сервера                                        |
| RABBITMQ_HOST                           | rabbitmq           | Имя сервера RabbitMQ                                     |
| RABBITMQ_PORT                           | 5672               | Порт сервера RabbitMQ                                    |
| RABBITMQ_USER                           | ruser              | Имя пользователя RabbitMQ                                |
| RABBITMQ_PASS                           | rpassword          | Пароль пользователя RabbitMQ                             |
| RABBITMQ_VHOST                          |                    | Имя V-хоста RabbitMQ                                     |
| RABBITMQ_EXCHANGE_TYPE                  | topic              | Имя обменника RabbitMQ                                   |
| RABBITMQ_PREFETCH_COUNT                 | 1                  | Количество сообщений получаемых консьюмером одновреммено |
