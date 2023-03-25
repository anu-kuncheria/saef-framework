from load_data import *
import sys
sys.path.append('../src')
import network as net


links_path = os.path.join(network_path, links)
nodes_path = os.path.join(network_path, nodes)
print("Reading in city boundaries...")
files = glob.glob(boundary_paths + "/*.shp")
print(files)

networkgdf = net.Network(links_path, nodes_path, crs="epsg:4326")
for f in files:
    print(f)
    city_name = f.split('/')[-1].split('.')[0].lower().strip()
    print("Started...", city_name)
    #make new directory
    if not os.path.exists(os.path.join(processed_path,city_name)):
        os.mkdir(os.path.join(processed_path,city_name))
    write_directory = os.path.join(processed_path,city_name)

    #clipping
    networkgdf.process_links(f, newclass_path, write_directory, city_name)
    print("Completed writing links file")
    print("===== Completed =====", city_name)