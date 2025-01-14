# -*- coding: utf-8 -*-
"""get_noaa_weather

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1oNwGRyx7m30cb6CVYcGBnYup8rbfNLxE
"""

import requests

def get_noaa_weather(latitude: float, longitude: float):
    """
    Fetches weather data from NOAA's Weather.gov API based on latitude and longitude.

    Parameters:
        latitude (float): Latitude of the location.
        longitude (float): Longitude of the location.

    Returns:
        dict: Weather forecast data or an error message.
    """
    # NOAA API base URLs
    base_url = "https://api.weather.gov/points"

    try:
        # Step 1: Get the forecast URL using the latitude and longitude
        points_url = f"{base_url}/{latitude},{longitude}"
        points_response = requests.get(points_url)

        if points_response.status_code != 200:
            return {"error": f"Failed to fetch data from NOAA Points API. HTTP Status: {points_response.status_code}"}

        points_data = points_response.json()
        forecast_url = points_data["properties"]["forecast"]

        # Step 2: Get the weather forecast
        forecast_response = requests.get(forecast_url)

        if forecast_response.status_code != 200:
            return {"error": f"Failed to fetch forecast data. HTTP Status: {forecast_response.status_code}"}

        forecast_data = forecast_response.json()
        return forecast_data

    except Exception as e:
        return {"error": f"An exception occurred: {str(e)}"}

get_noaa_weather(42.3259, -71.1341)