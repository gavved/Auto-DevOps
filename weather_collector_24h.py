import requests as req
import pandas as pd
from datetime import datetime
from constants import YR_USER_AGENT

latitude = 59.309965
longitude = 18.021515

# Menu
def main_menu():
    while True:
        print("-"*50)
        print("Main Menu:")
        print("1. Fetch weather forecast from SMHI, YR, or both.")
        print("2. Print weather forecast from SMHI, YR, or both.")
        print("9. Exit program...")

        val = input("Choose an option: ")

        if val == "1":
            print("-"*50)
            print("Do you want to fetch weather forecast from SMHI, YR, or both?")
            print("1. SMHI")
            print("2. YR")
            print("3. SMHI & YR")
            val = input("\nChoose an option: ")
            if val == "1":
                collect_smhi_data()
            elif val == "2":
                collect_yr_data()
            elif val == "3":
                collect_smhi_data()
                collect_yr_data()
            else:
                print("Invalid input, please try again!")

        elif val == "2":
            print("-"*50)
            print("Which weather forecast do you want to print? SMHI, YR, or both?")
            print("1. SMHI")
            print("2. YR")
            print("3. SMHI & YR")
            val = input("\nChoose an option: ")
            if val == "1":
                print_smhi_data()
            elif val == "2":
                print_yr_data()
            elif val == "3":
                print_smhi_data()
                print_yr_data()
            else:
                print("Invalid input, please try again!")

        elif val == "9":
            print("Exiting program...")
            break
        else:
            print("Invalid input, please try again: ")

# Collect weather data from SMHI
def collect_smhi_data():
    smhi_api_url = f"https://opendata-download-metfcst.smhi.se/api/category/pmp3g/version/2/geotype/point/lon/{longitude}/lat/{latitude}/data.json"
    smhi_weather_data = req.get(smhi_api_url)
    
    # Status code
    if smhi_weather_data.status_code == 200:
        smhi_weather_forecast = smhi_weather_data.json()

        # List to store forecast data
        forecast_data_smhi = []

        # Get current time
        current_time = datetime.now()

        # Counter for number of hours
        hours_collected = 0

        # Loop through the data
        for data in smhi_weather_forecast['timeSeries']:

            # Get forecast time and convert to datetime object
            valid_time = data['validTime']
            forecast_datetime = datetime.fromisoformat(valid_time[:-1])

            # Ensure forecast time is from current time onward
            if forecast_datetime >= current_time:

                # End loop after 24 collected hours
                if hours_collected >= 24:
                    break

                # Split date/time
                forecast_date, forecast_hour = valid_time.split("T")

                # Create an empty dictionary and loop through forecast data in JSON
                parameters = {}
                for param in data['parameters']:
                    parameters[param['name']] = param['values']

                # Temperature
                forecast_temp = parameters.get('t', [None])[0]

                # Rain or snow
                forecast_rain_or_snow = parameters.get('pcat', [None])[0]
                rain_or_snow_bool = True if forecast_rain_or_snow > 0 else False

                # Dictionary to store forecast parameters
                forecast_dict_smhi = {
                    "Created": datetime.now(),
                    "Longitude": longitude,
                    "Latitude": latitude,
                    "Date": forecast_date,
                    "Hour": forecast_hour[:5],
                    "Temperature (°C)": round(forecast_temp),
                    "Rain or Snow": rain_or_snow_bool,
                    "Provider": "SMHI"
                }

                # Add each forecast parameter to the list
                forecast_data_smhi.append(forecast_dict_smhi)
                
                # Increment counter for each collected hour
                hours_collected += 1

        # Save to Excel
        save_to_excel_smhi(forecast_data_smhi)

    else:
        print(f"Could not fetch weather forecast from SMHI. Status code: {smhi_weather_data.status_code}")
        if smhi_weather_data.status_code == 404:
            print("Error, check coordinates!")
        elif smhi_weather_data.status_code == 401 or 403:
            print("Error, access denied!")
        else:
            print("Unknown error, check API documentation and try again!")

# Collect weather data from YR
def collect_yr_data():
    yr_api_url = f"https://api.met.no/weatherapi/locationforecast/2.0/compact?lat={latitude}&lon={longitude}"
    yr_weather_data = req.get(yr_api_url)

    # API Access
    headers = {
        'User-Agent': YR_USER_AGENT
    }

    yr_weather_data = req.get(yr_api_url, headers=headers)
    
    # Status code
    if yr_weather_data.status_code == 200:
        yr_weather_forecast = yr_weather_data.json()

        # List to store forecast data
        forecast_data_yr = []

        # Get current time
        current_time = datetime.now()

        # Counter for number of hours
        hours_collected = 0

        # Loop through the data
        for data in yr_weather_forecast['properties']['timeseries']:

            # Get forecast time and convert to datetime object
            valid_time = data['time']
            forecast_datetime = datetime.fromisoformat(valid_time[:-1])

            # Ensure forecast time is from current time onward
            if forecast_datetime >= current_time:

                # End loop after 24 collected hours
                if hours_collected >= 24:
                    break  

                # Split date/time 
                forecast_date, forecast_hour = valid_time.split("T")

                # Get "Instant" parameters
                instant_parameters = data['data']['instant']['details']

                # Temperature
                forecast_temp = instant_parameters.get('air_temperature', None)

                # Get "Next 1 Hours" parameters
                next_1_hours_parameters = data['data'].get('next_1_hours', {}).get('details', {})
            
                # Rain or snow
                forecast_rain_or_snow = next_1_hours_parameters.get('probability_of_precipitation', None)
                rain_or_snow_bool = True if forecast_rain_or_snow is not None and forecast_rain_or_snow > 0 else False

                # Dictionary to store forecast parameters
                forecast_dict_yr = {
                    "Created": datetime.now(),
                    "Longitude": longitude,
                    "Latitude": latitude,
                    "Date": forecast_date,
                    "Hour": forecast_hour[:5],
                    "Temperature (°C)": round(forecast_temp),
                    "Rain or Snow": rain_or_snow_bool,
                    "Provider": "YR"
                }

                # Add each forecast parameter to the list
                forecast_data_yr.append(forecast_dict_yr)
            
                # Increment counter for each collected hour
                hours_collected += 1

        # Save to Excel
        save_to_excel_yr(forecast_data_yr)

    else:
        print(f"Could not fetch weather forecast from YR. Status code: {yr_weather_data.status_code}")
        if yr_weather_data.status_code == 404:
            print("Error, check coordinates!")
        elif yr_weather_data.status_code == 401 or 403:
            print("Error, access denied!")
        else:
            print("Unknown error, check API documentation and try again!")

def save_to_excel_smhi(forecast_data_smhi):
    # Create DataFrame from list
    df = pd.DataFrame(forecast_data_smhi)

    # Save DataFrame to Excel
    df.to_excel('smhi_weather_forecast_24h.xlsx', index=False)
    print("\nWeather forecast from SMHI has been fetched and saved to smhi_weather_forecast_24h.xlsx")

def save_to_excel_yr(forecast_data_yr):
    # Create DataFrame from list
    df = pd.DataFrame(forecast_data_yr)

    # Save DataFrame to Excel
    df.to_excel('yr_weather_forecast_24h.xlsx', index=False)
    print("\nWeather forecast from YR has been fetched and saved to yr_weather_forecast_24h.xlsx")

def print_smhi_data():
    try:
        # Read data from created Excel
        df = pd.read_excel('smhi_weather_forecast_24h.xlsx')

        created_date = pd.to_datetime(df['Created'][0]).date()
        print("-"*50)
        print(f"Weather forecast from SMHI, retrieved on {created_date}:\n")

        # Loop through created Excel
        for index, row in df.iterrows():
            date = row["Date"]
            hour = row["Hour"]
            temp = row["Temperature (°C)"]
            rain_or_snow = "Precipitation" if row['Rain or Snow'] == True else "No precipitation"

            print(f"{date} {hour} {temp} degrees, {rain_or_snow}")

    except FileNotFoundError:
        print("")
        print("No weather forecast from SMHI found, please try again!")

def print_yr_data():
    try:
        # Read data from created Excel
        df = pd.read_excel('yr_weather_forecast_24h.xlsx')

        created_date = pd.to_datetime(df['Created'][0]).date()
        print("-"*50)
        print(f"Weather forecast from YR, retrieved on {created_date}:\n")

        # Loop through created Excel
        for index, row in df.iterrows():
            date = row["Date"]
            hour = row["Hour"]
            temp = row["Temperature (°C)"]
            rain_or_snow = "Precipitation" if row['Rain or Snow'] == True else "No precipitation"

            print(f"{date} {hour} {temp} degrees, {rain_or_snow}")

    except FileNotFoundError:
        print("")
        print("No weather forecast from YR found, please try again!")


if __name__ == "__main__":
    main_menu()