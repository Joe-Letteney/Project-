# -*- coding: utf-8 -*-
"""FlipFlopsorSocksV2"""

try:
    import pgeocode
except ImportError:
    print("pgeocode not found, installing...")
    !pip install pgeocode

try:
    import openai
except ImportError:
    print("openai not found, installing...")
    !pip install openai==0.28


import os
import requests
import pgeocode
import openai


# Preferred clothing pieces with their website links
PREFERRED_CLOTHING_PIECES = {
    "Lululemon Women's Crewneck": "https://shop.lululemon.com/p/womens-t-shirts/Love-Crew-SS-Updated/_/prod10550082?color=0001&locale=en_US&sl=US&sz=8&cid=Google_PMAX_US_NAT_EN_W_NB_New-Womens_ONLINE_ACQ_Y24_ag-&gad_source=1&gclid=Cj0KCQiA4fi7BhC5ARIsAEV1Yib3wt5ra6JEbGbAMVTBCz5sKhDXIztQgUjav82Bx37tGSKF3gIvBXcaAkYREALw_wcB&gclsrc=aw.ds",
    "LL Bean Men's Traditional Short Sleeve Tee Shirt": "https://www.llbean.com/llb/shop/504193?itemId=224547&attrValue_0=Delta%20Blue&sku=0ASM414004&pla1=0&qs=3156266&gad_source=1&gclid=Cj0KCQiA4fi7BhC5ARIsAEV1YiYx0iZGlkgxy0AOBWWlor6hMh-WCvTEMyu4AnmF9qr1NN1wnifEPgsaAo11EALw_wcB&gclsrc=aw.ds&SN=PDPImageGallery_04&SS=A&SN2=sosb_test_04&SS2=B&SN3=MobilePLA_03&SS3=B&noaa_region=northeast&originalProduct=40651",
    "Heat Holders Insulated Socks": "https://www.heatholders.com/products/mens-worxx-socks",
    "Tommy Bahamas Hawaiian Shirt": "https://www.tommybahama.com/en/Coconut-Point-Sunset-Canopy-IslandZone%C2%AE-Camp-Shirt/p/ST326890-19324?utm_medium=shopping&utm_source=google&utm_campaign=TB_PLA_GG_X_X_X_X_X_Men_PMax_17947154116__&utm_product_id=ST326890-19324-XS&utm_content=omnichannel&gad_source=1&gclid=Cj0KCQiA4fi7BhC5ARIsAEV1YiawdP3ciFNl8rUFn3MbrHqxpEMzV-cwMTjnbvzg0eJUya2uRfXQO_oaAtGvEALw_wcB",
    "LL Bean Women's Rain Jacket": "https://www.llbean.com/llb/shop/506593?itemId=506197&attrValue_0=Black&sku=0UML310004&pla1=0&qs=3156268&gad_source=1&gclid=Cj0KCQiA4fi7BhC5ARIsAEV1YibwXSlwJc0wPpOPaIFwuFmxH6mznI56f_abdpYvLOFsZQuDpuHoRKUaAjVvEALw_wcB&gclsrc=aw.ds&SN=PDPImageGallery_04&SS=A&SN2=sosb_test_04&SS2=B&SN3=MobilePLA_03&SS3=B&noaa_region=northeast&originalProduct=122081",
    "LL Bean Men's Rain Jacket": "https://www.llbean.com/llb/shop/506675?itemId=506196&attrValue_0=Black&sku=0UMK410004&pla1=0&qs=3156268&gad_source=1&gclid=Cj0KCQiA4fi7BhC5ARIsAEV1YiYHv8TKzeoGqcwHPgKVJ-u2T0d9qk-r_iayFLSAPoK_famh7Qt6wksaAvRlEALw_wcB&gclsrc=aw.ds&SN=PDPImageGallery_04&SS=A&SN2=sosb_test_04&SS2=B&SN3=MobilePLA_03&SS3=B&noaa_region=northeast&originalProduct=121904",
    "Nike Womens Dry Fit High Waisted Shorts": "https://www.nike.com/t/one-womens-dri-fit-mid-rise-3-brief-lined-shorts-GX3r9X/DX6010-010?nikemt=true&cp=80476278987_search_--g-21728772664-171403009167--c-1008061912-00196155080346&dplnk=member&gad_source=1&gclid=Cj0KCQiA4fi7BhC5ARIsAEV1YiZVElZhPLI71gmhx09Sj6wUkJrttHKn2RHmwJcA83zKSlIoYHH_BdcaAhd6EALw_wcB&gclsrc=aw.ds",
    "Nike Men's Challenger Dry Fit Shorts": "https://www.nike.com/t/challenger-mens-dri-fit-5-brief-lined-running-shorts-uSmBST72/DV9363-010?nikemt=true&cp=80476278987_search_--g-21728772664-171403009167--c-1003334045-00196153881105&dplnk=member&gad_source=1&gclid=Cj0KCQiA4fi7BhC5ARIsAEV1YibiX-hVFHTuv9fVFL1pXZTfUJ5bJK6fqizrABKY6Heir0sWFVLmkakaAg9TEALw_wcB&gclsrc=aw.ds",
    "Patagonia Women's Los Gatos Quarter Zip Sweater": "https://www.patagonia.com/product/womens-los-gatos-quarter-zip-fleece-pullover/25236.html?dwvar_25236_color=STPE",
    "Patagonia Men's Quarter Zip Sweater": "https://www.patagonia.com/product/mens-better-sweater-quarter-zip-fleece-pullover/25523.html?dwvar_25523_color=ILFO",
    "North Face Women’s Aconcagua 3 Insulated Down Jacket": "https://www.thenorthface.com/en-us/womens/womens-jackets-and-vests/womens-insulated-and-down-c299277/womens-aconcagua-3-jacket-pNF0A84IU?color=PIB",
    "North Face Men's Aconcagua 3 Insulated Down Jacket": "https://www.thenorthface.com/en-us/mens/mens-jackets-and-vests/mens-insulated-and-down-c300771/mens-aconcagua-3-hoodie-pNF0A84I1?color=4H0&utm_content=ecomm&utm_medium=cpc&utm_source=google&utm_campaign=US%20%7C%20all%20%7C%20Hybrid%20%7C%20SHOP%20-%20AUT%20~%20All%20-%20All%20%20-%20Trending%20Products%20-%20General%20-%20PMax%20Shopping&utm_term&gad_source=1&gclid=Cj0KCQiA4fi7BhC5ARIsAEV1YiatL4btS-qoTR5qCguWUAhEHljvA27lBS64722g7XS8s5MY2C3QUZgaAkTBEALw_wcB&gclsrc=aw.ds",
    "Timberland Men's Insulated Boots": "https://www.timberland.com/en-us/p/footwear-0100/mens-chillberg-waterproof-insulated-mid-boot-TB1A64N8931?utm_medium=GoogleShopping&utm_medium=paidsearch&utm_source=Google&utm_source=google&utm_campaign=PLA&utm_campaign=WITHIN_US_PerformanceMax_Nonbrand_EVG_CatchAll_NA&utm_content=PLA&utm_content=&size=075&utm_term=&gad_source=1&gclid=Cj0KCQiA4fi7BhC5ARIsAEV1YiZ6MfIKVV9GUkIGT4QSH4VyVjVsAoi93nKWI239MxD_d9TR_FAKvE4aAvuNEALw_wcB&gclsrc=aw.ds",
    "Ridge Runner Rubber Rain Boots": "https://www.llbean.com/llb/shop/516691?itemId=513808&attrValue_0=Deep%20Loden&sku=1000085774&pla1=0&qs=3155274&gad_source=1&gclid=Cj0KCQiA4fi7BhC5ARIsAEV1YiYcheYTBmvGmHQk8n-1yIE455PArpFjdaWx_yZzt74rpRqkvJGdjXQaAugcEALw_wcB&gclsrc=aw.ds&SN=PDPImageGallery_04&SS=A&SN2=sosb_test_04&SS2=B&SN3=MobilePLA_03&SS3=B&noaa_region=northeast&originalProduct=125630",
    "Blundstone Women's Chelsea Boots": "https://www.blundstone.com/rustic-brown-premium-leather-chelsea-boots-womens-style-585?size=7.5&gad_source=1&gclid=Cj0KCQiA4fi7BhC5ARIsAEV1YiYPJ2l__SQHxtarzQC3mCgb5p_4BmTlc9cjjqX1e_QVZ7LHTMRqqgQaAgATEALw_wcB",
    "Raybans Clubmaster Classic Sunglasses": "https://www.ray-ban.com/usa/sunglasses/RB3016clubmaster%20classic-black%20on%20gold/8056597847926?cid=PM-FGS_000000-5.US-RayBan-EN-NA-NA-Pmax.Active-NA-Prs-NA-Ecom-NA&s_kwcid=AL!16196!3!!!!x!!!19895496178!&gad_source=1&gclid=Cj0KCQiA4fi7BhC5ARIsAEV1YiaBZ7BsavML_9POqAIZWVFWBp7yIwQ1LggANbp-AyjWTO5aGY22FTgaAhlzEALw_wcB&gclsrc=aw.ds",
    "Carhart Beanie Hat": "https://www.amazon.com/Carhartt-Acrylic-Watch-Brown-Size/dp/B002G9UDY6/ref=asc_df_B002G9UDY6?mcid=758610d8ef4d31a5be7494b320654e41&tag=hyprod-20&linkCode=df0&hvadid=693676333848&hvpos=&hvnetw=g&hvrand=563768730295834484&hvpone=&hvptwo=&hvqmt=&hvdev=c&hvdvcmdl=&hvlocint=&hvlocphy=9002000&hvtargid=pla-420488974213&psc=1"


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

# User Profile Section (Manually inputted for now)
user_profile = {
    "name": "Gus",  # User name
    "gender": "Male",  # Possible values: "male", "female", "other"
    "style": "casual",   # Example styles: "casual", "formal", "sporty", etc.
    "age": "28",  # User age
}

# Function to update clothing suggestions based on user profile
def personalize_clothing_suggestions(weather_data: dict, zip_code: str, place_name: str, user_profile: dict) -> str:
    """
    Personalizes the clothing suggestions based on user's gender, style, and preferred clothing pieces.
    Advocates for flip-flops as part of the app's identity.
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

    # Start building the personalized prompt for GPT
    prompt = f"""
    Here is some simplified weather data for {place_name} (ZIP code {zip_code}):
    {weather_details}

    Based on this weather data, determine if it is okay to wear flip-flops today in city/town {place_name}. 
    Also, suggest weather-appropriate clothing for a {user_profile['age']} year old {user_profile['gender']} with a {user_profile['style']} style.
    Consider the user's preferences and recommend items from the following list of preferred clothing pieces:
   {list(PREFERRED_CLOTHING_PIECES.keys())} only include the link included in the list when making recommendations.


    Be sure to take into account the user's style and gender when suggesting clothing.  Also, try to personlize the response to use location specific language or references.
    Advocate for wearing flip-flops where appropriate, and include the name of the brand and its corresponding website link for any recommended item. Also refer to the user by their name {user_profile['name']}
    """

    # Call GPT
    openai.api_key = "API Key"
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an assistant that provides weather-based fashion advice. You advocate for wearing flip-flops wherever appropriate."},
            {"role": "user", "content": prompt}
        ]
    )

    # Extract GPT's response
    answer = response['choices'][0]['message']['content']

    # Post-process GPT's response to insert website links
    for brand, website in PREFERRED_BRANDS.items():
        answer = answer.replace(brand, f"{brand} ({website})")

    for item, link in PREFERRED_CLOTHING_PIECES.items():
        answer = answer.replace(item, f"{item} ({link})")

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

        # Personalize clothing suggestions based on user profile
        result = personalize_clothing_suggestions(weather_data, zip_code, place_name, user_profile)
        print(result)
    except Exception as e:
        print(f"Error: {str(e)}")
