import pandas as pd
import numpy as np

from utils import plot_cols, daily_reset, daily_normalize, plot_series, plot_col_daily, plot_cols_separate

from math import pi

from scipy.ndimage import median_filter

YEAR = 2026

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

# On supprime les données du 5e encodeur (0)
# Aussi valable pour 2023 car les données ne ressemblent pas à grand chose
df = df.drop(columns=['enc_5'])

df.plot()

if YEAR == 2026:
    # abs() en dessous ne fonctionne bien que si les données des encodeurs
    # sont tout le temps +ve ou tout le temps -ve, en remettant des poids, on
    # a fait un bugué un encodeur de ce point de vue là. On corrige pour tout
    # laisser en -ve
    df.loc["2026-02-06 16:42:08":, 'enc_1'] -= 100

# Le sens dans lequel l'encodeur tourne n'a pas d'importance
df = abs(df)

# On convertit les données enregistrée par les encodeurs en longueur.
# Le diamètre de la poulie est de 2.6 cm -> périmètre = \pi * 2.6 cm.
# Les encodeurs enregistrent chaque 1/80ème de tour de poulie.
df *= 1/80 * (pi * 2.6)

plot_cols(df,
          labels=['Encodeur 1 (plante 1)', 'Encodeur 2 (plante 1)',
                  'Encodeur 3 (plante 2)', 'Encodeur 4 (plante 2)',
                  'Encodeur 6 (plante 3)'],
          title="Elongation cumulées des feuilles (données brutes)",
          ylabel="[cm]")

if YEAR == 2026:
    # L'encodeur 2 sample patiner à partir de 2026-02-03 01:00:04 alors qu'il
    # suivait assez fidèlement l'encodeur 3 (légèrement au-dessus de lui).
    # D'ailleurs, on voit qu'après le saut causé par la pince qui lâche
    df.loc["2026-02-03 01:00:04":"2026-02-04 09:34:06", 'enc_2'] = df.loc["2026-02-03 01:00:04":"2026-02-04 09:34:06", 'enc_3'] - 1
    
    # On corrige le saut de la poulie causée par la pince qui lâche
    df.loc["2026-02-04 09:35:06":, 'enc_2'] += 45.4563 - 7.04502
    
    df.loc["2026-02-06 16:42:08":, 'enc_2'] += 52.3992 - 48.8257

plot_cols(df,
          labels=['Encodeur 1 (plante 1)', 'Encodeur 2 (plante 1)',
                  'Encodeur 3 (plante 2)', 'Encodeur 4 (plante 2)',
                  'Encodeur 6 (plante 3)'],
          title="Elongation cumulées des feuilles (données corrigées)",
          ylabel="[cm]")

# On lisse les données
df = df.apply(median_filter, size=51)

plot_cols(df,
          labels=['Encodeur 1 (plante 1)', 'Encodeur 2 (plante 1)',
                  'Encodeur 3 (plante 2)', 'Encodeur 4 (plante 2)',
                  'Encodeur 6 (plante 3)'],
          title="Elongation cumulées des feuilles (données filtrées)",
          ylabel="[cm]")

# On ne garde que les journées complètes
days = np.unique(df.index.date)
df = df[days[1]:days[-1]]

'''
    feuilles est un dictionnaire reprenant pour chaque encodeur une
    liste d'intervalles de temps correspondant à la croissance d'une seule feuille.
    Cela permet d'afficher un intervalle dans lequel la feuille mesurée n'a pas
    été changée, et qui est donc plus facile à interpréter.
'''
if YEAR == 2026:
    feuilles = {
        # PLANTE 1
        # NOTE: on ne garde que les journées complètes, les vraies dates de changement
        # sont indiquées en commentaire à droite
        'enc_1': [
            # La poulie a patiné le 01-02, on ne garde que jusqu'au 31-01
            ("2026-01-28", "2026-01-31", "Plante 1", "rang 3"), # 02-02-2026 09:15
            ("2026-02-03", "2026-02-05", "Plante 1", "rang 5"),
            # Bizarrerie le 07/02, on commence au 08
            ("2026-02-07", "2026-02-12", "Plante 1", "rang 6") 
            ],
        'enc_2': [
            #("2026-01-27", "2026-01-28 16:05", "Plante 1", "rang 2"),
            ("2026-01-29", "2026-02-07", "Plante 1", "rang 4"), # 2026-01-28 16:10
            #("2026-02-14", None, "Plante 2", "rang 7")
            ],
        # PLANTE 2
        'enc_3': [
            #("2026-01-27", "2026-01-28 16:05", "Plante 2", "rang 2"),
            # Bug le 05-02, on ne garde que jusqu'au 04-02
            ("2026-01-29", "2026-02-04", "Plante 2", "rang 4"), # 2026-01-28 16:10
            ("2026-02-07", "2026-02-12", "Plante 2", "rang 6")
            ],
        'enc_4': [
            ("2026-01-27", "2026-02-01", "Plante 2", "rang 3"), # 2026-02-02 09:15
            ("2026-02-03", "2026-02-12", "Plante 2", "rang 5"), # 2026-02-02 09:20
            ],
        # PLANTE 3
        'enc_6': [
            # bug le 01-02, on ne garde que jusqu'au 31-01
            ("2026-01-27", "2026-01-31", "Plante 3", "rang 3"), # 2026-02-02 09:15
            ("2026-02-03", "2026-02-12", "Plante 3", "rang 5") # 2026-02-02 09:20
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
            ("2023-02-12", None, "Plante 1", "rang ?")
            ],
        'enc_2': [
            ("2023-02-09", "2023-02-13", "Plante 1", "rang ?"),
            ("2023-02-15", None, "Plante 1", "rang ?")
            ],
        'enc_3': [
            ("2023-02-11", None, "Plant 2", "rang ?"),
            ],
        'enc_4': [
            ("2023-02-16", None, "Plant 2", "rang ?")
            ],
        'enc_6': [
            ("2023-02-14", None, "Plant 3", "rang ?")
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
          title="Elongation cumulées des feuilles (journées complètes)",
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
        
        if YEAR == 2026:
            sampling_period = 1
        elif YEAR == 2023:
            sampling_period = 10
        else:
            sampling_period = 3
        
        plot_col_daily(df_f, col, sampling_period,
                       "Dynamique de croissance moyenne - {p}, {r} ({e})".format(p=plante, r=rang, e=col))  
