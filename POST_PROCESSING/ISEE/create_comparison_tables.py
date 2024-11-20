import pandas as pd
import os
import numpy as np
from arch.bootstrap import optimal_block_length, CircularBlockBootstrap
from scipy.stats import ttest_ind
import CFG_POST_PROCESS_ISEE as cfg

def count_exceedances(data, threshold):
    return np.sum(data < threshold)

dict_thresholds = {
    # 'CHNI_2D': {'N breeding pairs':
    #          {'SLR_US': {'p5': 0.359, 'p10': 0.634, 'p20': 4.023},
    #           'SLR_DS': {'p5': 0.001, 'p10': 0.195, 'p20': 1.793}}},
    #
    # 'IXEX_RPI_2D': {'Weighted usable area (ha)':
    #                 {'SLR_US': {'p5': 167.481, 'p10': 242.211, 'p20': 315.474},
    #                  'SLR_DS': {'p5': 469.675, 'p10': 557.836, 'p20': 1179.954}}},
    #
    # 'SAUV_2D': {'Migration habitat (ha)' :
    #                                {'SLR_US': {'p5': 141.53, 'p10': 146.60, 'p20':162.34},
    #                                'SLR_DS': {'p5': 1643.763, 'p10': 1992.601, 'p20': 2225.198}}},
    #
    # 'BIRDS_2D': {'Abundance (n individuals)' :
    #                  {'LKO': {'p5': 699.564, 'p10': 782.401, 'p20': 991.217}}}

    #
    # 'CHNI_2D': {'N breeding pairs':
    #                 {'SLR_US': {'p20': 4.023},
    #                  'SLR_DS': {'p20': 1.793}}},
    #
    # 'IXEX_RPI_2D': {'Weighted usable area (ha)':
    #                     {'SLR_US': {'p20': 315.474},
    #                      'SLR_DS': {'p20': 1179.954}}},
    #
    # 'SAUV_2D': {'Migration habitat (ha)':
    #                 {'SLR_US': {'p20': 162.34},
    #                  'SLR_DS': {'p20': 2225.198}}},
    #
    # 'BIRDS_2D': {'Abundance (n individuals)':
    #                  {'LKO': {'p20': 991.217}}}

    # 'CHNI_2D': {'N breeding pairs':
    #                 {'SLR_US': 4.023,
    #                  'SLR_DS': 1.793}},
    #
    # 'IXEX_RPI_2D': {'Weighted usable area (ha)':
    #                     {'SLR_US': 315.474,
    #                      'SLR_DS': 1179.954}},
    #
    # 'SAUV_2D': {'Migration habitat (ha)':
    #                 {'SLR_US': 162.34,
    #                  'SLR_DS': 2225.198}},
    #
    # 'BIRDS_2D': {'Abundance (n individuals)':
    #                  {'LKO': 991.217}}

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
                    {'LKO': {'thresh': 0.145},
                     'USL_US': {'thresh': 0.145},
                     'USL_DS': {'thresh': 0.145},
                     'SLR_US': {'thresh': 0.145},
                     'SLR_DS': {'thresh': 0.145}}
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

    'CWRM_2D': {'Total Wetland Area (ha)':{
        'LKO': {'thresh': 10935.77},
        'USL_US': {'thresh': 3383.96},
        'USL_DS': {'thresh': 1250.07}

    }},

    'IERM_2D': {'Total Wetland Area (ha)': {
        'SLR_US': {'thresh': 3012.98},
        'SLR_DS': {'thresh': 22488.04}
    }}

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

    'ONZI_1D': {'Probability of Lodge viability':
                        {'LKO': {'thresh': 1},
                        'USL_US': {'thresh': 1},
                        'USL_DS': {'thresh': 1},
                        'SLR_US': {'thresh': 1},
                        'SLR_DS': {'thresh': 1}}
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

    'CWRM_2D': {'Total Wetland Area (ha)': {
        'LKO': {'thresh': 1},
        'USL_US': {'thresh': 1},
        'USL_DS': {'thresh': 1}

    }},

    'IERM_2D': {'Total Wetland Area (ha)': {
        'SLR_US': {'thresh': 1},
        'SLR_DS': {'thresh': 1}
    }}
}


gap = 1




# LKO 1.0
# SLR_DS 0.06008342235207664
# SLR_US 0.33760014070084526
# USL_DS 0.965521581090431
# USL_US 1.0

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
    df_ref[var].fillna(0, inplace=True)
    array_ref = df_ref[var].to_numpy()

    opt = optimal_block_length(array_ref)
    block_size = int(np.ceil(opt['circular'].values[0]))

    return block_size

def bootstrap_mean_test(df_ref, df_plan, var, n_iter, block_size):

    df_ref = df_ref.copy()
    df_plan = df_plan.copy()

    array_ref = df_ref[var].to_numpy()
    array_plan = df_plan[var].to_numpy()

    # Compute the observed t-statistic
    observed_t_stat = ttest_ind(array_ref, array_plan, equal_var=False).statistic

    # Apply the null hypothesis that the means are equal mean1 = mean2
    overall_mean = np.mean(np.concatenate([array_ref, array_plan]))
    array_ref = array_ref - np.mean(array_ref) + overall_mean
    array_plan = array_plan - np.mean(array_plan) + overall_mean

    bootstrap_samples_ref = block_bootstrap(array_ref, block_size, n_iter=n_iter)
    bootstrap_samples_plan = block_bootstrap(array_plan, block_size, n_iter=n_iter)

    # For each bootstrap sample, compute the t-statistic
    bootstrap_t_stat = [
        ttest_ind(b_sample_a, b_sample_b, equal_var=False).statistic
        for b_sample_a, b_sample_b in zip(bootstrap_samples_ref, bootstrap_samples_plan)
    ]

    # Compute the p-value
    bs_comparison = bootstrap_t_stat >= observed_t_stat
    p_value = np.mean(bs_comparison)

    return p_value


gap = 1
n_iter = 1000
alpha = 0.05


folder_results = os.path.join(cfg.POST_PROCESS_RES, r'PI_CSV_RESULTS')

#list_supplies = ['Historical']

ref_plan = 'Bv7_2014BOC'

list_results = []
for pi, dict_var in dict_thresholds.items():
    print(pi)
    for var, dict_sect in dict_var.items():
        print(var)
        file_res = f'{pi}_{var}.csv'

        path_results = os.path.join(folder_results, file_res)

        df_res = pd.read_csv(path_results, sep=';', header=0)

        for supply, df_res_supply in df_res.groupby('SUPPLY_SCEN'):

            plans_to_compare = [plan for plan in df_res_supply['PLAN_NAME'].unique() if plan != ref_plan]
            print(plans_to_compare)

            for sect, dict_percentile in dict_sect.items():
                print(sect)

                df_res_sect = df_res_supply[df_res_supply['SECT_NAME'] == sect]
                df_res_ref = df_res_sect[df_res_sect['PLAN_NAME'] == ref_plan]

                df_res_ref = df_res_ref.copy()
                df_res_ref[var].fillna(0, inplace=True)

                mean_ref = df_res_ref[var].mean()

                try:
                    block_size = calculate_block_size(df_res_ref, var)
                except Exception as e:
                    print(e)
                    block_size = 1

                if pi in dict_pi_scores:
                    score_weights = list(dict_pi_scores[pi][var][sect].values())
                    thresholds = list(dict_percentile.values())

                    value_ref = calculate_threshold_score(df_res_ref, var, score_weights, thresholds)

                    df_res_agg_ref = pd.DataFrame({'PI_NAME': [f'{pi}_{var}'],
                                                   'VARIABLE': [var],
                                                   'SECT_NAME': [sect],
                                                   'SUPPLY_SCEN': [supply],
                                                   'PLAN_NAME': [ref_plan],
                                                   'VALUE_AGG': [value_ref],
                                                   'MEAN_AGG': [mean_ref],
                                                   'DIFF (%)': [np.nan]
                                                   })
                    list_results.append(df_res_agg_ref)

                for plan in plans_to_compare:

                    print(sect, supply, plan)
                    df_res_plan = df_res_sect[df_res_sect['PLAN_NAME'] == plan]
                    mean_plan = df_res_plan[var].mean()

                    if pi in dict_pi_scores:
                        score_weights = list(dict_pi_scores[pi][var][sect].values())
                        thresholds = list(dict_percentile.values())

                        value_plan = calculate_threshold_score(df_res_plan, var, score_weights, thresholds)

                    df_res_plan = df_res_plan.copy()
                    df_res_plan[var].fillna(0, inplace=True)

                    diff_exceedances = value_plan - value_ref
                    pct_change = ((mean_plan/mean_ref) - 1) * 100
                    df_res_agg_plan = pd.DataFrame({'PI_NAME': [pi],
                                                    'VARIABLE': [var],
                                                    'SECT_NAME': [sect],
                                                    'SUPPLY_SCEN': [supply],
                                                    'PLAN_NAME': [plan],
                                                    'VALUE_AGG': [diff_exceedances],
                                                    'MEAN_AGG': [mean_plan],
                                                    'DIFF (%)': [pct_change]
                                                   })
                    print(pi, sect, supply, plan)
                    p_value = bootstrap_mean_test(df_res_ref, df_res_plan, var, n_iter=n_iter, block_size=block_size)

                    df_res_agg_plan['P-value'] = [p_value]

                    if p_value > alpha:
                        df_res_agg_plan['STAT_DIFF'] = 'None'
                    else:
                        df_res_agg_plan['STAT_DIFF'] = '**'

                    df_res_agg_plan['CRITICAL_DIFF'] = ''
                    df_res_agg_plan.loc[df_res_agg_plan['VALUE_AGG'] == gap, 'CRITICAL_DIFF'] = '='
                    df_res_agg_plan.loc[df_res_agg_plan['VALUE_AGG'] > gap, 'CRITICAL_DIFF'] = '-'
                    df_res_agg_plan.loc[df_res_agg_plan['VALUE_AGG'] < gap, 'CRITICAL_DIFF'] = '+'

                    list_results.append(df_res_agg_plan)

df_res_all = pd.concat(list_results)

print(df_res_all)
output_results = os.path.join(folder_results, 'test_table_critical_thresholds_20241118.csv')
df_res_all.to_csv(output_results, sep=';', index=False)

                    #print(residuals)




