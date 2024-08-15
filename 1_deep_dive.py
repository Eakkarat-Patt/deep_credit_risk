import pandas as pd
from dcr import *

data2 = data[['id', 'time', 'gdp_time', 'FICO_orig_time', 'LTV_time']]

table = pd.crosstab(data.orig_time, columns='count', margins=True)

FICO = data2.groupby('time')['FICO_orig_time'].mean().reset_index(drop=False)

plt.plot('time', 'FICO_orig_time', data=FICO )
plt.xlabel('Time')
plt.ylabel('FICO')
plt.ylim([400, 850])
plt.show()