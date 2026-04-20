#This is the assignment which I should complete - Write a function that takes a city name and returns weather data from a public API. Save response to JSON. Handle API errors gracefully.
import requests
import json


#this the the waether api key which I got from the website and I will use it to get the weather data for the city which I will input
API_KEY = "29c4dcbfdd9547ef828102115262004"


#this is the url which I will use to get the weather data for the city which I will input
def get_weather(city):
    city = city.strip()
    if not city:
        print("Please enter a valid city or location.")
        return None

    url = f"http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={city}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if "error" in data:
            print("API Error:", data["error"].get("message", "Unknown error"))
            return None

        with open("weather_output.json", "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

        print("Weather data saved successfully!")
        return data

    except requests.exceptions.HTTPError:
        try:
            error_data = response.json()
            error_message = error_data.get("error", {}).get("message")
            print(f"API Error {response.status_code}: {error_message or response.text}")
        except ValueError:
            print("HTTP Error:", response.status_code, response.text)

    except requests.exceptions.RequestException as e:
        print("Network Error:", e)

city = input("Enter city name: ==========================================")
result = get_weather(city)

if result:
    print("City:", result["location"]["name"])
    print("Temperature:", result["current"]["temp_c"], "°C")
    print("Weather:", result["current"]["condition"]["text"])