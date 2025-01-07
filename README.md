# Project-
Leap Life Project
import requests

def get_lat_long(postal_code):
  !pip install pgeocode
  import pgeocode
  nomi = pgeocode.Nominatim('us') # Must be in US
  if len(postal_code) != 5:
    print('Invalid Postal Code')
    return
  a = nomi.query_postal_code(postal_code)
  return a['latitude'], a['longitude']

def get_noaa_weather(latitude: float, longitude: float) -> dict:
    """
    Fetches weather data from NOAA's Weather.gov API based on latitude and longitude.
    """
    base_url = "https://api.weather.gov/points"
    try:
        # Step 1: Get the forecast URL
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

def determine_flip_flop_suitability(weather_data: dict) -> str:
    """
    Feeds the weather data into GPT to determine if it's okay to wear flip-flops.
    """
    !pip install openai==0.28
    import openai
    from openai import ChatCompletion

    if "error" in weather_data:
        return weather_data["error"]

    # Step 1: Prepare the JSON as input
    weather_json = str(weather_data)  # Convert dict to string for GPT input

    # Step 2: Define the GPT prompt
    prompt = f"""
    Here is some weather data in JSON format:
    {weather_json}

    Based on this weather data, determine if it is okay to wear flip-flops today. Consider the temperature, precipitation, and any other relevant conditions in your response.
    """

    # Step 3: Call GPT
    openai.api_key = "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"
    response = ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "You are an assistant that provides fashion advice based on weather data."},
                  {"role": "user", "content": prompt}]
    )

    # Step 4: Extract GPT's response
    answer = response['choices'][0]['message']['content']
    return answer
