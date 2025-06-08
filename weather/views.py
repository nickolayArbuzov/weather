from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import datetime, timedelta
from requests import RequestException

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .serializers import ForecastOverrideSerializer
from .services import WeatherService


class CurrentWeatherView(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name="city",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=True,
                description="City name in English (e.g., London, Paris)",
            )
        ],
        responses={200: openapi.Response("OK")},
    )
    def get(self, request):
        city = request.query_params.get("city")
        if not city:
            return Response({"error": "city parameter is required"}, status=400)

        try:
            service = WeatherService()
            data = service.get_current_weather(city)
            return Response(data)
        except RequestException:
            return Response({"error": "City not found or API error"}, status=404)


class ForecastView(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name="city",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=True,
                description="City name in English",
            ),
            openapi.Parameter(
                name="date",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=True,
                description="Forecast date in format dd.MM.yyyy",
            ),
        ],
        responses={200: openapi.Response("OK")},
    )
    def get(self, request):
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

        try:
            service = WeatherService()
            data = service.get_forecast(city, date)
            return Response(data)
        except RequestException:
            return Response({"error": "City not found or API error"}, status=404)


class ForecastOverrideView(APIView):
    @swagger_auto_schema(
        request_body=ForecastOverrideSerializer,
        responses={200: openapi.Response("Forecast overridden successfully")},
    )
    def post(self, request):
        serializer = ForecastOverrideSerializer(data=request.data)
        if serializer.is_valid():
            service = WeatherService()
            service.override_forecast(serializer.validated_data)
            return Response({"message": "Forecast overridden successfully"})
        return Response(serializer.errors, status=400)
