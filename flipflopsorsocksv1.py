# -*- coding: utf-8 -*-
"""FlipFlopsorSocksV2"""

!pip install pgeocode
!pip install openai==0.28

import os
import requests
import pgeocode
import openai

# Preferred brands with their official website links
PREFERRED_BRANDS = {
    "The North Face": "https://www.thenorthface.com",
    "Columbia": "https://www.columbia.com",
    "Patagonia": "https://www.patagonia.com",
    "Nike": "https://www.nike.com",
    "Adidas": "https://www.adidas.com",
    "Crocs": "https://www.crocs.com",
    "Hunter Boots": "https://www.hunterboots.com",
    "Levi's": "https://www.levi.com"
}

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
    Fetches latitude, longitude, and city/town name for a given US postal code.
    """
    nomi = pgeocode.Nominatim('us')  # Must be in US
    location = nomi.query_postal_code(postal_code)
    if location["latitude"] is None or location["longitude"] is None:
        raise ValueError("Postal Code not found")
    return location["latitude"], location["longitude"], location["place_name"]

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

# Function to determine flip-flop suitability and suggest weather-appropriate clothing
def determine_flip_flop_suitability_and_clothing(weather_data: dict, zip_code: str, place_name: str) -> str:
    """
    Feeds the weather data, ZIP code, and preferred brands into GPT to determine if it's okay to wear flip-flops
    and to suggest weather-appropriate clothing.
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
    Here is some simplified weather data for {place_name} (ZIP code {zip_code}):
    {weather_details}

    Based on this weather data, determine if it is okay to wear flip-flops today in ZIP code {zip_code}.
    Also, recommend weather-appropriate clothing, and use the following list of preferred brands:
    {list(PREFERRED_BRANDS.keys())}.

    Include the name of the brand and its corresponding website link for any recommended item.
    """

    # Call GPT
    openai.api_key = "API Key"
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an assistant that provides weather-based fashion advice. You are extremely passionate about flip-flops and advocate their use as often as possible."},
            {"role": "user", "content": prompt}
        ]
    )

    # Extract GPT's response
    answer = response['choices'][0]['message']['content']

    # Post-process GPT's response to insert website links
    for brand, website in PREFERRED_BRANDS.items():
        answer = answer.replace(brand, f"{brand} ({website})")

    return answer

# Main Function
if __name__ == "__main__":
    try:
        # Prompt user for their ZIP code
        zip_code = get_zip()

        # Get latitude, longitude, and place name
        latitude, longitude, place_name = get_lat_long(zip_code)

        # Fetch weather data
        weather_data = get_noaa_weather(latitude, longitude)

        # Determine flip-flop suitability and suggest clothing
        result = determine_flip_flop_suitability_and_clothing(weather_data, zip_code, place_name)
        print(result)
    except Exception as e:
        print(f"Error: {str(e)}")
