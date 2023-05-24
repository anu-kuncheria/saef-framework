import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, LineString
import shapely.geometry as geom
import os


class Network:
    def __init__(self, links_path, nodes_path, crs="epsg:4326"):
        self.links_path = links_path
        self.nodes_path = nodes_path
        self.crs = crs
        self.gdf_links, self.gdf_nodes = self.load_network()

    def load_network(self):
        print("*********GDF section entering*********")
        links = pd.read_csv(self.links_path)
        nodes = pd.read_csv(self.nodes_path)
        nodes['geom'] = [Point(xy) for xy in zip(nodes.LON, nodes.LAT)]
        gdf_nodes = gpd.GeoDataFrame(nodes, geometry=nodes.geom, crs=self.crs)
        links['ref_lat'] = links['REF_IN_ID'].map(
            nodes.set_index('NODE_ID')['LAT'])
        links['ref_long'] = links['REF_IN_ID'].map(
            nodes.set_index('NODE_ID')['LON'])
        links['nref_lat'] = links['NREF_IN_ID'].map(
            nodes.set_index('NODE_ID')['LAT'])
        links['nref_long'] = links['NREF_IN_ID'].map(
            nodes.set_index('NODE_ID')['LON'])
        links['geometry'] = links.apply(
            lambda x: LineString([(x['ref_long'], x['ref_lat']), (x['nref_long'], x['nref_lat'])]), axis=1)
        gdf_links = gpd.GeoDataFrame(
            links, geometry=links.geometry, crs=self.crs)
        return gdf_links, gdf_nodes

    def process_links(self, boundary_file, newclass_path, write_directory, city_name):
        if boundary_file != '':
            """
            ETL function that loads raw network and filters the respective city links based on city boundry
            """
            print("-------------------Start data transformation-------------------")
            print(
                f"==== Loading the boundary and links file for {city_name} ====")
            city_boundary = gpd.read_file(boundary_file)
            assert city_boundary.crs == 'EPSG:4326', "CRS not epsg 4326. Check the CRS of the boundary shapefile"

            print("Clipping the network to city boundary.")
            city_links = gpd.clip(self.gdf_links, city_boundary)
            city_links = city_links[city_links['geometry'].apply(
                lambda x: x.type == 'LineString')]
            print("Number of links in the city:", len(city_links))
            print("End data transformation")
            # add new link classification data to this
            link_chr = pd.read_csv(newclass_path)
            city_links = city_links.merge(
                link_chr, left_on='LINK_ID', right_on='LINK_ID', how='left')
            # export data
            print(f"write data to {write_directory}")
            city_links.to_file(os.path.join(
                write_directory, f"citylinks_{city_name}.geojson"), driver="GeoJSON")
            print(f" # links: {len(city_links)}")
            print(" ==== Completed links processing ====")
        else:
            print("No boundary path")
