import streamlit as st
import pandas as pd
from app import collect_smhi_data, load_saved_data

st.set_page_config(page_title="Weather Forecast Dashboard", page_icon="🌦️", layout="centered")
st.title("🌦️ Weather Forecast Dashboard")

st.write("Fetch and view 24-hour weather forecasts from **SMHI** API.")

# Coordinates section
st.sidebar.header("Location Settings")
latitude = st.sidebar.number_input("Latitude", value=59.309965, format="%.6f")
longitude = st.sidebar.number_input("Longitude", value=18.021515, format="%.6f")

# Fetch data
st.subheader("Fetch New Forecast")
if st.button("Fetch Weather Data"):
    with st.spinner("Fetching data from SMHI..."):
        df_smhi, msg = collect_smhi_data(lat=latitude, lon=longitude)
        
        if df_smhi is not None:
            st.success("✅ SMHI forecast fetched successfully")
            st.dataframe(df_smhi, use_container_width=True)
        else:
            st.error(f"❌ {msg}")

st.divider()

# View saved data
st.subheader("📂 View Saved Forecast")
if st.button("Show Saved SMHI Data"):
    df = load_saved_data()
    if df is not None:
        st.success(f"✅ Loaded {len(df)} hours of forecast data")
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("⚠️ No saved SMHI forecast found. Fetch data first!")