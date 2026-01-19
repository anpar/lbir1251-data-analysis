import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from datetime import timedelta
from scipy.ndimage import median_filter

'''
    Sur les 3 dernières années (2023 à 2025), l'année 2024 contient les données
    les plus propres, qui produisent les graphes les plus intéressant à interpréter.
    
    Les données des années 2023 et 2025 sont plus bruitées, mais il est toujours
    possible d'en dire quelque chose.
'''

year = 2024

df = pd.read_csv('data/balances-{year}.csv'.format(year=year), sep=';')

# Backward compatibility
if year >= 2025:
    df['time'] = pd.to_datetime(df['time'], unit='d', origin="1899-12-30")
else:
    df['time'] = pd.to_datetime(df['time'], format='%d-%m-%y %H:%M')

df = df.set_index('time')

df *= -1

# En 2024, les données des balances ont enregistré un saut inopiné le 07-02 à 16h15,
# on corrige manuellement
if year == 2024:
    df.loc["2024-02-07 16:15:00":, 'plant_1'] -= (66.65 - 36.14)
    df.loc["2024-02-07 16:15:00":, 'plant_2'] -= (57.72 - 34.46)
    df.loc["2024-02-07 16:15:00":, 'plant_3'] -= (39.74 - 23.99)
    df.loc["2024-02-07 16:15:00":, 'tem_1'] -= (25.62 - 13.34)
    df.loc["2024-02-07 16:15:00":, 'tem_2'] -= (30.1 - 15.77)
    df.loc["2024-02-07 16:15:00":, 'tem_3'] -= 0

# Pour se faciliter un peu la vie par la suite
cols_tem = ['tem_1', 'tem_2', 'tem_3']
cols_plant = ['plant_1', 'plant_2', 'plant_3']
cols_trans = ['trans_1', 'trans_2', 'trans_3']

# Calcul de l'évaporation moyenne
df['evap'] = df[cols_tem].mean(axis=1)

# Calcul de la transpiration en soustrayant l'évaporation de l'évapotranspiration
df[cols_trans] = df[cols_plant].sub(df['evap'], axis="rows")

df = df.drop(columns=cols_tem + cols_plant)

days = np.unique(df.index.date)

'''
    Affichage des données brutes
'''
fig, ax = plt.subplots()
ax.plot(df['trans_1'], label="Transpiration cumulée plante 1")
ax.plot(df['trans_2'], label="Transpiration cumulée plante 2")
ax.plot(df['trans_3'], label="Transpiration cumulée plante 3")
ax.plot(df['evap'], label="Evaporation cumulée moyenne (3 pots vides)")
ax.set_title("Transpirations et évaporation cumulées")
ax.set_ylabel("[g d'eau]")
ax.set_xticks(days, labels=df.index.strftime('%d-%m-%Y').unique())
ax.tick_params('x', rotation=45)
ax.legend()
ax.grid(linestyle='--', alpha=0.5)
plt.show()

# On filtre les donnes pour réduire le bruit et supprimer les glitches
df[cols_trans] = df[cols_trans].apply(median_filter, size=21)

'''
    Affichage des transpirations cumulées après filtration pour réduire
    le bruit et les glitches
'''
fig, ax = plt.subplots()
ax.plot(df['trans_1'], label="Transpiration cumulée plante 1")
ax.plot(df['trans_2'], label="Transpiration cumulée plante 2")
ax.plot(df['trans_3'], label="Transpiration cumulée plante 3")
ax.set_ylabel("[g d'eau]")
ax.set_title("Transpirations cumulées (filtrées)")
ax.set_xticks(days, labels=df.index.strftime('%d-%m-%Y').unique())
ax.tick_params('x', rotation=45)
ax.legend()
ax.grid(linestyle='--', alpha=0.5)
plt.show()

# On ne garde que les journées complètes
df = df[days[1]:days[-1]]

# En 2023, les premiers jours de mesures semblent aberrants
if year == 2023:
    df = df[days[3]:]

days = np.unique(df.index.date)
hours = np.unique(df.index.hour)
            
'''
    Affichage des transpirations cumulées filtrées, en excluant le 1er et
    dernier jour incomplets
'''
fig, ax = plt.subplots()
ax.plot(df['trans_1'], label="Transpiration cumulée plante 1")
ax.plot(df['trans_2'], label="Transpiration cumulée plante 2")
ax.plot(df['trans_3'], label="Transpiration cumulée plante 3")
ax.set_title("Transpiration cumulées (filtrées et coupées)")
ax.set_ylabel("[g d'eau]")
ax.set_xticks(days, labels=df.index.strftime('%d-%m-%Y').unique())
ax.tick_params('x', rotation=45)
ax.legend()
ax.grid(linestyle='--', alpha=0.5)
plt.show()

# Sélection de la plante analysée
col = 'trans_1'

'''
    Affichage de la transpiration journalière cumulée
'''
fig, ax = plt.subplots()
for day in days:
    df_day = df[col][day.strftime('%Y-%m-%d')]
    
    ax.plot(df_day - min(df_day), color='blue')  
     
ax.set_title("Transpirations journalières cumulées")
ax.set_ylabel("[g d'eau]")
ax.set_xticks(days, labels=df.index.strftime('%d-%m-%Y').unique())
ax.tick_params('x', rotation=45)
ax.grid(linestyle='--', alpha=0.5)
plt.show()

'''
    Affichage de la transpiration journalière cumulée normalisée
'''
fig, ax = plt.subplots()
for day in days:
    df_day = df[col][day.strftime('%Y-%m-%d')]
    
    daily_trans = df_day - min(df_day)
    daily_trans /= max(daily_trans)
    daily_trans *= 100
    
    ax.plot(daily_trans, color='blue')  
     
ax.set_title("Transpirations journalières cumulées (normalisées)")
ax.set_ylabel("%")
ax.set_xticks(days, labels=df.index.strftime('%d-%m-%Y').unique())
ax.tick_params('x', rotation=45)
ax.grid(linestyle='--', alpha=0.5)
plt.show()

'''
    Calcul et affichage de la transpiration journalière cumulée normalisée, et sur 24h
'''
mean_daily_trans = 0

fig, ax = plt.subplots()
for i, day in enumerate(days):
    df_day = df[col][day.strftime('%Y-%m-%d')]
    
    daily_trans = df_day - min(df_day)
    daily_trans /= max(daily_trans)
    daily_trans *= 100
    
    # NOTE: this is technically not correct. By using to_numpy(), I'm discarding
    # the time index and summing vectors of data that are not perfectly aligned in
    # time. This is sufficient here, but ideally one would need to resample each
    # vector to given time indices before summing.
    if len(daily_trans) < 144:
        # This is just for that one time in 2024 where the scales skip 2 records,
        # pad the edges with identical values
        mean_daily_trans += np.pad(daily_trans.to_numpy(), 1, mode='edge')
    else:
        mean_daily_trans += daily_trans.to_numpy()
    
    ax.plot(df_day.index - timedelta(days=i), daily_trans,
            color='blue', alpha=0.2)  
     
ax.plot(df[days[0]:days[1]].index, mean_daily_trans/len(days),
        color='blue', linewidth=3)

ax.set_title("Transpirations journalières cumulées (normalisées)")
ax.set_ylabel("%")
ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
ax.tick_params('x', rotation=45)
ax.grid(linestyle='--', alpha=0.5)
plt.show()

'''
    Calcul et affichage de la dérivée de la transpiration cumulée
'''

cols_der = ['der_1', 'der_2', 'der_3']

# Le '1/6' fait référence à l'intervalle de temps séparant les données : 10 minutes = 1/6 d'heure
# Cela permet de donner une unité cohérente au résulat de np.gradient : des g d'eau/heure
df[cols_der] = np.gradient(df[cols_trans], 1/6, axis=0)
# On filtre car le résultat est très bruité et pratiquement illisible
df[cols_der] = df[cols_der].apply(median_filter, size=11)

col = 'der_1'

fig, ax = plt.subplots()
ax.plot(df[col])
ax.set_title("Dérivée de la transpiration cumulée")
ax.set_ylabel("g d'eau/heure")
ax.set_xticks(days, labels=df.index.strftime('%d-%m-%Y').unique())
ax.tick_params('x', rotation=45)
ax.grid(linestyle='--', alpha=0.5)
plt.show()

'''
    Calcul et affichage de la dérovée de transpiration journalière cumulée normalisée, et sur 24h
'''
mean_daily_der = 0

fig, ax = plt.subplots()
for i, day in enumerate(days):
    df_day = df[col][day.strftime('%Y-%m-%d')]
    
    daily_der = df_day - min(df_day)
    daily_der /= max(daily_der)
    daily_der *= 100
    
    # NOTE: this is technically not correct. By using to_numpy(), I'm discarding
    # the time index and summing vectors of data that are not perfectly aligned in
    # time. This is sufficient here, but ideally one would need to resample each
    # vector to given time indices before summing.
    if len(daily_der) < 144:
        # This is just for that one time in 2024 where the scales skip 2 records,
        # pad the edges with identical values
        mean_daily_der += np.pad(daily_der.to_numpy(), 1, mode='edge')
    else:
        mean_daily_der += daily_der.to_numpy()
    
    ax.plot(df_day.index - timedelta(days=i), daily_der,
            color='blue', alpha=0.2)  
     
ax.plot(df[days[0]:days[1]].index, mean_daily_der/len(days),
        color='blue', linewidth=3)

ax.set_title("Dérivées de la transpiration journalière cumulée, normalisées")
ax.set_ylabel("%")
ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
ax.tick_params('x', rotation=45)
ax.grid(linestyle='--', alpha=0.5)
plt.show()

# On pourrait refaire les calculs sur la transpiration moyenne des 3 plants
df['mean_trans'] = df[cols_trans].mean(axis=1)