from dcr import *

data, _, _, _, _, _, _ = dataprep(data)
data['PD'] = data['default_time'].mean()
data_default = data.loc[data['default_time'] == 1, :].copy()

data_default.loc[:, 'res_period'] = data_default.loc[:, 'res_time'] - data_default.loc[:, 'time']

# data_default.loc[:, 'res_period'].hist(bins=20)

# 5.4.3 Risk-Free LGD from Observed Workout Cash Flows
# LGD from sum of all cashflows during resolution period discounted back to observation time


def lgd_cal(data, discount_rate):
    df = data.copy()
    df.loc[:, 'recovery_res'] = df.loc[:, 'recovery_res'].astype(float)
    df.loc[:, 'lgd_result'] = (df.loc[:, 'balance_time'] - df.loc[:, 'recovery_res'] / (
            1 + df.loc[:, f'{discount_rate}'] / (100 * 4)) ** df.loc[:, 'res_period']) / df.loc[:, 'balance_time']
    # LGD models exclude the values of zero and one and we may set a floor 0.0001 and a cap of 0.9999
    df.loc[df['lgd_result'] <= 0, 'lgd_result'] = 0.0001
    df.loc[df['lgd_result'] >= 1, 'lgd_result'] = 0.9999
    return df['lgd_result']


data_default.loc[:, 'NLGD'] = lgd_cal(data_default, 'rate_time')
# ## 5.4.6 LGD Discount Rates
# - Loan contract rate
# - Bank weighted average cost of capital (WACC)
# - Market equilibrium return

# Calculate LGD discount rate using loan contract rate
data_default.loc[:, 'discount_period'] = data_default.loc[:, 'res_time'] - data_default.loc[:, 'orig_time']
data_default.loc[data_default['discount_period'] <= 1, 'discount_period'] = 1
data_default.loc[:, 'DR_L'] = (1 - data_default.loc[:, 'PD']) * data_default.loc[:, 'interest_rate_time'] / (
        4 * 100) + data_default.loc[:, 'PD'] * ((1 + data_default.loc[:, 'interest_rate_time'] / (4 * 100)) * (
        1 - data_default.loc[:, 'NLGD'])) ** (1 / data_default.loc[:, 'discount_period'])
# data_default.loc[:, 'DR_L'].hist(bins=50)
# Calculate LGD discount rate using Weighted average cost of capital (WACC)
data_default.loc[:, 'DLGD'] = 0.2 + 0.8 * data_default.loc[:, 'NLGD']
data_default.loc[:, 'equity'] = (data_default.loc[:, 'DLGD'] - data_default.loc[:, 'NLGD']) / (
        1 - data_default.loc[:, 'NLGD'])
data_default.loc[:, 'debt'] = 1 - data_default.loc[:, 'equity']
data_default.loc[:, 'DR_W'] = data_default.loc[:, 'equity'] * (
        data_default.loc[:, 'rate_time'] / (4 * 100) + 0.06 / 4) + data_default.loc[:, 'debt'] * (
                                      data_default.loc[:, 'rate_time'] / (4 * 100) + 0.02 / 4)

# Calculate LGD discount rate using Market equilibrium return
data_default.loc[:, 'beta'] = (0.2 * np.sqrt(1 - 0.5)) / 0.18  # beta coefficient
data_default.loc[:, 'DR_C'] = data_default.loc[:, 'rate_time'] / (4 * 100) + data_default.loc[:, 'beta'] * 0.06 / 4

# Comparison of LGD discount rates
data_default.loc[:, 'DR_E'] = data_default.loc[:, 'rate_time'] / (4 * 100) + 0.05 / 4  # European banking authority
data_default.loc[:, 'DR_F'] = data_default.loc[:, 'rate_time'] / (4 * 100)  # risk-free rate

def lgd_cal2(data, discount_rate):
    """
    This function is similar to lgd_cal but the discount_rate is already per quarter. Therefore, no need to divided by
    100*4 again here
    :param data:
    :param discount_rate:
    :return:
    """
    df = data.copy()
    df.loc[:, 'recovery_res'] = df.loc[:, 'recovery_res'].astype(float)
    df.loc[:, 'lgd_result'] = (df.loc[:, 'balance_time'] - df.loc[:, 'recovery_res'] / (
            1 + df.loc[:, f'{discount_rate}']) ** df.loc[:, 'res_period']) / df.loc[:, 'balance_time']
    # LGD models exclude the values of zero and one and we may set a floor 0.0001 and a cap of 0.9999
    df.loc[df['lgd_result'] <= 0, 'lgd_result'] = 0.0001
    df.loc[df['lgd_result'] >= 1, 'lgd_result'] = 0.9999
    return df['lgd_result']

data_default.loc[:, 'LGD_L'] = lgd_cal2(data_default, 'DR_L')
data_default.loc[:, 'LGD_W'] = lgd_cal2(data_default, 'DR_W')
data_default.loc[:, 'LGD_C'] = lgd_cal2(data_default, 'DR_C')

data_default_mean = data_default.groupby('time')[['LGD_L', 'LGD_W', 'LGD_C', 'NLGD']].mean()

# print(data_default[['LGD_L', 'LGD_W', 'LGD_C', 'NLGD']].dropna().describe().round(decimals=3))

# The following steps try to solve the resolution bias
data_default2 = data_default.dropna(subset=['res_time']).copy()
data_default2.loc[data_default2['res_period'] >= 20, 'res_period'] = 20
data_lgd_sum = data_default2.groupby('res_period')[['LGD_L', 'LGD_W', 'LGD_C', 'NLGD']].sum()
data_lgd_count = data_default2.groupby('res_period')[['LGD_L', 'LGD_W', 'LGD_C', 'NLGD']].count()

data_lgd_sum = data_lgd_sum.sort_values(by=['res_period'], ascending=False)
data_lgd_count = data_lgd_count.sort_values(by=['res_period'], ascending=False)

data_lgd_sum_cumsum = data_lgd_sum.cumsum()
data_lgd_count_cumsum = data_lgd_count.cumsum()
data_lgd_mean = data_lgd_sum_cumsum / data_lgd_count_cumsum

data_lgd_mean['time'] = 61 - data_lgd_mean.index
data_lgd_mean = data_lgd_mean.set_index('time')

data_lgd_mean2 = data_lgd_mean.iloc[np.full(41, 0)].reset_index(drop=True)

