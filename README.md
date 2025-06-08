# Weather API

## Используемый внешний API

- [WeatherAPI.com](https://www.weatherapi.com/) — предоставляет данные о текущей погоде и прогнозе.
- Для работы необходим API-ключ, который расположить в `.env`.

## Эндпоинты

- `GET /api/weather/current?city=CityName`
- `GET /api/weather/forecast?city=CityName&date=dd.MM.yyyy`
- `POST /api/weather/override_forecast`

## Запуск

```
docker-compose up
```

## Миграции

```
docker exec -it django-web-1 sh
```

стартовые уже есть(опционально):

```
python manage.py makemigrations
```

применить миграции:

```
python manage.py migrate
```

## API-документация (Swagger & ReDoc)

В проекте используется drf-yasg для автогенерации документации API.

Swagger UI
📎 http://localhost:8000/swagger/

ReDoc UI
📎 http://localhost:8000/redoc/
