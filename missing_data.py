import numpy as np
import pandas as pd
from skleaarn.preprocessing import MinMaxScaler
from scipy import stats

data = { 
   'Age': [25, 27, np.nan, 29, 30, 35, 40, np.nan, 55, 60, 65, np.nan, 75], 
    'Salary': [50000, 54000, 58000, 60000, np.nan, 75000, 80000, 85000, np.nan, 120000, 130000, 140000, 150000], 
    'Height': [5.5, 5.7, 5.8, np.nan, 6.0, 5.9, 6.1, np.nan, 5.6, 5.9, 5.8, 6.0, np.nan] 
} 
df = pd.DataFrame(data) 
 
print("Original DataFrame:\n", df)
 
df_dropped = df.dropna() 
print("\nDataFrame after dropping missing values:\n", df_dropped)

df_filled = df.fillna(df.mean()) 
print("\nDataFrame after filling missing values with mean:\n", df_filled) 

z_scores = np.abs(stats.zscore(df_filled)) 
outliers = (z_scores > 3).any(axis=1) 
df_no_outliers = df_filled[~outliers] 
print("\nDataFrame after removing outliers:\n", df_no_outliers)

scaler = MinMaxScaler() 
scaled_data = scaler.fit_transform(df_no_outliers) 
df_scaled = pd.DataFrame(scaled_data, columns=df_no_outliers.columns)

print("Scaled dataframe: ", df_scaled)
