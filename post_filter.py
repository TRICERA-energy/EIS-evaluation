import pandas as pd

# Replace the cluster number with the class letter
# This has to be done manually!

df = pd.read_csv('result_clusters_above650.csv', sep=';')
df['Cluster'] = df['Cluster'].replace(to_replace={0: 'Z', 1: 'Y', 2:'X'})

first_module = df['Name'].head(1).values[0][:4]
last_module = df['Name'].tail(1).values[0][:4]
print(first_module)
print(last_module)

df.rename(columns={'Cluster': 'Klasse'}, inplace=True)

df.to_csv(f'EIS_Klassifizierung_{first_module}_{last_module}.csv', sep=';', index=False)