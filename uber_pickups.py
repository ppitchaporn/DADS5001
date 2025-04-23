#python -m venv myvenv
#myvenv\Scripts\activate
#pip install streamlit pandas numpy plotly
#streamlit run uber_pickups.py

import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
from datetime import datetime
import plotly.express as px

st.title('Uber pickups in NYC')

DATE_COLUMN = 'date/time'
DATA_URL = ('https://s3-us-west-2.amazonaws.com/'
         'streamlit-demo-data/uber-raw-data-sep14.csv.gz')


#Fetch some data
@st.cache_data
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])
    return data

# Create a text element and let the reader know the data is loading.
data_load_state = st.text('Loading data...')
# Load 10,000 rows of data into the dataframe.
data = load_data(10000)
# Notify the reader that the data was successfully loaded.
data_load_state.text("Done! (using st.cache_data)")


#Use a button to toggle the raw data
if st.checkbox('Show raw data'):
    st.subheader('Raw data')
    st.write(data)

#Draw a histogram
st.subheader('Number of pickups by hour')
hist_values = np.histogram(
    data[DATE_COLUMN].dt.hour, bins=24, range=(0,24))[0]
st.bar_chart(hist_values)


#Exercise
#1. Convert 2D map to 3D map using PyDeck.
st.subheader("3D Hexagon Map of Uber pickups")

midpoint = (np.average(data['lat']), np.average(data['lon']))
#midpoint

st.pydeck_chart(
    pdk.Deck(
        map_style=None,
        initial_view_state=pdk.ViewState(
            latitude=midpoint[0],
            longitude=midpoint[1],
            zoom=11,
            pitch=50,
        ),
        layers=[
            pdk.Layer(
                "HexagonLayer",
                data=data,
                get_position='[lon, lat]',
                radius=100,
                elevation_scale=4,
                elevation_range=[0, 1000],
                pickable=True,
                extruded=True,
            ),
        ],
    )
)

#2. Use Date input
today_date = datetime.today()
d = st.date_input("Select pickup date: ", today_date)
st.write("Your pickup date is:", d)

#3. Use Selectbox
option = st.selectbox(
    "How would you like to pay?",
    ("Credit Card", "Bank Transfer", "PayPal", "Cash"),
    index=None,
    placeholder="Select payment method...",
)

st.write("You selected:", option)

#4. Use plotly (any charts)
# Extract date and hour from datetime
data['date'] = data[DATE_COLUMN].dt.date
data['hour'] = data[DATE_COLUMN].dt.hour

# Count pickups per date-hour
pickup_counts = data.groupby(['date', 'hour']).size().reset_index(name='pickups')

# Calculate average pickups per hour across all days
avg_hourly = pickup_counts.groupby('hour')['pickups'].mean().reset_index()

# Plot line chart
fig = px.line(
    avg_hourly,
    x='hour',
    y='pickups',
    title='Average Number of Uber Pickups per Hour',
    labels={
        'hour': 'Hour of Day (0–23)',
        'pickups': 'Average Pickups (rides)'
    }
)
st.plotly_chart(fig)


#5. Click a button to increase the number in the following message, "This page has run 24 times."
if "counter" not in st.session_state:
    st.session_state.counter = 0

st.session_state.counter += 1

st.header(f"This page has run {st.session_state.counter} times.")
st.button("Run it again")


