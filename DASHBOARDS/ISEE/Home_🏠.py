import streamlit as st
import pandas as pd
import importlib
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
import DASHBOARDS.ISEE.CFG_DASHBOARD as CFG_DASHBOARD

import os
print(os.getcwd())

st.set_page_config(
    page_title='ISEE Dashboard - GLAM Project',
    page_icon='🏞️',
    layout='wide',
    initial_sidebar_state='collapsed')
st.sidebar.caption('This app was developed by the Hydrodynamic and Ecohydraulic Services of the National Hydrological Service ' \
                'at Environment and Climate Change Canada, based on results from the Integrated Social, Economic, and Environmental System (ISEE).')

# Import PI configuration
pis_code = CFG_DASHBOARD.pi_list # PI list
pi_dct = {}
pi_type = {}
for pi in pis_code:
    pi_module_name = f'CFG_{pi}'
    PI_CFG = importlib.import_module(f'GENERAL.CFG_PIS.{pi_module_name}')
    pi_dct[pi] = PI_CFG.name
    pi_type[pi] = PI_CFG.type.replace('_',' ')
del PI_CFG

st.header('👋 Welcome to the ISEE Dashboard for Phase 2 of the Plan 2014 Expedited Review', divider="grey")
st.write('Choose what you want to see on the left panel. 👀')

_, col = st.columns([0.01,0.99])
with col:
    st.write('-> Timeseries 📈 plots annually aggregated values for multiple plans.')
    st.write("-> Difference ⚖️ compares annually aggregated values for multiple plans.")
    st.write('-> Dual maps 🗺️ shows two maps aggregated per tile to compare two plans.')
    st.write("-> Difference map 🌎 is a map aggregated per tile showing the difference between two plans.")
    st.write('-> Full resolution map 🔍 zooms on one tile of a difference map.')

plans_ts_dct={'hist':['OBS','PreProjectHistorical', 'Bv7_2014', 'GERBL2_2014_ComboA', 'GERBL2_2014_ComboB', 'Bv7_2014_ComboC', 'GERBL2_2014_ComboD'],
              'sto':['-','PreProject_STO_330', 'GERBL2_2014_STO_330', 'GERBL2_2014_ComboA_STO_330', 'GERBL2_2014_ComboB_STO_330', 'GERBL2_2014_ComboC_STO_330', 'GERBL2_2014_ComboD_STO_330'],
              'cc':['-','PreProject_RCP45', 'GERBL2_2014BOC_RCP45', 'GERBL2_2014_ComboA_RCP45', 'GERBL2_2014_ComboB_RCP45', 'GERBL2_2014_ComboC_RCP45', 'GERBL2_2014_ComboD_RCP45']}


st.subheader('Plans and water supplies')
st.write('Note that the plans available per PI may vary.')
df_plans = pd.DataFrame(data={'Name': ['Observations','PreProject','Plan 2014', 'Combo A', 'Combo B', 'Combo C', 'Combo D'],
                              'Historical':plans_ts_dct['hist'],
                              'Stochastic':plans_ts_dct['sto'],
                              'Climate change':plans_ts_dct['cc']})
st.write(df_plans.style.hide(axis='index').to_html(), unsafe_allow_html=True)

st.subheader('Sections')
st.write('Note that the sections available per PI may vary. See below.')

img_path = os.path.join(os.path.dirname(__file__), '..', '..', 'docs', 'domain', 'Domaine_GLAM.png')

st.image(img_path, caption='Division du domaine en section',
         width=800)

st.subheader('Available PIs')
st.write('**Shoreline and Coastal impacts**')

df = pd.DataFrame(data={'PI':
                        ['Agriculture Yield Loss', 'Buildings at risk', 'Flooded roads', 'Marina functionality impacts', 'Shoreline protection structure',
                                  'Water intakes', 'Waste water'],
                        'Type':
                        ['2D','2D','2D','2D','2D','2D','2D'],
                        'SLR_DS':['✅','✅','✅','✅','❌','✅','✅'],
                        'SLR_US':['✅','❌','✅','✅','❌','✅','❌'],
                        'USL_DS':['❌','✅','✅','✅','❌','✅','❌'],
                        'ULS_US':['❌','✅','✅','✅','❌','✅','✅'],
                           'LKO':['❌','✅','✅','✅','✅','✅','✅']})
st.write(df.style.hide(axis='index').to_html(), unsafe_allow_html=True)


st.markdown("**Ecosystems**")
df = pd.DataFrame(data={'PI':['Black tern', 'Exposed riverbed during winter', 'Least Bittern', 'Marsh birds', 'Muskrat winter lodge viability and occupancy',
                                  'Northern pike habitat', 'Turtle survival during winter', 'Water flow', 'Wetland class area', 'Wetland class area (LOSLR)', 'Wild Rice'],
                        'Type':['2D','1D and 2D','2D','2D','1D','2D', '1D', '2D', '2D', '2D', '1D'],
                        'SLR_DS':['✅','✅','✅','❌','✅','✅','✅','✅','❌','✅','✅'],
                        'SLR_US':['✅','✅','✅','❌','✅','✅','✅','✅','❌','✅','✅'],
                        'USL_DS':['❌','✅','❌','❌','✅','✅','✅','❌','✅','❌','✅'],
                        'ULS_US':['❌','✅','❌','❌','✅','✅','✅','❌','✅','❌','✅'],
                           'LKO':['❌','✅','❌','✅','✅','✅','✅','❌','✅','❌','✅']})
st.write(df.style.hide(axis='index').to_html(), unsafe_allow_html=True)