import pandas as pd
import os
import glob
import importlib
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
import POST_PROCESSING.ISEE.CFG_POST_PROCESS_ISEE as cfg
import DASHBOARDS.ISEE.CFG_DASHBOARD as CFG_DASHBOARD

# TODO: ajouter comboA et comboA dans les différents plans ici et pour les séries de supplies

dict_supply_plan = {'Historical': ['PreProjectHistorical', 'Bv7_2014', 'GERBL2_2014_ComboA', 'GERBL2_2014_ComboB', 'Bv7_2014_ComboC', 'GERBL2_2014_ComboD', 'OBS'],
                    'RCP45': ['PreProject_RCP45', 'GERBL2_2014BOC_RCP45', 'GERBL2_2014_ComboA_RCP45', 'GERBL2_2014_ComboB_RCP45', 'GERBL2_2014_ComboC_RCP45', 'GERBL2_2014_ComboD_RCP45'],
                    'STO330':['PreProject_STO_330', 'GERBL2_2014_STO_330', 'GERBL2_2014_ComboA_STO_330', 'GERBL2_2014_ComboB_STO_330', 'GERBL2_2014_ComboC_STO_330', 'GERBL2_2014_ComboD_STO_330']}
plan_rename_dict = {'OBS': 'OBS', 'Bv7_2014': 'GERBL2_2014', 'PreProjectHistorical': 'PreProject',
                    'GERBL2_2014_ComboA': 'GERBL2_2014_ComboA', 'GERBL2_2014_ComboB': 'GERBL2_2014_ComboB',
                    'Bv7_2014_ComboC': 'GERBL2_2014_ComboC', 'GERBL2_2014_ComboD': 'GERBL2_2014_ComboD',
                    'GERBL2_2014BOC_RCP45': 'GERBL2_2014', 'PreProject_RCP45': 'PreProject',
                    'GERBL2_2014_ComboA_RCP45': 'GERBL2_2014_ComboA', 'GERBL2_2014_ComboB_RCP45':'GERBL2_2014_ComboB',
                    'GERBL2_2014_ComboC_RCP45': 'GERBL2_2014_ComboC', 'GERBL2_2014_ComboD_RCP45': 'GERBL2_2014_ComboD',
                    'GERBL2_2014_STO_330': 'GERBL2_2014', 'PreProject_STO_330': 'PreProject',
                    'GERBL2_2014_ComboA_STO_330': 'GERBL2_2014_ComboA', 'GERBL2_2014_ComboB_STO_330': 'GERBL2_2014_ComboB',
                    'GERBL2_2014_ComboC_STO_330': 'GERBL2_2014_ComboC', 'GERBL2_2014_ComboD_STO_330': 'GERBL2_2014_ComboD',}

#TODO: Prendre le nom de variables du fichier config du PI correspondant
dict_variables = {'AYL_2D': {'VAR1_sum': 'Average Yield Loss for all crops ($)'},
                  'BIRDS_2D': {'VAR1_sum': 'Abundance (n individuals)'},
                  'CHNI_2D': {'VAR1_sum': 'N breeding pairs'},
                  'CWRM_2D': {'VAR4_sum': 'Wet Meadow area (ha)','VAR7_sum': 'Total Wetland area (ha)'},
                  'ERIW_MIN_1D': {'VAR1_mean': 'Exposed Riverbed Index'},
                  'IERM_2D': {'VAR3_sum': 'Wet Meadow area (ha)','VAR6_sum': 'Total Wetland area (ha)'},
                  'IXEX_RPI_2D': {'VAR1_sum': 'Weighted usable area (ha)'},
                  'MFI_2D': {'VAR1_sum': 'Impacts during the navigation season','VAR2_sum': 'Number of QMs with impacts'},
                  'NFB_2D': {'VAR7_sum': 'Residential (boolean)','VAR8_sum': 'Residential (Nb of QMs)','VAR9_sum': 'Total buildings (boolean)','VAR10_sum': 'Total buildings (Nb of QMs)'},
                  'ONZI_OCCUPANCY_1D': {'VAR1_mean': 'Probability of muskrat lodge viability','VAR6_mean': 'Percentage of the occupancy area in a cattail wetland'},
                  'PIKE_2D': {'VAR1_sum': 'Habitat available for spawning and embryo-larval development (ha)','VAR2_sum': 'Habitat available for spawning (ha)'},
                  'ROADS_2D': {'VAR1_sum': 'Primary roads (Nb of QMs)','VAR5_sum': 'All roads (Nb of QMs)','VAR6_sum': 'Primary roads (Length in m)','VAR10_sum': 'All roads (Length in m)'},
                  'SAUV_2D': {'VAR1_sum': 'Migration habitat (ha)'},
                  'TURTLE_1D': {'VAR1_mean' : 'Blanding turtle winter survival probability','VAR2_mean' : 'Snapping turtle winter survival probability','VAR3_mean' : 'Painted turtle winter survival probability'},
                  'WASTE_WATER_2D': {'VAR1_sum': 'number of wastewater facilities exceeding the average discharge threshold','VAR2_mean': 'weighted (duration, discharge) number of wastewater facilities impacted'},
                  'WATER_INTAKES_2D': {'VAR1_sum': 'number of water intake facilities exceeding the nominal capacity threshold','VAR2_mean': 'weighted (duration, capacity) number of intake facilities impacted'},
                  'ZIPA_1D': {'VAR1_mean': 'Wildrice survival probability'}}

# Import PI configuration
pis_code = CFG_DASHBOARD.pi_list
pis_code.remove('WL_ISEE_1D'); pis_code.remove('WL_GLRRM_1D')
pis_code.remove('ERIW_MIN_2D'); pis_code.remove('SHORE_PROT_STRUC_1D')
dict_multiplier = {}
for pi in pis_code:
    pi_module_name = f'CFG_{pi}'
    PI_CFG = importlib.import_module(f'GENERAL.CFG_PIS.{pi_module_name}')
    dict_multiplier[pi] = PI_CFG.multiplier
del PI_CFG

list_PIs = dict_variables.keys()
output_folder = os.path.join(cfg.POST_PROCESS_RES, 'PI_CSV_RESULTS_20260106')
os.makedirs(output_folder, exist_ok=True)

for pi in list_PIs:
    print(pi)
    dict_var_pi = dict_variables[pi]
    multiplier = dict_multiplier[pi]
    for col in dict_var_pi.keys():
        list_results = []
        value_col = dict_var_pi[col]
        print('->', value_col)
        for supply, list_plan in dict_supply_plan.items():

            for plan in list_plan:

                plan_shortname = plan_rename_dict[plan]

                path_plan_pi = os.path.join(cfg.POST_PROCESS_RES, *[pi, 'YEAR', 'SECTION', plan])

                if os.path.isdir(path_plan_pi):
                    print("      ", supply, plan)
                    list_sections = os.listdir(path_plan_pi)

                    for sect in list_sections:

                        file_res = glob.glob(os.path.join(path_plan_pi, *[sect, '*.feather'])) + glob.glob(os.path.join(path_plan_pi, *[sect, '*.parquet']))

                        if len(file_res) == 1:
                            file_res = file_res[0]

                            if file_res.endswith('.feather'):
                                df_res = pd.read_feather(file_res)
                            else:
                                df_res = pd.read_parquet(file_res)

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