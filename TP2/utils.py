import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import pandas as pd

import numpy as np

from datetime import timedelta

'''
    Transforme une donnée cumulée sur plusieurs jours (e.g., transpiration
    cumulée) en une donnée cumulée journalière : chaque journée redémarre à 0.
'''
def daily_reset(col):
    df = pd.Series(index=col.index)
    
    days = np.unique(col.index.date)
    
    for day in days:
        idx = day.strftime('%Y-%m-%d')
        
        df.loc[idx] = col[idx] - min(col[idx])
        
    return df
        
'''
    Normalise une donnée cumulée sur une journée (e.g., transpiration journalière
    cumulée) en une donnée cumulée normalisée. L'unité devient "% du total journalier".
'''
def daily_normalize(col):
    df = pd.Series(index=col.index)
    
    days = np.unique(col.index.date)
    
    for day in days:
        idx = day.strftime('%Y-%m-%d')
        
        df.loc[idx] = col[idx]/max(col[idx]) * 100
        
    return df

def plot_series(s, title, ylabel):
    fig, ax = plt.subplots(figsize=(8,4))

    days = np.unique(s.index.date)
    
    for day in days:
        ax.plot(s[day.strftime('%Y-%m-%d')], color='blue')
    
    ax.set_title(title, pad=15)
    ax.set_ylabel(ylabel)
    
    ax.spines[["top", "right"]].set_visible(False)

    print(s)
    print(s.max())
    ax.set_ylim(bottom=0, top=s.max())

    ax.set_xlim(left=s.index.min(), right=s.index.max())
    ax.set_xticks(np.unique(s.index.date), labels=s.index.strftime('%d-%m').unique())

    ax.tick_params(axis='both', which='major', labelsize=9)

    ax.grid(linestyle='--', alpha=0.5)

    plt.show()

def plot_cols_separate(df, title, ylabel):
    for col in df.columns.to_list():
        plot_series(df[col],
                    title="{t} - {c}".format(t=title, c=col),
                    ylabel=ylabel)

def plot_cols(df, title, ylabel, labels=None, colors=None, linestyles=None, bottom=0):
    cols = df.columns.tolist()
    
    if labels is None:
        labels = cols
    
    if colors is None:
        colors = ['C' + str(i) for i in range(len(cols))]
        
    if linestyles is None:
        linestyles = ['-'] * len(cols)
    
    fig, ax = plt.subplots(figsize=(8,4))
    
    for i, col in enumerate(cols):
        ax.plot(df[col],
                label=labels[i],
                color=colors[i],
                linestyle=linestyles[i])
    
    ax.set_title(title, pad=15)
    ax.set_ylabel(ylabel)
    
    ax.spines[["top", "right"]].set_visible(False)

    ax.set_ylim(bottom=bottom, top=df.to_numpy().max())

    ax.set_xlim(left=df.index.min(), right=df.index.max())
    ax.set_xticks(np.unique(df.index.date), labels=df.index.strftime('%d-%m').unique())

    ax.tick_params(axis='both', which='major', labelsize=6)

    if labels[0] is not None:
        ax.legend(bbox_to_anchor=(1.02, 0.5), loc='center left', fontsize=10, frameon=False)

    ax.grid(linestyle='--', alpha=0.5)

    plt.show()

def plot_col_daily(df, col, sampling_period, title):
    days = np.unique(df.index.date)
    
    # Nombre d'échantillon dans une journée
    N = int(24*60/sampling_period)
    
    fig, ax = plt.subplots(figsize=(8,4))
    
    average = 0
    for i, day in enumerate(days):
        df_day = df[col][day.strftime('%Y-%m-%d')]
        
        ax.plot(df_day.index - timedelta(days=i), df_day, color='blue', alpha=0.2)  
        
        if len(df_day) < N:
            print("Day: {d}, sample size is {Nr} (should be {N}).".format(d=day.strftime('%Y-%m-%d'),
                                                                         Nr=len(df_day),
                                                                         N=N))
            print("Padding the edges.")
            
            pad_length = (N - len(df_day))

            if pad_length % 2 == 0:
                pad = (pad_length//2, pad_length//2)
            else:
                pad = (0, pad_length)
            
            average += np.pad(df_day.to_numpy(), pad, mode='edge')
        else:
            average += df_day.to_numpy()

    ax.plot(pd.date_range(start=days[0], end=days[0] + timedelta(days=1), periods=N),
            average/len(days),
            color='blue', linewidth=3, label="Moyenne")
    
    ax.set_title(title)
    ax.set_ylabel("%")

    ax.spines[["top", "right"]].set_visible(False)

    ax.set_ylim(bottom=0, top=df[col].to_numpy().max())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.tick_params(axis='both', which='major', labelsize=9)

    ax.legend(fontsize=10, frameon=False)

    ax.grid(linestyle='--', alpha=0.5)
    
    plt.show()
