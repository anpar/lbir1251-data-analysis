import pandas as pd
import numpy as np

from utils import plot_cols, daily_reset, daily_normalize, plot_series, plot_col_daily, plot_cols_separate

from math import pi

from scipy.ndimage import median_filter

YEAR = 2025

df = pd.read_csv('data/croissance-{y}.csv'.format(y=YEAR), sep=';')

if YEAR == 2026:
    df['time'] = pd.to_datetime(df['time'], format='%d-%m-%Y %H:%M:%S')
elif YEAR == 2025:
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
if YEAR == 2026:
    feuilles = {
        # PLANTE 1
        'enc_1': [
            ("27-01-2026", "02-02-2026 09:15", "Plante 1", "rang 3"),
            ("02-02-2026 09:20", None, "Plante 1", "rang 5"),           
            ],
        'enc_2': [
            ("27-01-2026", "28-01-2026 16:05", "Plante 1", "rang 2"),
            ("28-01-2026 16:10", None, "Plante 1", "rang 4"),
            ],
        # PLANTE 2
        'enc_3': [
            ("27-01-2026", "28-01-2026 16:05", "Plante 2", "rang 2"),
            ("28-01-2026 16:10", None, "Plante 2", "rang 4"),
            ],
        'enc_4': [
            ("27-01-2026", "02-02-2026 09:15", "Plante 2", "rang 3"),
            ("02-02-2026 09:20", None, "Plante 2", "rang 5"),
            ],
        # PLANTE 3
        'enc_6': [
            ("27-01-2026", "02-02-2026 09:15", "Plante 3", "rang 3"),
            ("02-02-2026 09:20", None, "Plante 3", "rang 5")
            ]
        }
elif YEAR == 2025:
    feuilles = {
        'enc_1': [
            ("2025-02-01", "2025-02-06", "Plante 1", "rang 3"),
            ("2025-02-08", None, "Plante 1", "rang 5")
            ],
        'enc_2': [
            ("2025-01-29", "2025-02-02", "Plante 1", "rang 2"),
            ("2025-02-05", "2025-02-10", "Plante 1", "rang 4"),
            ("2025-02-13", None, "Plante 1", "rang 6")
            ],
        'enc_3': [
            ("2025-02-01", "2025-02-06",  "Plante 2", "rang 3"),
            ("2025-02-08", None,  "Plante 2", "rang 5")
            ],
        'enc_4': [
            (None, "2025-02-03",  "Plante 2", "rang 2"),
            ("2025-02-05", "2025-02-11", "Plante 2", "rang 4"),
            ("2025-02-13", None,  "Plante 2", "rang 6")
            ],
        'enc_6': [
            (None, "2025-02-03",  "Plante 3", "rang 2"),
            ("2025-02-05", "2025-02-11", "Plante 3", "rang 4"),
            ("2025-02-13", None, "Plante 3", "rang 6")
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
encs = ['enc_1', 'enc_2', 'enc_3', 'enc_4', 'enc_6']

plot_cols(df,
          labels=['Encodeur 1 (plante 1)', 'Encodeur 2 (plante 1)',
                  'Encodeur 3 (plante 2)', 'Encodeur 4 (plante 2)',
                  'Encodeur 6 (plante 3)'],
          title="Elongation cumulées des feuilles",
          ylabel="[cm]")

'''
    Affichage de la croissance cumulée journalière
'''
croissance_journalière = pd.DataFrame()
croissance_journalière[encs] = df[encs].apply(daily_reset)

plot_cols_separate(croissance_journalière, "Croissances journalières cumulées", "[cm]")

for col in encs:
    for limits in feuilles[col]:
        start, end, plante, rang = limits
        
        if start is None:
            df_f = croissance_journalière[col][:end]
        elif end is None:
            df_f = croissance_journalière[col][start:]
        else:
            df_f = croissance_journalière[col][start:end]

        days = np.unique(df_f.index.date)
        
        plot_series(df_f,
                    "Croissances cumulées journalières - {p}, {r} ({e})".format(p=plante, r=rang, e=col),
                    "[cm]")
    
'''
    On recommence en normalisant les courbes et en les affichant sur une période
    de 24h.
'''
croissance_journalière_norm = pd.DataFrame()
croissance_journalière_norm[encs] = croissance_journalière.apply(daily_normalize)

for col in encs:
    for limits in feuilles[col]:
        start, end, plante, rang = limits
        
        if start is None:
            df_f = croissance_journalière_norm[:end]
        elif end is None:
            df_f = croissance_journalière_norm[start:]
        else:
            df_f = croissance_journalière_norm[start:end]
        
        plot_col_daily(df_f, col, 3, "Dynamique de croissance moyenne - {p}, {r} ({e})".format(p=plante, r=rang, e=col))  
