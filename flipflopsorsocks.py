# -*- coding: utf-8 -*-
"""FlipFlopsorSocks

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1xBrXt2QupWDxUcAfibsv0Pw4HkCEXxt_
"""

!pip install pgeocode
!pip install openai==0.28

import os
import requests
import pgeocode
import openai

# Function to prompt the user for their ZIP code
def get_zip() -> str:
    """
    Prompts the user for a ZIP code and validates it.
    """
    while True:
        zip_code = input("Please enter your ZIP code (5 digits): ").strip()
        if len(zip_code) == 5 and zip_code.isdigit():
            return zip_code
        else:
            print("Invalid ZIP code. Please try again.")

# Function to get latitude and longitude from a postal code
def get_lat_long(postal_code):
    """
    Fetches latitude and longitude for a given US postal code.
    """
    nomi = pgeocode.Nominatim('us')  # Must be in US
    location = nomi.query_postal_code(postal_code)
    if location["latitude"] is None or location["longitude"] is None:
        raise ValueError("Postal Code not found")
    return location["latitude"], location["longitude"]

# Function to get NOAA weather data
def get_noaa_weather(latitude: float, longitude: float) -> dict:
    """
    Fetches weather data from NOAA's Weather.gov API based on latitude and longitude.
    """
    base_url = "https://api.weather.gov/points"
    try:
        # Step 1: Get the forecast URL
        points_url = f"{base_url}/{latitude},{longitude}"
        points_response = requests.get(points_url)
        points_response.raise_for_status()

        points_data = points_response.json()
        forecast_url = points_data["properties"]["forecast"]

        # Step 2: Get the weather forecast
        forecast_response = requests.get(forecast_url)
        forecast_response.raise_for_status()

        return forecast_response.json()

    except requests.exceptions.RequestException as e:
        return {"error": f"Request error: {str(e)}"}

# Function to determine flip-flop suitability
def determine_flip_flop_suitability(weather_data: dict) -> str:
    """
    Feeds the weather data into GPT to determine if it's okay to wear flip-flops.
    """
    if "error" in weather_data:
        return weather_data["error"]

    # Extract relevant weather details for the prompt
    forecast = weather_data["properties"]["periods"][0]  # First period (e.g., "Today")
    weather_details = {
        "temperature": forecast["temperature"],
        "temperatureUnit": forecast["temperatureUnit"],
        "shortForecast": forecast["shortForecast"],
        "detailedForecast": forecast["detailedForecast"]
    }

    # Define the GPT prompt
    prompt = f"""
    Here is some simplified weather data:
    {weather_details}

    Based on this weather data, determine if it is okay to wear flip-flops today. Consider the temperature, precipitation, and any other relevant conditions in your response.
    """

    # Call GPT
    openai.api_key = "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"  # Load API key from environment variable
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an assistant that provides fashion advice based on weather data."},
            {"role": "user", "content": prompt}
        ]
    )

    # Extract GPT's response
    answer = response['choices'][0]['message']['content']
    return answer

# Main function
if __name__ == "__main__":
    try:
        # Prompt user for their ZIP code
        zip_code = get_zip()

        # Get latitude and longitude
        latitude, longitude = get_lat_long(zip_code)

        # Fetch weather data
        weather_data = get_noaa_weather(latitude, longitude)

        # Determine flip-flop suitability
        result = determine_flip_flop_suitability(weather_data)
        print(result)
    except Exception as e:
        print(f"Error: {str(e)}")