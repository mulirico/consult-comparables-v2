import streamlit as st


col1, col2 = st.columns(2)
with col1:
    st.page_link('views/valuation.py', label='💰 **Valuation**', use_container_width=True)
with col2:
    st.page_link('views/csv_valuation.py', label='📊 **Statistics**', use_container_width=True)