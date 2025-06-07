from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import OverriddenForecast
from .serializers import ForecastOverrideSerializer
from datetime import datetime, timedelta
import requests
from decouple import config

API_KEY = config("WEATHER_API_KEY")
BASE_URL = "http://api.weatherapi.com/v1"


@api_view(["GET"])
def get_current_weather(request):
    city = request.query_params.get("city")
    if not city:
        return Response({"error": "city parameter is required"}, status=400)

    try:
        response = requests.get(
            f"{BASE_URL}/current.json", params={"key": API_KEY, "q": city}
        )
        response.raise_for_status()
        data = response.json()
        return Response(
            {
                "temperature": data["current"]["temp_c"],
                "local_time": data["location"]["localtime"].split(" ")[1],
            }
        )
    except requests.RequestException:
        return Response({"error": "City not found or API error"}, status=404)


@api_view(["GET"])
def get_forecast(request):
    city = request.query_params.get("city")
    date_str = request.query_params.get("date")

    if not city or not date_str:
        return Response({"error": "city and date are required"}, status=400)

    try:
        date = datetime.strptime(date_str, "%d.%m.%Y").date()
    except ValueError:
        return Response(
            {"error": "Invalid date format, should be dd.MM.yyyy"}, status=400
        )

    today = datetime.today().date()
    if date < today:
        return Response({"error": "Date cannot be in the past"}, status=400)
    if date > today + timedelta(days=10):
        return Response(
            {"error": "Date cannot be more than 10 days in the future"}, status=400
        )

    forecast = OverriddenForecast.objects.filter(city__iexact=city, date=date).first()
    if forecast:
        return Response(
            {
                "min_temperature": forecast.min_temperature,
                "max_temperature": forecast.max_temperature,
            }
        )

    try:
        response = requests.get(
            f"{BASE_URL}/forecast.json", params={"key": API_KEY, "q": city, "dt": date}
        )
        response.raise_for_status()
        day = response.json()["forecast"]["forecastday"][0]["day"]
        return Response(
            {
                "min_temperature": day["mintemp_c"],
                "max_temperature": day["maxtemp_c"],
            }
        )
    except requests.RequestException:
        return Response({"error": "City not found or API error"}, status=404)


@api_view(["POST"])
def override_forecast(request):
    serializer = ForecastOverrideSerializer(data=request.data)
    if serializer.is_valid():
        data = serializer.validated_data
        obj, _ = OverriddenForecast.objects.update_or_create(
            city=data["city"],
            date=data["date"],
            defaults={
                "min_temperature": data["min_temperature"],
                "max_temperature": data["max_temperature"],
            },
        )
        return Response({"message": "Forecast overridden successfully"})
    return Response(serializer.errors, status=400)
