import os
import pandas as pd


def group_year_station(df, station_cols, columns ):
    df = df[columns]
    df_out = (
        df
        .groupby("QM_YEAR")[station_cols]
        .agg(['min', 'mean', 'max'])
        .reset_index()
        .rename(columns={"QM_YEAR": "YEAR"})
    )
    df_out.columns = [
        f"{col}_{stat}" if stat != '' else col
        for col, stat in df_out.columns
    ]
    return df_out


# plan_name_dct = {
#     "obs_20241106": "OBS",
#
#     "GERBL2_2014BOC_def_hist_phase2_1961_2020": "Bv7_2014",
#     "GERBL2_2014BOC_comboA_hist_phase2_1961_2020": "GERBL2_2014_ComboA",
#     "GERBL2_2014BOC_comboB_hist_phase2_1961_2020": "GERBL2_2014_ComboB",
#     "GERBL2_P2014BOC_ComboC_hist_phase2_1961_2020": "Bv7_2014_ComboC",
#     "GERBL2_2014BOC_comboD_hist_phase2_1961_2020": "GERBL2_2014_ComboD",
#     "PreProject_historical_1961_2020": "PreProjectHistorical",
#
#     "GERBL2_2014BOC_def_cc_rcp45_RCA4_EARTH_2011_2070": "GERBL2_2014BOC_RCP45",
#     "GERBL2_2014BOC_comboA_RCA4_EARTH_rcp45_2011_2070": "GERBL2_2014_ComboA_RCP45",
#     "GERBL2_2014BOC_comboB_RCA4_EARTH_rcp45_2011_2070": "GERBL2_2014_ComboB_RCP45",
#     "GERBL2_2014BOC_ComboC_RCA4_EARTH_rcp45_2011_2070": "GERBL2_2014_ComboC_RCP45",
#     "GERBL2_2014BOC_ComboD_RCA4_EARTH_rcp45_2011_2070": "GERBL2_2014_ComboD_RCP45",
#     "PreProject_default_RCA4_EARTH_rcp45_2011_2070": "PreProject_RCP45",
#
#     "GERBL2_2014BOC_def_stochastic_330_2011_2070": "GERBL2_2014_STO_330",
#     "GERBL2_2014BOC_comboA_stochastic_330_2011_2070": "GERBL2_2014_ComboA_STO_330",
#     "GERBL2_2014BOC_comboB_stochastic_330_2011_2070": "GERBL2_2014_ComboB_STO_330",
#     "GERBL2_2014BOC_ComboC_stochastic_330_2011_2070": "GERBL2_2014_ComboC_STO_330",
#     "GERBL2_2014BOC_ComboD_stochastic_330_2011_2070": "GERBL2_2014_ComboD_STO_330",
#     "PreProject_default_stochastic_330_2011_2070": "PreProject_STO_330"
# }

# plan_name_dct = {
#     "GERBL2_2014BOC_def_cc_rcp45_RCA4_EARTH_2011_2070": "GERBL2_2014BOC_RCP45",
#     "GERBL2_2014BOC_comboA_RCA4_EARTH_rcp45_2011_2070": "GERBL2_2014_ComboA_RCP45",
#     "GERBL2_2014BOC_comboB_RCA4_EARTH_rcp45_2011_2070": "GERBL2_2014_ComboB_RCP45",
#     "GERBL2_2014BOC_ComboC_RCA4_EARTH_rcp45_2011_2070": "GERBL2_2014_ComboC_RCP45",
#     "GERBL2_2014BOC_ComboD_RCA4_EARTH_rcp45_2011_2070": "GERBL2_2014_ComboD_RCP45",
#     "PreProject_default_RCA4_EARTH_rcp45_2011_2070": "PreProject_RCP45"
# }

plan_name_dct = {"obs_20241106":"OBS"}

# plan_name_dct = {
#     "PreProject_historical_1961_2020": "PreProjectHistorical"}

res_path=fr'T:\GLAM\Output_ISEE\results_off\DASHBOARD_RESULTS_NEW'

dct_station_section={'LKO':'ONT_MLV_M', 'USL_US':'OGDE_MLV_M', 'USL_DS':'LSTD_MLV_M', 'SLR_US':'PTCL_MLV_M', 'SLR_DS':'SORL_MLV_M'}

station_cols=list(dct_station_section.values())
section=list(dct_station_section.keys())

columns= ['QM_YEAR']+station_cols

name='WL_1D'

base_path = r"T:\GLAM\Input_ISEE\prod\TS\HYD"

ref_file=os.path.join(base_path, 'ts_hyd_control.csv')
df_ref=pd.read_csv(ref_file, sep=';')
plan_ref_column='TS_VERSION'
file_ref_column='TS_DATAFILE_1D'
folder_ref_column='TS_FLDR'
Dash_plan_ID_column='TS_ID'


for plan in plan_name_dct.keys():
    print(plan)

    folder=df_ref.loc[df_ref[plan_ref_column]==plan, folder_ref_column].iloc[0]
    file=df_ref.loc[df_ref[plan_ref_column]==plan, file_ref_column].iloc[0]
    print(file)

    if 'ISEE_WL' in file:
        ISEE_file=file
        GLRMM_file=file.replace('_ISEE_WL', '')
    else:
        GLRMM_file = file
        ISEE_file = file.replace('.csv', 'ISEE_WL.csv')

    files=[ISEE_file, GLRMM_file]

    if 'obs' in plan:
        print('OBSERVATION series, only ISEE WL but it has the GLRRM file name :) !!')
        files=[GLRMM_file]

    for f in files:

        if f==ISEE_file:
            name_PI='WL_ISEE_1D'
        else:
            name_PI = 'WL_GLRRM_1D'

        path=os.path.join(base_path, folder, plan, f)

        dash_plan_ID=df_ref.loc[df_ref[plan_ref_column]==plan, Dash_plan_ID_column].iloc[0]

        print(path)

        df_plan=pd.read_csv(path, sep=';')

        print(list(df_plan))

        df_plan=df_plan.loc[df_plan['QM_YEAR']!=1961]

        print(df_plan.head())

        print(station_cols)
        print(columns)

        print(dct_station_section['USL_DS'])
        if 'PreProject' in plan:
            #print(f'!! WEIRD, {dct_station_section['USL_DS']} is there even if it is preproject !?')
            station_cols_new = station_cols.copy()
            station_cols_new.remove(dct_station_section['USL_DS'])
            columns_new=columns.copy()
            columns_new.remove(dct_station_section['USL_DS'])
            section_new=section.copy()
            section_new.remove('USL_DS')

        else:
            station_cols_new = station_cols
            columns_new = columns
            section_new=section

        print(station_cols_new)
        df_plan_group = group_year_station(df_plan, station_cols_new, columns_new)

        print(df_plan_group.head())

        print(list(df_plan_group))

        print(section_new)

        for s in section_new:
            print(s)

            stat_sct=dct_station_section[s]

            print(stat_sct)

            cols_stat=[c for c in df_plan_group.columns if stat_sct in c]

            cols=['YEAR']+cols_stat

            print(cols)

            df_plan_group_sect=df_plan_group[cols]

            dct={f'{stat_sct}_min':'VAR1', f'{stat_sct}_mean':'VAR2', f'{stat_sct}_max':'VAR3'}

            df_plan_group_sect = df_plan_group_sect.rename(columns=dct)

            print(list(df_plan_group_sect))

            file_folder=os.path.join(res_path, name_PI,  dash_plan_ID,  s)

            path=os.path.join(file_folder, f'{name_PI}_{dash_plan_ID}_{s}.feather')

            if not os.path.exists(file_folder):
                os.makedirs(file_folder)

            df_plan_group_sect.to_feather(path)

quit()
