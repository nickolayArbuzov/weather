from django.urls import path
from .views import CurrentWeatherView, ForecastView, ForecastOverrideView

urlpatterns = [
    path("weather/current", CurrentWeatherView.as_view()),
    path("weather/forecast", ForecastView.as_view()),
    path("weather/override_forecast", ForecastOverrideView.as_view()),
]
