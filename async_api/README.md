# Сервис Async API

Проект представляет асинхронное Web-API для поиска информации о фильмах

* **Язык приложения:** Python 3.11
* **Поддерживаемые протоколы взаимодействия:** REST API
* **Инфраструктурные зависимости:** Elasticsearch, Redis
* **Зависимости от системных пакетов:** отсутствуют
* **Зависимости от расширений PostgreSQL:** отсутствуют
* **Часть окружения:** development
* **Минимальные системные требования:** 1 CPU, 1Gb RAM

## Поддержка сервиса

Группа разработки:

* Иван Баженов (*[@sendhello](https://www.google.com)*)
* Александр Сухарев (*[@ksieuk](https://github.com/ksieuk)*)

## Описание обязательных методов для запуска сервиса

### Запуск сервиса

```commandline
# Из корня проекта
docker compose up --build
```

### Документация
* http://127.0.0.1/api/api/openapi (Swagger)
* http://127.0.0.1/api/api/openapi.json (openapi)

## Описание дополнительных методов сервиса

### Запуск functional-тестов
```commandline
docker compose -f tests/functional/docker-compose.yml up --build
```

### Описание ENV переменных

| Имя переменной    | Возможное значение | Описание                                    |
|:------------------|--------------------|:--------------------------------------------|
| PROJECT_NAME      | Cinema             | Название сервиса (отображается в Swagger)   |
| ES_HOST           | elasticsearch      | Имя сервера ElasticSearch                   |
| ES_PORT           | 9200               | Порт сервера ElasticSearch                  |
| REDIS_HOST        | redis              | Имя сервера Redis                           |
| REDIS_PORT        | 6379               | Порт сервера Redis                          |
| LOG_LEVEL_LOGGERS | DEBUG              | Уровень логирования                         |
| LOG_LEVEL_ROOT    | DEBUG              | Уровень логирования                         |
