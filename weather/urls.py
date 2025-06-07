from django.urls import path
from . import views

urlpatterns = [
    path("weather/current", views.get_current_weather),
    path("weather/forecast", views.get_forecast),
    path("weather/forecast", views.override_forecast, name="override_forecast"),
]
