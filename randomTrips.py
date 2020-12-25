# -*- coding: utf-8 -*-
import os, sys, glob
import xml.etree.ElementTree as ET
import multiprocessing
from multiprocessing.pool import Pool
import sumolib
import pandas as pd
import numpy as np
import time
from tqdm import tqdm
from joblib import Parallel, delayed, parallel_backend
from utils import SUMO_preprocess


# import sumo tool xmltocsv
os.environ['SUMO_HOME']='/opt/sumo-1.8.0'


# import sumo tool xmltocsv
if 'SUMO_HOME' in os.environ:
    tools = os.path.join('/opt/sumo-1.8.0/', 'tools')
    curr_dir = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(os.path.join(tools))
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")
    
# Informacion de origen / destino como aparece en TAZ file 
origin_district = ['LesCorts']
destination_distric = ['PgSanJoan']
    
# number of cpus
processors = multiprocessing.cpu_count() # due to memory lack -> Catalunya  map = 2GB

# Static paths
sim_dir = '/root/Desktop/MSWIM/Revista/sim_files'   # directory of sumo cfg files
random_dir =  os.path.join(sim_dir, 'RandomTrips', 'TRIPS') # xml directoryRandomTrips
traffic = os.path.join(sim_dir,'..', 'TrafficPgSanJoan.csv')
dua = os.path.join(random_dir,'..', 'DUA')
config = os.path.join(random_dir,'..', 'CFG')
outputs = os.path.join(random_dir,'..', 'OUTPUTS') 
detector = os.path.join(random_dir,'..', 'DETECTOR') 
csv = os.path.join(random_dir,'..', 'CSV')
parsed = os.path.join(random_dir,'..', 'PARSED')
reroute = os.path.join(random_dir,'..', 'REROUTE')


# Sumo templates
duarouter_conf = os.path.join(sim_dir,'duarouter.cfg.xml') # duaroter.cfg file location
sumo_cfg = os.path.join(sim_dir, 'osm.sumo.cfg')
detector_dir = os.path.join(random_dir, '..','detector.add.xml')


# Custom routes via
route_0 = '237659862#23 208568871#3 208568871#4 208568871#5'

# General settings
end_hour = 24
seed = 0
k = 0
rr_prob = 0.5

class folders:
    random_dir = random_dir
    traffic = traffic
    dua = dua
    config = config
    outputs = outputs
    detector = detector
    csv = csv
    parsed = parsed
    reroute = reroute
    
    
    
def clean_folder(folder):
    files = glob.glob(os.path.join(folder,'*'))
    [os.remove(f) for f in files]
    print(f'Cleanned: {folder}')
    
def RandomTrips():
    def exec_randomTrips(fname, ini_time, veh_number):
        # SUMO Tool randomtrips
        sumo_tool = os.path.join(tools, 'randomTrips.py')
            
        # output directory
        output = os.path.join(folders.random_dir,  f'{fname}.xml')
          
        # net file
        net = os.path.join(sim_dir, 'osm.net.xml')
        
        # add files
        add = os.path.join(sim_dir, 'vtype.xml')
        vtype = "passenger"
        
        begin = ini_time
        end =  begin + 15*60  # 15 minutes 
        
        # vehicles arrival 
        period = (end - begin) / veh_number
      
        # Execute random trips
        cmd = f"python {sumo_tool} \
            -n {net} \
            -a {add}  \
            -b {begin} -e {end} -p {period} \
            --trip-attributes 'type=\"{vtype}\" departSpeed=\"0\"' \
            --edge-permission passenger  \
            -s {seed}  \
            -o {output}"
        os.system(cmd)
    
    
    def custom_routes():
        randomtrips = os.listdir(folders.random_dir)
        
        for trip in randomtrips:
            # file locations
            trip_loc = os.path.join(folders.random_dir, trip)
            
            # Open original file
            tree = ET.parse(trip_loc)
            root = tree.getroot()
             
            # Update via route in xml
            [child.set('via', route_0) for child in root]
    
            # Write xml
            cfg_name = os.path.join(folders.random_dir, trip)
            tree.write(cfg_name) 
                
    def trips_for_traffic():
        traffic_df = pd.read_csv(folders.traffic)
        
        # generate randomtrips file each 15 min
        col = list(traffic_df)
        col = col[1:-1]
        
        print(f'\nGenerating {len(col) * end_hour} randomTrips ......')
        for hour in range(end_hour):  #hora
            for minute in col:    # minuto
                vehicles = traffic_df[minute][hour]
                name = f'{hour}_{minute}_randomTrips'
                # convert to sec            
                ini_time = hour*3600 + (int(minute)) * 60
                exec_randomTrips(name, ini_time, vehicles)
        
        # verify generated trip files
        if len(os.listdir(folders.random_dir)) == len(col)*end_hour:
            print('OK')
        else:
            sys.exit(f'Missing randomTrips files in {folders.random_dir}')
    
    
    def change_veh_ID(trip_file, veh_id_number):
        # full path 
        file = os.path.join(folders.random_dir, trip_file)
        # Open original file
        tree = ET.parse(file)
        root = tree.getroot()
           
        # Update via route in xml
        veh_id = veh_id_number
        for child in root:
            veh_id += 1
            child.set('id',str(veh_id))
               
        # Write xml
        #new_file = str(os.path.join(folders.dua_trips, trip_file))
        tree.write(file) 
        return veh_id
              
    
    def update_vehicle_ID():
        trips = os.listdir(folders.random_dir)
        veh_id = 0
        print('Update vehicle IDs......\n')
         
        for f in tqdm(trips):
            veh_id = change_veh_ID(f, veh_id)
        
    
    def gen_DUArouter():
        print('\nGenerate DUA config...')
        #trip files
        trip_list = os.listdir(folders.random_dir)
        trip_list_str = ','.join([f'{os.path.join(folders.random_dir, elem)}' for elem in trip_list]) 
        
        # Open original file
        tree = ET.parse(duarouter_conf)
        
        # Update trip input
        parent = tree.find('input')
        ET.SubElement(parent, 'route-files').set('value', f'{trip_list_str}')    
         
        # Update output
        parent = tree.find('output')
        output_name = os.path.join(folders.dua, 'dua.rou.xml')
        ET.SubElement(parent, 'output-file').set('value', output_name)    
        
        # Update seed number
        parent = tree.find('random_number')
        ET.SubElement(parent, 'seed').set('value', str(seed))    
        
        # Write xml
        cfg_name = os.path.join(folders.config, 'duarouter.cfg.xml')
        tree.write(cfg_name) 
        print('OK')
    
    
    def exec_duarouter_cmd(fname):
        cmd = f'duarouter -c {fname}'
        os.system(cmd)   
    
    
    def gen_sumo_cfg():
        print('Generate sumo config file')
        # Open original file
        tree = ET.parse(sumo_cfg)
        
        # Update rou input
        parent = tree.find('input')
        ET.SubElement(parent, 'route-files').set('value', f'{os.path.join(folders.dua, "dua.rou.xml")}')   
        
        # Update detector
        ET.SubElement(parent, 'additional-files').set('value', f'{detector_dir}')    
    
        # Routing
        parent = tree.find('routing')
        ET.SubElement(parent, 'device.rerouting.probability').set('value', f'{rr_prob}')   

                
        # Update outputs
        curr_name = origin_district[0] + '_' + destination_distric[0]
        #outputs = ['fcd', 'vehroute', 'tripinfo']
        outputs = ['fcd', 'tripinfo']
        parent = tree.find('output')
        for out in outputs:
            ET.SubElement(parent, f'{out}-output').set('value', os.path.join(
                folders.outputs, f'{curr_name}_{out}_{k}.xml'))    
         
        # Write xml
        output_dir = os.path.join(folders.config, f'sumo_{rr_prob}_{k}.sumocfg')
        tree.write(output_dir)
        return output_dir
    
    
    
    def exec_sumo_sim(cfg_full_name):
        print('\nSimulating ......')
        cmd = f'sumo -c {cfg_full_name}'
        os.system(cmd)


    def singlexml2csv(f):
        # output directory
        output = os.path.join(folders.detector, f'{f.strip(".xml")}.csv')
        # SUMO tool xml into csv
        sumo_tool = os.path.join(tools, 'xml', 'xml2csv.py')
        # Run sumo tool with sumo output file as input
        cmd = 'python {} {} -s , -o {}'.format(sumo_tool, os.path.join(folders.detector,f), output)
        os.system(cmd)
    
    def SUMO_outputs_process():
        class options:
            sumofiles = outputs
            xmltocsv = csv
            parsed = parsed
            detector = detector
        SUMO_preprocess(options) 
        
        
    def reroute():
        reroute
    """
    # clean folders     
    clean_folder(folders.random_dir)       
    clean_folder(folders.config)       
    clean_folder(folders.dua) 
    clean_folder(folders.outputs) 
    clean_folder(folders.detector)
    clean_folder(folders.csv)
    clean_folder(folders.parsed)
      
   
    # trips
    trips_for_traffic()
    # via route Travessera
    custom_routes()
    update_vehicle_ID()
    # dua routes
    gen_DUArouter()
    exec_duarouter_cmd(os.path.join(folders.config, 'duarouter.cfg.xml'))
    # sumo sim
    cfg_full_name = gen_sumo_cfg()
    exec_sumo_sim(cfg_full_name)
    # detectors
    singlexml2csv('detector.xml')
    """
    # process sumo outputs  
    SUMO_outputs_process() 
    

RandomTrips()