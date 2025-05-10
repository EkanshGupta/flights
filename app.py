# app.py
import streamlit as st
import pandas as pd
import sqlite3
from tqdm import tqdm
import numpy as np

domestic_city_pairs = [
    ["ATL","SEA"], 
    ["ATL","DEN"], 
    ["ATL","LIH"],
    ["ATL","OGG"],
    ["ATL","SAN"], 
    ["ATL","SFO"], 
    ["ATL","DFW"],
    ["ATL","LAS"],
    ["ATL","PHX"], 
    ["ATL","BOS"], 
]
dom_city = [i[1] for i in domestic_city_pairs]

intl_city_pairs = [
    ["ATL","FCO",[5,7,9,11,13]], 
    ["ATL","DEL",[21,24,27,30,33]], 
    ["ATL","CDG",[5,7,9,11,13]],
    ["ATL","FRA",[5,7,9,11,13]],
    ["ATL","LHR",[5,7,9,11,13]], 
    ["ATL","ATH",[5,7,9,11,13]], 
    ["ATL","CAI",[5,7,9,11,13]],
    ["ATL","CUN",[4,5,6,7,8]],
    ["ATL","HND",[5,6,7,9,10]],
]
intl_city = [i[1] for i in intl_city_pairs]

def extract_price_and_currency(df):
    # Use regex to extract currency symbol (assumes symbol is at the start)
    df['currency'] = df['price'].str.extract(r'^([^\d]+)')  # non-digit characters at start
    # Extract numeric part, handle empty strings after replacement
    price_numeric = df['price'].str.replace(r'[^\d.]', '', regex=True)
    # Replace empty strings with NaN explicitly
    price_numeric = price_numeric.replace('', np.nan)
    # Assign and convert safely
    df['price_float'] = price_numeric.astype(float)
    # Drop rows where conversion failed
    df = df.dropna(subset=['price_float'])
    df['departure_date'] = pd.to_datetime(df['departure_date'], errors='coerce')
    df = df.dropna(subset=['departure_date'])
    df['departure_date'] = pd.to_datetime(df['departure_date'], errors='coerce')
    df = df.dropna(subset=['departure_date'])
    return df


# @st.cache_data()
def load_df_from_db(db_path, origin=None, destination=None, max_price=None):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query = "SELECT * FROM data_table WHERE 1=1"
    params = []

    if origin:
        query += " AND origin = ?"
        params.append(origin)
    if destination:
        query += " AND destination = ?"
        params.append(destination)
    # if max_price:
    #     query += " AND CAST(price AS FLOAT) <= ?"
    #     params.append(max_price)

    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df


def main():
    st.title("Flight Data Viewer")

    st.sidebar.header("Initial Query Parameters")
    origin = st.sidebar.text_input("Origin (optional)")
    destination = st.sidebar.text_input("Destination (optional)")
    
    if st.sidebar.button("Load Data", key="load_button"):
        if not origin or not destination:
            st.error("Please enter both origin and destination.")
            return
    
        if (origin=="ATL" and destination in dom_city) or (origin in dom_city and destination=="ATL"):
            db_file = "./logs/dataDB_domestic.db"
        elif (origin=="ATL" and destination in intl_city) or (origin in intl_city and destination=="ATL"):
            db_file = "./logs/dataDB_intl.db"
        else:
            print("Incorrect origin and destination")
            return
    
        # max_price = st.sidebar.number_input("Max Price (optional)", min_value=0.0, value=0.0, step=10.0)
        max_price = None
    
        with st.spinner("Querying database and loading DataFrame..."):
            df = load_df_from_db(db_file, origin or None, destination or None, max_price or None)

            if df.empty:
                st.warning("No data found for given parameters.")
                return
            
        # with st.spinner("Preprocessing results"):
            df = extract_price_and_currency(df)
            st.success(f"Loaded {len(df)} rows.")
            st.session_state.df = df
    
    if 'df' in st.session_state:
        df = st.session_state.df
        with st.spinner("Populating filters"):
            st.sidebar.header("Post-load Filters")
            min_price = float(df['price_float'].min())
            max_price = float(df['price_float'].max())
            min_date = df['departure_date'].min()
            max_date = df['departure_date'].max()
            unique_names = sorted(df['name'].dropna().unique().tolist())
            unique_days = sorted(df['days'].dropna().unique().astype(int).tolist())
        
            unique_stops = sorted(df['stops'].dropna().unique().tolist())
            numeric_stops = sorted({int(s) for s in unique_stops if str(s).isdigit()})
        
            with st.sidebar.form("filter_form"):
                date_range = st.date_input("Departure Date Range", value=(min_date, max_date))
                price_range = st.slider("Price Range", min_price, max_price, (min_price, max_price))
                max_stops = st.slider("Max Stops", 0, max(numeric_stops) if numeric_stops else 3, 2)
                name_selected = st.selectbox("Airline/Flight Name", options=["All"] + unique_names)
                days_selected = st.selectbox("Trip Length (days)", options=["All"] + unique_days)
                apply_filters = st.form_submit_button("Apply Filters")

        if apply_filters:
            with st.spinner("Applying filters"):
                filtered = df[
                    (df['price_float'] >= price_range[0]) &
                    (df['price_float'] <= price_range[1]) &
                    (df['departure_date'] >= pd.to_datetime(date_range[0])) &
                    (df['departure_date'] <= pd.to_datetime(date_range[1])) &
                    (pd.to_numeric(df['stops'], errors='coerce') <= max_stops)
                ]
    
                if name_selected != "All":
                    filtered = filtered[filtered['name'] == name_selected]
                if days_selected != "All":
                    filtered = filtered[filtered['days'] == int(days_selected)]
                filtered = filtered.sort_values(by="price_float", ascending=True)
                st.write(f"Filtered results: {len(filtered)} rows. Displaying {min(len(filtered), 10000)} rows")
                st.dataframe(filtered.head(10000))
    else:
        st.info("Use the sidebar to load data.")
        
if __name__ == "__main__":
    main()
