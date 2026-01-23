import pandas as pd
import numpy as np

import matplotlib.pyplot as plt

year = 2025

# About encoding='latin-1' : https://stackoverflow.com/questions/5552555/unicodedecodeerror-invalid-continuation-byte#31492722
df = pd.read_csv('data/porometre-{year}.csv'.format(year=year), sep=';',
                 encoding='latin-1')

df['time'] = df['date'] + ' ' + df['heure']
df['time'] = pd.to_datetime(df['time'], format='%d-%m-%y %H:%M')                            

df = df.drop(columns=['date', 'heure'])

# Groupping by and describing the stomatal conductance
df.groupby('état_f')['cond'].describe()

df.groupby('pos_f')['cond'].describe()

df.groupby('face_f')['cond'].describe()

df.groupby('pos_f')['cond'].describe()

# Scatter plot stomatal conductance vs. PAR
df.plot.scatter(x='PAR', y='cond')

df.boxplot(column='cond', by='état_f')

df.boxplot(column='cond', by='pos_f')

df.boxplot(column='cond', by='rang_f')

df.boxplot(column='cond', by='face_f')

df['heure'] = df['time'].dt.hour

df.groupby('heure')['cond'].describe()

df.boxplot(column='cond', by='heure')

df.boxplot(column='PAR', by='heure')