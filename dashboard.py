import streamlit as st
import pandas as pd
from app import collect_smhi_data, collect_yr_data, load_saved_data

st.set_page_config(page_title="Weather Forecast Dashboard", page_icon="🌦️", layout="centered")
st.title("🌦️ Weather Forecast Dashboard")

st.write("Fetch and view 24-hour weather forecasts from **SMHI** and **YR** APIs.")

# Coordinates section
st.sidebar.header("Location Settings")
latitude = st.sidebar.number_input("Latitude", value=59.309965, format="%.6f")
longitude = st.sidebar.number_input("Longitude", value=18.021515, format="%.6f")

# Choose provider
st.subheader("Select Forecast Source")
option = st.selectbox("Weather Data Source", ("SMHI", "YR", "Both"))

# Fetch data
if st.button("Fetch Weather Data"):
    if option == "SMHI":
        df_smhi, msg = collect_smhi_data(lat=latitude, lon=longitude)
        if df_smhi is not None:
            st.success("✅ SMHI forecast fetched successfully")
            st.dataframe(df_smhi)
        else:
            st.error(msg)

    elif option == "YR":
        df_yr, msg = collect_yr_data(lat=latitude, lon=longitude)
        if df_yr is not None:
            st.success("✅ YR forecast fetched successfully")
            st.dataframe(df_yr)
        else:
            st.error(msg)

    else:
        df_smhi, msg1 = collect_smhi_data(lat=latitude, lon=longitude)
        df_yr, msg2 = collect_yr_data(lat=latitude, lon=longitude)
        if df_smhi is not None and df_yr is not None:
            st.success("✅ SMHI & YR forecasts fetched successfully")
            combined = pd.concat([df_smhi, df_yr])
            st.dataframe(combined)
        else:
            st.error(f"SMHI: {msg1}, YR: {msg2}")

st.divider()
st.header("📂 View Saved Forecasts")

col1, col2 = st.columns(2)
with col1:
    if st.button("Show Saved SMHI Data"):
        df = load_saved_data("smhi")
        if df is not None:
            st.dataframe(df)
        else:
            st.warning("No saved SMHI forecast found.")
with col2:
    if st.button("Show Saved YR Data"):
        df = load_saved_data("yr")
        if df is not None:
            st.dataframe(df)
        else:
            st.warning("No saved YR forecast found.")
