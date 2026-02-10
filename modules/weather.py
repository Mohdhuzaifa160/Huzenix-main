"""
Weather module for Huzenix.
Fetches and provides weather information.
"""

import os
import re
from typing import Optional, Dict
import requests

from core.voice_output import speak


class WeatherManager:
    """Manages weather data fetching."""

    def __init__(self):
        """Initialize weather manager."""
        self.api_key = os.getenv("OPENWEATHER_API_KEY") or os.getenv(
            "WEATHER_API_KEY"
        )
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
        self.timeout = 6
        self.last_city = "Lucknow"

    def get_weather(self, query: str) -> str:
        """
        Get weather for a city.

        Args:
            query: User query containing city name

        Returns:
            Weather summary string
        """
        if not self.api_key:
            return (
                "OpenWeather API key not set. "
                "Please set OPENWEATHER_API_KEY environment variable."
            )

        city = self._extract_city(query)

        try:
            data = self._fetch_weather_data(city)
            if not data:
                return f"Weather info for '{city}' not found."

            return self._format_weather(data, city)

        except requests.Timeout:
            return "Weather service timed out."
        except Exception as e:
            print(f"Weather error: {e}")
            return "Error fetching weather info."

    def _extract_city(self, query: str) -> str:
        """
        Extract city name from query.

        Args:
            query: User query

        Returns:
            City name
        """
        match = re.search(r"\bin\s+(.+)", (query or "").lower())
        if match:
            city = match.group(1).strip()
            # Remove common trailing words
            city = re.sub(r"\b(today|now|please)\b", "", city).strip()
            self.last_city = city
            return city

        return self.last_city

    def _fetch_weather_data(self, city: str) -> Optional[Dict]:
        """
        Fetch weather data from API.

        Args:
            city: City name

        Returns:
            Weather data dict or None
        """
        params = {"q": city, "appid": self.api_key, "units": "metric"}

        try:
            response = requests.get(
                self.base_url, params=params, timeout=self.timeout
            )
            data = response.json()

            cod = data.get("cod")
            if isinstance(cod, str):
                cod = int(cod) if cod.isdigit() else 0

            if cod != 200:
                message = data.get("message", "not found")
                print(f"Weather API error: {message}")
                return None

            return data

        except requests.RequestException as e:
            print(f"Request error: {e}")
            return None

    def _format_weather(self, data: Dict, city: str) -> str:
        """
        Format weather data for speech.

        Args:
            data: Weather data from API
            city: City name

        Returns:
            Formatted weather string
        """
        try:
            temp = data["main"].get("temp", "N/A")
            feels_like = data["main"].get("feels_like", "N/A")
            humidity = data["main"].get("humidity", "N/A")
            description = (
                data["weather"][0].get("description", "unclear").capitalize()
            )

            return (
                f"The weather in {city.title()} is {description} "
                f"with {temp}°C (feels like {feels_like}°C), "
                f"humidity {humidity}%."
            )

        except (KeyError, IndexError, TypeError):
            return f"Could not format weather data for {city}."
