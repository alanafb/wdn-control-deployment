import wntr
from math import sqrt
import numpy as np
from prim_algorithm import Graph

def euclidean_distance(coord1, coord2):
    x1, y1 = coord1
    x2, y2 = coord2
    distance = sqrt((x2 - x1)**2 + (y2 - y1)**2) / 1000
    return round(distance, 2)

def calcular_distancias(inp_file, nodos_sensorizados):
    # Cargar el modelo de la red de distribución de agua
    wn = wntr.network.WaterNetworkModel(inp_file)
    # Obtener las coordenadas de los nodos
    coordenadas_originales = {}
    for node_name, node in wn.nodes():
        # Suponiendo que las coordenadas están disponibles como atributos del nodo
        coordenadas_originales[node_name] = (node.coordinates[0], node.coordinates[1])

    # Crear un subdiccionario con los nodos de interés
    subdiccionario = {nodo: coordenadas_originales[nodo] for nodo in nodos_sensorizados if nodo in coordenadas_originales}

    # Calcular distancias entre cada par de nodos
    nodos = list(subdiccionario.keys())
    num_nodos = len(nodos)
    dist_matrix = np.zeros((num_nodos, num_nodos))

    # Calcular distancias entre cada par de nodos y guardarlas en la matriz
    for i in range(num_nodos - 1):
        for j in range(i + 1, num_nodos):
            nodo1 = nodos[i]
            nodo2 = nodos[j]
            distancia = euclidean_distance(subdiccionario[nodo1], subdiccionario[nodo2])

            # Almacenar la distancia en la matriz en ambas direcciones
            dist_matrix[i][j] = distancia
            dist_matrix[j][i] = distancia

    # Imprimir la matriz de distancias entre nodos
    print("Matriz de distancias entre nodos:")
    print(dist_matrix)

    # Crear un diccionario para mapear los índices de la matriz a las etiquetas de nodos
    index_to_label = {i: nodo for i, nodo in enumerate(nodos)}

    # Imprimir el diccionario de mapeo
    print("Índice de nodo en la matriz : Etiqueta del nodo")
    for index, label in index_to_label.items():
        print(f"{index}: {label}")

    g = Graph(num_nodos)
    g.graph = dist_matrix

    result = g.primMST()

    return result, index_to_label
