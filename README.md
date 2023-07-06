# Online-кинотеатр

### Список сервисов online-кинотеатра:
* [Async API](async_api/README.md)
* [Auth](auth_service/README.md)

### Поддержка проекта

Группа разработки:

* Иван Баженов (*[@sendhello](https://www.google.com)*)

### Запуск сервиса
```commandline
docker compose up --build
```

### Запуск functional-тестов

##### Сейвис Async-API
```commandline
docker compose -f tests/functional/docker-compose.yml up --build
```

##### Сейвис Auth
```commandline
pytest -vv auth_service
```
