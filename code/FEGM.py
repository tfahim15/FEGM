import copy
import time
import math
import sys
t = time.time()

# Class for graph entity
class Graph:
    def __init__(self):
        self.vertices = dict()
        self.adjacency = dict()

    def __repr__(self) -> str:
        return "\nVertices:" + str(self.vertices) \
               + "\nAdjacency List: " + str(self.adjacency) + "\n"


file_name = str(sys.argv[2])

# loading graphs from file
data = open("../data/"+file_name+"/"+file_name+"_ord_graph.txt").readlines()

Global_graphs = []
graph = None
for line in data:
    if line[0] == 't':
        if graph is None:
            graph = Graph()
        else:
            Global_graphs.append(graph)
            graph = Graph()
    if line[0] == 'v':
        line = line.split(' ')
        graph.vertices[int(line[1])] = int(line[2])
    if line[0] == 'e':
        _, vertex1, vertex2, label, order = line.split(" ")
        vertex1 = int(vertex1)
        vertex2 = int(vertex2)
        label = int(label)
        order = int(order)
        if vertex1 in graph.adjacency:
            graph.adjacency[vertex1].append((vertex2, label, order))
        else:
            graph.adjacency[vertex1] = [(vertex2, label, order)]
        if vertex2 in graph.adjacency:
            graph.adjacency[vertex2].append((vertex1, label, order))
        else:
            graph.adjacency[vertex2] = [(vertex1, label, order)]

Global_graphs.append(graph)


# gSpan: finds rightmost path of a DFS code
def RightMostPath(code):
    adj = dict()
    ur = 0
    for c in code:
        ur = max(ur, c[0])
        ur = max(ur, c[1])
        if c[1] > c[0]:
            adj[c[1]] = c[0]
    result = [ur]
    u = ur
    while u != 0:
        u = adj[u]
        result.append(u)
    return ur, list(reversed(result))


def find_order(graph, u, v):
    for v_, l, o in graph.adjacency[u]:
        if v == v_:
            return o


# gSpan: finds rightmost path extensions of a DFS code
def RightMostExtensions(code, graphs):
    result = dict()
    for i in range(len(graphs)):
        graph = graphs[i]
        temp_result = dict()
        if code.__len__() == 0:
            for u in graph.adjacency:
                for e in graph.adjacency[u]:
                    v, edge_label, order = e
                    u_label = graph.vertices[u]
                    v_label = graph.vertices[v]
                    temp_result[(0, 1, u_label, v_label, edge_label, -0.5)] = 1
        else:
            isomorphisms = subgraphIsomorphisms_ordered(code, graph)
            u, R = RightMostPath(code)
            for isomorphism in isomorphisms:
                for v in R:
                    if u == v:
                        continue
                    iso_u = isomorphism[u]
                    iso_v = isomorphism[v]
                    for e in graph.adjacency[iso_u]:
                        if e[0] != iso_v:
                            continue
                        edge_label = e[1]
                        order = e[2]
                        exists = False
                        for c in code:
                            if c[0] == u and c[1] == v and c[4] == edge_label:
                                exists = True
                            elif c[0] == v and c[1] == u and c[4] == edge_label:
                                exists = True
                        if not exists:
                            mlt_order = -1
                            for c in code:
                                if find_order(graph, isomorphism[c[0]], isomorphism[c[1]]) < order:
                                    mlt_order = max(mlt_order, c[5])

                            temp_result[(u, v, graph.vertices[iso_u], graph.vertices[iso_v], edge_label, mlt_order + 0.5)] = 1
                ur = u
                for u in R:
                    iso_u = isomorphism[u]
                    for e in graph.adjacency[iso_u]:
                        iso_v, edge_label, order = e
                        if iso_v in isomorphism.values():
                            continue
                        u_label, v_label = graph.vertices[iso_u], graph.vertices[iso_v]
                        mlt_order = -1
                        for c in code:
                            if find_order(graph, isomorphism[c[0]], isomorphism[c[1]])< order:
                                mlt_order = max(mlt_order, c[5])
                        temp_result[(u, ur+1, u_label, v_label, edge_label, mlt_order + 0.5)] = 1

        for key in temp_result:
            if key in result:
                cur = result[key]
                cur.append(i)
                result[key] = cur
            else:
                result[key] = [i]
    return result


def verify_subgraphIsomorphisms(code, graph, isomorphism):
    ret = True
    for u1, v1, _, _, _, o1 in code:
        for u2, v2, _, _, _, o2 in code:
            if u1 == u2 and v1 == v2:
                continue
            if o1 < o2 and find_order(graph, isomorphism[u1], isomorphism[v1]) > find_order(graph, isomorphism[u2], isomorphism[v2]):
                ret = False
            if o1 > o2 and find_order(graph, isomorphism[u1], isomorphism[v1]) < find_order(graph, isomorphism[u2], isomorphism[v2]):
                ret = False
    return ret


# gSpan: finds subgraph isomorphisms from a DFS code to a graph
def subgraphIsomorphisms_ordered(code, graph):
    isomorphisms = []
    l0 = code[0][2]
    for v in graph.vertices:
        if graph.vertices[v] == l0:
            isomorphisms.append({0: v})
    for tuple in code:
        u, v, u_label, v_label, edge_label, _ = tuple
        temp_isomorphisms = []
        for isomorphism in isomorphisms:
            if v > u:
                iso_u = isomorphism[u]
                try:
                    _ = graph.adjacency[iso_u]
                except KeyError:
                    continue
                for e in graph.adjacency[iso_u]:
                    iso_v, iso_edge_label, order = e
                    if iso_v not in isomorphism.values() and graph.vertices[iso_v] == v_label and edge_label == iso_edge_label:
                        new_iso = copy.deepcopy(isomorphism)
                        new_iso[v] = iso_v
                        temp_isomorphisms.append(new_iso)

            else:
                iso_u = isomorphism[u]
                iso_v = isomorphism[v]
                for e in graph.adjacency[iso_u]:
                    c_iso_v, c_iso_edge_label, order = e
                    if c_iso_v == iso_v and edge_label == c_iso_edge_label:
                        temp_isomorphisms.append(copy.deepcopy(isomorphism))
        isomorphisms = temp_isomorphisms
    verified_isomorphisms = []
    for isomorphism in isomorphisms:
        if verify_subgraphIsomorphisms(code, graph, isomorphism):
            verified_isomorphisms.append(isomorphism)
    return verified_isomorphisms


# gSpan: builds graph from DFS code
def buildGraph(code):
    graph = Graph()
    for tuple in code:
        u, v, u_label, v_label, edge_label, order = tuple
        graph.vertices[u] = u_label
        graph.vertices[v] = v_label
        if u in graph.adjacency:
            graph.adjacency[u].append((v, edge_label, order))
        else:
            graph.adjacency[u] = [(v, edge_label, order)]
        if v in graph.adjacency:
            graph.adjacency[v].append((u, edge_label, order))
        else:
            graph.adjacency[v] = [(u, edge_label, order)]
    return graph


# gSpan: canonical ordering of tuples
def minTuple(tuple1, tuple2):
    u1, v1, u1_label, v1_label, edge1label, o1 = tuple1
    u2, v2, u2_label, v2_label, edge2label, o2 = tuple2
    if u1 == u2 and v1 == v2:
        if u1_label < u2_label:
            return tuple1
        elif u1_label > u2_label:
            return tuple2
        elif v1_label < v2_label:
            return tuple1
        elif v1_label > v2_label:
            return tuple2
        elif edge1label < edge2label:
            return tuple1
        elif edge1label > edge2label:
            return tuple2
        #elif o1 < o2:
            #return tuple1
        return tuple2
    else:
        if u1 < v1 and u2 < v2:  # both forward edge
            if v1 < v2:
                return tuple1
            elif v1 == v2 and u1 > u2:
                return tuple1
            return tuple2
        if u1 > v1 and u2 > v2:  # both backward edge
            if u1 < u2:
                return tuple1
            elif u1 == u2 and v1 < v2:
                return tuple1
            return tuple2
        if u1 < v1 and u2 > v2:  # tuple1 forward tuple2 backward
            if v1 <= u2:
                return tuple1
            return tuple2
        if u1 > v1 and u2 < v2:  # tuple1 backward tuple2 forward
            if u1 < v2:
                return tuple1
            return tuple2


# gSpan: finds minimum tuples
def minExtension(tuples):
    result = None
    for t in tuples:
        if result is None:
            result = t
        else:
            result = minTuple(result, t)
    return result


# gSpan: checks if a DFS code is canonical
def isCannonical(code):
    graph = buildGraph(code)
    c = []
    for i in range(len(code)):
        extension = minExtension(RightMostExtensions(c, [graph]))
        if extension is None:
            return False
        min_tuple = minTuple(extension, code[i])
        if (min_tuple[0], min_tuple[1], min_tuple[2], min_tuple[3], min_tuple[4]) != (code[i][0], code[i][1], code[i][2], code[i][3], code[i][4]):
            return False
        c.append(extension)
    return True


def append_ext(code, key):
    new_code = []
    for c in code:
        if c[5] > key[5]:
            new_code.append((c[0], c[1], c[2], c[3], c[4], c[5] + 1))
        else:
            new_code.append(c)
    c = key
    new_code.append((c[0], c[1], c[2], c[3], c[4], int(c[5] + 0.5)))
    return new_code


candidates, freq = 0, 0


# gSpan: recursively mines frequent subgraphs
def GSpan(code, graphs, min_sup):
    global candidates, freq
    candidates += 1
    code = copy.deepcopy(code)
    extentions = RightMostExtensions(code, graphs)
    for key in extentions:
        sup = len(extentions[key])
        new_code = append_ext(code, key)
        if not isCannonical(new_code):
            continue
        if sup >= min_sup:
            #print(code, key)
            freq += 1
            print("-", new_code)
            GSpan(new_code, graphs, min_sup)


import time
t = time.time()
base_sup = float(sys.argv[1])
print(base_sup)
GSpan([], Global_graphs, math.ceil(len(Global_graphs) * base_sup))
open("FEGM.txt", "a").write(str(time.time()-t)+" "+str(base_sup)+" "+str(candidates)+" "+str(freq)+" "+str(file_name)+"\n")