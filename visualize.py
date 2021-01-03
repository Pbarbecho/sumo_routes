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
import matplotlib.colors as mcolors
import os


rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
## for Palatino and other serif fonts use:
#rc('font',**{'family':'serif','serif':['Palatino']})
rc('text', usetex=False)

output_dir = '/root/Desktop/MSWIM/Revista/sim_files'

# real traffic on Travessera de Gracia
traffic = pd.read_csv('/root/Desktop/MSWIM/Revista/TrafficPgSanJoan.csv')



origin = 'Hospitalet'
destination = 'SanAdria'
#################################### Reroute 0 ####################################
# taz ma rr=0 
taz_ma_df_0 = pd.read_csv('/root/Desktop/MSWIM/Revista/sim_files/Taz/ma/0_0/detector/detector.csv')
summary_taz_ma_df_0 = pd.read_csv(f"/root/Desktop/MSWIM/Revista/sim_files/Taz/ma/0_0/xmltocsv/{origin}_{destination}_summary_0.csv")

# taz dua rr=0 
taz_dua_df_0 = pd.read_csv('/root/Desktop/MSWIM/Revista/sim_files/Taz/dua/0_0/detector/detector.csv')
summary_taz_dua_df_0 = pd.read_csv(f"/root/Desktop/MSWIM/Revista/sim_files/Taz/dua/0_0/xmltocsv/{origin}_{destination}_summary_0.csv")

# random rr=0
random_df_0 = pd.read_csv('/root/Desktop/MSWIM/Revista/sim_files/RandomTrips/0_0/detector/detector.csv')
summary_random_df_0 = pd.read_csv(f"/root/Desktop/MSWIM/Revista/sim_files/RandomTrips/0_0/xmltocsv/{origin}_{destination}_summary_0.csv")

# SUMO outputs
random_traffic_metrics_df_0 = pd.read_csv('/root/Desktop/MSWIM/Revista/sim_files/RandomTrips/0_0/parsed/data.csv')
taz_ma_traffic_metrics_df_0 =  pd.read_csv('/root/Desktop/MSWIM/Revista/sim_files/Taz/ma/0_0/parsed/data.csv')
taz_dua_traffic_metrics_df_0 =  pd.read_csv('/root/Desktop/MSWIM/Revista/sim_files/Taz/dua/0_0/parsed/data.csv')
# SUMO summary.shift()
taz_dua_summary_df_0 =  pd.read_csv(f'/root/Desktop/MSWIM/Revista/sim_files/Taz/dua/0_0/xmltocsv/{origin}_{destination}_summary_0.csv')
taz_ma_summary_df_0 =  pd.read_csv(f'/root/Desktop/MSWIM/Revista/sim_files/Taz/ma/0_0/xmltocsv/{origin}_{destination}_summary_0.csv')
random_summary_df_0 =  pd.read_csv(f'/root/Desktop/MSWIM/Revista/sim_files/RandomTrips/0_0/xmltocsv/{origin}_{destination}_summary_0.csv')
###################################################################################

#################################### Reroute 1 ####################################

# taz ma rr=1 
taz_ma_df_1 = pd.read_csv('/root/Desktop/MSWIM/Revista/sim_files/Taz/ma/0_1/detector/detector.csv')
summary_taz_ma_df_1 = pd.read_csv(f"/root/Desktop/MSWIM/Revista/sim_files/Taz/ma/0_1/xmltocsv/{origin}_{destination}_summary_0.csv")

# taz dua rr=1 
taz_dua_df_1 = pd.read_csv('/root/Desktop/MSWIM/Revista/sim_files/Taz/dua/0_1/detector/detector.csv')
summary_taz_dua_df_1 = pd.read_csv(f"/root/Desktop/MSWIM/Revista/sim_files/Taz/dua/0_1/xmltocsv/{origin}_{destination}_summary_0.csv")

# random rr=1
random_df_1 = pd.read_csv('/root/Desktop/MSWIM/Revista/sim_files/RandomTrips/0_1/detector/detector.csv')
summary_random_df_1 = pd.read_csv(f"/root/Desktop/MSWIM/Revista/sim_files/RandomTrips/0_1/xmltocsv/{origin}_{destination}_summary_0.csv")
# SUMO Outputs
random_traffic_metrics_df_1 = pd.read_csv('/root/Desktop/MSWIM/Revista/sim_files/RandomTrips/0_1/parsed/data.csv')
taz_ma_traffic_metrics_df_1 =  pd.read_csv('/root/Desktop/MSWIM/Revista/sim_files/Taz/ma/0_1/parsed/data.csv')
taz_dua_traffic_metrics_df_1 =  pd.read_csv('/root/Desktop/MSWIM/Revista/sim_files/Taz/dua/0_1/parsed/data.csv')    
# SUMO summary
taz_dua_summary_df_1 =  pd.read_csv(f'/root/Desktop/MSWIM/Revista/sim_files/Taz/dua/0_1/xmltocsv/{origin}_{destination}_summary_0.csv')
taz_ma_summary_df_1 =  pd.read_csv(f'/root/Desktop/MSWIM/Revista/sim_files/Taz/ma/0_1/xmltocsv/{origin}_{destination}_summary_0.csv')
random_summary_df_1 =  pd.read_csv(f'/root/Desktop/MSWIM/Revista/sim_files/RandomTrips/0_1/xmltocsv/{origin}_{destination}_summary_0.csv')
#####################################################################################

    
random_df_1['Hour'] = range(24)
random_df_1['RP'] = 1
random_df_1['Routing'] = 'Random'
random_df_0['Hour'] = range(24)
random_df_0['RP'] = 0
random_df_0['Routing'] = 'Random'


taz_ma_df_0['Hour'] = range(24)
taz_ma_df_0['RP'] = 0
taz_ma_df_0['Routing'] = 'marouter'
taz_ma_df_1['Hour'] = range(24)
taz_ma_df_1['RP'] = 1
taz_ma_df_1['Routing'] = 'marouter'

taz_dua_df_0['Hour'] = range(24)
taz_dua_df_0['RP'] = 0
taz_dua_df_0['Routing'] = 'duarouter'
taz_dua_df_1['Hour'] = range(24)
taz_dua_df_1['RP'] = 1
taz_dua_df_1['Routing'] = 'duarouter'

# Merge csv files 0 / 1 / real
# ma
parsed_ma_df = taz_ma_df_0.merge(taz_ma_df_1, on='Hour', suffixes=('_tazma0', '_tazma1'))
# dua
parsed_dua_df = taz_dua_df_0.merge(taz_dua_df_1, on='Hour', suffixes=('_tazdua0', '_tazdua1'))
# random 
parsed_random_df = random_df_0.merge(random_df_1, on='Hour', suffixes=('_random0', '_random1'))

# ma / dua / random / real
dfs = parsed_ma_df.merge(parsed_dua_df, on='Hour').merge(parsed_random_df, on='Hour').merge(traffic, on='Hour')

# Filter data
traffic_df = dfs.filter(['Hour',
                        'interval_vehicleSum_tazma0',
                        'interval_vehicleSum_tazma1',
                        'interval_vehicleSum_tazdua0',
                        'interval_vehicleSum_tazdua1',
                        'interval_vehicleSum_random0',
                        'interval_vehicleSum_random1',
                        'Total'])

traffic_df.rename(columns={'interval_vehicleSum_tazma0':'MANR',
                           'interval_vehicleSum_tazma1':'MAR',
                           'interval_vehicleSum_tazdua0':'DUANR',
                           'interval_vehicleSum_tazdua1':'DUAR',
                           'interval_vehicleSum_random0':'RNR',
                           'interval_vehicleSum_random1':'RR',
                           'Total':'Real'},inplace=True)

# sort traffic df
df = pd.melt(traffic_df, id_vars=['Hour'], value_vars=['MANR', 'MAR', 'DUANR', 'DUAR', 'RNR', 'RR', 'Real'], 
             var_name='Routing',
             value_name='Traffic')

# save to sim folder
df.to_csv('/root/Desktop/MSWIM/Revista/sim_files/data.csv')


# Files list
f_list = [taz_ma_traffic_metrics_df_0, 
        taz_ma_traffic_metrics_df_1, 
        taz_dua_traffic_metrics_df_0, 
        taz_dua_traffic_metrics_df_1,
        random_traffic_metrics_df_0,
        random_traffic_metrics_df_1]

# Files list
sum_list = [taz_ma_summary_df_0, 
            taz_ma_summary_df_1, 
            taz_dua_summary_df_0, 
            taz_dua_summary_df_1,
            random_summary_df_0,
            random_summary_df_1]


f_names = ['MANR', 'MAR', 'DUANR', 'DUAR', 'RNR', 'RR']
markers=['x','o','+','^','s','v','s']




#PLots
def plot_traffic():
    
    # traffic filtes
    cols = ['MANR', 'MAR', 'DUANR', 'DUAR', 'RNR', 'RR', 'Real']
  
    # plot traffic intensity
    fig, ax = plt.subplots(figsize=(6,4))
    new_df = traffic_df.copy()
    for i, col in enumerate(cols):
        if col =='Real':
           
            new_df.rename(columns={'Real':'Workin day'}, inplace=True)
            col = 'Workin day'
          
            new_df.plot(kind='line',x='Hour',y=col, marker=markers[i], ax=ax)
            ymax = new_df['Workin day'].max() 
            xmax = new_df.loc[new_df['Workin day'] == ymax, 'Hour']
            plt.axhline(ymax, color='tab:orange')
            style = dict(size=10, color='black')
            margin = 10
            ax.text(xmax,ymax+margin, "Peak hour", **style)
            
    plt.ylabel('# of vehicles')
    #plt.title('Traffic intensity')
    plt.xticks(np.arange(min(traffic_df['Hour']), max(traffic_df['Hour'])+1, 2.0))
    plt.yticks(np.arange(min(traffic_df['Hour']), ymax+50, 50.0))
    plt.grid(True, linewidth=1, linestyle='--')    
    
    
def plot_routing_traffic():
    
    # traffic filtes
    cols = ['MANR', 'DUANR', 'RNR', 'Real']
    
    #cols = ['MAR', 'DUAR', 'RR', 'Real']
     
    # box plot
    box_plt = traffic_df.filter(cols)
    box_plt.plot.box(figsize=(6,3))
    plt.title('Number of vehicles (during a working day)')     
    
    # pairs relationship 
    plt.figure()
    sns.pairplot(df, hue='Routing')
    
     
    # plot traffic intensity
    fig, ax = plt.subplots(figsize=(6,4))
    for i, col in enumerate(cols):
        traffic_df.plot(kind='line',x='Hour',y=col, marker=markers[i], ax=ax)
    plt.ylabel('# of vehicles')
    plt.title('Traffic intensity')
    plt.xticks(np.arange(min(traffic_df['Hour']), max(traffic_df['Hour'])+1, 2.0))
    plt.grid(True, linewidth=1, linestyle='--')  
    

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
    plt.grid(True, linewidth=1, linestyle='--')      
    ax.legend()
    
       
 
def fundamental_metrics():   
    # Plot  mean distance/triptime/speed
    # receives df and title
 
    # filter columns
    cols = ['avrg_speed','tripinfo_duration','tripinfo_routeLength','tripinfo_timeLoss','tripinfo_waitingCount','tripinfo_waitingTime']
    for f in f_list:
        f = f.filter(cols)
    
    i, p_x, p_y = 0,3,2
    fig, axs = plt.subplots(p_x,p_y,  sharex=True)
    
    for x in range(p_x):
        for y in range(p_y):    
            if i < len(cols):
                metric = cols[i]
                d_dic = {'MANR':taz_ma_traffic_metrics_df_0[f'{metric}'],
                         'MAR':taz_ma_traffic_metrics_df_1[f'{metric}'],
                         'DUANR':taz_dua_traffic_metrics_df_0[f'{metric}'],
                         'DUAR':taz_dua_traffic_metrics_df_1[f'{metric}'],
                         'RNR':random_traffic_metrics_df_0[f'{metric}'],
                         'RR':random_traffic_metrics_df_1[f'{metric}']}
                df = pd.DataFrame(d_dic)
                #df.mean().plot(kind='bar', color=mcolors.TABLEAU_COLORS, ax=axs[x,y])
                df.mean().plot(kind='bar', ax=axs[x,y])
                axs[x,y].set_title(f'Avrg. {metric}')
                i+=1
    plt.subplots_adjust(top=0.92, bottom=0.08, left=0.10, right=0.95, hspace=0.25,
                    wspace=0.35)
   


def fundamental_metrics_hist():   
    # Plot  mean distance/triptime/speed
    # receives df and title
    
  # filter columns
    cols = ['avrg_speed','tripinfo_duration','tripinfo_routeLength','tripinfo_timeLoss','tripinfo_waitingCount','tripinfo_waitingTime']
    for f in f_list:
        f = f.filter(cols)
    
    n_bins, i, p_x, p_y = 5,0,3,2
    fig, axs = plt.subplots(p_x,p_y, figsize=(8,8), sharex=False, sharey=False)
    
    for x in range(p_x):
        for y in range(p_y):    
          if i < len(cols):
                metric = cols[i]
                d_dic = {'MANR':taz_ma_traffic_metrics_df_0[f'{metric}'],
                         'MAR':taz_ma_traffic_metrics_df_1[f'{metric}'],
                         'DUANR':taz_dua_traffic_metrics_df_0[f'{metric}'],
                         'DUAR':taz_dua_traffic_metrics_df_1[f'{metric}'],
                         'RNR':random_traffic_metrics_df_0[f'{metric}'],
                         'RR':random_traffic_metrics_df_1[f'{metric}']
                         }
                df = pd.DataFrame(d_dic)
                df.plot.hist(n_bins, density=True, histtype='step', legend=False, stacked=False,  ax=axs[x,y])
                #axs[x,y].legend(prop={'size': 5})                
                axs[x,y].set_title(f'Avrg. {metric}')
                i+=1
    axs[x,y].legend(loc='upper center', bbox_to_anchor=(-0.2, -0.3),
          ncol=3, fancybox=True, shadow=True)
                
    plt.subplots_adjust(top=0.92, bottom=0.08, left=0.10, right=0.95, hspace=0.3,
                    wspace=0.35)    
    
    
    
def summary_plot():

    # tag dfs
    taz_ma_summary_df_0['Routing'] = 'MANR'
    taz_ma_summary_df_1['Routing'] = 'MAR'
    taz_dua_summary_df_0['Routing'] = 'DUANR'
    taz_dua_summary_df_1['Routing'] = 'DUAR'
    random_summary_df_0['Routing'] = 'RNR'
    random_summary_df_1['Routing'] = 'RR'
    #traffic = pd.read_csv('/root/Desktop/MSWIM/Revista/TrafficPgSanJoan.csv')
    traffic['Routing'] = 'Real'
    
    # filter cols   
    # summmaty sumo output metric  step_running
    cols = ['step_time', 'step_inserted', 'Routing']
    df = sum_list[0].append(sum_list[1:], ignore_index=True)    
    df = df.filter(cols)
   
    
    # plot step running vehicles
    fig, ax = plt.subplots(figsize=(6,4))
    traffic.plot(kind='line',x='Hour', y='Total', marker='.', label='Real', ax=ax)
    for i, name in enumerate(f_names):
        temp_df = df[df['Routing']==name]
        # group by hour mean nu,ber of vehicles
        temp_df = temp_df.groupby(pd.cut(temp_df["step_time"], np.arange(0, 1+24*3600,3600))).max()
        # obtain veh/hour
        temp_df['Hour'] = range(24) 
        temp_df['shift'] = temp_df['step_inserted'].shift().fillna(0)
        temp_df['vehicles'] = temp_df['step_inserted'] - temp_df['shift'] 
        # plot veh/hour
        temp_df.plot(kind='line',x='Hour', y='vehicles', marker=markers[i], label=name, ax=ax)
        
    plt.ylabel('# of vehicles')
    plt.xlabel('Hour')
    plt.title('Traffic intensity')
    plt.xticks(np.arange(min(traffic_df['Hour']), max(traffic['Hour'])+1, 2.0))
    plt.grid(True, linewidth=1, linestyle='--')    
    
         
# number of vehicles     
plot_traffic() 

plot_routing_traffic()
# points O/D
[traffic_metrics(f, name) for f,name in zip(f_list,f_names)]
# Fundamental metrics matrix   
fundamental_metrics()
# Histograma fundamental metrics
fundamental_metrics_hist()
# Summary SUMO output
summary_plot()

plt.show()

   