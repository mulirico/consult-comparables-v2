import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium
from consult_comparables_v2.service import get_instant_valuation


def display_property(payload, comparables, actual_price):
    st.subheader("Reference Property")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Estimated Value (€)", f"{comparables['valuation']:,}")
        st.metric("Actual Sale (€)", f"{actual_price:,}")
        st.metric("Difference (€)", f"{comparables['valuation'] - actual_price:,}")
    with col2:
        st.write(f"Type: {payload['property_type']}")
        st.write(f"Bedrooms: {payload['beds']}")
        st.write(f"Area (sqm): {payload['sqm']}")

    lat = payload['current_latitude']
    lon = payload['current_longitude']
    m = folium.Map(location=[lat, lon], zoom_start=13)
    folium.Marker(
        location=[lat, lon],
        popup="Reference Property",
        icon=folium.Icon(color="red")
    ).add_to(m)
    top_comparables = comparables['top_comparables']
    count = 0
    while count < min(len(top_comparables), 5):
        location = top_comparables[count].get('location')
        lat_lng = location.split(',')
        folium.Marker(
            location=[float(lat_lng[0]), float(lat_lng[1])],
            popup=f"{top_comparables[count]['region']} - {top_comparables[count]['beds']} Beds "
                  f"- €{top_comparables[count]['price']:,}"
                  f" - {top_comparables[count]['id']}(Id)",
            icon=folium.Icon(color="blue")
        ).add_to(m)
        count += 1

    st_folium(m, width=800, height=500)

    st.subheader("Comparables")
    st.dataframe(comparables['top_comparables'])

    avg_price_sqm = comparables['avg_sqm_price']
    fluctuation = round(((comparables["valuation"] - actual_price) / actual_price) * 100, 2)
    if fluctuation < 0:
        absolute_fluctuation = fluctuation * -1
    else:
        absolute_fluctuation = fluctuation
    st.subheader("Valuation Summary")
    summary = pd.DataFrame([
        {
            "Metric": "Average €/m²",
            "Value": round(avg_price_sqm, 2)
        },
        {
            "Metric": "Sold reference €/m²",
            "Value": round(sold_price / payload["sqm"], 2)
        },
        {
            "Metric": "Fluctuation (%)",
            "Value": fluctuation
        },
        {
            "Metric": "Confidence",
            "Value": (
                "High" if absolute_fluctuation < 20
                else "Moderate" if 20 < absolute_fluctuation < 30
                else "Low"
            )
        },
    ])
    st.table(summary)
    st.divider()
    st.json(comparables)

st.title('Request instant valuation API v2')
st.divider()

st.subheader('Enter your property data below')
form = st.form('get_valuation')
sold_price = form.number_input('Price in ppr')
lat = form.text_input('Latitude',)
lng = form.text_input('Longitude')
bed = form.number_input('Bedrooms', min_value=0)
property_type = form.text_input('Property type', value='Detached House')
sqm = form.number_input('Sqm')
submitted = form.form_submit_button("Evaluate")
payload = {
    "current_latitude": f"{lat}",
    "current_longitude": f"{lng}",
    "property_type": property_type,
    "market_type": [
        "Residential Sale"
    ],
    "beds": bed,
    "sqm": sqm,
    "listing_type": [
        "sold"
    ]
}

if submitted:
    response = get_instant_valuation(payload)
    if response is not None:
        if response.status_code == 200:
            st.session_state['sold_price'] = sold_price
            st.session_state['valuation_data'] = response.json()
            st.session_state['payload'] = payload
        else:
            st.session_state['valuation_data'] = None
            st.write('Request error: \n'
                     f'{response.status_code} \n { response.json()}')

if 'valuation_data' in st.session_state and 'payload' in st.session_state:
    if st.session_state['valuation_data']:
        display_property(st.session_state['payload'] , st.session_state['valuation_data'], st.session_state['sold_price'])
