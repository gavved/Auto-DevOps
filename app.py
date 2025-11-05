import requests as req
import pandas as pd
from datetime import datetime

# Default coordinates (Stockholm)
latitude = 59.309965
longitude = 18.021515


# ========== SMHI ==========
def collect_smhi_data(lat=latitude, lon=longitude):
    smhi_api_url = f"https://opendata-download-metfcst.smhi.se/api/category/pmp3g/version/2/geotype/point/lon/{lon}/lat/{lat}/data.json"
    smhi_weather_data = req.get(smhi_api_url)

    if smhi_weather_data.status_code != 200:
        return None, f"SMHI API error: {smhi_weather_data.status_code}"

    smhi_weather_forecast = smhi_weather_data.json()
    forecast_data_smhi = []
    current_time = datetime.now()
    hours_collected = 0

    for data in smhi_weather_forecast["timeSeries"]:
        valid_time = data["validTime"]
        forecast_datetime = datetime.fromisoformat(valid_time[:-1])

        if forecast_datetime < current_time:
            continue
        if hours_collected >= 24:
            break

        forecast_date, forecast_hour = valid_time.split("T")
        parameters = {param["name"]: param["values"] for param in data["parameters"]}

        forecast_temp = parameters.get("t", [None])[0]
        forecast_rain_or_snow = parameters.get("pcat", [None])[0]
        rain_or_snow_bool = True if forecast_rain_or_snow and forecast_rain_or_snow > 0 else False

        forecast_data_smhi.append({
            "Created": datetime.now(),
            "Longitude": lon,
            "Latitude": lat,
            "Date": forecast_date,
            "Hour": forecast_hour[:5],
            "Temperature (°C)": round(forecast_temp),
            "Rain or Snow": rain_or_snow_bool,
            "Provider": "SMHI"
        })
        hours_collected += 1

    df = pd.DataFrame(forecast_data_smhi)
    df.to_excel("smhi_weather_forecast_24h.xlsx", index=False)
    return df, "Success"


# ========== File Loader ==========
def load_saved_data():
    """Load previously saved forecast data from Excel."""
    try:
        return pd.read_excel("smhi_weather_forecast_24h.xlsx")
    except FileNotFoundError:
        return None
    
if __name__ == "__main__":
    print("Testing SMHI data collection...")
    print(f"Fetching weather for Stockholm (lat: {latitude}, lon: {longitude})")

    # Test collect_smhi_data
    df, status = collect_smhi_data()

    if df is not None:
        print(f"\n✅ Success! Status: {status}")
        print(f"\nCollected {len(df)} hours of forecast data")
        print("\nFirst 5 rows:")
        print(df.head())
        print("\nFile saved as: smhi_weather_forecast_24h.xlsx")
    else:
        print(f"\n❌ Error: {status}")

    # Test load_saved_data
    print("\n" + "="*50)
    print("Testing load_saved_data...")
    loaded_df = load_saved_data()

    if loaded_df is not None:
        print(f"✅ Successfully loaded {len(loaded_df)} rows from file")
    else:
        print("❌ No saved file found")