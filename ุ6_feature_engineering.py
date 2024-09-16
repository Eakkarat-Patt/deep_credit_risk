from dcr import *
# prepare NaN data
sample_na = data.query('FICO_orig_time <= 650')
sample_na2 = sample_na.sample(int(0.8*len(sample_na)), random_state=1234, replace=False)
sample_na3 = sample_na2[['id', 'time']].copy()
sample_na3.loc[:, 'indicator'] = 1
sample_na3 = sample_na3.drop_duplicates()

data2 = pd.merge(data, sample_na3, on=['id', 'time'], how='left')
data2.loc[:, 'FICO_orig_time2'] = data2.FICO_orig_time
data2.loc[data2['indicator']==1, 'FICO_orig_time2'] = np.NaN

data3 = data2[['FICO_orig_time', 'FICO_orig_time2']]