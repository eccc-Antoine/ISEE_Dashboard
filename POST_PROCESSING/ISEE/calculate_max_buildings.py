import pandas as pd
import os
import numpy as np
import CFG_POST_PROCESS_ISEE as cfg




dict_pi_var = {

    'NFB_2D': ['Residential (boolean)',
               'Total buildings (boolean)']}

list_plan_lower_better = ['ROADS_2D', 'NFB_2D', 'WASTE_WATER_2D', 'WATER_INTAKES_2D', 'AYL_2D', 'MFI_2D']
list_plan_higher_better = [pi for pi in dict_pi_var.keys() if pi not in list_plan_lower_better]

#file_struct_protection = r"P:\GLAM\Dashboard\ISEE_Dash_portable\ISEE_POST_PROCESS_DATA_3\PI_CSV_RESULTS\SHOR_PROT_STRUC_RESULTS_ALL_SCENARIO.csv"
#df_struct_prot = pd.read_csv(file_struct_protection, sep=';', header=0)

folder_results = os.path.join(cfg.POST_PROCESS_RES, r'PI_CSV_RESULTS_20250212')

#list_supplies = ['Historical']

ref_plan = 'GERBL2_2014'
list_plans = ['PreProject', 'GERBL2_2014_ComboC', 'GERBL2_2014_ComboD']
list_pis = list(dict_pi_var.keys())
#list_pis = ['CHNI_2D']

list_sections = ['LKO', 'USL_US', 'USL_DS', 'SLR_US', 'SLR_DS']



list_results = []
for pi, list_var in dict_pi_var.items():
    if pi in list_pis:
        print(pi)
        for var in list_var:
        #for var, dict_sect in dict_var.items():

            file_res = f'{pi}_{var}.csv'

            path_results = os.path.join(folder_results, file_res)

            df_res = pd.read_csv(path_results, sep=';', header=0)

            df_res = df_res[df_res['PLAN_NAME'].isin([ref_plan]+list_plans)]

            # merge sections canada/us (sum) by year for each plan
            list_sections_merged = []
            for section in list_sections:

                df_sect = df_res[df_res['SECT_NAME'].str.startswith(section)]

                # Grouper par PLAN et YEAR, puis sommer la colonne Value
                result = df_sect.groupby(['PLAN_NAME', 'SUPPLY_SCEN', 'YEAR'])[var].sum().reset_index()
                result['SECT_NAME'] = section
                result = result[['PLAN_NAME', 'SUPPLY_SCEN', 'SECT_NAME', 'YEAR', var]].copy()
                list_sections_merged.append(result)
                print(result)
            df_sect_agg = pd.concat(list_sections_merged)


            for supply, df_res_supply in df_sect_agg.groupby('SUPPLY_SCEN'):

                plans_to_compare = [plan for plan in df_res_supply['PLAN_NAME'].unique() if plan != ref_plan]

                for sect, df_res_sect in df_res_supply.groupby('SECT_NAME'):

                    max_ref = 0

                    df_res_ref = df_res_sect[df_res_sect['PLAN_NAME'] == ref_plan]
                    df_res_ref = df_res_ref.copy()
                    df_res_ref[var] = df_res_ref[var].fillna(0)

                    for plan in [ref_plan]+plans_to_compare:

                        df_res_plan = df_res_sect[df_res_sect['PLAN_NAME'] == plan]

                        df_res_plan = df_res_plan.copy()
                        df_res_plan[var] = df_res_plan[var].fillna(0)

                        max_plan = df_res_plan[var].max()
                        if plan == ref_plan:
                            max_ref = max_plan
                            diff_sum = 0

                        else:
                            diff_sum = max_plan - max_ref

                        df_res_agg_plan = pd.DataFrame({'PI_NAME': [pi],
                                                            'VARIABLE': [var],
                                                            'SECT_NAME': [sect],
                                                            'SUPPLY_SCEN': [supply],
                                                            'PLAN_NAME': [plan],
                                                            'MAX': [max_plan],
                                                            'DIFF (PLAN - 2014BOC)': [diff_sum]})

                        list_results.append(df_res_agg_plan)

df_res_all = pd.concat(list_results)

print(df_res_all)
output_results = os.path.join(folder_results, f'NFB_MAX_RESULTS.csv')
df_res_all.to_csv(output_results, sep=';', index=False)




