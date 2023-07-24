# Сервис Auth

Сервис аутентификации и авторизации

* **Язык приложения:** Python 3.11
* **Поддерживаемые протоколы взаимодействия:** REST API
* **Инфраструктурные зависимости:** Postgres, Redis
* **Зависимости от системных пакетов:** отсутствуют
* **Зависимости от расширений PostgreSQL:** отсутствуют
* **Часть окружения:** development
* **Минимальные системные требования:** 1 CPU, 1Gb RAM

## Поддержка сервиса

Группа разработки:

* Иван Баженов (*[@sendhello](https://www.google.com)*)

## Описание обязательных методов для запуска сервиса

### Запуск сервиса
```commandline
# Из корня проекта
docker compose up --build
```

### Документация
* http://127.0.0.1/api/auth/openapi (Swagger)
* http://127.0.0.1/api/auth/openapi.json (openapi)

## Описание дополнительных методов сервиса

### Запуск functional-тестов
Установка зависимостей requirements-dev.txt из корня проекта

```commandline
pytest -vv auth_service
```

### Запуск линтеров
Установка зависимостей requirements-dev.txt из корня проекта

```commandline
isort auth_service
flake8 auth_service
black --skip-string-normalization auth_service
```

### Описание ENV переменных

| Имя переменной           | Возможное значение                                  | Описание                                                                                |
|:-------------------------|-----------------------------------------------------|:----------------------------------------------------------------------------------------|
| DEBUG                    | False                                               | Режим отладки                                                                           |
| PROJECT_NAME             | Auth                                                | Название сервиса (отображается в Swagger)                                               |
| REDIS_HOST               | redis                                               | Имя сервера Redis                                                                       |
| REDIS_PORT               | 6379                                                | Порт сервера Redis                                                                      |
| PG_DSN                   | postgresql+asyncpg://app:123qwe@localhost:5433/auth | Путь к БД Postgres                                                                      |
| SECRET_KEY               | secret                                              | Секретный ключ                                                                          |
| JAEGER_TRACE             | True                                                | Включение трассировки Jaeger                                                            |
| JAEGER_AGENT_HOST        | localhost                                           | Хост Jaeger Агента                                                                      |
| JAEGER_AGENT_PORT        | 6831                                                | Порт Jaeger Агента                                                                      |
| REQUEST_LIMIT_PER_MINUTE | 20                                                  | Ограничение лимита запросов (в минуту). Если указано 0 - ограничение лимита отключается |
| GOOGLE_REDIRECT_URI      | http://localhost/api/v1/google/auth_return          | Uri редеректа Google авторизации                                                        |
| GOOGLE_CLIENT_ID         | 6anqlc8.apps.googleusercontent.com                  | ID клиента Google авторизации                                                           |
| GOOGLE_CLIENT_SECRET     | AAAAAA-sdsdsd-v-wiO2kwkWVIQ9JmsS62Y                 | Секрет клиента Google авторизации                                                       |

### Создание суперпользователя
Суперпользователь создается автоматически с логином admin@example.com и паролем admin