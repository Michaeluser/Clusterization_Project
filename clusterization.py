import json
import os
import numpy as np
import random
import math
import cffi


#METHOD
medoid = True


#GLOBAL_VARIABLES
t_md = True
pr_points = [] #physicaal representation of points
points_amount = 10000
cluster_mask = [p for p in range(points_amount)] #what each each point on dist_matrix represents(custer or point)
cr_info = {} #info dict about every cluster, that has structure: [[[x,y], average_incluster_distance, cns_f, color][p1, p2, p3...]] p1, p2, p3 are points indices in the pr_points

ffi = cffi.FFI()
C_module = ffi.dlopen("./functions.so")
    
WIDTH = 800
HEIGHT = 800


x_margins = (-5000, 5000)
y_margins = (-5000, 5000)
avg_idc = 250

dists_matrix = np.zeros(shape = (points_amount, points_amount), dtype = np.float32)


#UTILITY_FUNCTIONS

def recalculate_dists(target_point, rocol_value, matrix):
    row_size = matrix.shape[1]
    col_size = matrix.shape[0]
    
    if(t_md):
        if(row_size < 1500):
            for row in range(row_size):
                if(type(cluster_mask[row]) == int):
                    point = pr_points[cluster_mask[row]]
                else:
                    point = cr_info[cluster_mask[row]][0][0]
                matrix[row][rocol_value] = abs(point[0] - target_point[0]) + abs(point[1] - target_point[1])

            for col in range(col_size):
                matrix[rocol_value][col] = matrix[col][rocol_value]
        else:
            points_array = []
            point = None
            for row in range(row_size):
                if(type(cluster_mask[row]) == int):
                    point = pr_points[cluster_mask[row]]
                else:
                    point = cr_info[cluster_mask[row]][0][0]
                points_array.append(point)
            
            inner_arrs = [ffi.new("short[2]", p) for p in points_array]
            ptr_array = ffi.new("short*[]", inner_arrs)
            
            out_array = C_module.calculate_vector(target_point, ptr_array, len(points_array))
            out_array = np.frombuffer(ffi.buffer(out_array, len(points_array) * ffi.sizeof("float")), dtype = np.float32)
            
            matrix[:, rocol_value] = out_array
            matrix[rocol_value, :] = out_array
    else:
        for row in range(row_size):
            if(type(cluster_mask[row]) == int):
                point = pr_points[cluster_mask[row]]
            else:
                point = cr_info[cluster_mask[row]][0][0]
            matrix[row][rocol_value] = abs(point[0] - target_point[0]) + abs(point[1] - target_point[1])

        for col in range(col_size):
            matrix[rocol_value][col] = matrix[col][rocol_value]
            
    
    matrix[rocol_value][rocol_value] = 50000
        
def cavr_dist(centroid, points):
    p_amnt = len(points)
    avg_d = 0
    for i in range(p_amnt):
        i_point = pr_points[points[i]]
        avg_d += math.sqrt((centroid[0] - i_point[0])**2 + (centroid[1] - i_point[1])**2)
    avg_d /= p_amnt
    return avg_d
    
#crap(CReate or APpend a cluster)
def crap_cluster(crr, crl, crr_name, crl_name, cd_f): #crr_name is either name of a cluster string:"C1C2C15" or index of a point:42
    x1, y1, x2, y2 = None, None, None, None
    new_cluster = [[[-1, -1], -1, True, None], []]
    crr_flag = isinstance(crr, (list, tuple)) and len(crr) == 2 and all(isinstance(v, (int, float)) for v in crr)
    crl_flag = isinstance(crl, (list, tuple)) and len(crl) == 2 and all(isinstance(v, (int, float)) for v in crl)

    crr_avg = None
    crl_avg = None
    
    if crr_flag:
        x1, y1 = crr
    else:
        new_cluster[1].extend(crr[1])
        x1, y1 = crr[0][0][0], crr[0][0][1]
        if(cd_f): crr_avg = cavr_dist([x1, y1], crr[1])
        
    if crl_flag:
        x2, y2 = crl
    else:
        new_cluster[1].extend(crl[1])
        x2, y2 = crl[0][0][0], crl[0][0][1]
        if(cd_f): crl_avg = cavr_dist([x2, y2], crl[1])
    
    
    if (crl_flag and crr_flag):
        c_x = (x1 + x2) / 2
        c_y = (y1 + y2) / 2
        new_cluster[0][0][0] = c_x
        new_cluster[0][0][1] = c_y
        new_cluster[1].append(crr_name)
        new_cluster[1].append(crl_name)
    else:
        if (not crr_flag and crl_flag):
            new_cluster[1].append(crl_name)
        elif(crr_flag and not crl_flag):
            new_cluster[1].append(crr_name)
        c_points = new_cluster[1]
        
        c_x, c_y = None, None
        if(not medoid):
            c_x, c_y = comp_centroid(c_points, len(c_points))
        else:
            c_x, c_y = locate_medoid(c_points)
            
        new_cluster[0][0][0] = c_x
        new_cluster[0][0][1] = c_y
    
    if(cd_f): #cd_f means calculate distance flag
        avg_dist = cavr_dist(new_cluster[0][0], new_cluster[1])
        if (avg_dist > avg_idc):
            if(crr_flag and not crl_flag):
                crl[0][2] = False
                return crl
            elif(not crr_flag and crl_flag):
                crr[0][2] = False
                return crr
            elif(not crr_flag and not crl_flag):
                if(crr_avg > crl_avg):
                    crr[0][2] = False
                    return crr
                else:
                    crl[0][2] = False
                    return crl
        elif (avg_dist == avg_idc):
            new_cluster[0][2] = False
        new_cluster[0][1] = avg_dist
    
    return new_cluster
            
        

def locate_medoid(c_points):
    n_p = len(c_points)
    centroid = comp_centroid(c_points, n_p)
    medoid = None
    min_dist = abs(pr_points[c_points[0]][0] - centroid[0]) + abs(pr_points[c_points[0]][1] - centroid[1])
    for i, p in enumerate(c_points):
        dist = abs(pr_points[p][0] - centroid[0]) + abs(pr_points[p][1] - centroid[1])
        if(dist <= min_dist): 
            min_dist = dist
            medoid = pr_points[p]
    return medoid
        
def comp_centroid(c_points, points_amount):
    x_cord = 0
    y_cord = 0
    for i in range(points_amount):
        x_cord += pr_points[c_points[i]][0]
        y_cord += pr_points[c_points[i]][1]
    x_cord /= points_amount
    y_cord /= points_amount
    return [x_cord, y_cord]

def calculate_distances():
    for i in range(points_amount):
        i_point = pr_points[i]
        for k in range(i, points_amount):
            if (i == k): dists_matrix[i][k] = 0; continue
            dists_matrix[i][k] = abs(i_point[0] - pr_points[k][0]) + abs(i_point[1] - pr_points[k][1]) #calculating manhattan distance to simplify computation cost
            # print(f"{i} & {k}", end = ",")
    for l in range(points_amount):
        for p in range(l):
            dists_matrix[l][p] = dists_matrix[p][l]
            
def generate_anchors():
    anchor_offset = 10 #offset is used to guarantee that anchor points are generated at the ledge of the map
    k = 0
    pr_points_set = set(tuple(p) for p in pr_points)
    while k < 20:
        x_cord = random.randint(x_margins[0] + anchor_offset, x_margins[1] - anchor_offset)
        y_cord = random.randint(y_margins[0] + anchor_offset, y_margins[1] - anchor_offset)
        if ((x_cord, y_cord) not in pr_points_set): 
            pr_points.append([x_cord, y_cord])
            pr_points_set.add((x_cord, y_cord))
        else:
            continue
        k += 1

def generate_residuum():
    pindex = 0
    pr_points_set = set(tuple(p) for p in pr_points)
    while pindex < (points_amount - 20):
        x_offset = random.randint(-100, 100)
        y_offset = random.randint(-100, 100)
        
        point = random.choice(pr_points)
        x_cord = point[0] + x_offset
        y_cord = point[1] + y_offset
        
        x_cord = min(x_cord, 5000)
        if (x_cord < -5000): x_cord = -5000
        
        y_cord = min(y_cord, 5000) 
        if (y_cord < -5000): y_cord = -5000
        
        if((x_cord, y_cord) not in pr_points_set):
            pr_points.append([x_cord, y_cord])
            pr_points_set.add((x_cord, y_cord))
        else:
            continue
        pindex += 1
        
#CLEAN DIRECTORY
pr_file = "pr_points.json"
cr_file = None
num = 0

try:
    os.remove(pr_file)
except FileNotFoundError:
    pass

while True:
    cr_file = f"cr_info{num}.json"
    try:
        os.remove(cr_file)
    except FileNotFoundError:
        break
    num += 1
        
#PREPARE_MAP
generate_anchors()
generate_residuum()
if(t_md):
    inner_arrays = [ffi.new("short[2]", p) for p in pr_points]
    ptr_arr = ffi.new("short*[]", inner_arrays)
    ffi.cdef("""float* calculate_distances(short* array[], int m_size);""")
    ffi.cdef("""float* calculate_vector(short target_point[2], short* points_array[], short size);""")
    dists_matrix = C_module.calculate_distances(ptr_arr, points_amount)
else:
    calculate_distances()
    

#MAIN ALGORITHM
if (t_md):
    dists_matrix = np.frombuffer(ffi.buffer(dists_matrix, points_amount ** 2 * ffi.sizeof("float")), dtype = np.float32)
    dists_matrix = np.reshape(dists_matrix, (points_amount, points_amount))

with open("pr_points.json", "w") as file:
    json.dump(pr_points, file, indent = 4)

ctr = 0
cd_f = False
cluster_numerator = 0
nmb = 0
while (True):
    print(f"{ctr} - gen")
    m_idx = np.unravel_index(np.argmin(dists_matrix), dists_matrix.shape)
    
    if (dists_matrix.shape[0] <= 1):
        # The clustering is complete or nearly complete. Stop processing.
        break
    
    if (dists_matrix.shape[0] <= 100):
        cd_f = True
    
    rel_class = None #value of 1 represents a cluster, value of 0 represents a point
    cel_class = None #value of 1 represents a cluster, value of 0 represents a point
    crr = None #represents a cluster or a point
    crl = None #represents a cluster or a point
    
    crr_name = cluster_mask[m_idx[0]] #make crr_name represent the point by its index in pr_points
    crl_name = cluster_mask[m_idx[1]] #make crl_name represent the point by its index in pr_points
    rel_class = 0 if(type(crr_name) == int) else 1
    cel_class = 0 if(type(crl_name) == int) else 1
    
    if(rel_class == 0):
        crr = pr_points[crr_name] #get point coordinates
    else:
        crr = cr_info[crr_name] #get cluster instance
        
    if(cel_class == 0):
        crl = pr_points[crl_name] #get point coordinates
    else:
        crl = cr_info[crl_name] #get cluster instance
        
    cluster = crap_cluster(crr, crl, crr_name, crl_name, cd_f) #creating a new cluster out of existing pair of (point, point); (point, cluster); (cluster, cluster)
    if(cluster[0][2] == False):
        if(cluster[0][1] == avg_idc):
            i, j = sorted(m_idx, reverse=True)
            for idx in (i, j):
                dists_matrix = np.delete(dists_matrix, idx, axis=0)
                dists_matrix = np.delete(dists_matrix, idx, axis=1)
                del cluster_mask[idx] #get rid of the row cluster

            if(rel_class == 1):
                try:
                    del cr_info[crr_name] #deleting old cluster that now is part of a bigger cluster
                except KeyError:
                    # print("Key Error")
                    pass
            
            if(cel_class == 1):
                try:
                    del cr_info[crl_name] #deleting old cluster that now is part of a bigger cluster
                except KeyError:
                    # print("Key Error")
                    pass
            
            ncluster_name = f"C{cluster_numerator}"
            cluster_numerator += 1
            cr_info[ncluster_name] = cluster
        else:
            xx_cond = crr[0][0][0] == cluster[0][0][0]
            yy_cond = crr[0][0][1] == cluster[0][0][1]
            if(xx_cond and yy_cond):
                dists_matrix = np.delete(dists_matrix, m_idx[0], axis = 0)  #delete i-th row
                dists_matrix = np.delete(dists_matrix, m_idx[0], axis = 1)  #delete i-th column
                try:
                    del cluster_mask[m_idx[0]]
                except KeyError:
                    # print("Key Error")
                    pass
            else:
                dists_matrix = np.delete(dists_matrix, m_idx[1], axis = 0)  #delete p-th row
                dists_matrix = np.delete(dists_matrix, m_idx[1], axis = 1)  #delete p-th column
                try:
                    del cluster_mask[m_idx[1]]
                except KeyError:
                    # print("Key Error")
                    pass
        ctr += 1
        continue
    if(rel_class == 1):
        try:
            del cr_info[crr_name] #deleting old cluster that now is part of a bigger cluster
        except KeyError:
            # print("Key Error")
            pass

    if(cel_class == 1):
        try:
            del cr_info[crl_name] #deleting old cluster that now is part of a bigger cluster
        except KeyError:
            # print("Key Error")
            pass
    
    ncluster_name = f"C{cluster_numerator}"
    cluster_numerator += 1
    cr_info[ncluster_name] = cluster
    
    #thus we're left with p-th row and column
    i, j = sorted(m_idx, reverse = True)
    
    dists_matrix = np.delete(dists_matrix, i, axis=0)
    dists_matrix = np.delete(dists_matrix, i, axis=1)
    del cluster_mask[i]
    
    cluster_mask[j] = ncluster_name
    recalculate_dists(cluster[0][0], j, dists_matrix) #recalculate distances to the newly created cluster
    
    
    if(len(cr_info) < 30 and dists_matrix.shape[0] < 100):
        with open(f"cr_info{nmb}.json", "w") as file:
            json.dump(cr_info, file, indent = 4)
        nmb += 1
        
    ctr += 1

