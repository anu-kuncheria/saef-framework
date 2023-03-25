from collections import defaultdict

def ranking_worse(df, sim =  ['B60', "UET", 'SOT', 'SOF'], compare1 = 'B60', compare2 = 'SOF'):
    allcols = ['vmt_', 'vhd_','fuel_', 'vmtload_nrs_','vhdload_nrs_','cong_miles_','highway_acc_']
    rankdf = df[['city']]
    city_idx = []
    metric_maxval = []
    for col in allcols:
        coi = [f'{col}{s}' for s in sim]
        subdf = df[coi]
        rank = subdf.rank(1, method = 'first')
        city_idx .extend(list(rank.idxmax(axis = 1).index))
        metric_maxval.extend(list(rank.idxmax(axis = 1).values))
        rankdf = rankdf.merge(rank,  left_index=True, right_index=True)

    city_max = defaultdict(list)
    for f in range(len(metric_maxval)):
        city_max[city_idx[f]].append(metric_maxval[f])

    city_worse_df= pd.DataFrame(columns = ['city', compare1, compare2])
    for k,v in city_max.items():
        city_name = df.iloc[k,0]
        compare1_counter = 0
        compare2_counter = 0
        for eachv in city_max[k]:
            if eachv[-3:] == compare1 :
                compare1_counter += 1
            elif eachv[-3:] == compare2:
                compare2_counter += 1
        city_worse_df.loc[len(city_worse_df),:] = [city_name, compare1_counter, compare2_counter]
        city_worse_df[[compare1, compare2]] = city_worse_df[[compare1, compare2]].astype(int)

    return rankdf, city_worse_df

if __name__ == "__main__":
    trafficmetrics_cities = pd.read_csv("../data/metrics/cities_mobility_metrics.csv")
    rank_df, city_worse_df = ranking_worse(data = trafficmetrics_cities, sim =  ['B60', "UET", 'SOT', 'SOF'], compare1 = 'B60', compare2 = 'SOF')

