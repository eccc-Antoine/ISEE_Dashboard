import os
import pandas as pd


dct_var={'VAR1':'OW', 'VAR2':'SAV', 'VAR3':'EM', 'VAR4':'WM', 'VAR5':'SW', 'VAR6':'UPL', 'VAR7':'Total_wetland'}

for var in dct_var.keys():
    print(dct_var[var])

    df=pd.read_feather(fr"P:\GLAM\Dashboard\ISEE_Dash_portable\ISEE_POST_PROCESS_DATA_3\CWRM_2D\YEAR\PT_ID\GERBL2_2014BOC_RCP45\LKO\{var}_CWRM_2D_YEAR_GERBL2_2014BOC_RCP45_LKO_PT_ID_483_2012_2070")

    #print(list(df))

    df.to_csv(fr'P:\GLAM\Dashboard\ISEE_Dash_portable\ISEE_POST_PROCESS_DATA_3\CWRM_2D\For_Richard\Climate_change_4_5_2012_2070\{dct_var[var]}_CWRM_2D_YEAR_GERBL2_2014BOC_RCP45_LKO_PT_ID_483_2012_2070.csv', sep=';', index=None)



quit()