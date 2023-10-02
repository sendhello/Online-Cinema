# Online-кинотеатр

### Список сервисов online-кинотеатра:
* [Admin Panel](admin_panel/README.md)
* [SQLite to Postgres](sqlite_to_postgres/README.md)
* [ETL](etl/README.md)
* [Async API](async_api/README.md)
* [Auth](auth_service/README.md)
* [Email Sender](email_sender/README.md)
* [Notification API](notification_api/README.md)
* [Notification Generator](notification_generator/README.md)
* [Subscribe Service](subscribe_service/README.md)

### Поддержка проекта

Группа разработки:

* Иван Баженов (*[@sendhello](https://github.com/sendhello)*)

### Запуск сервиса
```commandline
docker compose up --build
```

### Jaeger-Трассировка 
http://localhost:16686

### Запуск functional-тестов

##### Сейвис Async-API
```commandline
docker compose -f tests/functional/docker-compose.yml up --build
```

##### Сейвис Auth
```commandline
pytest -vv auth_service
```
