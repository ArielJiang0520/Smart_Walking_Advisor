import theta
from Cluster import Cluster

import sys
sys.path.append('./')
import database_getter

import random
from collections import defaultdict

# alpha is the boundary to determin if two places belong to the same cluster
# theta < alpha: not close enough; theta > alpha: close enough
ALPHA = 25

def fill_up_clusters(id_list, clusters):
    for i,id in enumerate(id_list):
        print(f'current loop: {i}\tcurrent clusters: {len(clusters)}\tcurrent id: {id}')
        if clusters == []:
            clusters.append(Cluster(head=id))
        else:
            max_index = -1
            max_score = -1e9
            for n,c in enumerate(clusters):
                s = theta.similarity(database_getter.get_location_info(id),\
                    database_getter.get_location_info(c.head))
                    #print(f"{n} {l} v.s. {c.get_head()} -> {s}")
                if s > max_score:
                    max_score = s
                    max_index = n
            if max_score < ALPHA:
                print("Add a new cluster for {}".format(\
                    database_getter.get_location_info(id)[0]))
                clusters.append(Cluster(head=id))
            else:
                print("{} belongs to the same cluster as {}".format(\
                    database_getter.get_location_info(id)[0],\
                    database_getter.get_location_info(clusters[max_index].head)[0]))
                clusters[max_index].add_member(id)
    return clusters

CLUSTERS = []
id_list = database_getter.get_location_index_as_list("1")
fill_up_clusters(id_list, CLUSTERS)
for n,c in enumerate(CLUSTERS):
    print(n)
    for m in c.members:
        print(f"\t{database_getter.get_location_info(m)[0]}")

# head_freq_set = set()
#
#id_list = database_getter.get_location_index_as_list("1")
# for i in range(5):
#     CLUSTERS = []
#     print(f"rep - {i+1}")
#     random.shuffle(id_list)
#     fill_up_clusters(id_list, CLUSTERS)
#     for n,c in enumerate(CLUSTERS):
#         if not c.is_empty():
#             print(n, database_getter.get_location_info(c.get_head())[0])
#             head_freq_set.add(c.get_head())
#
# sorted_candidates = sorted(list(head_freq_set),\
#     key=lambda x:database_getter.get_total_location_frequency(x),\
#     reverse=True)
#
# try:
#     sorted_candidates.remove(database_getter.get_user_home_id("1"))
# except:
#     pass
#
# fp = open('cluster log.txt',"w+")
# for c in sorted_candidates:
#     print(c, database_getter.get_total_location_frequency(c))
#     fp.write(database_getter.get_location_info(c)[0]+str(\
#         database_getter.get_total_location_frequency(c)))
#
# FINAL_CLUSTERS = []
# for x in range(5):
#     FINAL_CLUSTERS.append(Cluster())
#
# fill_up_clusters(sorted_candidates,FINAL_CLUSTERS)
#
# fp.write("final clusters")
# for n,c in enumerate(FINAL_CLUSTERS):
#     if not c.is_empty():
#         print(n, database_getter.get_location_info(c.get_head())[0])
#         fp.write(str(n) + " " + \
#             database_getter.get_location_info(c.get_head())[0])
