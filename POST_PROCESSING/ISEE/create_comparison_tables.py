import pandas as pd
import os
import numpy as np
from arch.bootstrap import optimal_block_length, CircularBlockBootstrap
from scipy.stats import ttest_ind, mannwhitneyu, wilcoxon, theilslopes, skew
import CFG_POST_PROCESS_ISEE as cfg
from statsmodels.tsa.stattools import adfuller
from statsmodels.stats.descriptivestats import sign_test


def count_exceedances(data, threshold):
    return np.sum(data < threshold)

def calculate_threshold_score(df_res, var, score_weights, thresholds):
    score = 0
    for i in range(0, len(thresholds)):

        weight = score_weights[i]
        if i == 0:
            n = len(df_res[df_res[var] < thresholds[i]]) * weight
        else:
            n = len(df_res[(df_res[var] >= thresholds[i - 1]) & (df_res[var] < thresholds[i])]) * weight
        score += n
    return score

def block_bootstrap(data, block_size, n_iter):
    """Perform block bootstrap on a time series."""
    n = len(data)
    bootstrap_samples = []
    for _ in range(n_iter):
        sample = []
        for _ in range(n // block_size):
            # Randomly select a block start position
            block_start = np.random.randint(0, n - block_size + 1)
            # Append the block to the bootstrap sample
            sample.extend(data[block_start:block_start + block_size])
        # Ensure the sample length is equal to the original data length
        bootstrap_samples.append(np.array(sample[:n]))
    return bootstrap_samples

def calculate_block_size(df_ref, var):
    df_ref = df_ref.copy()
    df_ref[var] = df_ref[var].fillna(0)
    array_ref = df_ref[var].to_numpy()

    opt = optimal_block_length(array_ref)
    block_size = int(np.ceil(opt['circular'].values[0]))

    return block_size

# def bootstrap_mean_test(df_ref, df_plan, var, n_iter, block_size):
#
#     df_ref = df_ref.copy()
#     df_plan = df_plan.copy()
#
#     array_ref = df_ref[var].to_numpy()
#     array_plan = df_plan[var].to_numpy()
#
#     # Compute the observed t-statistic
#     observed_t_stat = ttest_ind(array_ref, array_plan, equal_var=False).statistic
#
#     # Apply the null hypothesis that the means are equal mean1 = mean2
#     overall_mean = np.mean(np.concatenate([array_ref, array_plan]))
#     array_ref = array_ref - np.mean(array_ref) + overall_mean
#     array_plan = array_plan - np.mean(array_plan) + overall_mean
#
#     bootstrap_samples_ref = block_bootstrap(array_ref, block_size, n_iter=n_iter)
#     bootstrap_samples_plan = block_bootstrap(array_plan, block_size, n_iter=n_iter)
#
#     # For each bootstrap sample, compute the t-statistic
#     bootstrap_t_stat = [
#         ttest_ind(b_sample_a, b_sample_b, equal_var=False).statistic
#         for b_sample_a, b_sample_b in zip(bootstrap_samples_ref, bootstrap_samples_plan)
#     ]
#
#     # Compute the p-value
#     bs_comparison = bootstrap_t_stat >= observed_t_stat
#     p_value = np.mean(bs_comparison)
#
#     return p_value


def bootstrap_mean_test(df_ref, df_plan, var, n_iter, block_size):
    """
    Perform a t-test with block bootstrapping to compare means of two distributions.

    Parameters:
        df_ref: DataFrame containing the reference data.
        df_plan: DataFrame containing the plan data.
        var: The column name for the variable to compare.
        n_iter: Number of bootstrap iterations.
        block_size: Size of the blocks for bootstrapping.

    Returns:
        p_value: The p-value from the bootstrap test.
        confidence_interval: Bootstrap confidence interval for the mean difference.
    """

    # Create copies of the input DataFrames
    df_ref = df_ref.copy()
    df_plan = df_plan.copy()

    df_ref[var] = df_ref[var].fillna(0)
    df_plan[var] = df_plan[var].fillna(0)

    array_ref = df_ref[var].to_numpy()
    array_plan = df_plan[var].to_numpy()

    # Compute the observed t-statistic (original data)
    observed_t_stat = ttest_ind(array_ref, array_plan, equal_var=False).statistic

    # Compute the observed mean difference
    observed_mean_diff = np.mean(array_ref) - np.mean(array_plan)

    # Apply the null hypothesis (means are equal: mean_ref = mean_plan)
    # Center the two arrays around their combined mean
    overall_mean = np.mean(np.concatenate([array_ref, array_plan]))
    array_ref = array_ref - np.mean(array_ref) + overall_mean
    array_plan = array_plan - np.mean(array_plan) + overall_mean

    # Generate bootstrap samples for both distributions
    bootstrap_samples_ref = block_bootstrap(array_ref, block_size, n_iter=n_iter)
    bootstrap_samples_plan = block_bootstrap(array_plan, block_size, n_iter=n_iter)

    # Compute bootstrap t-statistics and mean differences
    bootstrap_t_stat = []
    bootstrap_mean_diffs = []

    for b_sample_ref, b_sample_plan in zip(bootstrap_samples_ref, bootstrap_samples_plan):
        bootstrap_t_stat.append(ttest_ind(b_sample_ref, b_sample_plan, equal_var=False).statistic)
        bootstrap_mean_diffs.append(np.mean(b_sample_ref) - np.mean(b_sample_plan))

    # Convert bootstrap results to numpy arrays for easier analysis
    bootstrap_t_stat = np.array(bootstrap_t_stat)
    bootstrap_mean_diffs = np.array(bootstrap_mean_diffs)

    # Compute the bootstrap p-value (proportion of bootstrap t-statistics >= observed t-statistic)
    bs_comparison = bootstrap_t_stat >= observed_t_stat
    p_value = np.mean(bs_comparison)

    # Compute the 95% confidence interval for the mean difference
    lower_ci = np.percentile(bootstrap_mean_diffs, 2.5)
    upper_ci = np.percentile(bootstrap_mean_diffs, 97.5)

    # Return the p-value and confidence interval
    return p_value, (lower_ci, upper_ci)


def bootstrap_median_test_mannwhit(df_ref, df_plan, var, n_iter, block_size):
    """
    Perform a Mann-Whitney U test with block bootstrapping to compare medians of two distributions.

    Parameters:
        df_ref: DataFrame containing the reference data.
        df_plan: DataFrame containing the plan data.
        var: The column name for the variable to compare.
        n_iter: Number of bootstrap iterations.
        block_size: Size of the blocks for bootstrapping.

    Returns:
        p_value: The p-value from the bootstrap test.
        confidence_interval: Bootstrap confidence interval for the median difference.
    """

    df_ref = df_ref.copy()
    df_plan = df_plan.copy()

    df_ref[var] = df_ref[var].fillna(0)
    df_plan[var] = df_plan[var].fillna(0)

    array_ref = df_ref[var].to_numpy()
    array_plan = df_plan[var].to_numpy()

    # Compute the observed U statistic
    observed_u_stat, observed_p_value = mannwhitneyu(array_ref, array_plan, alternative='two-sided')

    # Combine data and compute the overall median
    combined_data = np.concatenate([array_ref, array_plan])
    overall_median = np.median(combined_data)

    # Center the data around the combined median (null hypothesis: medians are equal)
    array_ref = array_ref - np.median(array_ref) + overall_median
    array_plan = array_plan - np.median(array_plan) + overall_median

    # Generate bootstrap samples
    bootstrap_samples_ref = block_bootstrap(array_ref, block_size, n_iter=n_iter)
    bootstrap_samples_plan = block_bootstrap(array_plan, block_size, n_iter=n_iter)

    # For each bootstrap sample, compute the U statistic
    bootstrap_u_stats = [
        mannwhitneyu(b_sample_a, b_sample_b, alternative='two-sided').statistic
        for b_sample_a, b_sample_b in zip(bootstrap_samples_ref, bootstrap_samples_plan)
    ]

    # Compute the p-value
    bs_comparison = np.array(bootstrap_u_stats) >= observed_u_stat
    p_value = np.mean(bs_comparison)

    # Compute bootstrap confidence intervals for the median difference
    bootstrap_median_diffs = [
        np.median(b_sample_a) - np.median(b_sample_b)
        for b_sample_a, b_sample_b in zip(bootstrap_samples_ref, bootstrap_samples_plan)
    ]

    lower_ci = np.percentile(bootstrap_median_diffs, 2.5)
    upper_ci = np.percentile(bootstrap_median_diffs, 97.5)

    return p_value, (lower_ci, upper_ci)

def bootstrap_median_test_wilcoxon(df_ref, df_plan, var, n_iter, block_size):
    """
    Perform a Wilcoxon signed-rank test with block bootstrapping to compare medians of two paired distributions.

    Parameters:
        df_ref: DataFrame containing the reference data.
        df_plan: DataFrame containing the plan data.
        var: The column name for the variable to compare.
        n_iter: Number of bootstrap iterations.
        block_size: Size of the blocks for bootstrapping.

    Returns:
        p_value: The p-value from the bootstrap test.
        confidence_interval: Bootstrap confidence interval for the median difference.
    """

    df_ref = df_ref.copy()
    df_plan = df_plan.copy()

    df_ref[var] = df_ref[var].fillna(0)
    df_plan[var] = df_plan[var].fillna(0)

    array_ref = df_ref[var].to_numpy()
    array_plan = df_plan[var].to_numpy()

    # Ensure paired data
    if len(array_ref) != len(array_plan):
        raise ValueError("Data must be paired; ensure `df_ref` and `df_plan` have the same length for the given variable.")

    # Compute the observed Wilcoxon statistic
    observed_stat, observed_p_value = wilcoxon(array_ref, array_plan, alternative='two-sided')

    # Center the data around the combined median (null hypothesis: medians are equal)
    combined_data = np.concatenate([array_ref, array_plan])
    overall_median = np.median(combined_data)

    array_ref_centered = array_ref - np.median(array_ref) + overall_median
    array_plan_centered = array_plan - np.median(array_plan) + overall_median

    # Generate bootstrap samples
    bootstrap_samples_ref = block_bootstrap(array_ref_centered, block_size, n_iter=n_iter)
    bootstrap_samples_plan = block_bootstrap(array_plan_centered, block_size, n_iter=n_iter)

    # For each bootstrap sample, compute the Wilcoxon statistic
    bootstrap_stats = []
    for b_sample_a, b_sample_b in zip(bootstrap_samples_ref, bootstrap_samples_plan):
        diff = b_sample_a - b_sample_b
        if np.all(diff != 0):
            stat = wilcoxon(b_sample_a, b_sample_b, alternative='two-sided').statistic
            bootstrap_stats.append(stat)

    # bootstrap_stats = [
    #     wilcoxon(b_sample_a, b_sample_b, alternative='two-sided').statistic
    #     for b_sample_a, b_sample_b in zip(bootstrap_samples_ref, bootstrap_samples_plan)
    # ]
    if len(bootstrap_stats)>n_iter/100:
        # Compute the p-value
        bs_comparison = np.array(bootstrap_stats) >= observed_stat
        p_value = np.mean(bs_comparison)

        # Compute bootstrap confidence intervals for the median difference
        bootstrap_median_diffs = [
            np.median(b_sample_a) - np.median(b_sample_b)
            for b_sample_a, b_sample_b in zip(bootstrap_samples_ref, bootstrap_samples_plan)
        ]

        lower_ci = np.percentile(bootstrap_median_diffs, 2.5)
        upper_ci = np.percentile(bootstrap_median_diffs, 97.5)
    else:
        p_value, lower_ci, upper_ci = np.nan, np.nan, np.nan

    return p_value, (lower_ci, upper_ci)


def check_stationarity(residuals, alpha=0.05):
    stationarity = True
    # Check the variance of the residuals
    residual_variance = np.var(residuals)

    if residual_variance > 0.1:
        result = adfuller(residuals)
        p_value = result[1]
        if p_value > alpha:
            stationarity = False

    return stationarity


def calculate_trend(residuals, alpha=0.05):

    x = np.arange(len(residuals))

    # Compute Theil-Sen estimator and confidence interval
    slope, intercept, lower_slope, upper_slope = theilslopes(residuals, x, alpha=alpha)

    return slope, intercept, lower_slope, upper_slope


def run_stat_tests(residuals, df_res, alpha=0.05):
    stationnary = True
    trend = False
    symmetric = True
    signif_diff = False
    test = ''
    slope=np.nan
    stationnary = check_stationarity(residuals)
    if stationnary:
        # Calculate skewness
        residual_skew = skew(residuals)
        print(residual_skew)
        if abs(residual_skew) < 0.5:
            test = 'Wilcoxon'
            # test de wilcoxon ...
            w_stat, p_value = wilcoxon(residuals, alternative='two-sided')

        else:
            symmetric = False
            test = 'Sign test'

            stat, p_value = sign_test(residuals, mu0=0)

        print(f"STATIONNARY = {stationnary} SYMMETRY = {symmetric} TEST = {test} P-value = {p_value}")


    else:
        slope, intercept, lower_slope, upper_slope = calculate_trend(residuals)
        if lower_slope <= 0 <= upper_slope:
            slope = np.nan
        else:
            trend=True

        detrended_residuals = np.diff(residuals)
        residual_skew = skew(detrended_residuals)
        if abs(residual_skew) < 0.5:
            test = 'Wilcoxon'

            symmetric = True
            w_stat, p_value = wilcoxon(detrended_residuals, alternative='two-sided')

        else:
            test = 'Sign test'
            symmetric = False
            stat, p_value = sign_test(detrended_residuals, mu0=0)

        print(f"STATIONNARY = {stationnary} SYMMETRY = {symmetric} TEST = {test} P-value = {p_value}")
            # would need to detrend the residuals and compare medians.
    if p_value <= alpha:
        signif_diff = True

    df_res['STATIONNARY'] = stationnary
    df_res['SYMMETRY'] = symmetric
    df_res['TREND'] = trend
    df_res['SLOPE'] = slope
    df_res['TEST'] = test
    df_res['P-value'] = p_value
    df_res['SIGNIF_DIFF'] = signif_diff

    return df_res

def estimate_critical_periods(df, var, year_col, low_thresh, high_thresh, n_yrs):

    count_critical_periods = 0
    for i, row in df.iterrows():
        year = row[year_col]
        value = row[var]
        if value<low_thresh:
            #print(f'LOW THRESHOLD REACHED IN YEAR: {year}')
            df_following = df.loc[df[year_col].isin(list(range(year+1, year+n_yrs+1)))].copy()
            if len(df_following) == n_yrs:
                n_yr = len(df_following[df_following[var] < high_thresh])
                if n_yr == 0:
                    #print(f"CRITICAL PERIOD FOLLOWING YEAR: {year}")
                    count_critical_periods+=1

    return count_critical_periods



dict_thresholds = {

    'CHNI_2D': {'N breeding pairs':
             {'SLR_US': {'p10': 0.634, 'p20': 4.023},
              'SLR_DS': {'p10': 0.195, 'p20': 1.793}}},

    'IXEX_RPI_2D': {'Weighted usable area (ha)':
                    {'SLR_US': {'p5': 167.481, 'p10': 242.211, 'p20': 315.474},
                     'SLR_DS': {'p5': 469.675, 'p10': 557.836, 'p20': 1179.954}}},

    'SAUV_2D': {'Migration habitat (ha)' :
                                   {'SLR_US': {'p5': 141.53, 'p10': 146.60, 'p20':162.34},
                                   'SLR_DS': {'p5': 1643.763, 'p10': 1992.601, 'p20': 2225.198}}},

    'BIRDS_2D': {'Abundance (n individuals)' :
                     {'LKO': {'p5': 699.564, 'p10': 782.401, 'p20': 991.217}}},

    'ONZI_1D': {'Probability of Lodge viability':
                    {'LKO': {'low': 0.109, 'high': 0.799},
                     'USL_US': {'low': 0.109, 'high': 0.799},
                     'USL_DS': {'low': 0.109, 'high': 0.799},
                     'SLR_US': {'low': 0.109, 'high': 0.799},
                     'SLR_DS': {'low': 0.109, 'high': 0.799}}
                },

    'TURTLE_1D': {'Turtle winter survival probability':
                    {'LKO': {'thresh': 1},
                     'USL_US': {'thresh': 1},
                     'USL_DS': {'thresh': 1},
                     'SLR_US': {'thresh': 1},
                     'SLR_DS': {'thresh': 1}}
                },

    'ZIPA_1D': {'Wildrice survival probability': {
        'LKO': {'thresh': 1},
        'USL_US': {'thresh': 1},
        'USL_DS': {'thresh': 0.965},
        'SLR_US': {'thresh': 0.337},
        'SLR_DS': {'thresh': 0.06}
    }},

    'ERIW_MIN_1D': {'Exposed Riverbed Index': {
        'LKO': {'thresh': 0.72},
        'USL_US': {'thresh': 0.72},
        'USL_DS': {'thresh': 0.72},
        'SLR_US': {'thresh': 0.72},
        'SLR_DS': {'thresh': 0.72}
    }},

    'CWRM_2D': {
        'Total Wetland area (ha)':{
        'LKO': {'thresh': 10935.77},
        'USL_US': {'thresh': 3383.96},
        'USL_DS': {'thresh': 1250.07}},
        # 'Wet meadow area (ha)':{
        #     'LKO':'low_supply_mean',
        #     'USL_US': 'low_supply_mean',
        #     'USL_DS': 'low_supply_mean'}
    },

    'IERM_2D': {'Total Wetland area (ha)': {
        'SLR_US': {'thresh': 3012.98},
        'SLR_DS': {'thresh': 22488.04}},

        # 'Wet meadow area (ha)': {
        #     'LKO': 'low_supply_mean',
        #     'USL_US': 'low_supply_mean',
        #     'USL_DS': 'low_supply_mean'}
    },

    # 'PIKE_2D': {'Habitat available for spawning and embryo-larval development (ha)':
    #                 {'LKO': {'low': 628.98, 'high': 1668.05},
    #                  'USL_US': {'low': 243.64, 'high': 592.12},
    #                  'USL_DS': {'low': 43.5, 'high': 102.03},
    #                  'SLR_US': {'low': 159.19, 'high': 381.06},
    #                  'SLR_DS': {'low': 0.01, 'high': 2924.89},
    #                  }}

}

# SLR_DS 22488.043432168757
# SLR_US 3012.9883364243196

dict_pi_scores = {
    'CHNI_2D': {'N breeding pairs':
                 {'SLR_US': {'p10': 2, 'p20': 1},
                  'SLR_DS': {'p10': 2, 'p20': 1}}
                              },

    'IXEX_RPI_2D': {'Weighted usable area (ha)':
                {'SLR_US': {'p5': 3, 'p10': 2, 'p20': 1},
                 'SLR_DS': {'p5': 3, 'p10': 2, 'p20': 1}}
                    },

    'SAUV_2D': {'Migration habitat (ha)' :
                   {'SLR_US': {'p5': 3, 'p10': 2, 'p20':1},
                   'SLR_DS': {'p5': 3, 'p10': 2, 'p20': 1}}
                },

    'BIRDS_2D': {'Abundance (n individuals)' :
                     {'LKO': {'p5': 3, 'p10': 2, 'p20': 1}}
                 },

    'TURTLE_1D': {'Turtle winter survival probability':
                    {'LKO': {'thresh': 1},
                     'USL_US': {'thresh': 1},
                     'USL_DS': {'thresh': 1},
                     'SLR_US': {'thresh': 1},
                     'SLR_DS': {'thresh': 1}}
                },

    'ZIPA_1D': {'Wildrice survival probability':{
        'LKO': {'thresh': 1},
        'USL_US': {'thresh': 1},
        'USL_DS': {'thresh': 1},
        'SLR_US': {'thresh': 1},
        'SLR_DS': {'thresh': 1}
    }},

    'ERIW_MIN_1D': {'Exposed Riverbed Index': {
        'LKO': {'thresh': 1},
        'USL_US': {'thresh': 1},
        'USL_DS': {'thresh': 1},
        'SLR_US': {'thresh': 1},
        'SLR_DS': {'thresh': 1}
    }},

    'CWRM_2D': {'Total Wetland area (ha)': {
        'LKO': {'thresh': 1},
        'USL_US': {'thresh': 1},
        'USL_DS': {'thresh': 1}}},

    'IERM_2D': {'Total Wetland area (ha)': {
        'SLR_US': {'thresh': 1},
        'SLR_DS': {'thresh': 1}}

    }
}

dict_pi_var = {
    'CHNI_2D': ['N breeding pairs'],

    'IXEX_RPI_2D': ['Weighted usable area (ha)'],

    'SAUV_2D': ['Migration habitat (ha)'],

    'BIRDS_2D': ['Abundance (n individuals)'],

    'ONZI_1D': ['Probability of Lodge viability'],

    'TURTLE_1D': ['Turtle winter survival probability'],

    'ZIPA_1D': ['Wildrice survival probability'],

    'ERIW_MIN_1D': ['Exposed Riverbed Index'],

    'CWRM_2D': ['Total Wetland area (ha)', 'Wet Meadow area (ha)'],

    'IERM_2D': ['Total Wetland area (ha)', 'Wet Meadow area (ha)'],

    # 'PIKE_2D': ['Habitat available for spawning and embryo-larval development'],

    'AYL_2D':  ['Average Yield Loss for all crops ($)'],

    'ROADS_2D': ['Primary roads (Nb of QMs)',
                 'Secondary roads (Nb of QMs)',
                 'Tertiary roads (Nb of QMs)',
                 'All roads (Nb of QMs)',
                 'Primary roads (Length in m)',
                 'Secondary roads (Length in m)',
                 'Tertiary roads (Length in m)',
                 'All roads (Length in m)']
    }



dict_pi_frequency_high_lows = {'ONZI_1D': {'Probability of Lodge viability':5}}

#list_mean_comparison = ['CHNI_2D', 'IXEX_RPI_2D', 'SAUV_2D', 'BIRDS_2D', 'ERIW_MIN_1D', 'ONZI_1D', 'CWRM_2D', 'IERM_2D', 'AYL_2D', 'ROADS_2D']
list_mean_comparison = []
list_median_comparison = ['CHNI_2D', 'IXEX_RPI_2D', 'SAUV_2D', 'BIRDS_2D', 'ERIW_MIN_1D', 'ONZI_1D', 'CWRM_2D', 'IERM_2D', 'ROADS_2D']
list_pi_test = ['CHNI_2D', 'IXEX_RPI_2D', 'SAUV_2D', 'BIRDS_2D', 'ERIW_MIN_1D', 'ONZI_1D', 'CWRM_2D', 'IERM_2D', 'ROADS_2D']

wm_low_supply_yrs = {'Historical': [1961, 1962, 1963, 1964, 1965, 1966, 1967, 2001, 2002],
                   'STO330': [2028, 2029, 2040, 2041, 2042, 2043, 2044, 2045, 2046, 2047, 2048, 2049, 2050],
                   'RCP45':[2011, 2012, 2013, 2014, 2015, 2036, 2037, 2038, 2041, 2042, 2052, 2053]}

gap = 1
n_iter = 0
alpha = 0.05


folder_results = os.path.join(cfg.POST_PROCESS_RES, r'PI_CSV_RESULTS')

#list_supplies = ['Historical']

ref_plan = 'GERBL2_2014'
list_plans = ['PreProject', 'GERBL2_2014_ComboC']
list_pis = list(dict_pi_var.keys())
#list_pis = ['CHNI_2D']

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

            for supply, df_res_supply in df_res.groupby('SUPPLY_SCEN'):

                plans_to_compare = [plan for plan in df_res_supply['PLAN_NAME'].unique() if plan != ref_plan]

                for sect, df_res_sect in df_res_supply.groupby('SECT_NAME'):

                    mean_ref = 0
                    median_ref = 0

                    df_res_ref = df_res_sect[df_res_sect['PLAN_NAME'] == ref_plan]
                    df_res_ref[var] = df_res_ref[var].fillna(0)

                    value_ref = np.nan
                    p_value_med, low_ci_med, high_ci_med = np.nan, np.nan, np.nan
                    p_value_mean, low_ci_mean, high_ci_mean = np.nan, np.nan, np.nan
                    block_size = np.nan
                    diff_mean, diff_median = np.nan, np.nan
                    for plan in [ref_plan]+plans_to_compare:

                        df_res_plan = df_res_sect[df_res_sect['PLAN_NAME'] == plan]

                        df_res_plan = df_res_plan.copy()
                        df_res_plan[var] = df_res_plan[var].fillna(0)


                        if len(df_res_plan) == len (df_res_ref):

                            ## COMPARAISON DE MOYENNES ET MÉDIANES
                            if (pi in ['IERM_2D', 'CWRM_2D']) & (var == 'Wet meadow area (ha)'):
                                low_supply_yrs = wm_low_supply_yrs[supply]
                                df_res_plan = df_res_plan[df_res_plan['YEAR'].isin(low_supply_yrs)]

                            mean_plan = df_res_plan[var].mean()
                            median_plan = df_res_plan[var].median()

                            residuals = df_res_plan[var].to_numpy() - df_res_ref[var].to_numpy()

                            if plan == ref_plan:
                                pct_change_mean = 0
                                pct_change_median = 0
                                mean_ref = mean_plan
                                median_ref = median_plan
                            else:
                                if median_ref == 0:
                                    pct_change_median = np.nan
                                else:
                                    pct_change_median = ((median_plan / median_ref) - 1) * 100

                                if mean_ref == 0:
                                    pct_change_mean = np.nan
                                else:
                                    pct_change_mean = ((mean_plan / mean_ref) - 1) * 100

                                diff_mean = np.mean(residuals)
                                diff_median = np.median(residuals)

                        # if pi in list_mean_comparison:
                        #     try:
                        #         block_size = calculate_block_size(df_res_ref, var)
                        #     except Exception as e:
                        #         print(e)
                        #         block_size = 1
                        #
                        #     if len(df_res_plan) == len(df_res_ref):
                        #         p_value_mean, (low_ci_mean, high_ci_mean) = bootstrap_mean_test(df_res_ref, df_res_plan, var, n_iter=n_iter, block_size=block_size)
                        #         print(p_value_mean)
                        #


                        #     try:
                        #         block_size = calculate_block_size(df_res_ref, var)
                        #     except Exception as e:
                        #         print(e)
                        #         block_size = 1
                        #     if len(df_res_plan) == len(df_res_ref):
                        #         p_value_med, (low_ci_med, high_ci_med) = bootstrap_median_test_wilcoxon(df_res_ref, df_res_plan, var, n_iter=n_iter, block_size=block_size)
                        #         print(p_value_med)

                    # df_res_agg_plan = pd.DataFrame({'PI_NAME': [pi],
                    #                                 'VARIABLE': [var],
                    #                                 'SECT_NAME': [sect],
                    #                                 'SUPPLY_SCEN': [supply],
                    #                                 'PLAN_NAME': [plan],
                    #                                 'BOOTSTRAP_BLOCK_SIZE': [block_size],
                    #                                 'MEAN_AGG': [mean_plan],
                    #                                 'DIFF MEAN (ABS.)': [diff_mean],
                    #                                 'DIFF MEAN (%)': [pct_change_mean],
                    #                                 'meanTest_CI_2.5': [low_ci_mean + diff_mean],
                    #                                 'meanTest_CI_97.5': [high_ci_mean + diff_mean],
                    #                                 'meanTest_P-Value': [p_value_mean],
                    #                                 'MEDIAN_AGG':[median_plan],
                    #                                 'DIFF MEDIAN (%)': [pct_change_median],
                    #                                 'DIFF MEDIAN (ABS.)': [diff_median],
                    #                                 'medianTest_CI_2.5': [low_ci_med + diff_median],
                    #                                 'medianTest_CI_97.5': [high_ci_med + diff_median],
                    #                                 'medianTest_P-Value': [p_value_med]
                    #                                 })
                            df_res_agg_plan = pd.DataFrame({'PI_NAME': [pi],
                                                            'VARIABLE': [var],
                                                            'SECT_NAME': [sect],
                                                            'SUPPLY_SCEN': [supply],
                                                            'PLAN_NAME': [plan],
                                                            'MEAN_AGG': [mean_plan],
                                                            'DIFF MEAN (ABS.)': [diff_mean],
                                                            'DIFF MEAN (%)': [pct_change_mean],
                                                            'MEDIAN_AGG':[median_plan],
                                                            'DIFF MEDIAN (%)': [pct_change_median],
                                                            'DIFF MEDIAN (ABS.)': [diff_median]
                                                            })
                            if pi in list_pi_test:
                                if plan != ref_plan:
                                    df_res_agg_plan = run_stat_tests(residuals, df_res_agg_plan, alpha=alpha)

                        # df_res_agg_plan.loc[df_res_agg_plan['meanTest_P-Value']<=alpha, 'MeanTest_Significant'] = '*'
                        # df_res_agg_plan.loc[df_res_agg_plan['medianTest_P-Value']<=alpha, 'MedianTest_Significant'] = '*'


                            if pi in dict_pi_scores:
                                if var in dict_pi_scores[pi]:
                                    score_weights = list(dict_pi_scores[pi][var][sect].values())
                                    thresholds = list(dict_thresholds[pi][var][sect].values())
                                    #thresholds = list(dict_percentile.values())
                                    if len(df_res_plan) == len(df_res_ref):

                                        if plan == ref_plan:

                                            value_ref = calculate_threshold_score(df_res_ref, var, score_weights, thresholds)
                                            df_res_agg_plan['VALUE_AGG'] = value_ref
                                            # df_res_agg_ref = pd.DataFrame({'PI_NAME': [pi],
                                            #                                 'VARIABLE': [var],
                                            #                                'SECT_NAME': [sect],
                                            #                                'SUPPLY_SCEN': [supply],
                                            #                                'PLAN_NAME': [ref_plan],
                                            #                                'VALUE_AGG': [value_ref],
                                            #                                'MEAN_AGG': [mean_ref],
                                            #                                'DIFF (%)': [np.nan]
                                            #                                })
                                        else:

                                            value_plan = calculate_threshold_score(df_res_plan, var, score_weights, thresholds)

                                            diff_exceedances = value_plan - value_ref
                                            df_res_agg_plan['VALUE_AGG'] = diff_exceedances
                                            df_res_agg_plan['CRITICAL_DIFF'] = ''
                                            df_res_agg_plan.loc[df_res_agg_plan['VALUE_AGG'] == gap, 'CRITICAL_DIFF'] = '='
                                            df_res_agg_plan.loc[df_res_agg_plan['VALUE_AGG'] > gap, 'CRITICAL_DIFF'] = '-'
                                            df_res_agg_plan.loc[df_res_agg_plan['VALUE_AGG'] < -gap, 'CRITICAL_DIFF'] = '+'

                            if pi in dict_pi_frequency_high_lows:
                                if var in dict_pi_frequency_high_lows[pi]:
                                    if len(df_res_plan) == len(df_res_ref):

                                        low_thresh, high_thresh = dict_thresholds[pi][var][sect]['low'], dict_thresholds[pi][var][sect]['high']
                                        n_yrs = dict_pi_frequency_high_lows[pi][var]
                                        #value_ref = np.nan
                                        if plan == ref_plan:
                                            value_ref = estimate_critical_periods(df_res_ref, var, 'YEAR', low_thresh, high_thresh, n_yrs)
                                            df_res_agg_plan['VALUE_AGG'] = value_ref
                                        else:
                                            value_plan = estimate_critical_periods(df_res_ref, var, 'YEAR', low_thresh, high_thresh, n_yrs)
                                            diff_exceedances = value_plan - value_ref
                                            df_res_agg_plan['VALUE_AGG'] = diff_exceedances
                                            df_res_agg_plan.loc[df_res_agg_plan['VALUE_AGG'] == 0, 'CRITICAL_DIFF'] = '='
                                            df_res_agg_plan.loc[df_res_agg_plan['VALUE_AGG'] > 0, 'CRITICAL_DIFF'] = '-'
                                            df_res_agg_plan.loc[df_res_agg_plan['VALUE_AGG'] < 0, 'CRITICAL_DIFF'] = '+'

                            # list_cols = ['PI_NAME', 'VARIABLE', 'SECT_NAME', 'SUPPLY_SCEN', 'PLAN_NAME', 'BOOTSTRAP_BLOCK_SIZE',
                            #              'MEAN_AGG', 'DIFF MEAN (ABS.)', 'DIFF MEAN (%)', 'meanTest_CI_2.5', 'meanTest_CI_97.5',
                            #              'meanTest_P-Value', 'MeanTest_Significant', 'MEDIAN_AGG', 'DIFF MEDIAN (%)', 'DIFF MEDIAN (ABS.)',
                            #              'medianTest_CI_2.5', 'medianTest_CI_97.5', 'medianTest_P-Value', 'MedianTest_Significant', 'VALUE_AGG', 'CRITICAL_DIFF']
                            #
                            # list_cols_df = [col for col in list_cols if col in df_res_agg_plan.columns]

                            list_results.append(df_res_agg_plan)

                    #
                    # for plan in plans_to_compare:
                    #     df_res_plan = df_res_sect[df_res_sect['PLAN_NAME'] == plan]
                    #     df_res_plan = df_res_plan.copy()
                    #     mean_plan = df_res_plan[var].mean()
                    #     pct_change = ((mean_plan / mean_ref) - 1) * 100
                    #
                    #     print(pi, sect, supply, plan)
                    #     p_value = bootstrap_mean_test(df_res_ref, df_res_plan, var, n_iter=n_iter, block_size=block_size)
                    #     df_res_agg_plan = pd.DataFrame({'PI_NAME': [pi],
                    #                                     'VARIABLE': [var],
                    #                                     'SECT_NAME': [sect],
                    #                                     'SUPPLY_SCEN': [supply],
                    #                                     'PLAN_NAME': [plan],
                    #                                     'MEAN_AGG': [mean_plan],
                    #                                     'DIFF (%)': [pct_change]
                    #                                     })
                    #     df_res_agg_plan['P-value'] = [p_value]
                    #
                    #     if p_value > alpha:
                    #         df_res_agg_plan['STAT_DIFF'] = 'None'
                    #     else:
                    #         df_res_agg_plan['STAT_DIFF'] = '**'
                    #
                    #     df_res_agg_plan['CRITICAL_DIFF'] = ''
                    #     df_res_agg_plan.loc[df_res_agg_plan['VALUE_AGG'] == gap, 'CRITICAL_DIFF'] = '='
                    #     df_res_agg_plan.loc[df_res_agg_plan['VALUE_AGG'] > gap, 'CRITICAL_DIFF'] = '-'
                    #     df_res_agg_plan.loc[df_res_agg_plan['VALUE_AGG'] < gap, 'CRITICAL_DIFF'] = '+'
                    #
                    #     list_results.append(df_res_agg_plan)

df_res_all = pd.concat(list_results)

print(df_res_all)
output_results = os.path.join(folder_results, f'test_table_critical_thresholds_20241121_{n_iter}iter.csv')
df_res_all.to_csv(output_results, sep=';', index=False)

                    #print(residuals)




