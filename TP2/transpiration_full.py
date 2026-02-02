import pandas as pd
import numpy as np

from utils import daily_reset, daily_normalize, plot_cols, plot_cols_separate, plot_col_daily

from scipy.ndimage import median_filter

'''
    Sur les 3 dernières années (2023 à 2025), l'année 2024 contient les données
    les plus propres, qui produisent les graphes les plus intéressant à interpréter.
    
    Les données des années 2023 et 2025 sont plus bruitées, mais il est toujours
    possible d'en dire quelque chose.
'''

YEAR = 2024

data = pd.read_csv('data/balances-{y}.csv'.format(y=YEAR), sep=';')

# Backward compatibility
if YEAR >= 2025:
    data['time'] = pd.to_datetime(data['time'], unit='d', origin="1899-12-30")
else:
    data['time'] = pd.to_datetime(data['time'], format='%d-%m-%y %H:%M')

# Use time as an index for the DataFrame
data = data.set_index('time')

# Change the sign of scales readings (poids des pots -> g d'eau évapotranspirés)
data *= -1

# Correction manuelle pour le saut inopiné des balances en 2024
if YEAR == 2024:
    data.loc["2024-02-07 16:15:00":, 'plant_1'] -= (66.65 - 36.14)
    data.loc["2024-02-07 16:15:00":, 'plant_2'] -= (57.72 - 34.46)
    data.loc["2024-02-07 16:15:00":, 'plant_3'] -= (39.74 - 23.99)
    data.loc["2024-02-07 16:15:00":, 'tem_1']   -= (25.62 - 13.34)
    data.loc["2024-02-07 16:15:00":, 'tem_2']   -= (30.1 - 15.77)
    data.loc["2024-02-07 16:15:00":, 'tem_3']   -= 0

# Calcul de l'évaporation moyenne
data['evap'] = data[['tem_1', 'tem_2', 'tem_3']].mean(axis=1)

data = data.drop(columns=['tem_1', 'tem_2', 'tem_3'])

# Affichage de l'évpotranspiration cumulée
plot_cols(data, 
          labels=['Plante 1', 'Plante 2', 'Plante 3', 'Moyenne pots témoins'],
          colors=['C0', 'C1', 'C2', 'gray'],
          linestyles=['-', '-', '-', '--'],
          title="Evapotranspirations cumulées",
          ylabel="[g d'eau]")

# Calcul de la transpiration en soustrayant l'évaporation de l'évapotranspiration
trans_cumulée = pd.DataFrame()
trans_cumulée[['Plante 1', 'Plante 2', 'Plante 3']] = data[['plant_1', 'plant_2', 'plant_3']].sub(data['evap'], axis="rows")

data = data.drop(columns=['plant_1', 'plant_2', 'plant_3'])

# Affichage des données brutes
plot_cols(trans_cumulée, 
          labels=['Plante 1', 'Plante 2', 'Plante 3'],
          title="Transpirations cumulées",
          ylabel="[g d'eau]")

# On filtre les donnes pour réduire le bruit et supprimer les glitches
trans_cumulée = trans_cumulée.apply(median_filter, size=21)

# Affichage des transpirations cumulées après filtration pour réduire
# le bruit et les glitches
plot_cols(trans_cumulée,
          labels=['Plante 1', 'Plante 2', 'Plante 3'],
          title="Transpirations cumulées (données filtrées)",
          ylabel="[g d'eau]")

days = np.unique(data.index.date)

# On ne garde que les journées complètes
trans_cumulée = trans_cumulée[days[1]:days[-1]]

# En 2023, les premiers jours de mesures semblent aberrants
if YEAR == 2023:
    data = data[days[3]:]

days = np.unique(data.index.date)
            
# Affichage des transpirations cumulées filtrées, en excluant le 1er et
# dernier jour incomplets
plot_cols(trans_cumulée,
          labels=['Plante 1', 'Plante 2', 'Plante 3'],
          title="Transpirations cumulées (données filtrées, jours complets)",
          ylabel="[g d'eau]")

trans_journalière = pd.DataFrame()
trans_journalière[['Plante 1', 'Plante 2', 'Plante 3']] = trans_cumulée.apply(daily_reset)

# Affichage de la transpiration journalière cumulée
plot_cols_separate(trans_journalière, title="Transpiration journalière", ylabel="[g d'eau]")

trans_journalière_norm = pd.DataFrame()
trans_journalière_norm[['Plante 1', 'Plante 2', 'Plante 3']] = trans_journalière.apply(daily_normalize)

# Affichage de la transpiration journalière cumulée normalisée
# plot_cols_separate(trans_journalière_norm, title="Transpiration journalière (normalisée)", ylabel="[g d'eau]")

for col in trans_journalière_norm.columns.to_list():
    plot_col_daily(trans_journalière_norm,
                   col,
                   10,
                   "Dynamique de la transpiration journalière - {p})".format(p=col))


trans_vitesse = pd.DataFrame()
# Le '1/6' fait référence à l'intervalle de temps séparant les données : 10 minutes = 1/6 d'heure
# Cela permet de donner une unité cohérente au résulat de np.gradient : des g d'eau/heure
trans_vitesse[['Plante 1', 'Plante 2', 'Plante 3']] = trans_cumulée.apply(np.gradient, args=(1/6,))

# On filtre car le résultat est très bruité et pratiquement illisible
trans_vitesse = trans_vitesse.apply(median_filter, size=11)

# Affichage de la vitesse de transpiration
plot_cols_separate(trans_vitesse, title="Dérivée de la transpiration cumulée", ylabel="[g d'eau/heure]")

trans_vitesse_norm = trans_vitesse.apply(daily_normalize)
#plot_cols_separate(trans_vitesse_norm, title="Dérivée de la transpiration cumulée, normalisée", ylabel="%")
    
# Calcul et affichage de la transpiration journalière cumulée normalisée, et sur 24h
for col in trans_vitesse_norm.columns.to_list():
    plot_col_daily(trans_vitesse_norm,
                   col,
                   10,
                   "Dynamique de la vitesse de transpiration - {p})".format(p=col))
