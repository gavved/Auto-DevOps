import requests as req
import pandas as pd
from datetime import datetime

# Default coordinates (Stockholm)
latitude = 59.3293
longitude = 18.0686


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
        if hours_collected >= 48:
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
    return df, "Success"