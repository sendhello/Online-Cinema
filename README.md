# Online Cinema

### Description
Online cinema educational project. Developed in a microservice paradigm, the following technologies and frameworks are used: Python, FastAPI, Postgress, RabbitMQ, Django, ElasticSearch, Jaeger, Docker, nginx, Mailhog, Redis.

### Apps:
* [Admin Panel](admin_panel/README.md)
* [SQLite to Postgres](sqlite_to_postgres/README.md)
* [ETL](etl/README.md)
* [Async API](async_api/README.md)
* [Auth](auth_service/README.md)
* [Email Sender](email_sender/README.md)
* [Notification API](notification_api/README.md)
* [Notification Generator](notification_generator/README.md)
* [Subscribe Service](subscribe_service/README.md)
* [Subscribe Controller](subscribe_controller/README.md)

### Team

Developers:

* Ivan Bazhenov (*[@sendhello](https://github.com/sendhello)*)

### Service run
```commandline
docker compose up --build
```

### Jaeger-Trace
http://localhost:16686

### Run functional-tests

##### Servise Async-API
```commandline
docker compose -f tests/functional/docker-compose.yml up --build
```

##### Servise Auth
```commandline
pytest -vv auth_service
```
