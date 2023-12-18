import wntr
import networkx as nx
import numpy as np
from prim_algorithm import Graph

def obtener_resultado(inp_file, nodos_sensorizados):
    # Cargar el modelo de la red de distribución de agua
    wn = wntr.network.WaterNetworkModel(inp_file)

    # Crea una matriz vacía para almacenar las distancias entre nodos críticos
    num_nodos = len(nodos_sensorizados)
    dist_matrix = np.zeros((num_nodos, num_nodos))
        
    # Convertir la red de WNTR a un grafo de NetworkX
    grafo = wn.to_graph()
    # Seleccionar dos nodos para calcular la distancia
    # Calcula las distancias entre todos los pares de nodos críticos
    for i, source_node in enumerate(nodos_sensorizados):
        for j, target_node in enumerate(nodos_sensorizados):
            if i != j:
                distance = nx.shortest_path_length(grafo.to_undirected(), source=source_node, target=target_node)
                dist_matrix[i][j] = distance
                
    # Imprime la matriz de distancias entre nodos críticos
    print("Matriz de distancias entre nodos sensorizados:")
    print(dist_matrix)

    # Crear un diccionario para mapear los índices de la matriz a las etiquetas de nodos
    index_to_label = {i: nodo for i, nodo in enumerate(nodos_sensorizados)}

    # Imprimir el diccionario de mapeo
    print("Índice de nodo en la matriz : Etiqueta del nodo")
    for index, label in index_to_label.items():
        print(f"{index}: {label}")

    g = Graph(len(nodos_sensorizados))
    g.graph = dist_matrix

    result = g.primMST()

    return result, index_to_label

