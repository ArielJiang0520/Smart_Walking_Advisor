import theta
from Cluster import Cluster

import sys
sys.path.append('./')
import database_getter

sys.path.append('./data analyzer/location analyzer')
import FindPlaces

import random
from collections import defaultdict

def classifier(uid, id, clusters):
    print("location name = {}".format(database_getter.get_location_info(uid,id)[0]))
    if not is_in_clusters(uid, id, clusters):
        print("Does not exist in clusters")
        if not fits_into_clusters(uid, id, clusters):
            print("Does not fit into any cluster")
            if not build_new_cluster(uid, id, clusters):
                return False
        else:
            print('Fits into one of the clusters')
    else:
        print("Exists in clusters")
    return True

def is_in_clusters(uid, id, clusters):
    for n,c in enumerate(clusters):
        if c.has_id(id):
            return n+1
    return 0


def fits_into_clusters(uid, id, clusters) -> bool:
    info = database_getter.get_location_info(uid, id)
    for c in clusters:
        if c.accept_id(info):
            c.add_member(id)
            return True
    return False

def build_new_cluster(uid, id, clusters) -> bool:
    print("Building a new cluster...")
    info = database_getter.get_location_info(uid, id)
    lat,long = info[2],info[3]
    types = [t for t in info[4].split(',') \
        if not database_getter.is_in_address_type(t)]
    associate_event = info[7]

    if associate_event == 'school':
        new_cluster = Cluster(uid=uid)
        id_list = database_getter.get_location_with_event_as_list(\
            uid,associate_event)
        new_cluster.init_cluster(set(id_list))
        clusters.append(new_cluster)
        return True

    for t in types:
        print(f"type = {t}")
        id_list = [i[1] for i in FindPlaces.get_nearby_places(location=(\
            lat,long), keyword=t, radius=theta.MAX_CLUSTER_RADIUS)]
        visited_ids = set(database_getter.contains_visited_places(\
            uid, id_list))

        print("\tvisted places that have the same type:")
        exclude = set()
        for v in visited_ids:
            v_info = database_getter.get_location_info(uid, v)
            n = is_in_clusters(uid, v, clusters)
            if n != 0:
                print("\t\t(already in another cluster)")
                v_types = [t for t in v_info[4].split(',') \
                    if not database_getter.is_in_address_type(t)]
                v_id_overlap = len(set(v_types)&set(types))
                v_cluster_overlap = len(set(v_types)&set(\
                    clusters[n-1].dominant_types))
                if v_id_overlap > v_cluster_overlap:
                    print("\t\t(removed from old cluster)")
                    clusters[n-1].remove_member(v)
                else:
                    exclude.add(v)
            print(f"\t\t{v} {v_info[0]}")

        if len(exclude) >= 3:
            print("warning: exclude length >= 3")

        visited_ids = visited_ids - exclude
        visited_ids.add(id)
        if len(visited_ids) >= theta.MIN_VISITED_PLACE:
            print("\t\thas enough to build a cluster!")
            new_cluster = Cluster(uid=uid)
            new_cluster.init_cluster(visited_ids)
            clusters.append(new_cluster)
            return True
    return False

id_list = database_getter.get_location_index_as_list("1")
random.shuffle(id_list)

clusters = []
alienated_points = []

for n,id in enumerate(id_list):
    print("=======================================================")
    name = database_getter.get_location_info("1",id)[0]
    if classifier(uid="1",id=id,\
        clusters=clusters):
        print(f'RESULT: {name} is in a cluster')
    else:
        print(f'RESULT: {name} did not build a cluster')
        alienated_points.append(id)

# print("\n\n++++++++++++++++++++++++++++++++++++++++++++++++++++")
# print("REVISIT")
# revisit = []
# new_alienated_points = []
# for a in alienated_points:
#     types = [t for t in database_getter.get_location_info(\
#         "1",a)[4].split(",") if not \
#         database_getter.is_in_address_type(t)]
#     if len(types) >= 3:
#         revisit.append(a)
#     else:
#         new_alienated_points.append(a)
#
# for id in revisit:
#     name = database_getter.get_location_info("1",id)[0]
#     if classifier(uid="1",id=id,\
#         clusters=clusters):
#         print(f'RESULT: {name} is in a cluster')
#     else:
#         print(f'RESULT: {name} did not build a cluster')
#         new_alienated_points.append(id)

print("\n\n++++++++++++++++++++++++++++++++++++++++++++++++++++")
for n,c in enumerate(clusters):
    print(c)
    c.store_to_database(n+1)

for a in alienated_points:
    name = database_getter.get_location_info("1",a)[0]
    print(name)
# print(database_getter.get_location_info("1","ChIJox2o9w3e3IARzsU0eAOfEFs"))
