# Post-Processing of ISEE results for the Dashboard

The post-processing mostly consists in the aggregation of ISEE results per year, per plan, per section, per tile and per point id. The files usable by the dashboard are then uploaded to Azure.

## Before running the post-processing of a PI
0. Open the prod2 server to enter your username and password (or else the scripts won't have access)
1. Check if the results are in prod2\GLAM\Output_ISEE\results_off\DASHBOARD_RESULTS_NEW
2. Change the PIs configuration in GENERAL\CFG_PIS if necessary (if you want to add a new plan for example)
3. Change the CFG_POST_PROCESS_ISEE.py file based on your needs (please read the comments)
4. Delete old post-processed results if necessary in projets$\GLAM\Dashboard\ISEE_Dash_portable\ISEE_POST_PROCESS_DATA_3

## Run the post-processing
During the post-processing, main events will be printed in the terminal. The intermediate and supplementary information will be written in a log file in the logs directory.
In the log file name, the date and time will be written, in addition to the prefix set in the configs.

To run the post-processing : python main.py

## After the post-processing
Please check your terminal and the logs to make sure you post-processed what you wanted. Check also your out folder in projets$\GLAM\Dashboard\ISEE_Dash_portable\ISEE_POST_PROCESS_DATA_3.
Finally, you can go the online version of the Dashboard to see your results if the PI config was not changed. Else, you need to push the app to Azure or run the dashboard locally.

If the results in the dashboard are erroneous, most of the time it's one of those problems :
- the files in prod2\GLAM\Output_ISEE\results_off\DASHBOARD_RESULTS_NEW contain errors or are missing ;
- the PIs or post-processing config were not updated correctly ;
- you didn't open the shared servers recently.

You can try running the post-processing again (sometimes it works).

If you changed the PIs configuration in GENERAL/CFG_PIS, we need to update the app online separately to see your results (ask Antoine/Marianne F).