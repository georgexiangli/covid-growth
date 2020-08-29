from math import sqrt
import numpy as np
import copy


def main():
    print("Program Start")
    d_dict = {}
    with open('time_series_covid19_deaths_global.csv') as f:
        
        data = list(f)[1:]
        
        for d in data:
            l = d.strip('\n').split(',')
            c = l[1] # country
            
            add_row(c, d_dict, l, 4)

    with open('time_series_covid19_deaths_US.csv') as f:
        data = list(f)[1:]
        for d in data:
            l = d.strip('\n').split(',')
            c = l[7]
            add_row(c, d_dict, l, 11)

    f.close()

    for c in d_dict:
        d_dict[c] = [int(round(item)) for item in d_dict[c]]

    #------------------------------------------------
    # Find US and Canadian data
    us_data_str = ",".join(str(item) for item in d_dict['US'])
    canada_data_str = ",".join(str(item) for item in d_dict['Canada'])

    with open('File Path for US_CAN_data.txt', 'w') as out_file:
        out_file.write(us_data_str + '\n')
        out_file.write(canada_data_str)

    out_file.close()

    #------------------------------------------------
    # Find US and Canada daily mortality increase
    us_diff = [x - y for x, y in zip(d_dict['US'][1:], d_dict['US'])]
    us_diff_str = ",".join(str(item) for item in us_diff)
    canada_diff = [x - y for x, y in zip(d_dict['Canada'][1:], d_dict['Canada'])]
    canada_diff_str = ",".join(str(item) for item in canada_diff)

    with open('File Path for US_CAN_diff.txt', 'w') as out_file:
        out_file.write(us_diff_str + '\n')
        out_file.write(canada_diff_str)

    out_file.close()

    #------------------------------------------------
    # Feature computation

    f_dict = {}

    out_file = open('File Path for 2_4_8_features.txt', 'w')

    for c in d_dict:
        # print(c)
        country_data = d_dict[c]
        f_dict[c] = {} 
        f_dict[c]['days'] = [-1, -1, -1]
        f_dict[c]['days'][0], f_dict[c]['days'][1], f_dict[c]['days'][2] = days_to(country_data, 2, 4, 8)
        out_file.write(",".join(str(item) for item in f_dict[c]['days']) + '\n')

    out_file.close()

    #------------------------------------------------
    # Hierarchical Clustering
    # Single Linkage
    k = 8
    clusters = hierarchical_clustering(f_dict, k, 'SLD')

    for i in range(len(clusters)):
        for country in clusters[i]:
            f_dict[country]['sld_cluster'] = i
    
    out_file = open('File Path for single_linkage.txt', 'w')

    sld_clusters = []

    for country in f_dict:
        sld_clusters.append(str(f_dict[country]['sld_cluster']))

    out_file.write(",".join(sld_clusters))

    out_file.close()

    #------------------------------------------------
    # Hierarchical Clustering
    # Complete Linkage
    clusters = hierarchical_clustering(f_dict, k, 'CLD')

    for i in range(len(clusters)):
        for country in clusters[i]:
            f_dict[country]['cld_cluster'] = i
    
    out_file = open('File Path for complete_linkage.txt', 'w')

    cld_clusters = []

    for country in f_dict:
        cld_clusters.append(str(f_dict[country]['cld_cluster']))

    out_file.write(",".join(cld_clusters))

    out_file.close()

    #------------------------------------------------
    # k-means
    clusters, centers = kmeans(f_dict, k)

    for i in range(len(clusters)):
        # print(clusters[i])
        for country in clusters[i]:
            f_dict[country]['kmeans'] = i

    out_file = open('File Path for kmeans_clusters.txt', 'w')

    kmeans_clusters = []

    for country in f_dict:
        kmeans_clusters.append(str(f_dict[country]['kmeans']))

    out_file.write(",".join(kmeans_clusters))

    out_file.close()

    out_file = open('File Path for kmeans_centers.txt', 'w')

    for center in centers:
        out_file.write(",".join([str(item) for item in center]) + '\n')
    
    out_file.close()

    #------------------------------------------------
    # Distortion

    distortion = 0

    for cluster in clusters:
        center = find_center(cluster, f_dict)
        for country in cluster:
            c_days = f_dict[country]['days']
            distance = euclidean(c_days, center, True)
            distortion += distance

    # for c in f_dict:
    #     c_days = f_dict[c]['days']
    #     c_cluster = f_dict[c]['kmeans']
    #     # print(c + ' ' + str(c_cluster))
    #     center = centers[c_cluster]

    #     distance = euclidean(c_days, center)
    #     print(distance)
    #     distortion += distance

    # print(clusters)
    # print(centers)

    out_file = open('File Path for distortion.txt', 'w')

    out_file.write(str(round(distortion, 4)))

    out_file.close()
    # print(centers)
    # print(distortion)

    # for cluster in clusters:
    #     print(center(cluster, f_dict))


    print("Program Finish")

def add_row(c, d_dict, row, data_start_idx):
    """Add country to data, summing provinces and states"""
    if c in d_dict:
        province_state_deaths = [float(x) for x in row[data_start_idx:]]
        d_dict[c] = [a + b for a, b in zip(province_state_deaths, d_dict[c])]

    else:
        d_dict[c] = [float(x) for x in row[data_start_idx:]]
    
def days_to(country_data, divisor1, divisor2, divisor3):
    """Returns index where value was less than or equal to specified amounts"""
    country_data_reversed = country_data[::-1]
    most_recent = country_data_reversed[0]

    if most_recent == 0:
        return 0, 0, 0

    value1 = most_recent // divisor1
    value2 = most_recent // divisor2
    value3 = most_recent // divisor3

    found1 = False
    found2 = False
    found3 = False

    for idx in range(len(country_data_reversed)):
        if not found1 and (country_data_reversed[idx] <= value1):
            days1 = idx
            found1 = True

            if value1 == 0:
                remaining_values = (len(country_data) - (days1 + 1)) // 2
                return days1, remaining_values, remaining_values

        if not found2 and (country_data_reversed[idx] <= value2):
            days2 = idx - days1
            found2 = True

            if value2 == 0:
                return days1, days2, len(country_data) - (days1 + days2 + 1)

        if not found3 and (country_data_reversed[idx] <= value3):
            days3 = idx - (days2 + days1)
            found3 = True

    return days1, days2, days3

def euclidean(a, b, use_sum_of_squares=False):
    """Find the Euclidean distance between two points"""
    sum_of_squares = sum((a[i]-b[i])**2 for i in range(len(a)))
    
    if use_sum_of_squares:
        return sum_of_squares

    return sqrt(sum_of_squares)

# linkage distance
def clustering_distance(cluster1, cluster2, f_dict, clustering_type): 
    """Find linkage distance for hierarchical clustering"""
    res = float('inf')

    if clustering_type == 'CLD':
        res *= -1

    # c1, c2 each is a country in the corresponding cluster
    for c1 in cluster1:
        for c2 in cluster2:
            dist = euclidean(f_dict[c1]['days'], f_dict[c2]['days'])
            if clustering_type == 'SLD' and dist < res:
                res = dist
            
            if clustering_type == 'CLD' and dist > res:
                res = dist
    return res

# hierarchical clustering (sld, 'euclidean')
def hierarchical_clustering(f_dict, k, clustering_type):
    """Method for creating hierarchical clusters"""
    n = len(f_dict)
    clusters = [{d} for d in f_dict.keys()]
    for _ in range(n-k):
        dist = float('inf')
        best_pair = (None, None)
        for i in range(len(clusters)-1):
            for j in range(i+1, len(clusters)):
                test_dist = clustering_distance(clusters[i], clusters[j], f_dict, clustering_type)
                if test_dist < dist:
                    dist = test_dist
                    best_pair = (i,j)
        new_clu = clusters[best_pair[0]] | clusters[best_pair[1]]
        # del clusters[best_pair[0]]
        # del clusters[best_pair[1] - 1]
        clusters = [clusters[i] for i in range(len(clusters)) if i not in best_pair]
        clusters.append(new_clu)

    return clusters

def find_center(cluster, f_dict):
    """Find the center of a cluster"""
    return np.round(np.average([f_dict[c]['days'] for c in cluster], axis = 0), 4)

def kmeans(f_dict, k):
    """Method for k-means clustering"""
    countries = sorted([c for c in f_dict.keys()])
    init_num = np.random.choice(len(countries) - 1, k)
    clusters = [{countries[i]} for i in init_num]
    country_c = [countries[i] for i in init_num]

    print(init_num)
    # for c in country_c:
    #     print(f_dict[c]['days'])

    while True:
        new_clusters = [set() for _ in range(k)]
        centers = [find_center(cluster, f_dict) for cluster in clusters]
        # print(centers)
        for c in countries:
            clu_ind = np.argmin([euclidean(f_dict[c]['days'], centers[i]) for i in range(k)])
            new_clusters[clu_ind].add(c)
        # repeat until convergence
        if all(new_clusters[i] == clusters[i] for i in range(k)):
            return clusters, centers
        else:
            clusters = copy.deepcopy(new_clusters)

if __name__=="__main__":
    main()