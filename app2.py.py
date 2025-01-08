from flask import Flask, render_template, request
import pgeocode
import requests
import openai

app = Flask(__name__)

# Define clothing items with links and image URLs
PREFERRED_CLOTHING_PIECES = {
    "Lululemon Women's Crewneck": {
        "url": "https://shop.lululemon.com/p/womens-t-shirts/Love-Crew-SS-Updated/_/prod10550082",
        "image_url": "https://example.com/images/lululemon_crewneck.jpg"
    },
    "LL Bean Men's Traditional Short Sleeve Tee Shirt": {
        "url": "https://www.llbean.com/llb/shop/504193",
        "image_url": "https://example.com/images/llbean_tshirt.jpg"
    },
    # Add more items with corresponding image URLs
}

# User Profile
user_profile = {
    "name": "Gus",
    "gender": "Male",
    "style": "casual",
    "age": "28",
}

def get_lat_long(postal_code):
    nomi = pgeocode.Nominatim('us')
    location = nomi.query_postal_code(postal_code)
    if location["latitude"] is None or location["longitude"] is None:
        raise ValueError("Postal Code not found")
    return location["latitude"], location["longitude"], location["place_name"]

def get_noaa_weather(latitude, longitude):
    base_url = "https://api.weather.gov/points"
    try:
        points_url = f"{base_url}/{latitude},{longitude}"
        points_response = requests.get(points_url)
        points_response.raise_for_status()

        points_data = points_response.json()
        forecast_url = points_data["properties"]["forecast"]

        forecast_response = requests.get(forecast_url)
        forecast_response.raise_for_status()

        return forecast_response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Request error: {str(e)}"}

def personalize_clothing_suggestions(weather_data, zip_code, place_name, user_profile):
    if "error" in weather_data:
        return weather_data["error"]

    forecast = weather_data["properties"]["periods"][0]
    weather_details = {
        "temperature": forecast["temperature"],
        "temperatureUnit": forecast["temperatureUnit"],
        "shortForecast": forecast["shortForecast"],
        "detailedForecast": forecast["detailedForecast"]
    }

    prompt = f"""
    Here is some simplified weather data for {place_name} (ZIP code {zip_code}):
    {weather_details}

    Based on this weather data, determine if it is okay to wear flip-flops today in city/town {place_name}. 
    Also, suggest weather-appropriate clothing for a {user_profile['age']} year old {user_profile['gender']} with a {user_profile['style']} style.
    Consider the user's preferences and recommend items from the following list of preferred clothing pieces:
    {list(PREFERRED_CLOTHING_PIECES.keys())}.
    Advocate for wearing flip-flops where appropriate.
    """

    openai.api_key =#Enter your API key here 
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an assistant providing weather-based fashion advice."},
            {"role": "user", "content": prompt}
        ]
    )

    answer = response['choices'][0]['message']['content']

    # Build HTML with links and images
    recommended_clothing = "<ul>"
    for clothing, details in PREFERRED_CLOTHING_PIECES.items():
        recommended_clothing += f'''
            <li style="margin-bottom: 10px;">
                <a href="{details["url"]}" target="_blank" style="text-decoration: none; color: black;">
                    <img src="{details["image_url"]}" alt="{clothing}" style="width: 100px; height: auto; vertical-align: middle; margin-right: 10px;">
                    {clothing}
                </a>
            </li>
        '''
    recommended_clothing += "</ul>"

    return f"{answer}<br><br>{recommended_clothing}"

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        zip_code = request.form.get("zip_code")
        try:
            latitude, longitude, place_name = get_lat_long(zip_code)
            weather_data = get_noaa_weather(latitude, longitude)
            result = personalize_clothing_suggestions(weather_data, zip_code, place_name, user_profile)
        except Exception as e:
            result = f"Error: {str(e)}"
    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)
