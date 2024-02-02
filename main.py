# -*- coding: utf-8 -*-
"""
Created on Sat Dec  2 17:34:21 2023

@author: alana
"""

import node as nodec
#from node import Node, check_connections, draw_graph
from network_node_distance import obtener_resultado
from distancia_euclidea import calcular_distancias
from pruebas_chama import get_selected_sensors

def crear_nodos(result, index_to_label):
    nodes_list = [nodec.Node(is_SCADA=value['is_SCADA'], name=index_to_label[key]) for key, value in result.items()]

    # Establecer connects_to_SCADA si corresponde
    for i, (key, value) in enumerate(result.items()):
        node = nodes_list[i]
        for connection in value['connections']:
            connection_index = list(index_to_label.keys()).index(connection)
            if nodes_list[connection_index].is_SCADA:
                node.connects_to_SCADA = True
                node.is_PLC = True
                break  # Detener la verificación si ya se encontró una conexión a SCADA

    # Iterar sobre cada nodo en result para configurar connected_to
    for i, value in enumerate(result.values()):
        current_node = nodes_list[i]
        connections = value['connections']
        
        # Obtener los nodos conectados y establecer connected_to en cada nodo
        for connection in connections:
            connection_index = list(index_to_label.keys()).index(connection)
            connected_node = nodes_list[connection_index]
            current_node.connected_to.append(connected_node)

    return nodes_list


# Usar la función para obtener result e index_to_label
inp_file = 'C:\\Users\\alana\\Documents\\A_TFM\\WORKSPACE\\CTOWN.INP'

nodos_sensorizados = get_selected_sensors(inp_file, 7)
result, index_to_label = obtener_resultado(inp_file, nodos_sensorizados)
#result, index_to_label = calcular_distancias(inp_file, nodos_sensorizados)
nodes_list = crear_nodos(result, index_to_label)

nodec.draw_graph(nodes_list)
nodec.check_connections(nodes_list)
nodec.draw_graph(nodes_list)

nodec.add_random_nodes(nodes_list, 1)
nodec.draw_graph(nodes_list)
nodec.check_connections(nodes_list)
nodec.draw_graph(nodes_list)