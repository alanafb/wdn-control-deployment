import networkx as nx
import matplotlib.pyplot as plt
import random
import warnings

# Suprimir todos los warnings 
warnings.filterwarnings("ignore")

class Node:
    def __init__(self, is_SCADA=False, connects_to_SCADA=False, is_PLC=False, name=None):
        self.is_SCADA = is_SCADA
        self.connects_to_SCADA = connects_to_SCADA
        self.is_PLC = is_PLC
        self.connected_to = []
        self.name = name

    def connect_to(self, node):
        self.connected_to.append(node)

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
        plc_node.connect_to(self)
        print(f"Nodo {self.name} reconectado a PLC {plc_node.name}")

    def connect_PLC_to_SCADA_chain(self, chain):
        if len(chain) > 3 and chain[2] not in chain[0].connected_to:
            self.connect_to(chain[2])
            print(f"Nueva conexión de nodo {chain[2].name} a PLC {chain[0].name}")

    def add_nodes(self, chain, node_list):
        len_conexiones = len(chain)
        if len_conexiones >= 4 and len_conexiones %2 == 0:
            self.add_node_between(chain[-2], node_list)

    def add_node_between(self, node_before, node_list):
        new_node = Node(name=f"{node_before.name}_{self.name}")
         # Verificar si new_node ya existe en node_list
        if any(node.name == new_node.name for node in node_list):
            print(f"El nodo {new_node.name} ya existe en la lista. No se añadió.")
            return
        node_before.connected_to.remove(self)
        node_before.connect_to(new_node)
        new_node.connect_to(self)
        node_list.append(new_node)
        print(f"Nuevo nodo añadido entre {node_before.name} y {self.name}")

    
def find_extremes(graph):
    # Encontrar todos los nodos sin sucesores
    return [node for node in graph.nodes if not any(graph.successors(node))]

def find_PLC_nodes(node_list):
    PLC_nodes = [node.name for node in node_list if node.is_PLC]
    return PLC_nodes

def find_SCADA_nodes(node_list):
    SCADA_nodes = [node.name for node in node_list if node.is_SCADA]
    return SCADA_nodes

def generate_paths_from_SCADA(graph, SCADA_node, extreme_nodes):
    paths_SCADA = []
    for extreme_node in extreme_nodes:
        paths = list(nx.all_simple_paths(graph, SCADA_node, extreme_node))
        # Obtener la lista más larga
        longest_path = max(paths, key=len, default=[])
        # Añadir la lista más larga a paths_SCADA después de aplanarla
        paths_SCADA.append(longest_path)

    return paths_SCADA

def generate_paths_from_PLC(graph, PLC_nodes, extreme_nodes, paths_SCADA):
    paths_PLC = []
    for PLC_node in PLC_nodes:
        for extreme_node in extreme_nodes:
            for path_SCADA in paths_SCADA:
                if PLC_node in path_SCADA and extreme_node in path_SCADA:
                    index_PLC = path_SCADA.index(PLC_node)
                    path_to_extreme = path_SCADA[index_PLC:]
                    paths_PLC.append(path_to_extreme)
    return paths_PLC

def order_nodes_by_names(node_list, names):
    # Crea un diccionario para mapear nombres a nodos
    name_to_node = {node.name: node for node in node_list}
    # Utiliza la lista de nombres para ordenar los nodos
    ordered_nodes = [name_to_node[name] for name in names if name in name_to_node]
    return ordered_nodes

def check_connections(node_list, cadenas_PLC, cadenas_SCADA):
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
    
    for chain_names in cadenas_PLC:
        chain_nodes = order_nodes_by_names(node_list, chain_names)
        if chain_nodes:
            chain_nodes[0].connect_PLC_to_SCADA_chain(chain_nodes)
        else:
            print(f"No se encontró nodo para la cadena {chain_names}")
    for complete_chain_names in cadenas_SCADA:
        complete_chain_nodes = order_nodes_by_names(node_list, complete_chain_names)
        if complete_chain_nodes:
            complete_chain_nodes[-1].add_nodes(complete_chain_nodes, node_list)
        else:
            print(f"No se encontró nodo para la cadena {chain_names}")

def process_graph(G, nodes_list):
    # Encontrar nodos extremos
    extreme_nodes = find_extremes(G)
    
    # Encontrar nodos PLC y SCADA
    PLC_nodes = find_PLC_nodes(nodes_list)
    SCADA_nodes = find_SCADA_nodes(nodes_list)[0]
    
    print(f"extreme_nodes: {extreme_nodes}")
    print(f"PLC_nodes: {PLC_nodes}")
    print(f"SCADA_node: {SCADA_nodes}")
      
    # Generar caminos desde SCADA a nodos extremos
    paths_SCADA = generate_paths_from_SCADA(G, SCADA_nodes, extreme_nodes)
    
    # Imprimir caminos desde SCADA a nodos extremos
    print("Caminos desde SCADA a nodos extremos:")
    for paths in paths_SCADA:
        print(paths) 
        
    # Generar caminos desde PLC a nodos extremos utilizando caminos desde SCADA
    paths_PLC = generate_paths_from_PLC(G, PLC_nodes, extreme_nodes, paths_SCADA)
    
    # Imprimir caminos desde PLC a nodos extremos
    print("Caminos desde PLC a nodos extremos:")
    for paths in paths_PLC:
        print(paths)

    return paths_SCADA, paths_PLC        

                
def create_graph(node_list):
    G = nx.DiGraph()
    Gpos = nx.Graph()

    for node in node_list:
        attributes = {'color': 'skyblue'}
        if node.is_SCADA:
            attributes['color'] = 'red'
        elif node.is_PLC:
            attributes['color'] = 'green'
        G.add_node(node.name, **attributes)
        Gpos.add_node(node.name, **attributes)

    for node in node_list:
        for connected_node in node.connected_to:
            G.add_edge(node.name, connected_node.name)
            Gpos.add_edge(node.name, connected_node.name)

    return G, Gpos

def draw_graph(G, Gpos):
    node_colors = [G.nodes[node]['color'] for node in G.nodes]
    pos = nx.kamada_kawai_layout(Gpos)
    nx.draw(G, pos, with_labels=True, node_color=node_colors, font_weight='bold', connectionstyle='arc3,rad=0.1')
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
        if new_node.connects_to_SCADA:
            scada_nodes = [node for node in node_list if node.is_SCADA]
            if scada_nodes:
                connected_node = random.choice(scada_nodes)
                new_node.connected_to = [connected_node]

                # Añadir el nuevo nodo a la lista connected_to del nodo conectado
                connected_node.connected_to.append(new_node)

        # Si connects_to_SCADA es False, conectar a un nodo aleatorio con is_SCADA a False
        else:
            non_scada_nodes = [node for node in node_list if not node.is_SCADA]
            if non_scada_nodes:
                connected_node = random.choice(non_scada_nodes)
                if connected_node.is_PLC:
                    # Añadir el nuevo nodo a la lista connected_to del nodo conectado
                    connected_node.connected_to.append(new_node)
                    if new_node.is_PLC:
                        new_node.connected_to = [connected_node]
                else:
                    new_node.connected_to = [connected_node]


        node_list.append(new_node)

