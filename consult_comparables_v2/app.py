import streamlit as st


home_page = st.Page(
    page = "views/home.py",
    title = "Home",
    default = True
)
valuation_page = st.Page(
    page = "views/valuation.py",
    title = "Valuation"
)
upload_csv_page = st.Page(
    page = "views/csv_valuation.py",
    title = "Import CSV"
)
pg = st.navigation([home_page, valuation_page, upload_csv_page])

pg.run()