import json
import urllib.request
import pandas as pd
import datetime
from urllib.parse import quote

import streamlit as st
import folium
from folium.features import DivIcon
from streamlit_folium import st_folium

st.set_page_config(layout="wide", page_title="Satellite & Canopy Tiles Viewer")

center_lat = 37.9838
center_lon = 23.7275

st.sidebar.header("Meteoblue Heat Map")
selected_date = st.sidebar.date_input("Select Date", value=datetime.date(2026, 6, 28))
selected_time = st.sidebar.time_input("Select Time", value=datetime.time(22, 0))

formatted_time = f"{selected_date.isoformat()}T{selected_time.strftime('%H:%M:%S')}+00:00"
encoded_time = quote(formatted_time)



m = folium.Map(location=[center_lat, center_lon], tiles="Cartodb dark_matter", zoom_start=17)

folium.TileLayer(
    tiles='http://localhost:8000/v1/satelite/{z}/{x}/{y}.png',
    attr='Satellite Tiles',
    name='Satellite Tiles',
    overlay=True,
    control=True,
    max_zoom=20,
).add_to(m)

# Add Canopy Mask Layer
folium.TileLayer(
    tiles='http://localhost:8000/v1/canopy/{z}/{x}/{y}.png',
    attr='Canopy Mask',
    name='Canopy Mask',
    overlay=True,
    control=True,
    max_zoom=20,
    opacity=0.8
).add_to(m)

# Add Heat Map Layer
folium.raster_layers.ImageOverlay(
    image=f'http://localhost:8000/v1/heat-map/athens/{encoded_time}.webp',
    bounds=[[37.85, 23.55], [38.15, 23.95]],
    opacity=0.5,
    name='Temperature Heat Map',
    overlay=True,
    control=True,
).add_to(m)

folium.LayerControl().add_to(m)

st.set_option("client.toolbarMode", "viewer")

st_data = st_folium(m, use_container_width=True, height=600, returned_objects=[])
