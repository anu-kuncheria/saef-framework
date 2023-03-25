from load_data import *
import sys
sys.path.append('../src')
from functools import reduce
import traffic_metrics as tr

simulations_run = [list(simulations["sim1"].values()), list(simulations["sim2"].values()),
list(simulations["sim3"].values()),list(simulations["sim4"].values())]

allsim_data = []
for sim in simulations_run:
    print(f" ============= Starting {sim[0]} =========")
    data = []
    dir_names = [f for f in os.listdir(clippedlinks_dir) if not f.startswith('.')]

    for d in dir_names:
        cityname = d
        print(f" Starting city {cityname} ....")
        citylinks_path = os.path.join(clippedlinks_dir,d, f'citylinks_{cityname}.geojson')

        traff = tr.MobilitiAnalysis(citylinks_path, flow_path = sim[1], speed_path = sim[2], fuel_path = sim[3])
        total_vmt, nrs_vmtload = traff.vmt_city()
        total_vhd, nrs_vhdload = traff.vhd_city()
        total_fuel = traff.fuel_gallons(traff.city_fuel)
        congested_8am_miles = traff.congested8am_miles(traff.city_flow)
        estimated_highway_accidents = traff.SPF_segments(traff.city_flow)

        data.append(
            {'city': d,
            f'vmt_{sim[0]}': total_vmt,
            f'vhd_{sim[0]}': total_vhd,
            f'fuel_{sim[0]}': total_fuel,
            f'vmtload_nrs_{sim[0]}':nrs_vmtload,
            f'vhdload_nrs_{sim[0]}':nrs_vhdload,
            f'cong_miles_{sim[0]}': congested_8am_miles,
            f'highway_acc_{sim[0]}': estimated_highway_accidents })

    allsim_data.append(data)

b60_df, uet_df, sot_df, sof_df= pd.DataFrame(allsim_data[0]), pd.DataFrame(allsim_data[1]), pd.DataFrame(allsim_data[2]), pd.DataFrame(allsim_data[3])
traffic_df = reduce(lambda x,y: pd.merge(x,y, on='city', how='outer'), [b60_df, uet_df, sot_df, sof_df])
print(traffic_df.shape)
print(traffic_df.head(2))
print(traffic_df.columns)
traffic_df.to_csv("../data/metrics/cities_mobility_metrics.csv", index = False)

