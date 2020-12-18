SUMO routes generate automatically sumo cfg files to simulations based on sumo template located at sim_files folder. Requires folder sctructure (folders) is included in the Project folder: 

Project

├── outputs

├── parsed

├── plots

├── sim_files

│   ├── DUA

│   ├── CONFIG

│   ├── O

│   └── SUMO

└── xmltocsv


sim_files folder contains sumo templates (files):

sim_files

├── catalunya.net.xml

├── catalunya.sumo.cfg

├── duarouter.cfg.xml

├── od2trips.cfg.xml

├── route_files.cfg

├── TAZ.xml

├── Accidents.csv

└── vtype.xml



The final file generated from simulations is called data.csv and contains the dataset of sumo output simulations. 



```bash

Install anaconda:
https://www.anaconda.com/products/individual  -> Download last version

$cp ~/Downloads/Anaconda3-2020.11-Linux-x86_64.sh /tmp/
$bash Anaconda3-2020.11-Linux-x86_64.sh

Optional configurations:
$conda config --set auto_activate_base false
$conda deactivate


Download the project:
$git clone https://github.com/Pbarbecho/sumo_routes.git


Project:
$cd sumo_routes


Create environment:
$ conda create --name sumo --file environment.txt


Activate env:
$ conda activate sumo


To deactivate env :
$conda deactivate

```
