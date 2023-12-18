# -*- coding: utf-8 -*-
"""
Created on Tue Nov 21 20:00:17 2023

@author: alana
"""

import sys
import networkx as nx
import matplotlib.pyplot as plt

class Graph():
    def __init__(self, vertices):
        self.V = vertices
        self.graph = [[0 for column in range(vertices)]
                        for row in range(vertices)]

    def printMST(self, parent):
        print("Edge \tWeight")
        for i in range(1, self.V):
            print(parent[i], "-", i, "\t", self.graph[i][parent[i]])

    def minKey(self, key, mstSet):
        min = sys.maxsize
        for v in range(self.V):
            if key[v] < min and mstSet[v] == False:
                min = key[v]
                min_index = v
        return min_index

    def primMST(self):
        key = [sys.maxsize] * self.V
        parent = [None] * self.V
        key[0] = 0
        mstSet = [False] * self.V
        parent[0] = -1

        for cout in range(self.V):
            u = self.minKey(key, mstSet)
            mstSet[u] = True
            for v in range(self.V):
                if self.graph[u][v] > 0 and mstSet[v] == False and key[v] > self.graph[u][v]:
                    key[v] = self.graph[u][v]
                    parent[v] = u
                    
        # Crear el diccionario de nodos con conexiones y is_first_node
        nodes = {}
        for i in range(self.V):
            nodes[i] = {'is_SCADA': (i == 0), 'connections': []}

        # Crear las conexiones en cada nodo excepto en el nodo raíz (0)
        for i in range(1, self.V):
            nodes[parent[i]]['connections'].append(i)
            nodes[i]['connections'].append(parent[i])

        self.printMST(parent)
        
        MST = nx.Graph()
        for i in range(1, self.V):
            if parent[i] is not None:
                MST.add_edge(parent[i], i, weight=self.graph[i][parent[i]])

        try:
            # Cambiar el método de generación del layout del MST
            pos_mst = nx.kamada_kawai_layout(MST) if MST.number_of_nodes() <= 50 else nx.shell_layout(MST)
        except nx.NetworkXError as e:
            print("Error al generar el layout del MST:", e)
            pos_mst = None

        if pos_mst:
            # Visualización del MST
            plt.figure(figsize=(8, 6))
            plt.title('Minimum Spanning Tree (MST)')
            nx.draw(MST, pos_mst, with_labels=True, node_size=500, node_color='skyblue', font_weight='bold')
            labels_mst = nx.get_edge_attributes(MST, 'weight')
            nx.draw_networkx_edge_labels(MST, pos_mst, edge_labels=labels_mst)
            plt.show()
            
        return nodes