import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from math import pi
from datetime import timedelta
from scipy.ndimage import median_filter

'''
    Il faut un peu jouer avec le choix de l'encodeur qu'on étudie (variable
    'col' ci-dessous) pour trouver celui qui montre les données les plus interprétables.

    'enc_6' produit les plus jolis graphiques a priori.
'''

year = 2025
col = 'enc_6'

df = pd.read_csv('data/croissance-{year}.csv'.format(year=year), sep=';')

if year == 2025:
    df['time'] = pd.to_datetime(df['time'], format='%Y-%m-%d %H:%M:%S UTC')
    # Conversion d'UTC vers notre fuseau horaire (+1h)
    df['time'] += pd.Timedelta('01:00:00')
else:
    # Backward compatibility
    df['time'] = pd.to_datetime(df['time'], format='%d-%m-%y %H:%M')

df = df.set_index('time')

# Le sens dans lequel l'encodeur tourne n'a pas d'importance
df = abs(df)

# On supprime les données du 5e encodeur (0)
# Aussi valable pour 2023 car les données ne ressemblent pas à grand chose
df = df.drop(columns=['enc_5'])

# On lisse les données
df = df.apply(median_filter, size=51)

days = np.unique(df.index.date)
hours = np.unique(df.index.hour)

# On ne garde que les journées complètes
df = df[days[1]:days[-1]]

days = np.unique(df.index.date)

# On convertit les données enregistrée par les encodeurs en longueur.
# Le diamètre de la poulie est de 2.6 cm -> périmètre = \pi * 2.6 cm.
# Les encodeurs enregistrent chaque 1/80ème de tour de poulie.
df *= 1/80 * (pi * 2.6)

'''
    feuilles est un dictionnaire reprenant pour chaque encodeur une
    liste d'intervalles de temps correspondant à la croissance d'une seule feuille.
    Cela permet d'afficher un intervalle dans lequel la feuille mesurée n'a pas
    été changée, et qui est donc plus facile à interpréter.
'''
if year == 2025:
    feuilles = {
        'enc_1': [
            ("2025-02-01", "2025-02-06"),
            ("2025-02-08", None)
            ],
        'enc_2': [
            ("2025-01-29", "2025-02-02"),
            ("2025-02-05", "2025-02-10"),
            ("2025-02-13", None)
            ],
        'enc_3': [
            ("2025-02-01", "2025-02-06"),
            ("2025-02-08", None)
            ],
        'enc_4': [
            (None, "2025-02-03"),
            ("2025-02-05", "2025-02-11"),
            ("2025-02-13", None)
            ],
        'enc_6': [
            (None, "2025-02-03"),
            ("2025-02-05", "2025-02-11"),
            ("2025-02-13", None)
            ]
        }
else:
    feuilles = {
        'enc_1': [
            ("2023-02-12", None)
            ],
        'enc_2': [
            ("2023-02-09", "2023-02-13"),
            ("2023-02-15", None)
            ],
        'enc_3': [
            ("2023-02-11", None),
            ],
        'enc_4': [
            ("2023-02-16", None)
            ],
        'enc_6': [
            ("2023-02-14", None)
            ]
        }

'''
    Affichage des données brutes
'''
fig, ax = plt.subplots()
ax.plot(df, label=df.columns)
ax.legend()
ax.set_title("Croissance cumulée des feuilles")
ax.set_ylabel("[cm]")
ax.set_xticks(days, labels=df.index.strftime('%d-%m-%Y').unique())
ax.tick_params('x', rotation=45)
ax.grid(linestyle='--', alpha=0.5)
plt.show()

'''
    Affichage de la croissance cumulée journalière
'''
fig, ax = plt.subplots()
for day in days:
    df_day = df[col][day.strftime('%Y-%m-%d')]
    
    ax.plot(df_day - min(df_day), color='blue')  
     
ax.set_title("Croissances journalières cumulées ({enc})".format(enc=col))
ax.set_ylabel("[cm]")
ax.set_xticks(days, labels=df.index.strftime('%d-%m-%Y').unique())
ax.tick_params('x', rotation=45)
ax.grid(linestyle='--', alpha=0.5)
plt.show()

for limits in feuilles[col]:
    start, end = limits
    
    if start is None:
        df_f = df[col][:end]
    elif end is None:
        df_f = df[col][start:]
    else:
        df_f = df[col][start:end]
           
    days = np.unique(df_f.index.date)
        
    fig, ax = plt.subplots()
    for day in days:
        df_day = df_f[day.strftime('%Y-%m-%d')]
        
        ax.plot(df_day - min(df_day), color='blue')  
         
    ax.set_title("Croissances journalières cumulées ({enc})".format(enc=col))
    ax.set_ylabel("[cm]")
    ax.set_xticks(days, labels=df_f.index.strftime('%d-%m-%Y').unique())
    ax.tick_params('x', rotation=45)
    ax.grid(linestyle='--', alpha=0.5)
    plt.show()
    
'''
    On recommence en normalisant les courbes et en les affichant sur une période
    de 24h.
'''
for limits in feuilles[col]:
    start, end = limits
    
    if start is None:
        df_f = df[col][:end]
    elif end is None:
        df_f = df[col][start:]
    else:
        df_f = df[col][start:end]
           
    days = np.unique(df_f.index.date)
        
    mean_normalized = 0
    
    fig, ax = plt.subplots()
    for i, day in enumerate(days):
        df_day = df_f[day.strftime('%Y-%m-%d')]
        
        norm_df_day = df_day - min(df_day)
        norm_df_day /= max(norm_df_day) 
        norm_df_day *= 100
        
        # NOTE: this is technically not correct. By using to_numpy(), I'm discarding
        # the time index and summing vectors of data that are not perfectly aligned in
        # time. This is sufficient here, but ideally one would need to resample each
        # vector to given time indices before summing.7
       
        # Backward compatibility
        if year == 2025:
            size = 480  # En 2025 : sampling toutes les 3 minutes -> 480 samples/jour
        else:
            size = 144  # En 2023 : sampling toutes les 10 minutes -> 144 samples/jour
    
        if len(norm_df_day) < size:
            # Pad the end when the encoder skipped one or more beats
            mean_normalized += np.append(norm_df_day.to_numpy(), [100]*(size - len(norm_df_day)))
        else:
            mean_normalized += norm_df_day.to_numpy()
        
        ax.plot(df_day.index - timedelta(days=i), norm_df_day,
                color='blue', alpha=0.2)  
    
    # See NOTE above, also applies here
    ax.plot(pd.date_range(start=days[0], end=days[1], periods=size),
            mean_normalized/len(days),
            color='blue', linewidth=3)
    
    ax.set_title("Croissances journalières cumulées normalisées ({enc})".format(enc=col))
    ax.set_ylabel("%")
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.tick_params('x', rotation=45)
    ax.grid(linestyle='--', alpha=0.5)
    plt.show()