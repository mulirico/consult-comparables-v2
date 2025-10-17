import pandas as pd
import requests
import streamlit as st
from consult_comparables_v2.service import read_csv, match_eircode_return_property_info, get_instant_valuation

st.title('Valuation endpoint statistics')
st.divider()

form = st.form('Submit csv')
properties = form.file_uploader(
    label='Upload properties CSV',
    type='csv',
)
prices = form.file_uploader(
    label='Upload prices CSV',
    type='csv',
)
submitted = form.form_submit_button('Get statistics')

if submitted:
    if properties:
        load_properties_csv = read_csv(properties)
        st.session_state['property_data'] = load_properties_csv
    if prices:
        load_prices_csv = read_csv(prices)
        st.session_state['price_data'] = load_prices_csv


if 'property_data' in st.session_state and 'price_data' in st.session_state:
    with st.spinner('Loading...', show_time=True):
        properties = st.session_state['property_data']
        prices = st.session_state['price_data']
        st.session_state['matched_data'] = match_eircode_return_property_info(properties, prices)

        if 'matched_data' in st.session_state:
            data = st.session_state['matched_data']
            summary_rows = []
            errors = []
            for row in data:
                payload = {
                    "current_latitude": f"{row['Latitude']}",
                    "current_longitude": f"{row['Longitude']}",
                    "property_type": f'{row['PropertyType']}',
                    "market_type": [
                        "Residential Sale"
                    ],
                    "beds": f'{row['Beds']}',
                    "sqm": f'{row['SqrMetres']}',
                    "listing_type": [
                        "sold"
                    ]
                }

                response = get_instant_valuation(payload)
                if isinstance(response, requests.Response) and response.status_code == 200:
                    valuation_data = response.json()
                    sold_price = row['Price']
                    sqm = row['SqrMetres']
                    avg_price_sqm = valuation_data.get('avg_sqm_price', None)
                    sold_price_sqm = sold_price / sqm if sqm else None
                    fluctuation = round(((valuation_data["valuation"] - sold_price) / sold_price) * 100, 2) \
                        if sold_price else None
                    summary_rows.append({
                        'Eircode': row['Eircode'],
                        'Valuation': valuation_data['valuation'],
                        'Sold Price (ppp)': sold_price,
                        'Avg Price Sqm (valuation)': avg_price_sqm,
                        'Avg Price Sqm (ppp)': sold_price_sqm,
                        'Fluctuation (%)': fluctuation
                    })
                else:
                    if isinstance(response, requests.Response):
                        error_message = (
                            f'Error requesting for property: {row["Eircode"]} \n'
                            f'Status code: {response.status_code} \n'
                            f'Body: {response.json()}'
                        )
                        errors.append(error_message)
                    else:
                        error_message = (
                            f'Error requesting for property: {row["Eircode"]} \n'
                            f'Exception: {response}'
                        )
                        errors.append(error_message)

            if summary_rows:
                summary_df = pd.DataFrame(summary_rows)
                st.dataframe(summary_df)
            else:
                st.write('No data to exhibit.')

            if errors:
                with st.expander('Errors'):
                    for error in errors:
                        st.write(f'{error}\n')

    st.success('Done!')