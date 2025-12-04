import pandas as pd
import importlib
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
import DASHBOARDS.ISEE.CFG_DASHBOARD as CFG_DASHBOARD
import DASHBOARDS.UTILS.Home_utils as UTILS
import os
from io import BytesIO
import zipfile

# Will reset everytime you go back to Home page
# I want to create it before importing the streamlit package
logger, log_filename, log_path = UTILS.start_session_logger()
logger.info('The log file was created')
UTILS.upload_log_to_blob(log_path,'session-logs',log_filename)

try:
    import streamlit as st
    st.session_state.logger = logger
    st.session_state.logger.info('Streamlit was imported')
    st.set_page_config(
        page_title='ISEE Dashboard - GLAM Project',
        page_icon='🏞️',
        layout='wide',
        initial_sidebar_state='collapsed')
    st.sidebar.caption('This app was developed by the Hydrodynamic and Ecohydraulic Services of the National Hydrological Service ' \
                    'at Environment and Climate Change Canada, based on results from the Integrated Social, Economic, and Environmental System (ISEE).')
    st.session_state.logger.info('Setup page config')

    st.header('👋 Welcome to the ISEE Dashboard for Phase 2 of the Plan 2014 Expedited Review', divider="grey")
    st.write('Choose what you want to see on the left panel. 👀')

    _, col = st.columns([0.01,0.99])
    with col:
        st.write('-> Timeseries 📈 plots annually aggregated values for multiple plans.')
        st.write("-> Difference ⚖️ compares annually aggregated values for multiple plans.")
        st.write('-> Dual maps 🗺️ shows two maps aggregated per tile to compare two plans.')
        st.write("-> Difference map 🌎 is a map aggregated per tile showing the difference between two plans.")
        st.write('-> Full resolution map 🔍 zooms on one tile of a difference map.')

    st.session_state.logger.info('Instructions are written')

    st.subheader('Plans and water supplies')
    st.write('Note that the plans available per PI may vary.')
    st.write('**Historical**')
    df_plans = pd.DataFrame(data={'Full name': ['PreProject_historical_1961_2020','GERBL2_2014BOC_def_hist_phase2_1961_2020',
                                                'GERBL2_P2014BOC_ComboA_hist_phase2_1961_2020','GERBL2_P2014BOC_ComboB_hist_phase2_1961_2020',
                                                'GERBL2_P2014BOC_ComboCv2_hist_phase2_1961_2020            ','GERBL2_P2014BOC_ComboD_hist_phase2_1961_2020',
                                                'obs_20241106'],
                                'Name used in dashboard': ['PreProject','2014','ComboA','ComboB','ComboC','ComboD','OBS']})
    st.write(df_plans.style.set_properties(subset=['Full name'],**{'width': '450px'}).set_properties(subset=['Name used in dashboard'],**{'width': '200px'}).hide(axis='index').to_html(), unsafe_allow_html=True)

    st.write('**Climate change**')
    df_plans = pd.DataFrame(data={'Full name': ['PreProject_default_RCA4_EARTH_rcp45_2011_2070','GERBL2_2014BOC_def_cc_rcp45_RCA4_EARTH_2011_2070',
                                                'GERBL2_2014BOC_ComboA_RCA4_EARTH_rcp45_2011_2070','GERBL2_2014BOC_ComboB_RCA4_EARTH_rcp45_2011_2070',
                                                'GERBL2_2014BOC_ComboCv2_RCA4_EARTH_rcp45_2011_2070','GERBL2_2014BOC_ComboD_RCA4_EARTH_rcp45_2011_2070'],
                                'Name used in dashboard': ['PreProject_CC','2014_CC','ComboA_CC','ComboB_CC','ComboC_CC','ComboD_CC']})
    st.write(df_plans.style.set_properties(subset=['Full name'],**{'width': '450px'}).set_properties(subset=['Name used in dashboard'],**{'width': '200px'}).hide(axis='index').to_html(), unsafe_allow_html=True)

    st.write('**Stochastic**')
    df_plans = pd.DataFrame(data={'Full name': ['PreProject_default_stochastic_330_2011_2070','GERBL2_2014BOC_def_stochastic_330_2011_2070',
                                                'GERBL2_2014BOC_ComboA_stochastic_330_2011_2070','GERBL2_2014BOC_ComboB_stochastic_330_2011_2070',
                                                'GERBL2_2014BOC_ComboCv2_stochastic_330_2011_2070','GERBL2_2014BOC_ComboD_stochastic_330_2011_2070'],
                                'Name used in dashboard': ['PreProject_STO','2014_STO','ComboA_STO','ComboB_STO','ComboC_STO','ComboD_STO']})
    st.write(df_plans.style.set_properties(subset=['Full name'],**{'width': '450px'}).set_properties(subset=['Name used in dashboard'],**{'width': '200px'}).hide(axis='index').to_html(), unsafe_allow_html=True)

    st.session_state.logger.info('Plans are in tables')

    st.subheader('Sections')
    st.write('Note that the sections available per PI may vary. See below.')

    img_path = os.path.join(os.path.dirname(__file__), '..', '..', 'docs', 'domain', 'Domaine_GLAM.png')
    st.image(img_path, caption='Division du domaine en section',
            width=800)

    st.session_state.logger.info('Sections image is there')

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
    st.write(df.style.set_properties(subset=['PI'],**{'width': '330px'}).set_properties(subset=['Type'],**{'width': '100px'}).hide(axis='index').to_html(), unsafe_allow_html=True)


    st.markdown("**Ecosystems**")
    df = pd.DataFrame(data={'PI':['Black tern', 'Exposed riverbed during winter', 'Least Bittern', 'Marsh birds', 'Muskrat winter lodge viability and occupancy',
                                    'Northern pike habitat', 'Turtle survival during winter', 'Water flow', 'Wetland class area', 'Wetland class area (LOSLR)', 'Wild Rice'],
                            'Type':['2D','1D and 2D','2D','2D','1D','2D', '1D', '2D', '2D', '2D', '1D'],
                            'SLR_DS':['✅','✅','✅','❌','✅','✅','✅','✅','❌','✅','✅'],
                            'SLR_US':['✅','✅','✅','❌','✅','✅','✅','✅','❌','✅','✅'],
                            'USL_DS':['❌','✅','❌','❌','✅','✅','✅','❌','✅','❌','✅'],
                            'ULS_US':['❌','✅','❌','❌','✅','✅','✅','❌','✅','❌','✅'],
                            'LKO':['❌','✅','❌','✅','✅','✅','✅','❌','✅','❌','✅']})
    st.write(df.style.set_properties(subset=['PI'],**{'width': '330px'}).set_properties(subset=['Type'],**{'width': '100px'}).hide(axis='index').to_html(), unsafe_allow_html=True)

    st.session_state.logger.info('PIs are in tables')

    UTILS.upload_log_to_blob(log_path,'session-logs',log_filename)

    st.divider()
    st.subheader(':grey[For development purposes]')
    st.write(':grey[This dashboard is still in development to add new features and improvements every week. To help us detect bugs, we created logs to track any errors.]')
    st.write(":grey[This section is to download the logs of the last 10 sessions opened. You'll need the right password to download the files, this is for the people working on the app only.]")

    col_pwd, col_dwnld = st.columns(2,vertical_alignment='bottom')

    with col_pwd:
        log_access = st.text_input(':grey[Password]',type='password')
        if log_access == 'SessionLogs2025!':
            download_okay = True
            st.session_state.logger.info('Prepare logs to download')
        else:
            download_okay = False
    with col_dwnld:
        recent_logs = UTILS.get_logs_from_blob('session-logs')
        if not recent_logs:
            st.error("No log files found")
        else:
            # Create a zip file
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
                for blob in recent_logs:
                    data = UTILS.download_blob_to_bytes('session-logs',log_filename)
                    # Add each log file to the ZIP archive
                    zipf.writestr(blob.name, data)
            zip_buffer.seek(0)  # Go back to start of BytesIO buffer

            st.download_button(
                    label='Download logs',
                    data=zip_buffer,
                    file_name="last_10_logs.zip",
                    mime="application/zip",
                    disabled=not download_okay)
except Exception as e:
    if logger in st.session_state:
        logger = st.session_state.logger
    logger.error("A error occured.", exc_info=True)
    UTILS.upload_log_to_blob(log_path,'session-logs',log_filename)

print('-------------END-----------')
