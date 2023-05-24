import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from pathlib import Path
import seaborn as sns
import os
import yaml
import glob

config_file = "config.yaml"
a_yaml_file = open(config_file)
config = yaml.load(a_yaml_file, Loader=yaml.FullLoader)

network_path = config["main"]["network_path"]
links = config["main"]["links"]
nodes = config["main"]["nodes"]
newclass_path = config["main"]["linkcharac_path"]

boundary_paths = config["test"]["boundary_root"]

if not os.path.exists(config["main"]["processed_path"]):
    os.mkdir(config["main"]["processed_path"])
processed_path = config["main"]["processed_path"]

if not os.path.exists(config["main"]["processed_path_metrics"]):
    os.mkdir(config["main"]["processed_path_metrics"])
processed_path_metrics = config["main"]["processed_path_metrics"]

simulations = {
    "sim1": {
        "name": config["main"]["sim_one_name"],
        "flow_path": os.path.join(config["main"]["sim_one_path"], config["main"]["fpath"]),
        "speed_path": os.path.join(config["main"]["sim_one_path"], config["main"]["spath"]),
        "fuel_path": os.path.join(config["main"]["sim_one_path"], config["main"]["fupath"])
    },
    "sim2": {
        "name": config["main"]["sim_two_name"],
        "flow_path": os.path.join(config["main"]["sim_two_path"], config["main"]["fpath"]),
        "speed_path": os.path.join(config["main"]["sim_two_path"], config["main"]["spath"]),
        "fuel_path": os.path.join(config["main"]["sim_two_path"], config["main"]["fupath"])
    },
    "sim3": {
        "name": config["main"]["sim_three_name"],
        "flow_path": os.path.join(config["main"]["sim_three_path"], config["main"]["fpath"]),
        "speed_path": os.path.join(config["main"]["sim_three_path"], config["main"]["spath"]),
        "fuel_path": os.path.join(config["main"]["sim_three_path"], config["main"]["fupath"])
    },
    "sim4": {
        "name": config["main"]["sim_four_name"],
        "flow_path": os.path.join(config["main"]["sim_four_path"], config["main"]["fpath"]),
        "speed_path": os.path.join(config["main"]["sim_four_path"], config["main"]["spath"]),
        "fuel_path": os.path.join(config["main"]["sim_four_path"], config["main"]["fupath"])
    }
}
