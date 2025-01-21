import streamlit as st

def load_feather_icons():
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] {
            background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-dollar-sign"><line x1="12" y1="1" x2="12" y2="23"></line><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>');
            background-size: 20px;
            background-repeat: no-repeat;
            background-position: 10px 10px;
            padding-top: 40px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

def load_custom_css():
    with open('.streamlit/style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
