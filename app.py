from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st


st.set_page_config(page_title="California Housing Data (1990)", layout="wide")
st.title("California Housing Data (1990) by Zhang Shiyan")


@st.cache_data
def load_data(path, modified_time):
    return pd.read_csv(path)


data_path = Path(__file__).resolve().parent / "housing.csv"
if not data_path.is_file():
    st.error("Please place housing.csv in the same folder as app-housing.py.")
    st.stop()

try:
    data = load_data(str(data_path), data_path.stat().st_mtime_ns)
except (OSError, pd.errors.ParserError, pd.errors.EmptyDataError) as error:
    st.error(f"Unable to read housing.csv: {error}")
    st.stop()

required_columns = {
    "latitude", "longitude", "median_house_value", "median_income", "ocean_proximity"
}
missing_columns = required_columns - set(data.columns)
if missing_columns:
    st.error(f"Missing columns in housing.csv: {', '.join(sorted(missing_columns))}")
    st.stop()

minimum_value = st.slider(
    "Minimal Median House Value", min_value=0, max_value=500001, value=200000
)
st.subheader("See more filters in the sidebar:")

location_types = sorted(data["ocean_proximity"].dropna().unique().tolist())
selected_locations = st.sidebar.multiselect(
    "Choose the location type", options=location_types, default=location_types
)
income_level = st.sidebar.radio("Choose income level", ["Low", "Medium", "High"])

filtered = data.loc[
    (data["median_house_value"] >= minimum_value)
    & data["ocean_proximity"].isin(selected_locations)
]
if income_level == "Low":
    filtered = filtered.loc[filtered["median_income"] <= 2.5]
elif income_level == "Medium":
    filtered = filtered.loc[
        (filtered["median_income"] > 2.5) & (filtered["median_income"] < 4.5)
    ]
else:
    filtered = filtered.loc[filtered["median_income"] >= 4.5]

st.caption(f"Matching districts: {len(filtered):,}")
if filtered.empty:
    st.info("No districts match these filters. Try changing the selections.")

st.map(filtered[["latitude", "longitude"]].dropna())

st.subheader("Median House Value Distribution")
figure, axis = plt.subplots()
axis.hist(filtered["median_house_value"].dropna(), bins=30, edgecolor="white")
axis.set_xlabel("Median House Value (USD)")
axis.set_ylabel("Number of Districts")
figure.tight_layout()
st.pyplot(figure)
plt.close(figure)
