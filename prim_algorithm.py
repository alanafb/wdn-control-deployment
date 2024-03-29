# -*- coding: utf-8 -*-
"""
Created on Tue Nov 21 20:00:17 2023

@author: alana
"""

import sys
import networkx as nx
import matplotlib.pyplot as plt
import warnings

# Suprimir todos los warnings (No se recomienda a menos que estés seguro de lo que estás haciendo)
warnings.filterwarnings("ignore")

class Graph():
    def __init__(self, vertices, cable=None, inalambrica=None):
        self.V = vertices
        self.graph = [[0 for column in range(vertices)]
                      for row in range(vertices)]
        self.cable = cable
        self.inalambrica = inalambrica

    def printMST(self, parent, cable, inalambrica, selectores):
        print("Edge \tWeight")
        for i in range(1, self.V):
            if cable is not None and inalambrica is not None:
                active_graph = cable if selectores[i-1] == 1 else inalambrica
                print(parent[i], "-", i, "\t", active_graph[i][parent[i]])
            else:
                print(parent[i], "-", i, "\t", self.graph[i][parent[i]])



    def minKey(self, key, mstSet):
        min = sys.maxsize
        for v in range(self.V):
            if key[v] < min and mstSet[v] == False:
                min = key[v]
                min_index = v
        return min_index

    def constructMST(self, parent):
        MST = nx.Graph()
        for i in range(1, self.V):
            if parent[i] is not None:
                MST.add_edge(parent[i], i, weight=self.graph[i][parent[i]])
        return MST

    def visualizeMST(self, MST):
        try:
            pos_mst = nx.kamada_kawai_layout(MST) if MST.number_of_nodes() <= 50 else nx.shell_layout(MST)
        except nx.NetworkXError as e:
            print("Error al generar el layout del MST:", e)
            pos_mst = None

        if pos_mst:
            plt.figure(figsize=(8, 6))
            plt.title('Minimum Spanning Tree (MST)')
            nx.draw(MST, pos_mst, with_labels=True, node_size=500, node_color='skyblue', font_weight='bold')
            labels_mst = nx.get_edge_attributes(MST, 'weight')
            nx.draw_networkx_edge_labels(MST, pos_mst, edge_labels=labels_mst)
            plt.show()

    def createNodesDictionary(self, parent):
        nodes = {}
        for i in range(self.V):
            nodes[i] = {'is_SCADA': (i == 0), 'connections': []}

        for i in range(1, self.V):
            nodes[parent[i]]['connections'].append(i)

        for node_id, data in nodes.items():
            print(f"Node {node_id}: {data['connections']}")

        return nodes


    def primMST(self):
        key = [sys.maxsize] * self.V
        parent = [None] * self.V
        key[0] = 0
        mstSet = [False] * self.V
        parent[0] = -1

        # Antes del bucle
        selectores = []

        for cout in range(self.V):
            u = self.minKey(key, mstSet)
            mstSet[u] = True

            if self.cable is not None and self.inalambrica is not None:
                # Preguntar al usuario qué matriz desea utilizar
                choice = input(f"Para la iteración {cout + 1}, ¿desea utilizar la matriz cable o la matriz inalámbrica? (1/2): ")

                # Verificar la elección y actualizar self.graph en consecuencia
                if choice == '1':
                    self.graph = self.cable
                    selectores.append(1)
                elif choice == '2':
                    self.graph = self.inalambrica
                    selectores.append(2)
                else:
                    print("Opción no válida. Utilizando la matriz por defecto.")
                    self.graph = self.cable
                    selectores.append(1)

            for v in range(self.V):
                if self.graph[u][v] > 0 and mstSet[v] == False and key[v] > self.graph[u][v]:
                    key[v] = self.graph[u][v]
                    parent[v] = u

        self.printMST(parent, self.cable, self.inalambrica, selectores)

        MST = self.constructMST(parent)
        self.visualizeMST(MST)

        nodes = self.createNodesDictionary(parent)
        return nodes
