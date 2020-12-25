#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 16 21:59:07 2020

@author: root
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import matplotlib as mpl
from matplotlib import rc
rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
## for Palatino and other serif fonts use:
#rc('font',**{'family':'serif','serif':['Palatino']})
rc('text', usetex=False)



# real traffic on Travessera de Gracia
traffic = pd.read_csv('/root/Desktop/MSWIM/Revista/TrafficPgSanJoan.csv')
# taz trips on Travessera de Gracia
taz_df = pd.read_csv('/root/Desktop/MSWIM/Revista/detector/Hospitalet_PgSanJoan_detector_0.csv')
# random trips on Travessera de Gracia
random_df = pd.read_csv('/root/Desktop/MSWIM/Revista/sim_files/RandomTrips/DETECTOR/detector.csv')


# SUMO Outputs
random_traffic_metrics_df = pd.read_csv('/root/Desktop/MSWIM/Revista/sim_files/RandomTrips/PARSED/data.csv')
taz_traffic_metrics_df =  pd.read_csv('/root/Desktop/MSWIM/Revista/parsed/data.csv')


# Prepare dataframes
taz_df['Hour'] = range(24)
random_df['Hour'] = range(24)

# Merge csv files
parsed_df = taz_df.merge(random_df, on='Hour', suffixes=('_taz', '_random')).merge(traffic, on='Hour')

# Filter traffic columns to plot
traffic_df = parsed_df.filter(['Hour','interval_vehicleSum_taz','interval_vehicleSum_random', 'Total'])
traffic_df.rename(columns={'interval_vehicleSum_taz':'od2trips','interval_vehicleSum_random':'random','Total':'real'},inplace=True)

# sort traffic df
df = pd.melt(traffic_df, id_vars=['Hour'], value_vars=['od2trips', 'random', 'real'], 
             var_name='Routing',
             value_name='Traffic')



def traffic():
    # box plot
    box_plt = traffic_df.filter(['real', 'od2trips','random'])
    box_plt.plot.box(figsize=(8,4))
    plt.title('Number of vehicles (during a working day)')     
    
    # pairs relationship 
    plt.figure()
    h = sns.pairplot(df, hue='Routing', markers='+')
    
    
    # plot traffic intensity
    fig, ax = plt.subplots(figsize=(8,6))
    cols = ['od2trips', 'random', 'real']
    marker=['o','x','+']
    for i, col in enumerate(cols):
        traffic_df.plot(kind='line',x='Hour',y=col, marker=marker[i], ax=ax)
    plt.ylabel('# of vehicles')
    plt.title('Traffic intensity')
    plt.xticks(np.arange(min(traffic_df['Hour']), max(traffic_df['Hour'])+1, 2.0))
    plt.grid(True)


def traffic_metrics(df, tittle):
    
    # Plot origin destination (longitud latitude)
    # receives df and title
    mpl.style.use('default')
    df = df.filter(['ini_x_pos', 'ini_y_pos','end_x_pos', 'end_y_pos' ])
    
    fig, ax = plt.subplots(figsize=(10,8))
    df.plot.scatter(x='ini_x_pos',y='ini_y_pos', c='tab:orange', label='Origen', ax=ax)
    df.plot.scatter(x='end_x_pos',y='end_y_pos', c='tab:blue', label='Destination', ax=ax)
    plt.ylabel('Logitud')
    plt.xlabel('Latitud')
    plt.title(f'{tittle}')
    plt.grid(True)    
    ax.legend()
    
    
    
 
def fundamental_metrics():   
    # Plot  mean distance/triptime/speed
    # receives df and title
    
    # filter columns
    cols = ['lane_count','avrg_speed','tripinfo_duration','tripinfo_routeLength','tripinfo_timeLoss','tripinfo_waitingCount','tripinfo_waitingTime']
    
    random = random_traffic_metrics_df.filter(cols)
    taz = taz_traffic_metrics_df.filter(cols)
  
  
    fig, axs = plt.subplots(3,3, figsize=(10,8), sharex=True)
    i=0
    for x in range(3):
        for y in range(3):    
            if i < len(cols):
                metric = cols[i]
                d_dic = {'Random':random[f'{metric}'],'Od2trips':taz[f'{metric}'] }
                df = pd.DataFrame(d_dic)
                df.mean().plot(kind='bar', subplots=True, ax=axs[x,y])
                axs[x,y].set_title(f'Avrg. {metric}')
                i+=1
    plt.subplots_adjust(top=0.92, bottom=0.08, left=0.10, right=0.95, hspace=0.25,
                    wspace=0.35)
   
    
    
def fundamental_metrics_hist():   
    # Plot  mean distance/triptime/speed
    # receives df and title
    
    # filter columns
    cols = ['lane_count','avrg_speed','tripinfo_duration','tripinfo_routeLength','tripinfo_timeLoss','tripinfo_waitingCount','tripinfo_waitingTime']
    
    random = random_traffic_metrics_df.filter(cols)
    taz = taz_traffic_metrics_df.filter(cols)
  
  
    fig, axs = plt.subplots(3,3, figsize=(10,8), sharex=True)
    i=0
    for x in range(3):
        for y in range(3):    
            if i < len(cols):
                metric = cols[i]
                d_dic = {'Random':random[f'{metric}'],'Od2trips':taz[f'{metric}'] }
                df = pd.DataFrame(d_dic)
                df.plot.hist(ax=axs[x,y])
                axs[x,y].set_title(f'Avrg. {metric}')
                i+=1
    plt.subplots_adjust(top=0.92, bottom=0.08, left=0.10, right=0.95, hspace=0.25,
                    wspace=0.35)    
    
     
traffic() 
traffic_metrics(taz_traffic_metrics_df, 'od2trips')
traffic_metrics(random_traffic_metrics_df, 'Random')

fundamental_metrics()
fundamental_metrics_hist()
plt.show()

   
