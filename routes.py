import os, sys, glob
import xml.etree.ElementTree as ET
import multiprocessing
import sumolib
import pandas as pd
import numpy as np
import time
from tqdm import tqdm
from joblib import Parallel, delayed, parallel_backend

# import sumo tool xmltocsv
os.environ['SUMO_HOME']='/opt/sumo-1.8.0'

from utils import SUMO_preprocess, parallel_batch_size

# number of cpus
processors = multiprocessing.cpu_count() # due to memory lack -> Catalunya  map = 2GB

# Static paths
sim_dir = '/root/Desktop/MSWIM/Revista/sim_files'   # directory of sumo cfg files
routes_output = os.path.join(sim_dir, 'DUA')               # duarouter output files 
sumo_cfg_output = os.path.join(sim_dir, 'SUMO')   
simulation_outputs = os.path.join(sim_dir, '../outputs')   # simulation outputs folder   
xmltocsv_dir = os.path.join(sim_dir,'..', 'xmltocsv') # xml directory
parsed_dir = os.path.join(sim_dir,'..', 'parsed')
detector_dir = os.path.join(sim_dir,'detector.add.xml')


# Custom routes via
route_0 = '237659862#23 208568871#3 208568871#4 208568871#5'

# SUMO templeates
o_dir = os.path.join(sim_dir, 'O')                         # O file location
od2trips_conf = os.path.join(sim_dir,'od2trips.cfg.xml')   # od2trips.cfg file location     
duarouter_conf = os.path.join(sim_dir,'duarouter.cfg.xml') # duaroter.cfg file location
sumo_cfg = os.path.join(sim_dir, 'osm.sumo.cfg')

# Informacion de origen / destino como aparece en TAZ file 
origin_district = ['LesCorts']
destination_distric = ['PgSanJoan']
    
# General settings
veh_num = 10  # number of vehicles in O file
n_repetitions = 1 # number of repetitions 
sim_time = 24 # in hours # TO DO parameter of time in files
end_hour = 24
factor = 1.1 # multiplied by the number of vehicles



class folders:
    dua = routes_output
    cfg = sumo_cfg_output
    outputs = simulation_outputs
    xml2csv = xmltocsv_dir
    parse = parsed_dir
    O = o_dir
    detector = detector_dir
        
    
def clean_folder(folder):
    files = glob.glob(os.path.join(folder,'*'))
    [os.remove(f) for f in files]
    
    

def gen_routes(O, k):
    
    # Generate od2trips cfg
    cfg_name, output_name = gen_od2trips(O,k)
    
    # Execute od2trips
    exec_od2trips(cfg_name)
    
    # Custom route via='edges'
    via_trip = custom_routes(output_name, k)
    
    # Generate DUArouter cfg
    cfg_name, output_name = gen_DUArouter(via_trip, k)
        
    # Generate sumo cfg
    gen_sumo_cfg(output_name, k)
    
    
def gen_route_files():
    # generate cfg files
    for h in origin_district:
        print(f'\nGenerating cfg files for TAZ: {h}')
        for sd in tqdm(destination_distric):
            time.sleep(1)
            
            # build O file    
            O_name = os.path.join(o_dir, f'{h}_{sd}')
            create_O_file(O_name, f'{h}', f'{sd}', veh_num)
            
            # Generate cfg files 
            for k in tqdm(range(n_repetitions)):
                time.sleep(1) 
                gen_routes(O_name, k)
    
    

def create_O_file(fname, origin_district, destination_distric, vehicles):
    #create 24 hour files
    traffic = pd.read_csv('/root/Desktop/MSWIM/Revista/TrafficPgSanJoan.csv')
 
    df = pd.DataFrame(traffic)
    #traffic_24 = traffic_df['Total'].values
    name = os.path.basename(fname)
     
    col = list(df)
    col = col[1:-1]
    for hour in range(end_hour):  #hora
        for minute in col:    # minuto
            vehicles = df[minute][hour]
            
            h = hour
            m = str(minute)
            until = int(minute) + 15
            
            O_file_name = os.path.join(o_dir,f'{h}_{m}_{name}')
            O = open(f"{O_file_name}", "w")
            
            #num_vehicles = traffic_24[h] * 1.1 # margin of duarouter checkroutes
            text_list = ['$OR;D2\n',               # O format
                     f'{h}.{m} {h}.{until}\n',  # Time 0-48 hours
                     f'{factor}\n',         # Multiplication factor
                     f'{origin_district} '     # Origin
                 	 f'{destination_distric} ',   # Destination
                     f'{vehicles}']            # NUmber of vehicles x multiplication factor
            O.writelines(text_list)
            O.close()


def custom_routes(trips, k):
    trip = os.path.join(o_dir, trips)
    
    # Open original file
    tree = ET.parse(trip)
    root = tree.getroot()
     
    # Update via route in xml
    [child.set('via', route_0) for child in root]

    # name    
    curr_name = os.path.basename(trips).split('_')
    curr_name = curr_name[0] + '_' + curr_name[1]
    output_name = os.path.join(o_dir, f'{curr_name}_trips_{k}.rou.xml')
           
    # Write xml
    cfg_name = os.path.join(o_dir, output_name)
    tree.write(cfg_name) 
    return output_name
    
    
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
    # read O files
    O_files_list = os.listdir(o_dir)
    O_listToStr = ' '.join([f'{os.path.join(o_dir, elem)},' for elem in O_files_list]) 
    O_listToStr = O_listToStr[:-1] # delete last coma
    # Open original file
    tree = ET.parse(od2trips_conf)
    
    # Update O input
    parent = tree.find('input')
    ET.SubElement(parent, 'od-matrix-files').set('value', f'{O_listToStr}')    
            
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
    
    # Update detector
    ET.SubElement(parent, 'additional-files').set('value', f'{detector_dir}')    

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
    expected_files = len(origin_district)*len(destination_distric)*n_repetitions
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
                
        summary = pd.DataFrame(out_list, columns=['Origin', 'Destination','Routes', 'Repetition']).sort_values(by=['Repetition', 'Origin', 'Destination'])
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
        print(f'\n{len(os.listdir(simulation_outputs))} outputs generated: {simulation_outputs}')
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
        detector = '/root/Desktop/MSWIM/Revista/detector'
    SUMO_preprocess(options)
      
"""
# Clear folders
clean_folder(folders.dua)
clean_folder(folders.cfg)
clean_folder(folders.outputs)
clean_folder(folders.parse)
clean_folder(folders.xml2csv)
clean_folder(folders.O)
clean_folder(folders.detector)


# Generate cfg files
gen_route_files()

# Execute DUArouter 
exec_DUArouter()
           
# Execute simulations
summary()

# Exec simulations
simulate()     
"""
# Outputs preprocess
SUMO_outputs_process()
