# -*- coding: utf-8 -*-
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

# import sumo tool xmltocsv
if 'SUMO_HOME' in os.environ:
    tools = os.path.join('/opt/sumo-1.8.0/', 'tools')
    curr_dir = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(os.path.join(tools))
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")
    
    
    
# number of cpus
processors = multiprocessing.cpu_count() # due to memory lack -> Catalunya  map = 2GB

# Static paths
sim_dir = '/root/Desktop/MSWIM/Revista/sim_files'   # directory of sumo cfg files
random_dir =  os.path.join(sim_dir, 'RandomTrips', 'TRIPS') # xml directoryRandomTrips
xmltocsv_dir = os.path.join(sim_dir,'..', 'xmltocsv') # xml directory

parsed_dir = os.path.join(sim_dir,'..', 'parsed')
detector_dir = os.path.join(sim_dir,'detector.add.xml')

# Custom routes via
route_0 = '237659862#23 208568871#3 208568871#4 208568871#5'


class folders:
    random_dir = random_dir
    xml2csv = xmltocsv_dir
    parse = parsed_dir
 

def RandomTrips():
    def exec_randomTrips(fname):
        # SUMO Tool randomtrips
        sumo_tool = os.path.join(tools, 'randomTrips.py')
            
        # output directory
        output = os.path.join(folders.random_dir,  f'{fname}.xml')
          
        # net file
        net = os.path.join(sim_dir, 'osm.net.xml')
        
        # add files
        add = os.path.join(sim_dir, 'vtype.xml')
        vtype = "passenger"
        
        # Execute random trips
        cmd = f"python {sumo_tool} \
              -n {net} \
              -a {add}  \
              --trip-attributes 'type=\"{vtype}\"' \
              --edge-permission passenger  \
              -s 0  \
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
                
        
    
    exec_randomTrips('randomTrips')
    custom_routes()
    
RandomTrips()