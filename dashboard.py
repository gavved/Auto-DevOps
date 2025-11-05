import streamlit as st
import pandas as pd
from app import collect_smhi_data
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

st.set_page_config(page_title="SMHI Weather Forecast", page_icon="🌦️", layout="wide")
st.title("🌦️ SMHI Weather Forecast Dashboard")

st.write("View 48-hour weather forecast from **SMHI** API.")

st.sidebar.header("Plats")

cities = [
    ("Stockholm",   59.3293, 18.0686),
    ("Göteborg",    57.7089, 11.9746),
    ("Malmö",       55.6050, 13.0038),
    ("Uppsala",     59.8586, 17.6389),
    ("Västerås",    59.6099, 16.5448),
    ("Örebro",      59.2741, 15.2066),
    ("Linköping",   58.4109, 15.6216),
    ("Helsingborg", 56.0465, 12.6945),
    ("Jönköping",   57.7826, 14.1618),
    ("Norrköping",  58.5877, 16.1924),
]

city_names = [c[0] for c in cities]
selected_city = st.sidebar.selectbox("Välj stad (topp 10)", city_names, index=0)

city_lat, city_lon = next((lat, lon) for name, lat, lon in cities if name == selected_city)

latitude = city_lat
longitude = city_lon

with st.spinner("Hämtar prognos från SMHI..."):
    df_smhi, msg = collect_smhi_data(lat=latitude, lon=longitude)

if df_smhi is not None:
    st.success(f"✅ Prognos hämtad för {selected_city} ({latitude:.4f}, {longitude:.4f})")
    st.dataframe(df_smhi, width="stretch")
else:
    st.error(msg)




st.subheader("☁️ Daily Precipitation (48h Forecast)")

chart_df = df_smhi.copy()
chart_df["Datetime"] = pd.to_datetime(chart_df["Date"] + " " + chart_df["Hour"])
chart_df["Weekday"] = chart_df["Datetime"].dt.strftime("%A")

# Classify rain vs snow based on temperature
def classify_precip(row):
    if row["Rain or Snow"]:
        return "Snow" if row["Temperature (°C)"] <= 0 else "Rain"
    return None

chart_df["WeatherType"] = chart_df.apply(classify_precip, axis=1)

# Summarize per day
daily_summary = chart_df.groupby("Date")["WeatherType"].apply(lambda x: set(filter(None, x))).reset_index()
daily_summary["Weekday"] = pd.to_datetime(daily_summary["Date"]).dt.strftime("%A")


daily_summary["Rain"] = daily_summary["WeatherType"].apply(lambda x: "🌧️" if "Rain" in x else "❌")
daily_summary["Snow"] = daily_summary["WeatherType"].apply(lambda x: "❄️" if "Snow" in x else "❌")
daily_summary_display = daily_summary[["Weekday", "Date", "Rain", "Snow"]]

# Display without index
st.dataframe(daily_summary_display, use_container_width=True, hide_index=True)


#----------- Temperature Trend Plot ----------

st.subheader(f"🌡️ Temperature Trend (12Hours) — {selected_city}")

city_df, msg = collect_smhi_data(lat=latitude, lon=longitude)
if city_df is not None:
    city_df["Datetime"] = pd.to_datetime(city_df["Date"] + " " + city_df["Hour"])
    city_df = city_df.sort_values("Datetime").head(12)  

    fig, ax = plt.subplots(figsize=(8, 3), facecolor="#f0f0f0")  # light grey background
    ax.plot(city_df["Datetime"], city_df["Temperature (°C)"], color='orange', linewidth=2)

    # Axis labels
    ax.set_ylabel("Temperature (°C)", fontsize=10)
    ax.set_title(f"{selected_city} — Next 12 Hours Temperature", fontsize=12)
    ax.grid(False) # Remove gridlines

    # Removed spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)

    # adjust/remove ticks
    ax.tick_params(left=False, bottom=True)

    #  x-axis ticks: show every 2nd hour
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

    st.pyplot(fig)
