import pandas as pd
import sys, os
from tqdm import tqdm
from joblib import Parallel, delayed, parallel_backend
import math
import time
import multiprocessing
import xml.etree.ElementTree as ET
import psutil

rlist = ['dua', 'duaiterate','ma','od2']
rrlist = ['0_0', '0_1']
basedir = '/root/Desktop/MSWIM/Revista/sim_files/Taz'

random_0 = '/root/Desktop/MSWIM/Revista/sim_files/RandomTrips/0_0/outputs/Hospitalet_SanAdria_emission_0.xml'
random_1 = '/root/Desktop/MSWIM/Revista/sim_files/RandomTrips/0_1/outputs/Hospitalet_SanAdria_emission_0.xml'

paths = []
for e in rlist:
    for re in rrlist:
        newpath = os.path.join(basedir, e, re, 'outputs/Hospitalet_SanAdria_emission_0.xml')
        paths.append(newpath)
paths.append(random_0)
paths.append(random_1)

paths = [random_0]



def emissions_tripinfo(emissionsfile):
    # Open original file
    tree = ET.parse(emissionsfile)
    root = tree.getroot()
    tuple_values = []
    
    children = root.getchildren()
    
    
    for child in children:
        print(child.attrib)
    """
        for citer, subchild in enumerate(child.getchildren()):
            tuple_values.append((subchild.get('time'), root[citer][0].attrib['CO2'], root[citer][0].attrib['x'], root[citer][0].attrib['y']))
    df = pd.DataFrame(tuple_values, columns =['Time', 'CO2', 'x', 'y']) 
    ouputdir = os.path.join(os.path.basedir(emissionsfile), '..','emissions', 'emissions.csv')
    df.to_csv(ouputdir, index=False, header=True)
    """
    
for p in tqdm(paths):
    emissions_tripinfo(p)
    