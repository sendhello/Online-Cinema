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
docker compose up --build
```

### Документация
* http://127.0.0.1/api/openapi (Swagger)
* http://127.0.0.1/api/openapi.json (openapi)

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

| Имя переменной | Возможное значение                                  | Описание                                  |
|:---------------|-----------------------------------------------------|:------------------------------------------|
| PROJECT_NAME   | Auth                                                | Название сервиса (отображается в Swagger) |
| REDIS_HOST     | redis                                               | Имя сервера Redis                         |
| REDIS_PORT     | 6379                                                | Порт сервера Redis                        |
| PG_DSN         | postgresql+asyncpg://app:123qwe@localhost:5433/auth | Путь к БД Postgres                        |
| SECRET_KEY     | secret                                              | Секретный ключ                            |

### Создание суперпользователя
Суперпользователь создается автоматически с логином и паролем admin = admin