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


# ========== YR ==========
def collect_yr_data(lat=latitude, lon=longitude):
    yr_api_url = f"https://api.met.no/weatherapi/locationforecast/2.0/compact?lat={lat}&lon={lon}"
    yr_weather_data = req.get(yr_api_url)

    if yr_weather_data.status_code != 200:
        return None, f"YR API error: {yr_weather_data.status_code}"

    yr_weather_forecast = yr_weather_data.json()
    forecast_data_yr = []
    current_time = datetime.now()
    hours_collected = 0

    for data in yr_weather_forecast["properties"]["timeseries"]:
        valid_time = data["time"]
        forecast_datetime = datetime.fromisoformat(valid_time[:-1])

        if forecast_datetime < current_time:
            continue
        if hours_collected >= 24:
            break

        forecast_date, forecast_hour = valid_time.split("T")
        instant_parameters = data["data"]["instant"]["details"]
        forecast_temp = instant_parameters.get("air_temperature", None)
        next_1_hours_parameters = data["data"].get("next_1_hours", {}).get("details", {})
        forecast_rain_or_snow = next_1_hours_parameters.get("probability_of_precipitation", None)
        rain_or_snow_bool = True if forecast_rain_or_snow and forecast_rain_or_snow > 0 else False

        forecast_data_yr.append({
            "Created": datetime.now(),
            "Longitude": lon,
            "Latitude": lat,
            "Date": forecast_date,
            "Hour": forecast_hour[:5],
            "Temperature (°C)": round(forecast_temp),
            "Rain or Snow": rain_or_snow_bool,
            "Provider": "YR"
        })
        hours_collected += 1

    df = pd.DataFrame(forecast_data_yr)
    df.to_excel("yr_weather_forecast_24h.xlsx", index=False)
    return df, "Success"


# ========== File Loaders ==========
def load_saved_data(provider: str):
    """Load previously saved forecast data from Excel."""
    try:
        if provider.lower() == "smhi":
            return pd.read_excel("smhi_weather_forecast_24h.xlsx")
        elif provider.lower() == "yr":
            return pd.read_excel("yr_weather_forecast_24h.xlsx")
    except FileNotFoundError:
        return None
