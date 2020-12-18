import pandas as pd
import sys, os
from tqdm import tqdm
from joblib import Parallel, delayed, parallel_backend
import math
import time
import multiprocessing

# number of cpus
processors = multiprocessing.cpu_count() # due to memory lack -> Catalunya  map = 2GB

# import sumo tool xmltocsv
if 'SUMO_HOME' in os.environ:
    tools = os.path.join('/opt/sumo-1.5.0/', 'tools')
    curr_dir = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(os.path.join(tools))
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")


def parallel_batch_size(plist):
    if len(plist) < processors:
        batch = 1
    else:
        batch = int(math.ceil(len(plist)/processors))
    return batch


def SUMO_preprocess(options):
    # Process SUMO output files to build the dataset
    def save_file(df, name, parsed_dir):
        #print(f'Parsed --> {name}')
        if 'ID' in df.keys():
            df.sort_values(by=['ID'], inplace=True)
        df.to_csv(os.path.join(parsed_dir, f'{name}.csv'), index=False, header=True)
        
    
    def parallelxml2csv(f, options):
        # output directory
        output = os.path.join(options.xmltocsv, f'{f.strip(".xml")}.csv')
        # SUMO tool xml into csv
        sumo_tool = os.path.join(tools, 'xml', 'xml2csv.py')
        # Run sumo tool with sumo output file as input
        cmd = 'python {} {} -s , -o {}'.format(sumo_tool, os.path.join(options.sumofiles,f), output)
        os.system(cmd)



    def bulid_list_of_df(csv):
        time.sleep(1)
        dname = csv.split('.')[0].split('_')
        data = pd.read_csv(os.path.join(options.xmltocsv, csv))
        dname.append(data)
        return dname


    def convert_xml2csv(files_list):
        if files_list:
            print(f'\nGenerating {len(files_list)} csv files. This may take a while .........')
            batch = parallel_batch_size(files_list)
           
            # Parallelize files generation
            with parallel_backend("loky"):
                Parallel(n_jobs=processors, verbose=0, batch_size=batch)(delayed(parallelxml2csv)(
                     f, options) for f in files_list)
        else:
            sys.exit(f"Empty or missing output data files: {options.sumofiles}")

               
      
    def xml2csv(options): 
        # convert xml to csv
        files_list = os.listdir(options.sumofiles)
        
        # convert xmls to csvs
        convert_xml2csv(files_list)
        
        # Read generated csvs
        csvs_list = os.listdir(options.xmltocsv)
        
        if len(csvs_list) == len(files_list):
            data_list = []
            print(f'\nBuilding {len(csvs_list)} dataframes from sumo outputs ......\n')
            
            # build list of dataframes        
            [data_list.append(bulid_list_of_df(csv)) for csv in tqdm(csvs_list)]
            
            # convert to a single dataframe
            result_df = pd.DataFrame(data_list, columns=['Origin', 'Destination', 'Output','Repetition','Dataframe'])
            return result_df           
        else:
            sys.exit(f'Missing csv files: {options.xmltocsv}')
            
 
           
    def merge_files(options):
        #combine all files in the parsed dir
        parsed_files = os.listdir(options.parsed)
        print(f'\nCombining {len(parsed_files)} files')
        combined_csv = pd.concat([pd.read_csv(os.path.join(options.parsed, pf)) for pf in parsed_files ])
        #export to csv
        combined_csv.to_csv(os.path.join(options.parsed, "data.csv"), index=False, header=True)
        return combined_csv
                
     
                
    def veh_trip_info(df):
        # filter know features
        df = df.filter(items=['tripinfo_duration', 
                              'tripinfo_routeLength', 
                              'tripinfo_timeLoss', 
                              'tripinfo_waitingCount', 
                              'tripinfo_waitingTime', 
                              'tripinfo_arrivalLane', 
                              'tripinfo_departLane',
                              'tripinfo_id']).rename(columns={'tripinfo_id':'ID'})
        return df
    
                
    def parallel_parse_output_files(key, group_df):
        # save parsed files
        df_name = f'{key[0]}_{key[1]}_{key[2]}'
        # Process sumo outputs
        vehroute = group_df.loc[group_df['Output'] == 'vehroute', 'Dataframe'].iloc[0]
        fcd = group_df.loc[group_df['Output'] == 'fcd', 'Dataframe'].iloc[0]
        tripinfo = group_df.loc[group_df['Output'] == 'tripinfo', 'Dataframe'].iloc[0]
        taz_locations_edgenum_df = lanes_counter_taz_locations(vehroute)                  # Count edges on route from vehroute file and get from/to TAZ locations
        veh_speed_positions_df = avrg_speed_and_geo_positions(fcd)                        # Get average speed and initial/end positions (x,y)
        tripinfo_df = veh_trip_info(tripinfo) 
        # merge dataframes
        sdata = taz_locations_edgenum_df.merge(veh_speed_positions_df,on='ID').merge(tripinfo_df,on='ID')
        # save each scenario in parsed files
        save_file(sdata, f'{df_name}', options.parsed)
						
											      
        
    def lanes_counter_taz_locations(df):
        # contador de edges en ruta
        df['lane_count'] = df['route_edges'].apply(lambda x: len(x.split()))
        df = df.filter(items=['vehicle_id', 'lane_count', 'vehicle_fromTaz', 'vehicle_toTaz']).rename(columns={'vehicle_id':'ID'})
        
        return df


    def get_positions(df, id,min,max):
        # get initial and end positions based on ini/end time of vehicle id
        ini_pos =  df.loc[(df['vehicle_id'] == id) & (df['timestep_time'] == min)].iloc[0]
        end_pos =  df.loc[(df['vehicle_id'] == id) & (df['timestep_time'] == max)].iloc[0]
        return id, min, max, ini_pos.vehicle_x, ini_pos.vehicle_y, end_pos.vehicle_x, end_pos.vehicle_y 
        
       
    def avrg_speed_and_geo_positions(df):
        # get average speed
        speed_df = df.groupby(['vehicle_id']).mean().reset_index()
        speed_df = speed_df.filter(items=['vehicle_id','vehicle_speed']).rename(columns={'vehicle_id':'ID','vehicle_speed':'avrg_speed'})
        # Prepare df with ini end times of vehicles 
        df = df.filter(items=['vehicle_id', 'timestep_time','vehicle_x', 'vehicle_y'])
        df.dropna(subset = ["vehicle_id"], inplace=True)
        # get initial end times of vechiel
        time_df = df.groupby(['vehicle_id']).timestep_time.agg(['min','max']).reset_index()
        # Get positions df
        positions_list = [get_positions(df,id,min,max) for id,min,max in zip(time_df['vehicle_id'], time_df['min'], time_df['max'])]
        positions_df = pd.DataFrame(positions_list, columns=['ID', 'ini_time', 'end_time', 'ini_x_pos', 'ini_y_pos','end_x_pos', 'end_y_pos'])
        # Merge speed and positions df
        speed_and_positions = speed_df.merge(positions_df, on='ID')
        return speed_and_positions
    
    
    def parse_df(df):
        # process dataframe    
        nfiles = len(df.index)
        efiles = nfiles/len(df["Output"].unique()) # total files / number of output sumo (tripinfo, fcd, vehroute)
       
        print(f'\nReading {nfiles} dataframes. Expected {efiles} parsed files. This may take a while .........')        

        # group df by features
        grouped_df = df.groupby(['Origin', 'Destination', 'Repetition'])
        # parse dataframe
        [parallel_parse_output_files(key, group_df) for key, group_df in tqdm(grouped_df)]


   
    # Execute functions               
    df = xml2csv(options)   # Convert outputs to csv 
  #  parse_df(df)            # Convert csv to dataframes and filter files fileds
  #  merge_files(options)    # Merge dataframes into a single file 'data.csv'
    
    
    
    
    
    
    
    