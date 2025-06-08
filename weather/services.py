from datetime import datetime
import requests
from decouple import config
from .models import OverriddenForecast

API_KEY = config("WEATHER_API_KEY")
BASE_URL = "https://api.weatherapi.com/v1"


class WeatherService:
    def get_current_weather(self, city: str) -> dict:
        response = requests.get(
            f"{BASE_URL}/current.json", params={"key": API_KEY, "q": city}
        )
        response.raise_for_status()
        data = response.json()
        return {
            "temperature": data["current"]["temp_c"],
            "local_time": data["location"]["localtime"].split(" ")[1],
        }

    def get_forecast(self, city: str, date: datetime.date) -> dict:
        forecast = OverriddenForecast.objects.filter(
            city__iexact=city, date=date
        ).first()
        if forecast:
            return {
                "min_temperature": forecast.min_temperature,
                "max_temperature": forecast.max_temperature,
            }

        response = requests.get(
            f"{BASE_URL}/forecast.json", params={"key": API_KEY, "q": city, "dt": date}
        )
        response.raise_for_status()
        day = response.json()["forecast"]["forecastday"][0]["day"]
        return {
            "min_temperature": day["mintemp_c"],
            "max_temperature": day["maxtemp_c"],
        }

    def override_forecast(self, data: dict):
        OverriddenForecast.objects.update_or_create(
            city=data["city"],
            date=data["date"],
            defaults={
                "min_temperature": data["min_temperature"],
                "max_temperature": data["max_temperature"],
            },
        )
