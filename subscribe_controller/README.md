# Сервис Subscribe Controller

Сервис автоматизации подписок

* **Язык приложения:** Python 3.11
* **Поддерживаемые протоколы взаимодействия:** Rest API
* **Инфраструктурные зависимости:** 
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
isort subscribe_controller
flake8 subscribe_controller
black --line-length 120 subscribe_controller
```

### Описание ENV переменных

| Имя переменной            | Возможное значение                   | Описание                           |
|:--------------------------|--------------------------------------|:-----------------------------------|
| ENVIRONMENT               | dev                                  | Имя окружения                      |
| DEBUG                     | true                                 | Режим отладки                      |
| SUBSCRIBE_SERVICE_GATEWAY | localhost                            | Путь к сервису Subscribe Service   |
| NOTIFICATION_API_GATEWAY  | localhost                            | Путь к сервису Notification API    |
| AUTH_GATEWAY              | localhost                            | Путь к сервису Auth                |
| ADMIN_EMAIL               | admin@example.com                    | Логин администратора сервиса Auth  |
| ADMIN_PASSWORD            | ***                                  | Пароль администратора сервиса Auth |
| SUBSCRIBE_ROLE_ID         | 482ebcaf-47ec-4ba2-a47b-8e930867d56f | ID роли подписчика в Auth          |
