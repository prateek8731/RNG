import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import matplotlib.pyplot as plt
from datetime import datetime
from collections import Counter
from io import BytesIO

# --- Page Setup ---
st.set_page_config(page_title="LottoMax Prediction Dashboard", layout="wide")
st.title("🎯 LottoMax Prediction Engine")

# --- Tabs ---
tabs = st.tabs(["📁 Upload Data", "📊 Statistics", "🔮 Predictions", "🧾 Logs"])

# --- Session State ---
if "predictions" not in st.session_state:
    st.session_state.predictions = []

# --- Tab 1: Upload ---
with tabs[0]:
    st.header("Upload LottoMax Historical CSV")
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        df.columns = df.columns.str.strip()  # Clean column names
        st.session_state.df = df
        st.success("CSV loaded successfully!")
        st.write(df.tail())
    elif "df" in st.session_state:
        df = st.session_state.df
        st.write(df.tail())
    else:
        st.warning("Upload a file to begin.")

# --- Helper Functions ---
def generate_weighted_prediction(freq, recent_draws, n=3, count=7, low=1, high=50):
    predictions = []
    weighted_pool = []

    # Frequency to weighted pool
    for number, frequency in freq.items():
        weighted_pool.extend([number] * frequency)

    # Remove recent numbers (last 3 draws)
    exclude = set()
    for i in range(1, 8):
        exclude.update(recent_draws[f"Number{i}"].tail(3).values)

    # Generate unique predictions
    for _ in range(n):
        chosen = []
        while len(chosen) < count:
            candidate = np.random.choice(weighted_pool)
            if candidate not in chosen and candidate not in exclude:
                chosen.append(candidate)
        chosen.sort()
        bonus = np.random.randint(low, high + 1)
        predictions.append({"Numbers": chosen, "Bonus": bonus, "Time": datetime.now()})
    return predictions

def convert_df_to_csv(predictions_df):
    return predictions_df.to_csv(index=False).encode("utf-8")

# --- Tab 2: Stats ---
with tabs[1]:
    st.header("Statistical Visualizations")
    if "df" in st.session_state:
        df = st.session_state.df
        numbers_df = df[[col for col in df.columns if col.startswith("Number")]]
        flat_series = numbers_df.values.flatten()
        value_counts = pd.Series(flat_series).value_counts().reset_index()
        value_counts.columns = ["Number", "Frequency"]

        chart = alt.Chart(value_counts).mark_bar().encode(
            x=alt.X("Number:O", sort="-y"),
            y="Frequency:Q",
            tooltip=["Number", "Frequency"]
        ).properties(title="Frequency of Drawn Numbers", width=800, height=400)
        st.altair_chart(chart)
    else:
        st.warning("No data to analyze. Upload a CSV in the Upload tab.")

# --- Tab 3: Predictions ---
with tabs[2]:
    st.header("Generate Predictions")
    st.write("Click the button to generate AI-assisted predictions.")

    if st.button("🔮 Generate Predictions"):
        if "df" in st.session_state:
            df = st.session_state.df
            numbers = []
            for i in range(1, 8):
                numbers.extend(df[f"Number{i}"].values)
            freq = Counter(numbers)
            st.session_state.predictions = generate_weighted_prediction(freq, df)
        else:
            st.warning("Upload CSV data first.")

    if st.session_state.predictions:
        predictions_df = pd.DataFrame([{
            "Draw Time": p["Time"].strftime("%Y-%m-%d %H:%M:%S"),
            "Numbers": ', '.join(map(str, p["Numbers"])),
            "Bonus": p["Bonus"]
        } for p in st.session_state.predictions])

        st.write(predictions_df)

        csv_download = convert_df_to_csv(predictions_df)
        st.download_button("📥 Download Predictions as CSV", data=csv_download, file_name="predictions.csv", mime="text/csv")

# --- Tab 4: Logs ---
with tabs[3]:
    st.header("Logs and Debug Info")
    if "df" in st.session_state:
        st.subheader("Dataset Info")
        st.write(st.session_state.df.describe(include='all'))
        st.write("Total Draws:", len(st.session_state.df))
    if st.session_state.predictions:
        st.subheader("Prediction Log")
        for i, p in enumerate(st.session_state.predictions):
            st.text(f"[{i+1}] {p['Time'].strftime('%Y-%m-%d %H:%M:%S')} - Numbers: {p['Numbers']} Bonus: {p['Bonus']}")
