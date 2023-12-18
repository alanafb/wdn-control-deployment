import networkx as nx
import matplotlib.pyplot as plt
import copy

class Node:
    def __init__(self, is_SCADA=False, connects_to_SCADA=False, is_PLC=False, name=None):
        self.is_SCADA = is_SCADA
        self.connects_to_SCADA = connects_to_SCADA
        self.is_PLC = is_PLC
        self.connected_to = []
        self.name = name

    def connect_to(self, node):
        self.connected_to.append(node)
        node.connected_to.append(self)

    def disconnect_from_SCADA(self):
        if self.connects_to_SCADA:
            self.connects_to_SCADA = False
            print("Nodo " + self.name + " desconectado de SCADA")
            # Buscar la conexión a SCADA y eliminarla
            for node in self.connected_to:
                if node.is_SCADA:
                    self.connected_to.remove(node)
                    node.connected_to.remove(self)
                    print("Conexión a SCADA eliminada en Nodo " + self.name)
                    break

    def connect_to_PLC(self, plc_node):
        self.connect_to(plc_node)
        print("Nodo " + self.name + " reconectado a PLC " + plc_node.name)

    def connect_PLC_to_SCADA_chain(self, chain):
        if len(chain) > 3:
            chain[0].connect_to(chain[2])
            print("Nueva conexión de nodo " + chain[2].name + " a PLC " + chain[0].name)

    def add_node_between(self, node_before, node_after, node_list):
        new_node = Node(name=(node_before.name + "_" + node_after.name))
        node_before.connected_to.remove(node_after)
        node_after.connected_to.remove(node_before)
        new_node.connect_to(node_before)
        new_node.connect_to(node_after)
        node_list.append(new_node)
        print("Nuevo nodo añadido entre " + node_before.name + " y " + node_after.name)


def encontrar_cadenas_PLC(nodos):
    def encontrar_conexiones_PLC(nodo, cadena_actual, cadenas):
        cadena_actual.append(nodo)
        conexiones = [n for n in nodo.connected_to if n not in cadena_actual and not n.is_SCADA]

        if not conexiones:  # Si no hay más conexiones, agrega la cadena a las cadenas encontradas
            nueva_cadena = tuple(cadena_actual)
            if nueva_cadena not in cadenas and nueva_cadena[::-1] not in cadenas:
                print("Cadena: " + str([nodo.name for nodo in nueva_cadena]))
                cadenas.add(nueva_cadena)

        for conexion in conexiones:
            nueva_cadena = cadena_actual.copy()  # Crear una nueva lista para cada conexión
            encontrar_conexiones_PLC(conexion, nueva_cadena, cadenas)

    cadenas = set()

    for nodo_de_interes in nodos:
        if nodo_de_interes.connects_to_SCADA:
            for conexion in nodo_de_interes.connected_to:
                if not conexion.is_SCADA:
                    encontrar_conexiones_PLC(conexion, [nodo_de_interes], cadenas)


    return list(cadenas)

def encontrar_cadenas_general(nodos):
    def encontrar_conexiones_general(nodo, cadena_actual, cadenas):
        cadena_actual.append(nodo)
        conexiones = [n for n in nodo.connected_to if n not in cadena_actual and not n.is_SCADA]

        if not conexiones:  # Si no hay más conexiones, agrega la cadena a las cadenas encontradas
            nueva_cadena = tuple(cadena_actual)
            if nueva_cadena not in cadenas and nueva_cadena[::-1] not in cadenas:
                print("Cadena: " + str([nodo.name for nodo in nueva_cadena]))
                len_conexiones = len(nueva_cadena)
                if len_conexiones >= 4 and len_conexiones % 2 == 0:
                    nueva_cadena[len_conexiones-1].add_node_between(nueva_cadena[len_conexiones - 2], nueva_cadena[len_conexiones-1], nodos)
                cadenas.add(nueva_cadena)

        for conexion in conexiones:
            nueva_cadena = cadena_actual.copy()  # Crear una nueva lista para cada conexión
            encontrar_conexiones_general(conexion, nueva_cadena, cadenas)

    cadenas = set()

    for nodo_de_interes in nodos:
        conectado_solo_a_un_nodo = sum(1 for nodo in nodos if nodo_de_interes in nodo.connected_to) == 1
        if conectado_solo_a_un_nodo:
            for conexion in nodo_de_interes.connected_to:
                encontrar_conexiones_general(conexion, [nodo_de_interes], cadenas)

def actualizar_lista(lista_original, lista_nueva):
    for i in range(len(lista_original)):
        if lista_original[i] != lista_nueva[i]:
            lista_original[i] = lista_nueva[i]

def check_connections(node_list):
    for node_a in node_list:
        if not node_a.is_PLC and node_a.connects_to_SCADA:
            node_a.disconnect_from_SCADA()
            for node_b in node_list:
                if node_b != node_a and node_b.is_PLC:
                    node_a.connect_to_PLC(node_b)
                    break
        elif node_a.connects_to_SCADA:
            for node_b in node_list:
                if node_b != node_a and node_b.connects_to_SCADA and node_b in node_a.connected_to:
                    node_b.disconnect_from_SCADA()
            
    # añadir cadenas de nuevas conexiones a lista para no revisarlas al añadir nodos
    node_list_PLC = copy.deepcopy(node_list)
    PLC_SCADA_chains = encontrar_cadenas_PLC(node_list_PLC)
    for chain in PLC_SCADA_chains:
        chain[0].connect_PLC_to_SCADA_chain(chain)
        
    node_list_general = copy.deepcopy(node_list)
    encontrar_cadenas_general(node_list_general)
    
    actualizar_lista(node_list, node_list_PLC)
    node_list.extend(node_list_general)

def draw_graph(node_list):
    # Crear un grafo de NetworkX
    G = nx.Graph()

    # Agregar nodos al grafo con atributos
    for node in node_list:
        attributes = {'color': 'skyblue'}  # Color por defecto para nodos que no son SCADA ni PLC
        if node.is_SCADA:
            attributes['color'] = 'red'
        elif node.is_PLC:
            attributes['color'] = 'green'
        G.add_node(node.name, **attributes)

    # Agregar bordes (conexiones) al grafo
    for node in node_list:
        for connected_node in node.connected_to:
            G.add_edge(node.name, connected_node.name)

    # Dibujar el grafo
    node_colors = [G.nodes[node]['color'] for node in G.nodes]

    pos = nx.kamada_kawai_layout(G)  # Layout para ubicar los nodos
    nx.draw(G, pos, with_labels=True, node_color=node_colors, font_weight='bold')
    plt.show()            
            
# node_list = []

# # Crear instancias de nodos
# SCADA = Node(is_SCADA=True, name="SCADA")
# node1 = Node(name="Node 1", connects_to_SCADA=True)
# node2 = Node(name="Node 2")
# node3 = Node(name="Node 3")
# PLC1 = Node(is_PLC=True, name="PLC 1", connects_to_SCADA=True)
# PLC2 = Node(is_PLC=True, name="PLC 2", connects_to_SCADA=True)

# # Establecer conexiones entre nodos
# SCADA.connected_to = [node1, PLC1, PLC2]
# node1.connected_to = [SCADA, node2]
# node2.connected_to = [node1, node3]
# node3.connected_to = [node2]
# PLC1.connected_to = [SCADA, PLC2]
# PLC2.connected_to = [SCADA, PLC1]

# # Agregar los nodos a la lista de nodos
# node_list.extend([SCADA, node1, node2, node3, PLC1, PLC2])



# draw_graph(node_list)
# # Llamar a la función para chequear las conexiones
# check_connections(node_list)

# draw_graph(node_list)