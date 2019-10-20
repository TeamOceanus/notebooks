import netCDF4
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx

def polar_deg(x, y):
    z = x * 1j + y
    return np.angle(z)

def grid_coord(x, y):
    return (x - x % 5, y - y % 5)

def in_range(x, y):
    return 0 <= x < 360 and 0 <= y < 140

dataset = netCDF4.Dataset('./datasets/world_oscar_vel_5d2019.nc.gz')

uf = dataset.variables['uf'][0,0].data
vf = dataset.variables['vf'][0,0].data

graph = nx.DiGraph()
for x in range(0, 360, 5):
    for y in range(0, 140, 5):
        graph.add_node((x, y))

deg = polar_deg(uf, vf)
deg = np.swapaxes(deg, 1, 0)
dx = [5, 5, 0, -5, -5, -5, 0, 5]
dy = [0, -5, -5, -5, 0, 5, 5, 5]
edges_dict = dict()
for x in range(0, 360):
    for y in range(0, 140):
        if np.isnan(deg[x,y]):
            continue
        for i in range(8):
            if 2 * np.pi / 8 * i <= deg[x,y] < 2 * np.pi * (i + 1):
                gridx, gridy = grid_coord(x, y)
                nextx = gridx + dx[i]
                nexty = gridy + dy[i]
                if not in_range(nextx, nexty):
                    continue
                if ((gridx, gridy), (nextx, nexty)) not in edges_dict:
                    edges_dict[((gridx, gridy), (nextx, nexty))] = 1
                else:
                    edges_dict[((gridx, gridy), (nextx, nexty))] += 1

ebunch = [key + ({'capacity': val},) for key, val in edges_dict.items()]
print(ebunch)
graph.add_edges_from(ebunch)

centrality = nx.algorithms.in_degree_centrality(graph)
print(centrality)
print(max(centrality.keys()))
centrality_map = np.zeros((360, 140))
for key, val in centrality.items():
    for x in range(key[0], key[0] + 5):
        for y in range(key[1], key[1] + 5):
            centrality_map[x][y] = val

plt.figure(figsize=(18, 8))
plt.imshow(centrality_map.swapaxes(1, 0))
plt.show()
