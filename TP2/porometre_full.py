import pandas as pd

from scipy.stats import linregress

import matplotlib.pyplot as plt

import seaborn as sns

year = 2025

# About encoding='latin-1' : https://stackoverflow.com/questions/5552555/unicodedecodeerror-invalid-continuation-byte#31492722
df = pd.read_csv('data/porometre-{year}.csv'.format(year=year), sep=';',
                 encoding='latin-1')

df['time'] = df['date'] + ' ' + df['heure']
df['time'] = pd.to_datetime(df['time'], format='%d-%m-%y %H:%M')                            

df = df.drop(columns=['date', 'heure'])

'''
    Nuage de points : conductance stomatique vs. PAR + régression linéaire
    
    Note, il est aussi possible d'utiliser 
    ax = df.plot.scatter(x='PAR', y='cond')
'''
fig, ax = plt.subplots()

ax.plot(df['PAR'], df['cond'], 'o', label="Données mesurées")

# Régression linéaire avec scipy.stats.linregress
lreg = linregress(df['PAR'], df['cond'], nan_policy='omit')

ax.plot(df['PAR'], lreg.intercept + lreg.slope*df['PAR'], 'r', label="Régression linéaire")
ax.text(50, 500, "$r_{xy} = $" + "{0:.2f} (Pearson)".format(lreg.rvalue))

ax.set_title("Conductance stomatique vs. PAR")
ax.set_ylabel("mmol/m²/s")
ax.set_xlabel("µmol/m²/s")
ax.legend()
ax.grid(linestyle='--', alpha=0.5)
plt.show()

'''
    Conductance stomatique en fonction du rang de la feuille
'''
data = df[df['time'].between('2025-02-18', '2025-02-21')]

print("\nConductance stomatique vs. rang de la feuille".upper())
print(data.groupby('rang_f')['cond'].describe())

ax = sns.boxplot(data=data,
                 x='rang_f', y='cond',
                 order=['{0}-{1}'.format(i, i+1) for i in range(1, 19, 2)])
ax = sns.stripplot(data=data,
                   x='rang_f', y='cond', size=4)

ax.set_title("Conductance stomatique vs. rang de la feuille")
ax.set_ylabel("mmol/m²/s")
ax.set_xlabel("µmol/m²/s")
ax.grid(linestyle='--', alpha=0.5)

plt.show()

'''
    Conductance stomatique en fonction de l'heure
'''
df['heure'] = df['time'].dt.hour

print("\nConductance stomatique vs. heure".upper())
print(df.groupby('heure')['cond'].describe())

ax = sns.boxplot(data=df, x='heure', y='cond')
ax = sns.stripplot(data=df, x='heure', y='cond', size=4)

ax.set_title("Conductance stomatique vs. heure")
ax.set_ylabel("mmol/m²/s")
ax.set_xlabel("Heure")
ax.grid(linestyle='--', alpha=0.5)

plt.show()

'''
    PAR en fonction de l'heure
'''
print("\nPAR vs. heure".upper())
print(df.groupby('heure')['PAR'].describe())

ax = sns.boxplot(data=df, x='heure', y='PAR')
ax = sns.stripplot(data=df, x='heure', y='PAR', size=4)

ax.set_title("PAR vs. heure")
ax.set_ylabel("µmol/m²/s")
ax.set_xlabel("Heure")
ax.grid(linestyle='--', alpha=0.5)

plt.show()

'''
    Conductance stomatique vs. face de la feuille
'''
print("\nConductance stomatique vs. face de la feuille".upper())
print(df.groupby('face_f')['cond'].describe())

ax = sns.boxplot(data=df, x='face_f', y='cond')
ax = sns.stripplot(data=df, x='face_f', y='cond', size=4)

ax.set_title("Conductance stomatique vs. face de la feuille")
ax.set_ylabel("mmol/m²/s")
ax.set_xlabel("Face")
ax.grid(linestyle='--', alpha=0.5)

plt.show()

'''
    Conductance stomatique vs. face de la feuille en fonction de l'heure
'''

ax = sns.boxplot(data=df, x='heure', y='cond', hue='face_f')
#ax = sns.stripplot(data=df, x='heure', y='cond', hue='face_f')

ax.set_title("Conductance stomatique vs. heure et face de la feuille")
ax.set_ylabel("mmol/m²/s")
ax.set_xlabel("Heure")
ax.grid(linestyle='--', alpha=0.5)

plt.show()

'''
    Conductance stomatique vs. position sur la feuille
'''

ax = sns.boxplot(data=df, x='pos_f', y='cond')
ax = sns.stripplot(data=df, x='pos_f', y='cond')

ax.set_title("Conductance stomatique vs. heure et face de la feuille")
ax.set_ylabel("mmol/m²/s")
ax.set_xlabel("Heure")
ax.grid(linestyle='--', alpha=0.5)

plt.show()


'''
    Conductance stomatique vs. position sur la feuille
'''

ax = sns.boxplot(data=df, x='état_f', y='cond', hue="face_f")
#ax = sns.stripplot(data=df, x='pos_f', y='cond')

ax.set_title("Conductance stomatique vs. face et état de la feuille")
ax.set_ylabel("mmol/m²/s")
ax.set_xlabel("Etat de la feuille")
ax.grid(linestyle='--', alpha=0.5)

plt.show()


