import numpy as np
from sklearn.cluster import KMeans
import pandas as pd
import math
import plotly.graph_objects as go

# Define excluded modules. Has to be done manually.
faulty_modules = ['0659 (0660) Bj_1905 20,5°C', '1079 (1080) Bj_1906 23,7°C', '1080 (1079) Bj_1906 23,7°C', '1081 (1082) 23,7°C']
first_module = 650

# Load your JSON data into a Pandas DataFrame
with open('data_api_filtered.json', 'r') as file:
    data = pd.read_json(file, )

df_list = []

for module_data in data["filtered_data"]:
    measurements = pd.DataFrame(module_data["measurements"])
    measurements['Name'] = module_data["name"]
    measurements.rename(columns={'frequency': 'Frequency', 'phase_shift': 'PhaseShift', 'amplitude': 'Amplitude'}, inplace=True)
    df_list.append(measurements)

df = pd.concat(df_list, ignore_index=True)

# Convert to impedance data.
df_re_imag = df.copy()
df_re_imag['Real'] = df['Amplitude'] * np.cos(df['PhaseShift'].apply(math.radians))
df_re_imag['Imag'] = df['Amplitude'] * np.sin(df['PhaseShift'].apply(math.radians))
df_re_imag.drop(columns=['Amplitude', 'PhaseShift'], inplace=True)

# Group modules as list of dataframes
df_list_re_imag = []
for name, module_data in df_re_imag.groupby('Name'):
    df_new = pd.DataFrame(columns=['Name', 'Frequency', 'Real', 'Imag'])
    df_new['Name'] = name
    df_new['Frequency'] = module_data['Frequency']
    df_new['Real'] = module_data['Real']
    df_new['Imag'] = module_data['Imag']
    df_list_re_imag.append(module_data.reset_index())

# Create dataframe that is input for clustering.
df_cluster_re_imag = pd.DataFrame()

original_frequencies = df_list_re_imag[0]['Frequency'].tolist()
# Select frequencies that are considered. (~118 Hz, 100mHz)
common_frequencies = [original_frequencies[8], original_frequencies[28]]

for i, dfi in enumerate(df_list_re_imag):
    name = dfi.loc[1, 'Name']
    # Exclude modules with bad data.
    if name in faulty_modules:
        continue

    # Define classification batch
    if name[0] == '0':
        name_number = int(name[1:4])
    else:
        name_number = int(name[0:4])
    if name_number <= first_module:
        continue
    
    for freq in common_frequencies:
        try:
            df_cluster_re_imag.loc[name, f'Real_{freq}'] = dfi.loc[dfi['Frequency'] == freq, 'Real'].values[0]
            df_cluster_re_imag.loc[name, f'Imag_{freq}'] = dfi.loc[dfi['Frequency'] == freq, 'Imag'].values[0]
            
        except IndexError:
            print("INDEX ERROR!")
            print(name) 
            print(dfi)
  

## Clustering

nr_cluster = 3
# Fit k-means clustering
kmeans_re_imag = KMeans(n_clusters=nr_cluster)  # Set the number of clusters as needed
kmeans_re_imag.fit(df_cluster_re_imag)
y_fit_re_imag = kmeans_re_imag.predict(df_cluster_re_imag)

# Get the cluster labels
cluster_labels_re_imag = kmeans_re_imag.labels_

# Add cluster labels to the original DataFrame
df_cluster_re_imag['Cluster'] = cluster_labels_re_imag

df_cluster_re_imag.reset_index(inplace=True)
df_cluster_re_imag.rename(columns={'index': 'Name'}, inplace=True)

# Find indices where the values in the specified column equal the specified value

df_cluster_result = df_cluster_re_imag[['Name', 'Cluster']].copy()
df_cluster_result.to_csv(f'result_clusters_above{first_module}.csv', index=False, sep=';')

figs = [go.Figure() for i in range(nr_cluster)]

for i in range(nr_cluster):
    clusters = df_cluster_re_imag.loc[df_cluster_re_imag['Cluster'] == i, 'Name'].tolist()
    print('cluster', i)
    print(len(clusters))
    for dfi in df_list_re_imag:
        name = dfi.loc[1, 'Name']
        line1 = go.Scatter(x=dfi['Real'], y=-dfi['Imag'], mode='lines+markers', name=name)
        if name in clusters:
            figs[i].add_trace(line1)
        # Include faulty modules into each cluster plot, then decide manually.
        #if name in faulty_modules:
        #    figs[i].add_trace(line1)
    figs[i].update_layout(
        title=f'EIS - Nyquist',
        xaxis_title=r'$Z^{\prime}(\omega)$ ' +
                  '$[{}]$'.format('Ohms'),
        yaxis_title=r'$-Z^{\prime\prime}(\omega)$ ' +
                  '$[{}]$'.format('Ohms'),
        showlegend=True
    )
    figs[i].update_xaxes(range=[0.0035, 0.01])
    figs[i].update_yaxes(range=[-0.002, 0.002])


    #html_content = figs[i].to_html(full_html=False, include_mathjax='cdn')
    #with open(f"EIS_Nyquist_cluster{i}.html", "w") as f:
    #    f.write(html_content)

    figs[i].show()

# Plot all modules
fig_all = go.Figure()
fig_all.update_layout(
    title='EIS - Nyquist (all modules)',
    xaxis_title=r'$Z^{\prime}(\omega)$ ' +
                  '$[{}]$'.format('Ohms'),
    yaxis_title=r'$-Z^{\prime\prime}(\omega)$ ' +
                  '$[{}]$'.format('Ohms'),
    showlegend=True
)
fig_all.update_xaxes(range=[0.0035, 0.01])
fig_all.update_yaxes(range=[-0.002, 0.002])
for dfi in df_list_re_imag:
    name = dfi.loc[1, 'Name']
    line1 = go.Scatter(x=dfi['Real'], y=-dfi['Imag'], mode='lines+markers', name=name)
    fig_all.add_trace(line1)
fig_all.show()

#html_content = fig_all.to_html(full_html=False, include_mathjax='cdn')
#with open(f"EIS_Nyquist_all_clusters.html", "w") as f:
#    f.write(html_content)