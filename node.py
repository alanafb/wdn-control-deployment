import networkx as nx
import matplotlib.pyplot as plt
import copy
import random

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
            print(f"Nodo {self.name} desconectado de SCADA")
            # Buscar la conexión a SCADA y eliminarla
            for node in self.connected_to:
                if node.is_SCADA:
                    self.connected_to.remove(node)
                    node.connected_to.remove(self)
                    print(f"Conexión a SCADA eliminada en Nodo {self.name}")
                    break

    def connect_to_PLC(self, plc_node):
        self.connect_to(plc_node)
        print(f"Nodo {self.name} reconectado a PLC {plc_node.name}")

    def connect_PLC_to_SCADA_chain(self, chain):
        if len(chain) > 3 and chain[2] not in chain[0].connected_to:
            chain[0].connect_to(chain[2])
            print(f"Nueva conexión de nodo {chain[2].name} a PLC {chain[0].name}")

    def add_node_between(self, node_before, node_after, node_list):
        new_node = Node(name=f"{node_before.name}_{node_after.name}")
         # Verificar si new_node ya existe en node_list
        if any(node.name == new_node.name for node in node_list):
            print(f"El nodo {new_node.name} ya existe en la lista. No se añadió.")
            return
        node_before.connected_to.remove(node_after)
        node_after.connected_to.remove(node_before)
        new_node.connect_to(node_before)
        new_node.connect_to(node_after)
        node_list.append(new_node)
        print(f"Nuevo nodo añadido entre {node_before.name} y {node_after.name}")

    
            
def encontrar_cadenas_PLC(nodos):
    def encontrar_conexiones_PLC(nodo, cadena_actual, cadenas):
        cadena_actual.append(nodo)
        conexiones = [n for n in nodo.connected_to if n not in cadena_actual and not n.is_SCADA]

        if not conexiones:
            nueva_cadena = tuple(cadena_actual)
            if nueva_cadena not in cadenas and nueva_cadena[::-1] not in cadenas:
                print(f"Cadena: {[nodo.name for nodo in nueva_cadena]}")
                cadenas.add(nueva_cadena)

        for conexion in conexiones:
            nueva_cadena = cadena_actual.copy()
            encontrar_conexiones_PLC(conexion, nueva_cadena, cadenas)

    cadenas = set()

    for nodo_de_interes in nodos:
        if nodo_de_interes.connects_to_SCADA:
            for conexion in nodo_de_interes.connected_to:
                if not conexion.is_SCADA:
                    encontrar_conexiones_PLC(conexion, [nodo_de_interes], cadenas)

    return list(cadenas)

def encontrar_cadenas_general(nodos):
    def encontrar_conexiones_general(nodo, cadena_actual, cadenas_temporales):
        cadena_actual.append(nodo)
        conexiones = [n for n in nodo.connected_to if n not in cadena_actual]

        if not conexiones:
            nueva_cadena = tuple(cadena_actual)
            if nueva_cadena not in cadenas_temporales and nueva_cadena[::-1] not in cadenas_temporales:
                cadenas_temporales.append(nueva_cadena)

        for conexion in conexiones:
            nueva_cadena = cadena_actual.copy()
            encontrar_conexiones_general(conexion, nueva_cadena, cadenas_temporales)

    cadenas_temporales = []

    for nodo_de_interes in nodos:
        conectado_solo_a_un_nodo = sum(1 for nodo in nodos if nodo_de_interes in nodo.connected_to) == 1
        if conectado_solo_a_un_nodo:
            for conexion in nodo_de_interes.connected_to:
                encontrar_conexiones_general(conexion, [nodo_de_interes], cadenas_temporales)

    cadenas_finales = set()

    for cadena_temporal in cadenas_temporales:
        if cadena_temporal not in cadenas_finales and cadena_temporal[::-1] not in cadenas_finales:
            print(f"Cadena: {[nodo.name for nodo in cadena_temporal]}")
            len_conexiones = len(cadena_temporal)

            if len_conexiones >= 4 and len_conexiones % 2 == 0:
                cadena_temporal[len_conexiones-1].add_node_between(cadena_temporal[len_conexiones - 2], cadena_temporal[len_conexiones-1], nodos)

            cadenas_finales.add(cadena_temporal)

def actualizar_lista(lista_original, lista_nueva):
    for i in range(len(lista_original)):
        if lista_original[i] != lista_nueva[i]:
            lista_original[i] = lista_nueva[i]

def actualizar_lista_con_nuevos_nodos(lista_original, lista_nuevos_nodos):
    for nodo in lista_nuevos_nodos:
        if any(nodo.name == n.name for n in lista_original):
            for conexion in nodo.connected_to:
                if any(conexion.name == n.name for n in lista_original):
                    continue
                else:
                    lista_original[lista_original.index(next(n for n in lista_original if n.name == nodo.name))] = nodo
        else:
            lista_original.append(nodo)

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

    node_list_PLC = copy.deepcopy(node_list)
    PLC_SCADA_chains = encontrar_cadenas_PLC(node_list_PLC)
    for chain in PLC_SCADA_chains:
        chain[0].connect_PLC_to_SCADA_chain(chain)

    node_list_general = copy.deepcopy(node_list)
    encontrar_cadenas_general(node_list_general)

    actualizar_lista(node_list, node_list_PLC)
    actualizar_lista_con_nuevos_nodos(node_list, node_list_general)

def draw_graph(node_list):
    G = nx.Graph()

    for node in node_list:
        attributes = {'color': 'skyblue'}
        if node.is_SCADA:
            attributes['color'] = 'red'
        elif node.is_PLC:
            attributes['color'] = 'green'
        G.add_node(node.name, **attributes)

    for node in node_list:
        for connected_node in node.connected_to:
            G.add_edge(node.name, connected_node.name)

    node_colors = [G.nodes[node]['color'] for node in G.nodes]

    pos = nx.kamada_kawai_layout(G)
    nx.draw(G, pos, with_labels=True, node_color=node_colors, font_weight='bold')
    plt.show()
    
def add_random_nodes(node_list, num_nodes):
    for i in range(1, num_nodes + 1):
        new_node = Node(
            is_SCADA=False,
            connects_to_SCADA=random.choice([True, False]),
            is_PLC=random.choice([True, False]),
            name=f'added_{i}'
        )

        # Conectar el nuevo nodo a un nodo aleatorio ya presente en la lista original con is_SCADA a True
        if node_list and new_node.connects_to_SCADA:
            scada_nodes = [node for node in node_list if node.is_SCADA]
            if scada_nodes:
                connected_node = random.choice(scada_nodes)
                new_node.connected_to = [connected_node]

                # Añadir el nuevo nodo a la lista connected_to del nodo conectado
                connected_node.connected_to.append(new_node)

        # Si connects_to_SCADA es False, conectar a un nodo aleatorio con is_SCADA a False
        elif node_list:
            non_scada_nodes = [node for node in node_list if not node.is_SCADA]
            if non_scada_nodes:
                connected_node = random.choice(non_scada_nodes)
                new_node.connected_to = [connected_node]

                # Añadir el nuevo nodo a la lista connected_to del nodo conectado
                connected_node.connected_to.append(new_node)

        node_list.append(new_node)

