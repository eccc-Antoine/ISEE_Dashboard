IF NOT DEFINED ISEE_DASH_ROOT (SET ISEE_DASH_ROOT=C:\Users\FortierMa\Documents\Dashboard - ISEE\ISEE_Dashboard\DASHBOARDS\ISEE)
IF NOT DEFINED ISEE_DASH_PYENV (SET ISEE_DASH_PYENV=streamlit-isee)
IF NOT DEFINED CONDA_PATH (SET CONDA_PATH="C:\Users\FortierMa\AppData\Local\anaconda3\Library\bin\conda.bat")

cd %ISEE_DASH_ROOT%

call %CONDA_PATH% activate %ISEE_DASH_PYENV%

streamlit run ISEE_DASH_LIGHT_2.py

timeout /t -1