import os

import pandas as pd
import requests
import streamlit as st


def get_instant_valuation(payload):
    try:
        url = os.getenv('COMPARABLE_API_URL', 'http://127.0.0.1:8000/comparables/instant-valuation/')
        response = requests.post(
            url=url,
            json=payload
        )
        return response
    except BaseException as e:
        return e

def match_eircode_return_property_info(properties, prices):
    properties = properties.dropna(subset=['Eircode'])
    prices = prices.dropna(subset=['Eircode', 'Price'])
    merged = pd.merge(properties, prices[['Eircode', 'Price']], on='Eircode', how='inner')
    matched_data = []
    for _, row in merged.iterrows():
        item = row.to_dict()
        matched_data.append(item)

    return matched_data

def read_csv(file):
    data = pd.read_csv(file)
    return data
