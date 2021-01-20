import pandas as pd
import sys, os
from tqdm import tqdm
from joblib import Parallel, delayed, parallel_backend
import math
import time
import multiprocessing
import xml.etree.ElementTree as ET
import psutil
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib as mpl
from matplotlib import rc
import matplotlib.colors as mcolors
from scipy.interpolate import interp1d

rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
## for Palatino and other serif fonts use:
#rc('font',**{'family':'serif','serif':['Palatino']})
rc('text', usetex=False)

rlist = ['dua', 'duaiterate','ma','od2']
rrlist = ['0_0', '0_1']
basedir = '/root/Desktop/MSWIM/Revista/sim_files/Taz'
output_dir = '/root/Desktop/MSWIM/Revista/sim_files/emissions'

random_0 = '/root/Desktop/MSWIM/Revista/sim_files/RandomTrips/0_0/outputs/Hospitalet_SanAdria_emission_0.xml'
random_1 = '/root/Desktop/MSWIM/Revista/sim_files/RandomTrips/0_1/outputs/Hospitalet_SanAdria_emission_0.xml'


random_df_0 = pd.read_csv('/root/Desktop/MSWIM/Revista/sim_files/emissions/RandomTrips_0_0.csv')
random_df_1 = pd.read_csv('/root/Desktop/MSWIM/Revista/sim_files/emissions/RandomTrips_0_1.csv')
taz_dua_df_0 = pd.read_csv('/root/Desktop/MSWIM/Revista/sim_files/emissions/dua_0_0.csv')
taz_dua_df_1 = pd.read_csv('/root/Desktop/MSWIM/Revista/sim_files/emissions/dua_0_1.csv')
taz_ma_df_0 = pd.read_csv('/root/Desktop/MSWIM/Revista/sim_files/emissions/ma_0_0.csv')
taz_ma_df_1 = pd.read_csv('/root/Desktop/MSWIM/Revista/sim_files/emissions/ma_0_1.csv')
taz_duaiter_df_0 = pd.read_csv('/root/Desktop/MSWIM/Revista/sim_files/emissions/duaiterate_0_0.csv')
taz_duaiter_df_1 = pd.read_csv('/root/Desktop/MSWIM/Revista/sim_files/emissions/duaiterate_0_1.csv')
taz_od2_df_0 = pd.read_csv('/root/Desktop/MSWIM/Revista/sim_files/emissions/od2_0_0.csv')
taz_od2_df_1 = pd.read_csv('/root/Desktop/MSWIM/Revista/sim_files/emissions/od2_0_1.csv')



def process_sumo_emissions_randomTrips():
    # iterate over routing directories 
    emisions_dic = {}
    randomlist = ['RandomTrips']
    random_dir = os.path.join(basedir, '..')
    for routing in randomlist:
        for reroute in rrlist:
            path = os.path.join(random_dir, routing, reroute, 'outputs/Hospitalet_SanAdria_tripinfo_0.xml')
            print(f'Routing = {routing}_{reroute}')
            df = emissions_tripinfo(path)
            emisions_dic[f'{routing}_{reroute}'] = [df['NOx/km'].sum()]
            out_file = os.path.join(output_dir, f'{routing}_{reroute}.csv')
            df.to_csv(out_file, index=False, header=True )
    return emisions_dic
   


def process_sumo_emissions():
    # iterate over routing directories 
    emisions_dic = {}
    for routing in rlist:
        for reroute in rrlist:
            path = os.path.join(basedir, routing, reroute, 'outputs/Hospitalet_SanAdria_tripinfo_0.xml')
            print(f'Routing = {routing}_{reroute}')
            df = emissions_tripinfo(path)
            emisions_dic[f'{routing}_{reroute}'] = [df['NOx/km'].sum()]
            out_file = os.path.join(output_dir, f'{routing}_{reroute}.csv')
            df.to_csv(out_file, index=False, header=True )
    return emisions_dic

            
            
def emissions_tripinfo(emissionsfile):
    # Open original file
    tree = ET.parse(emissionsfile)
    root = tree.getroot()
    children = list(root.getchildren()) # time
    emissions_results = []
    
    for child in children:
        veh_attrib= child.attrib #returnt a dic
        emissions_attrib = child.getchildren()[0].attrib
        data_list = [veh_attrib['id'], veh_attrib['routeLength'], emissions_attrib['NOx_abs']]    
        emissions_results.append(data_list)    

    df = pd.DataFrame(emissions_results, columns=['id', 'routeLength', 'NOx_abs'], dtype=('float'))
    
    # compute emissions mg -> g/km
    df['NOx/km'] = (df['NOx_abs'])/(df['routeLength'])
    return df
    

def rename_cols(results):
    results = results.T
    results.rename(columns={'ma_0_0':'MAR',
                           'ma_0_1':'MAR-R',
                           'dua_0_0':'DUAR',
                           'dua_0_1':'DUAR-R',
                           'duaiterate_0_0':'DUAI',
                           'duaiterate_0_1':'DUAI-R',
                           'RandomTrips_0_0':'RT',
                           'RandomTrips_0_1':'RT-R',
                           'od2_0_0':'OD2',
                           'od2_0_1':'OD2-R'
                           },inplace=True)
    return results


def filter_no_reroute(results_df):
    return results_df.filter(items=['MAR', 'DUAR','DUAI','RT','OD2'])
    #return results_df.filter(items=['MAR-R', 'DUAR-R','DUAI-R','RT-R','OD2-R'])


def plot_emissions(emissions_df):
    # plot traffic intensity
    print(emissions_df)
    emissions_df.T.plot.bar()
    plt.ylabel('Total NOx emissions (g/km)')
    

# read emission outputs 
dic_A = process_sumo_emissions()    
dic_B = process_sumo_emissions_randomTrips()
# prepare dataframe
dic_A.update(dic_B)
print(dic_A)
results_df = pd.DataFrame.from_dict(dic_A, orient='index', columns=['NOx'])
results_df = rename_cols(results_df)
# filter reroute no reroute
results_df = filter_no_reroute(results_df)
# plot emissions
plot_emissions(results_df)
plt.show()
    