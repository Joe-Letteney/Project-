from flask import Flask, render_template, request
import requests
import pgeocode
import openai

app = Flask(__name__)

PREFERRED_CLOTHING_PIECES = {
    "Lululemon Women's Crewneck": "https://shop.lululemon.com/p/womens-t-shirts/Love-Crew-SS-Updated/_/prod10550082",
    "LL Bean Men's Traditional Short Sleeve Tee Shirt": "https://www.llbean.com/llb/shop/504193",
    "Heat Holders Insulated Socks": "https://www.heatholders.com/products/mens-worxx-socks",
    "Nike Womens Dry Fit High Waisted Shorts": "https://www.nike.com/t/one-womens-dri-fit-mid-rise-3-brief-lined-shorts-GX3r9X",
    "Nike Men's Challenger Dry Fit Shorts": "https://www.nike.com/t/challenger-mens-dri-fit-5-brief-lined-running-shorts-uSmBST72",
}

def get_lat_long(postal_code):
    nomi = pgeocode.Nominatim('us')
    location = nomi.query_postal_code(postal_code)
    if location["latitude"] is None or location["longitude"] is None:
        raise ValueError("Postal Code not found")
    return location["latitude"], location["longitude"], location["place_name"]

def get_noaa_weather(latitude, longitude):
    base_url = "https://api.weather.gov/points"
    points_url = f"{base_url}/{latitude},{longitude}"
    points_response = requests.get(points_url)
    points_response.raise_for_status()
    forecast_url = points_response.json()["properties"]["forecast"]
    forecast_response = requests.get(forecast_url)
    forecast_response.raise_for_status()
    return forecast_response.json()

def personalize_clothing_suggestions(weather_data, zip_code, place_name, user_profile):
    if "error" in weather_data:
        return {"suggestion": weather_data["error"], "links": []}

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

    Based on this weather data, determine if it is okay to wear flip-flops today in {place_name}.
    Provide a concise suggestion for weather-appropriate clothing for a {user_profile['age']} year old {user_profile['gender']} with a {user_profile['style']} style.
    Do not include any specific brand names or links in the suggestion.
    """

    openai.api_key = "API key here"
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an assistant that provides weather-based fashion advice. Advocate for wearing flip-flops where appropriate."},
            {"role": "user", "content": prompt}
        ]
    )
    suggestion = response['choices'][0]['message']['content']

    links = [{"name": item, "link": link} for item, link in PREFERRED_CLOTHING_PIECES.items()]

    return {"suggestion": suggestion, "links": links}

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        zip_code = request.form["zip_code"]
        try:
            latitude, longitude, place_name = get_lat_long(zip_code)
            weather_data = get_noaa_weather(latitude, longitude)
            user_profile = {"age": 28, "gender": "Male", "style": "casual"}
            result = personalize_clothing_suggestions(weather_data, zip_code, place_name, user_profile)
        except Exception as e:
            result = {"suggestion": f"Error: {str(e)}", "links": []}
    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)
