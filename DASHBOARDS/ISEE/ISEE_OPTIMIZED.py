import streamlit as st
from streamlit_theme import st_theme

st.set_page_config(
    page_title='ISEE Dashboard',
    page_icon='🏞️',
    layout='wide',
    initial_sidebar_state='collapsed')

st.header('Welcome to the ISEE Dashboard for the GLAM project 👋', divider="grey")
st.write('Choose what you want to see on the left. 👀')
st.write('PI and plan description')
st.image('../../docs/domain/Domaine_GLAM.png', caption='Division du domaine en section',
         width=800)
# Pour docker
# st.image('docs/domain/Domaine_GLAM.png', caption='Division du domaine en section',
#          width=800)