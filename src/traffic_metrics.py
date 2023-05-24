import geopandas as gpd
import pandas as pd
import numpy as np


class MobilitiResults:
    def __init__(self, path):
        self.path = path
        self.colnames = self.generate_column_names()

    def generate_column_names(self):
        result = ['link_id', '00:00']
        minc, hourc = 0, 0  # todo
        for i in range(0, 95):
            minc += 1
            if minc % 4 == 0:
                minc = 0
                hourc += 1
            mindigit = "00" if minc == 0 else str(minc * 15)
            result.append('%02d' % hourc + ':' + mindigit)
        result.append('unnamed')
        return result

    def read_file(self):
        file = pd.read_csv(self.path, sep='\t',
                           header=None, names=self.colnames)
        # dropping the last Nan column
        file.drop(file.columns[len(file.columns) - 1], axis=1, inplace=True)
        return file


class MobilitiAnalysis:
    def __init__(self, citylinks_path, flow_path, speed_path, fuel_path):
        self.city_links = gpd.read_file(citylinks_path)
        self.flow = MobilitiResults(flow_path).read_file()
        self.speed = MobilitiResults(speed_path).read_file()
        self.fuel = MobilitiResults(fuel_path).read_file()
        self.city_flow = self.resultscity_filter_len(self.flow)
        self.city_speed = self.resultscity_filter_len(self.speed)
        self.city_fuel = self.resultscity_filter_len(self.fuel)

    def round_two_decimals(self, number):
        return np.round(number, decimals=2)

    def resultscity_filter_len(self, df):
        df_sub = df[df.link_id.isin(self.city_links.LINK_ID)]
        df_city = df_sub.merge(
            self.city_links, left_on='link_id', right_on='LINK_ID', how='left')
        return df_city

    def vmt(self, flow):
        '''Vehicle Miles Travelled.
        Flow df needs to have the link atrribute length in it'''
        vmt = np.sum(flow.loc[:, "00:00":"23:45"].sum(
            axis=1) * 15 * 60 * flow.loc[:, 'LENGTH(meters)'] * 0.000621371)  # count*length of road VMT
        return self.round_two_decimals(vmt)

    def vmt_city(self):
        """
        Outputs total VMT and VMT load on neighborhoods
        """

        total_vmt = self.vmt(self.city_flow)

        neighborhood_flow_df = self.city_flow[self.city_flow['new_classi']
                                              == 'Neighbourhood Residential street']
        neighborhood_vmt = self.vmt(neighborhood_flow_df)
        neighborhood_networklen = np.round(
            neighborhood_flow_df['LENGTH(meters)'].sum() * 0.000621371, decimals=0)
        total_networklen = np.round(
            self.city_flow['LENGTH(meters)'].sum() * 0.000621371, decimals=0)
        prop = (neighborhood_vmt / total_vmt) / \
            (neighborhood_networklen / total_networklen)

        return total_vmt, self.round_two_decimals(prop), neighborhood_vmt

    def vhd(self, flow, speed, delaydf=False):
        """ 
        Input: flow and speed df with both having length attribute
        Output: VHD for whole area
        """
        d_f = flow.copy()
        d_f.set_index('link_id', inplace=True)
        d_f.loc[:, "00:00":"23:45"] = d_f.loc[:,
                                              "00:00":"23:45"] * 15 * 60  # flow to count

        d_time = speed.copy()
        d_time.set_index('link_id', inplace=True)
        d_time.loc[:, "00:00":"23:45"] = np.reciprocal(
            d_time.loc[:, "00:00":"23:45"])
        d_time.loc[:, "00:00":"23:45"] = d_time.loc[:, "00:00":"23:45"].mul(
            d_time['LENGTH(meters)'], axis=0)  # speed to time (in seconds)

        # freeflow tt in seconds
        d_time['tt_free'] = d_time['LENGTH(meters)'] / \
            (d_time['SPEED_KPH'] * 0.277778)
        d_delay = d_time.iloc[:, np.r_[0:96, -1]]
        d_delay = d_delay.sub(d_delay['tt_free'], axis=0)  # delay in seconds
        # convert negative delays to 0 . Negative delays occur because sometimes speeds are higher in 4th digit in the simulation due to rounding off numeric error in simulator
        d_delay[d_delay < 0] = 0
        # delay multiply by count
        delay_count_df = d_delay.loc[:, "00:00":"23:45"].mul(
            d_f.loc[:, "00:00":"23:45"])  # vehicle seconds delay

        if delaydf == False:
            # VHD
            return np.round(delay_count_df.sum().sum() / 3600, decimals=0)
        else:
            delay_count_df['VHD_link'] = delay_count_df.sum(
                axis=1) / 3600  # vehicle hours delay for each link
            delay_count_df.reset_index(inplace=True)
            return delay_count_df  # hours

    def vhd_city(self):
        total_vhd = self.vhd(self.city_flow, self.city_speed)

        if total_vhd > 0:
            neighborhood_flow_df = self.city_flow[self.city_flow['new_classi']
                                                  == 'Neighbourhood Residential street']
            neighborhood_speed_df = self.city_speed[self.city_speed['new_classi']
                                                    == 'Neighbourhood Residential street']
            neighborhood_vhd = self.vhd(
                neighborhood_flow_df, neighborhood_speed_df)
            neighborhood_networklen = np.round(
                neighborhood_flow_df['LENGTH(meters)'].sum() * 0.000621371, decimals=0)
            total_networklen = np.round(
                self.city_flow['LENGTH(meters)'].sum() * 0.000621371, decimals=0)
            prop = (neighborhood_vhd / total_vhd) / \
                (neighborhood_networklen / total_networklen)
        else:  # adjusting for 0 vhd in load calculations
            prop = 0
            neighborhood_vhd = 0

        return total_vhd, self.round_two_decimals(prop), neighborhood_vhd

    def fuel_gallons(self, fuel_city):
        """
        Fuel consumption
        """
        time = fuel_city.columns[1:97]
        fuel_b = []
        for i in time:
            fuel_b.append(fuel_city[i].sum())
        fuelga = np.sum(fuel_b) * 0.264172  # gallons
        return self.round_two_decimals(fuelga)

    def congested8am_miles(self, flow):
        flow['v_c8am'] = flow['08:00'] / flow['CAPACITY(veh/hour)'] * 3600
        congested_miles = flow[flow['v_c8am'] >=
                               1]['LENGTH(meters)'].sum() / 1000 * 0.621371
        return self.round_two_decimals(congested_miles)

    def SPF_segments(self, flow):
        alpha_highways = {1: 0, 2: -7.09, 3: -7.09, 4: -5.78, 5: -6.49,
                          6: -6.49, 7: -6.49, 8: -10.75}  # 1 lnae is ramps, so added as 0
        beta_highways = {1: 0, 2: 0.98, 3: 0.98,
                         4: 0.82, 5: 0.89, 6: 0.89, 7: 0.89, 8: 1.24}

        fc2_flow = flow[flow['FUNC_CLASS'].isin([1, 2])]
        fc2_flow['ADT'] = fc2_flow.iloc[:, 1:97].sum(axis=1) * 15 * 60

        fc2_flow['alpha'] = fc2_flow['NUM_PHYS_LANES'].map(alpha_highways)
        fc2_flow['beta'] = fc2_flow['NUM_PHYS_LANES'].map(beta_highways)
        fc2_flow['SPF'] = (fc2_flow['LENGTH(meters)'] * 0.000621371) * \
            (np.exp(fc2_flow['alpha'])) * (fc2_flow['ADT']**fc2_flow['beta'])
        return int(fc2_flow['SPF'].sum())
