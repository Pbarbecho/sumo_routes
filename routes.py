import os, sys
import xml.etree.ElementTree as ET
import multiprocessing
import sumolib
import pandas as pd
import numpy as np
import time
import math
from tqdm import tqdm
from joblib import Parallel, delayed, parallel_backend
# import sumo tool xmltocsv
os.environ['SUMO_HOME']='/opt/sumo-1.5.0'


from utils import SUMO_preprocess


# number of cpus
processors = multiprocessing.cpu_count()-18 # due to memory lack -> Catalunya  map = 2GB

# Static paths
sim_dir = '/root/Documents/SUMO_SEM/CATALUNYA/sim_files'   # directory of sumo cfg files
routes_output = os.path.join(sim_dir, 'DUA')               # duarouter output files 
sumo_cfg_output = os.path.join(sim_dir, 'SUMO')   
simulation_outputs = os.path.join(sim_dir, '../outputs')   # simulation outputs folder   
#xmltocsv_dir = os.path.join(sim_dir,'..', 'xmltocsv') # xml directory
#parsed_dir = os.path.join(sim_dir,'..', 'parsed')
# external netwrok drive dueto size GB
xmltocsv_dir = '/media/lab/xmltocsv' # xml directory
parsed_dir = '/media/lab/parsed'


# SUMO templeates
o_dir = os.path.join(sim_dir, 'O')                         # O file location
od2trips_conf = os.path.join(sim_dir,'od2trips.cfg.xml')   # od2trips.cfg file location     
duarouter_conf = os.path.join(sim_dir,'duarouter.cfg.xml') # duaroter.cfg file location
sumo_cfg = os.path.join(sim_dir, 'catalunya.sumo.cfg')

# Informacion de los hospitales y distritos tal como aparece en TAZ file 
hospitals = ['HospitalViladecans', 'HospitaldeBarcelona']
sanitary_districs = ['Sitges', 'Barcelona', 'Terrasa','Vic']
    
# General settings
veh_num = 80  # number of vehicles in O file
n_repetitions = 15 # number of repetitions 
sim_time = 48 # in hours # TO DO parameter of time in files
factor = 100 # multiplied by the number of vehicles


def gen_routes(O, k):
    
    # Generate od2trips cfg
    cfg_name, output_name = gen_od2trips(O,k)
    
    # Execute od2trips
    exec_od2trips(cfg_name)
    
    # Generate DUArouter cfg
    cfg_name, output_name = gen_DUArouter(output_name, k)
        
    # Generate sumo cfg
    gen_sumo_cfg(output_name, k)
    
    
def gen_route_files():
    print('\nGenerating cfg files\n')
    for h in hospitals:
        for sd in tqdm(sanitary_districs):
            time.sleep(1)
            
            # build O file    
            O_name = os.path.join(o_dir, f'{h}_{sd}')
            create_O_file(O_name, f'{h}', f'{sd}', veh_num)
            
            # Generate cfg files 
            for k in tqdm(range(n_repetitions)):
                time.sleep(1) 
                gen_routes(O_name, k)
    
    

def create_O_file(fname, hospital, sanitary_distric, vehicles):
    O = open(f"{fname}", "w")
    text_list = ['$OR;D2\n',               # O format
                 f'0.00 {sim_time}.00\n',  # Time 0-48 hours
                 f'{factor}.00\n',         # Multiplication factor
                 f'{hospital} '            # Origin
             	 f'{sanitary_distric} ',   # Destination
                 f'{vehicles}']            # NUmber of vehicles x multiplication factor
    O.writelines(text_list)
    O.close()


    
def gen_DUArouter(trips, i):
    # Open original file
    tree = ET.parse(duarouter_conf)
    
    # Update trip input
    parent = tree.find('input')
    ET.SubElement(parent, 'route-files').set('value', f'{trips}')    
     
    # Update output
    parent = tree.find('output')
    curr_name = os.path.basename(trips).split('_')
    curr_name = curr_name[0] + '_' + curr_name[1]
    output_name = os.path.join(routes_output, f'{curr_name}_dua_{i}.rou.xml')
    ET.SubElement(parent, 'output-file').set('value', output_name)    
    
    # Update seed number
    parent = tree.find('random_number')
    ET.SubElement(parent, 'seed').set('value', f'{i}')    
    
    # Write xml
    original_path = os.path.dirname(trips)
    cfg_name = os.path.join(original_path, f'{curr_name}_duarouter_{i}.cfg.xml')
    tree.write(cfg_name) 
    return cfg_name, output_name
        
    
    
def gen_od2trips(O,k):
    # Open original file
    tree = ET.parse(od2trips_conf)
    
    # Update O input
    parent = tree.find('input')
    ET.SubElement(parent, 'od-matrix-files').set('value', f'{O}')    
            
    # Update output
    parent = tree.find('output')
    output_name = f'{O}_od2_{k}.trip.xml'
    ET.SubElement(parent, 'output-file').set('value', output_name)    
    
    # Update seed number
    parent = tree.find('random_number')
    ET.SubElement(parent, 'seed').set('value', f'{k}')    
    
    # Write xml
    cfg_name = f'{O}_trips_{k}.cfg.xml'
    tree.write(cfg_name)
    return cfg_name, output_name    


def gen_sumo_cfg(dua, k):
    # Open original file
    tree = ET.parse(sumo_cfg)
    
    # Update rou input
    parent = tree.find('input')
    ET.SubElement(parent, 'route-files').set('value', f'{dua}')    
            
    # Update outputs
    parent = tree.find('output')
    curr_name = os.path.basename(dua).split('_')
    curr_name = curr_name[0] + '_' + curr_name[1]
    
    # outputs 
    outputs = ['fcd', 'vehroute', 'tripinfo']
    for out in outputs:
        ET.SubElement(parent, f'{out}-output').set('value', os.path.join(
            simulation_outputs, f'{curr_name}_{out}_{k}.xml'))    
     
    # Write xml
    output_dir = os.path.join(sumo_cfg_output, f'{curr_name}_{k}.sumo.cfg')
    tree.write(output_dir)
    
    
    
def exec_od2trips(fname):
    cmd = f'od2trips -c {fname}'
    os.system(cmd)


def exec_duarouter_cmd(fname):
    cmd = f'duarouter -c {fname}'
    os.system(cmd)    
    
    
def parallel_batch_size(plist):
    if len(plist) < processors:
        batch = 1
    else:
        batch = int(math.ceil(len(plist)/processors))
    return batch
   
    
def exec_DUArouter():
    cfg_files = os.listdir(o_dir)
  
    # Get dua.cfg files list
    dua_cfg_list = []
    [dua_cfg_list.append(cf) for cf in cfg_files if 'duarouter' in cf.split('_')]
    
    if dua_cfg_list:
        batch = parallel_batch_size(dua_cfg_list)
        
        # Generate dua routes
        print(f'\nGenerating duaroutes ({len(dua_cfg_list)} files) ...........\n')
        with parallel_backend("loky"):
            Parallel(n_jobs=processors, verbose=0, batch_size=batch)(delayed(exec_duarouter_cmd)(
                     os.path.join(o_dir, cfg)) for cfg in dua_cfg_list)
    else:
       sys.exit('No dua.cfg files}')
 
    

def summary():
    # Count generated files
    output_files = os.listdir(routes_output)   
    expected_files = len(hospitals)*len(sanitary_districs)*n_repetitions
    generated_files = len(output_files)/2 # /2 due to alt files
    print(f'\nExpected files: {expected_files}   Generated files: {generated_files}\n')
    if generated_files != expected_files:
        print('Missing files, check log at console')
    else:
        # Count routes 
        measure = ['id','fromTaz', 'toTaz']
        out_list = []
        for f in output_files:    
            if 'alt' not in f.split('.'):
                summary_list = sumolib.output.parse_sax__asList(os.path.join(routes_output,f), "vehicle", measure)
                temp_df = pd.DataFrame(summary_list).groupby(['fromTaz', 'toTaz']).count().reset_index()
                temp_df['Repetition'] = f.split('.')[0].split('_')[-1]
                out_list.append(temp_df.to_numpy()[0])
                
        summary = pd.DataFrame(out_list, columns=['Hospital', 'Accident','Routes', 'Repetition']).sort_values(by=['Repetition', 'Hospital', 'Accident'])
        save_to = os.path.join(sim_dir,'route_files.csv')
        summary.to_csv(save_to, index=False, header=True)
        print(summary)
        print(f'\nSummary saved to: {save_to}\n')
        
        
def clean_memory():
    #Clean memory cache at the end of simulation execution
    if os.name != 'nt':  # Linux system
        os.system('sync')
        os.system('echo 3 > /proc/sys/vm/drop_caches')
        os.system('swapoff -a && swapon -a')
    # print("Memory cleaned")
    
    
def simulate():
    simulations = os.listdir(sumo_cfg_output)
    if simulations: 
        batch = parallel_batch_size(simulations)
        # Execute simulations
        print('\nExecuting simulations ....')
        with parallel_backend("loky"):
                Parallel(n_jobs=processors, verbose=0, batch_size=batch)(delayed(exec_sim_cmd)(s) for s in simulations)
        clean_memory()
    else:
       sys.exit('No sumo.cfg files}')
  
                
       
def exec_sim_cmd(cfg_file):
    full_path = os.path.join(sumo_cfg_output, cfg_file)
    cmd = f'sumo -c {full_path}'
    os.system(cmd)
  
    
  
def SUMO_outputs_process():
    class options:
        sumofiles = simulation_outputs
        xmltocsv = xmltocsv_dir
        parsed = parsed_dir
    data = SUMO_preprocess(options)
    
      
    
# Generate cfg files
gen_route_files()

# Execute DUArouter 
exec_DUArouter()
           
        
# Execute simulations
summary()

# Exec simulations
simulate()     

# Outputs preprocess
SUMO_outputs_process()
