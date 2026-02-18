import pandas as pd
import os


pi_name='WL_ISEE_2D'

dst_folder=fr'T:\GLAM\Output_ISEE\results_off\DASHBOARD_RESULTS_NEW\WL_ISEE_2D'

def find_pt_id(df):
    df2 = df.drop(columns='PT_ID')
    overall_mean = df2.to_numpy().mean()
    abs_diff = (df2 - overall_mean).abs()
    min_diff = abs_diff.min().min()
    closest_locs = list(zip(*((abs_diff == min_diff).to_numpy().nonzero())))
    closest_positions = [(df2.index[r], df2.columns[c]) for r, c in closest_locs]
    closest_positions = closest_positions[0]
    row = df2.loc[closest_positions]
    id = df['PT_ID'].loc[closest_positions[0]]

    return id


folder=fr'T:\GLAM\Input_ISEE\prod\HYD\WL_QM'
plan_name_dct = {

    "PreProject_default_RCA4_EARTH_rcp45_2011_2070": "PreProject_RCP45"
}

#
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

# sections=['LKO', 'USL_US', 'USL_DS', 'SLR_US', 'SLR_DS']

sections=['USL_DS']

ref_df=pd.read_csv(fr"T:\GLAM\Input_ISEE\prod\TS\HYD\ts_hyd_control.csv", sep=';')

for p in plan_name_dct.keys():
    print(p)
    plan_name=ref_df.loc[ref_df['TS_VERSION']==p]

    plan_id=ref_df.loc[ref_df['TS_VERSION']==p, 'TS_ID'].iloc[0]

    pp = plan_name['TS_INPUT_HYD_FLDR'].iloc[0]

    for s in sections:
        path=os.path.join(folder, pp, s)
        liste=os.listdir(path)
        ##print(liste)
        for t in liste:
            path2 = os.path.join(path, t)
            ##print(path2)

            tile=t.replace('TILE_', '')

            liste2=os.listdir(path2)
            count = 0
            for file in liste2:

                if not file[-8:]=='.feather':
                    continue

                count += 1
                path3=os.path.join(path2, file)

                ##print(path3)

                ##print(path3.split('_')[-2])

                year = path3.split('_')[-2]

                df=pd.read_feather(path3)

                #print(list(df))

                min_cols=[col for col in df.columns if 'MIN' in col]

                df['VAR1']=df[min_cols].min(axis=1)

                #print(df['VAR1'])

                mean_cols=[col for col in df.columns if 'AVG' in col]

                df['VAR2']=df[mean_cols].mean(axis=1).round(3)

                #print(df['VAR2'])

                max_cols=[col for col in df.columns if 'MAX' in col]

                df['VAR3']=df[mean_cols].max(axis=1)

                #print(df['VAR3'])

                df=df[['PT_ID', 'VAR1', 'VAR2', 'VAR3']]

                #print(df.head())

                dst_folder_precise=os.path.join(dst_folder, plan_id, s, year)

                if not os.path.exists(dst_folder_precise):
                    os.makedirs(dst_folder_precise)

                dst_path=os.path.join(dst_folder_precise, f'{pi_name}_{plan_id}_{s}_{tile}_{year}.feather')

                df.to_feather(dst_path)

quit()


                # #print(list(df))
                #
                # df2=df.drop(columns='PT_ID')
                #
                # overall_mean = df2.to_numpy().mean()
                # #print("Overall mean:", overall_mean)
                #
                # abs_diff = (df2 - overall_mean).abs()
                #
                # # Find the minimal difference
                # min_diff = abs_diff.min().min()
                #
                # # Find all locations (row, column) where the value is closest to the mean
                # closest_locs = list(zip(*((abs_diff == min_diff).to_numpy().nonzero())))
                #
                # #print(len(closest_locs))
                #
                # # Map numeric row/col indices to actual labels
                # closest_positions = [(df2.index[r], df2.columns[c]) for r, c in closest_locs]
                #
                # # Get the actual value(s)
                # closest_values = [df2.loc[r, c] for r, c in closest_positions]
                #
                # closest_positions = closest_positions[0]
                # closest_values = closest_values[0]
                # #print("Closest positions:", closest_positions)
                #
                # row = df2.loc[closest_positions]
                # # val=row[closest_positions[0][1]]
                # #print(row)
                #
                # id = df['PT_ID'].loc[closest_positions[0]]
                #
                # #print(id)
                #
                # quit()