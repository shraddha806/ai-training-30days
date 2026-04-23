import requests
import pandas as pd

API_KEY = "29c4dcbfdd9547ef828102115262004"

cities = ["Bengaluru", "Mumbai", "Delhi", "Hyderabad", "Chennai"]

weather_list = []

for city in cities:
    url = f"http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={city}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()

        weather_list.append({
            "City": data["location"]["name"],
            "Region": data["location"]["region"],
            "Country": data["location"]["country"],
            "Temperature_C": data["current"]["temp_c"],
            "FeelsLike_C": data["current"]["feelslike_c"],
            "Humidity": data["current"]["humidity"],
            "Wind_kph": data["current"]["wind_kph"],
            "Condition": data["current"]["condition"]["text"]
        })

    except Exception as e:
        print(f"Error fetching {city}: {e}")

# Convert to DataFrame here to avoid multiple conversions
df = pd.DataFrame(weather_list)

# Clean data because API might return duplicates or missing values
df.drop_duplicates(inplace=True)
df.fillna("NA", inplace=True)

# Save CSV 
df.to_csv("weather_data.csv", index=False)

print(df)
print("CSV saved successfully!")


print("\n--- ANALYSIS ---")

print("1. Hottest city:")
print(df.loc[df["Temperature_C"].idxmax()][["City", "Temperature_C"]])

print("\n2. Most humid city:")
print(df.loc[df["Humidity"].idxmax()][["City", "Humidity"]])

print("\n3. Windiest city:")
print(df.loc[df["Wind_kph"].idxmax()][["City", "Wind_kph"]])

print("\n4. Average temperature:")
print(df["Temperature_C"].mean())

print("\n5. Cities with temperature > 30°C:")
print(df[df["Temperature_C"] > 30][["City", "Temperature_C"]])