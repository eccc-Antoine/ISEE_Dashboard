import pandas as pd
import os
import glob

import CFG_POST_PROCESS_ISEE as cfg



dict_supply_plan = {'Historical': ['OBS', 'Bv7_2014', 'PreProjectHistorical', 'Bv7_2014_ComboC'],
                    'RCP45': ['GERBL2_2014BOC_RCP45', 'PreProject_RCP45', 'GERBL2_2014_ComboC_RCP45'],
                    'STO330':['GERBL2_2014_STO_330', 'PreProject_STO_330', 'GERBL2_2014_ComboC_STO_330']}

plan_rename_dict = {'OBS': 'OBS', 'Bv7_2014': 'GERBL2_2014', 'PreProjectHistorical': 'PreProject', 'Bv7_2014_ComboC': 'GERBL2_2014_ComboC',
                    'GERBL2_2014BOC_RCP45': 'GERBL2_2014', 'PreProject_RCP45': 'PreProject', 'GERBL2_2014_ComboC_RCP45': 'GERBL2_2014_ComboC',
                    'GERBL2_2014_STO_330': 'GERBL2_2014', 'PreProject_STO_330': 'PreProject', 'GERBL2_2014_ComboC_STO_330': 'GERBL2_2014_ComboC'}



dict_variables = {'ERIW_MIN_1D': {'VAR1_mean': 'Exposed Riverbed Index'},

                  'CWRM_2D': {
                      'VAR4_sum': 'Wet Meadow area (ha)',
                      'VAR7_sum': 'Total Wetland area (ha)'},

                  'BIRDS_2D': {'VAR1_sum': 'Abundance (n individuals)'},

                  'IERM_2D': {
                      'VAR3_sum': 'Wet Meadow area (ha)',
                      'VAR6_sum': 'Total Wetland area (ha)'},

                  'SAUV_2D': {'VAR1_sum': 'Migration habitat (ha)'},

                  'CHNI_2D': {'VAR1_sum': 'N breeding pairs'},

                  'IXEX_RPI_2D': {'VAR1_sum': 'Weighted usable area (ha)'},

                  'PIKE_2D': {'VAR1_sum': 'Habitat available for spawning and embryo-larval development (ha)',
                              'VAR2_sum': 'Habitat available for spawning (ha)'},

                  'ONZI_1D': {'VAR1_mean' : 'Probability of lodge viability'},

                  'TURTLE_1D': {'VAR1_mean' : 'Blanding turtle winter survival probability',
                              'VAR2_mean' : 'Snapping turtle winter survival probability',
                              'VAR3_mean' : 'Painted turtle winter survival probability'},

                  'ZIPA_1D': {'VAR1_mean': 'Wildrice survival probability'},

                  'AYL_2D': {'VAR1_sum': 'Average Yield Loss for all crops ($)'},

                  'ROADS_2D': {'VAR1_sum': 'Primary roads (Nb of QMs)',
                               'VAR2_sum': 'Secondary roads (Nb of QMs)',
                               'VAR3_sum': 'Tertiary roads (Nb of QMs)',
                               'VAR5_sum': 'All roads (Nb of QMs)',
                               'VAR6_sum': 'Primary roads (Length in m)',
                               'VAR7_sum': 'Secondary roads (Length in m)',
                               'VAR8_sum': 'Tertiary roads (Length in m)',
                               'VAR10_sum': 'All roads (Length in m)'},

                  'MFI_2D': {'VAR1_sum': 'Impacts during the navigation season',
                             'VAR2_sum': 'Number of QMs with impacts'},

                  'NFB_2D': {'VAR1_sum': 'Accessory buildings (boolean)',
                             'VAR2_sum': 'Accessory building (Nb of QMs)',
                             'VAR3_sum': 'Strategic assets buildings (boolean)',
                             'VAR4_sum': 'Strategic assets buildings (Nb of QMs)',
                             'VAR5_sum': 'Non-residential (boolean)',
                             'VAR6_sum': 'Non-residential (Nb of QMs)',
                             'VAR7_sum': 'Residential (boolean)',
                             'VAR8_sum': 'Residential (Nb of QMs)',
                             'VAR9_sum': 'Total buildings (boolean)',
                             'VAR10_sum': 'Total buildings (Nb of QMs)'},
                  'WASTE_WATER_2D': {'VAR1_sum': 'Occurrence of impact'},
                  'WATER_INTAKES_2D': {'VAR1_sum': 'Occurrence of impact'}
                  }

dict_multiplier = {'ERIW_MIN_1D':{'VAR1_mean':1},

                   'CWRM_2D': {'VAR2_sum': 0.01,
                               'VAR3_sum': 0.01,
                               'VAR4_sum': 0.01,
                               'VAR5_sum': 0.01,
                               'VAR7_sum': 0.01},

                   'BIRDS_2D': {'VAR1_sum': 1},

                   'IERM_2D': {
                       'VAR3_sum': 0.01,
                       'VAR6_sum': 0.01},

                   'SAUV_2D': {'VAR1_sum': 0.01},

                   'CHNI_2D': {'VAR1_sum': 1},

                   'IXEX_RPI_2D': {'VAR1_sum': 0.01},

                   'PIKE_2D': {'VAR1_sum': 1,
                               'VAR2_sum': 1},

                   'ONZI_1D': {'VAR1_mean': 1},

                   'TURTLE_1D': {'VAR1_mean': 1,
                                 'VAR2_mean': 1,
                                 'VAR3_mean': 1},

                   'ZIPA_1D': {'VAR1_mean': 1},

                   'AYL_2D': {'VAR1_sum': 1},

                   'ROADS_2D': {f'VAR{i}_sum':1 for i in range(1, 11)},

                   'MFI_2D': {'VAR1_sum': 1,
                                'VAR2_sum': 1},

                   'NFB_2D': {f'VAR{i}_sum':1 for i in range(1, 11)},

                   'WASTE_WATER_2D': {'VAR1_sum': 1},

                   'WATER_INTAKES_2D': {'VAR1_sum': 1},

                   }

#list_PIs = ['ERIW_MIN_1D', 'CWRM_2D', 'BIRDS_2D', 'IERM_2D', 'SAUV_2D', 'CHNI_2D', 'IXEX_RPI_2D', 'ONZI_1D', 'TURTLE_1D', 'ZIPA_1D', 'ROADS_2D', 'AYL_2D']
list_PIs = dict_variables.keys()
#list_PIs = ['PIKE_2D']
output_folder = os.path.join(cfg.POST_PROCESS_RES, 'PI_CSV_RESULTS')
os.makedirs(output_folder, exist_ok=True)


for pi in list_PIs:


    dict_var_pi = dict_variables[pi]
    for col in dict_var_pi.keys():
        list_results = []
        value_col = dict_var_pi[col]
        multiplier = dict_multiplier[pi][col]
        print(pi, value_col)
        for supply, list_plan in dict_supply_plan.items():

            for plan in list_plan:

                plan_shortname = plan_rename_dict[plan]

                path_plan_pi = os.path.join(cfg.POST_PROCESS_RES, *[pi, 'YEAR', 'SECTION', plan])

                if os.path.isdir(path_plan_pi):
                    print("             ", supply, plan)
                    list_sections = os.listdir(path_plan_pi)

                    for sect in list_sections:

                        file_res = glob.glob(os.path.join(path_plan_pi, *[sect, '*.feather']))

                        if len(file_res) == 1:
                            file_res = file_res[0]

                            df_res = pd.read_feather(file_res)

                            df_res = df_res.rename(dict_var_pi, axis=1)

                            df_res[value_col] = df_res[value_col] * multiplier
                            df_res['PI_NAME'] = pi
                            df_res['SUPPLY_SCEN'] = supply
                            df_res['ISEE_TS_ID'] = plan
                            df_res['PLAN_NAME'] = plan_shortname
                            df_res['SECT_NAME'] = sect
                            df_res = df_res[['PI_NAME', 'SUPPLY_SCEN', 'ISEE_TS_ID', 'PLAN_NAME', 'SECT_NAME', 'YEAR', value_col]]

                            list_results.append(df_res)
                else:
                    print(f"PI: {pi} for PLAN: {plan} missing from pre-processed results")

            df_res_agg = pd.concat(list_results)
            output_file = os.path.join(output_folder, f'{pi}_{value_col}.csv')

            df_res_agg.to_csv(output_file, sep=';', index=False)