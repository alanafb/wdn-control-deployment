import node as nodec
from network_node_distance import obtener_resultado as obtener_resultado_cable
from distancia_euclidea import calcular_distancias as calcular_distancias_inalambricas
from pruebas_chama import get_selected_sensors
from prim_algorithm import Graph

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

def obtener_input_usuario():
    inp_file = input("Introduce la ruta al archivo INP: ")
    num_nodos_sensorizar = int(input("Introduce el número de nodos a sensorizar: "))
    tipo_conexion = int(input("Selecciona el tipo de conexión cable, inalámbrica o mixta (1/2/3): "))
    num_nodos_expansion = int(input("Introduce el número de nodos con los que quieres expandir la red: "))
    
    return inp_file, num_nodos_sensorizar, tipo_conexion, num_nodos_expansion

def seleccionar_funcion_conexion(tipo_conexion):
    if tipo_conexion == 1:
        return obtener_resultado_cable
    elif tipo_conexion == 2:
        return calcular_distancias_inalambricas
    elif tipo_conexion == 3:
        return
    else:
        print("Tipo de conexión no válido. Se utilizará la conexión por cable por defecto.")
        return obtener_resultado_cable

def main():
    inp_file, num_nodos_sensorizar, tipo_conexion, num_nodos_expansion = obtener_input_usuario()
    
    nodos_sensorizados = get_selected_sensors(inp_file, num_nodos_sensorizar)
    cable = None
    inalambrica = None
    
    if tipo_conexion == 1:
        funcion_obtener_resultado = seleccionar_funcion_conexion(tipo_conexion)
        cable, index_to_label = funcion_obtener_resultado(inp_file, nodos_sensorizados)
        g = Graph(len(nodos_sensorizados))
        g.graph = cable
   
    elif tipo_conexion == 2:
        funcion_obtener_resultado = seleccionar_funcion_conexion(tipo_conexion)
        inalambrica, index_to_label = funcion_obtener_resultado(inp_file, nodos_sensorizados)
        g = Graph(len(nodos_sensorizados))
        g.graph = inalambrica
        
    else:
        cable, index_to_label = obtener_resultado_cable(inp_file, nodos_sensorizados)
        inalambrica, index_to_label = calcular_distancias_inalambricas(inp_file, nodos_sensorizados)
        # Crear instancia de la clase Graph con matrices de distancia
        g = Graph(len(nodos_sensorizados), cable, inalambrica)
    
    # Llamar a primMST
    result = g.primMST()

    nodes_list = crear_nodos(result, index_to_label)

    nodec.draw_graph(nodes_list)
    nodec.check_connections(nodes_list)
    nodec.draw_graph(nodes_list)

    nodec.add_random_nodes(nodes_list, num_nodos_expansion)
    nodec.draw_graph(nodes_list)
    nodec.check_connections(nodes_list)
    nodec.draw_graph(nodes_list)

if __name__ == "__main__":
    main()
