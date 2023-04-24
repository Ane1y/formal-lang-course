from typing import Set, Tuple, Iterable, Dict

import networkx as nx
from pyformlang.cfg import CFG, Variable
from scipy import sparse

from wcnf import cfg_to_wcnf


def hellings(graph: nx.MultiDiGraph, cfg: CFG) -> Set[Tuple]:
    """
    Apply hellings algorithm to graph
    :param graph: given graph
    :param cfg: context free grammar
    :return: set of tuples of vertex, nonterminal, vertex
    """
    wcnf = cfg_to_wcnf(cfg)

    eps_prod_heads = [p.head.value for p in wcnf.productions if not p.body]
    term_productions = {p for p in wcnf.productions if len(p.body) == 1}
    var_productions = {p for p in wcnf.productions if len(p.body) == 2}

    r = {(v, h, v) for v in range(graph.number_of_nodes()) for h in eps_prod_heads} | {
        (u, p.head.value, v)
        for u, v, edge_data in graph.edges(data=True)
        for p in term_productions
        if p.body[0].value == edge_data["label"]
    }

    copied = r.copy()
    while copied:
        n, N, m = copied.pop()
        r_step = set()

        for u, M, v in r:
            if v == n:
                triple = {
                    (u, p.head.value, m)
                    for p in var_productions
                    if p.body[0].value == M
                    and p.body[1].value == N
                    and (u, p.head.value, m) not in r
                }
                r_step |= triple
        r |= r_step
        copied |= r_step
        r_step.clear()

        for u, M, v in r:
            if u == m:
                triple = {
                    (n, p.head.value, v)
                    for p in var_productions
                    if p.body[0].value == N
                    and p.body[1].value == M
                    and (n, p.head.value, v) not in r
                }
                r_step |= triple
        r |= r_step
        copied |= r_step

    return r


def query_hellings(
    graph: nx.MultiDiGraph,
    cfg: CFG,
    start_vertices: Iterable,
    final_vertices: Iterable,
    nonterminals: Variable,
) -> Dict[int, int]:
    result = {u: set() for u in start_vertices}
    hell = hellings(graph, cfg)
    for u, nt, v in hell:
        if nt == nonterminals and u in start_vertices and v in final_vertices:
            result[u].add(v)
    return result


def from_text_hellings(graph: nx.MultiDiGraph, cfg: str):
    return hellings(graph, CFG.from_text(cfg))


def from_file_hellings(graph: nx.MultiDiGraph, filename: str) -> Set[Tuple]:
    with open(filename) as file:
        return from_text_hellings(graph, file.read())


def matrix_based(graph: nx.MultiDiGraph, cfg: CFG) -> Set[Tuple[int, str, int]]:
    """
    Returns reachability of vertices
    :param graph:
    :param cfg:
    :return: set of tuples of vertex, nonterminal, vertex
    """
    wcnf = cfg_to_wcnf(cfg)

    epsilon_prod = [p.head.value for p in wcnf.productions if not p.body]

    term_productions = {p for p in wcnf.productions if len(p.body) == 1}
    var_productions = {p for p in wcnf.productions if len(p.body) == 2}

    nodes_num = graph.number_of_nodes()

    matrices = {
        v.value: sparse.dok_matrix((nodes_num, nodes_num), dtype=bool)
        for v in wcnf.variables
    }

    for i, j, data in graph.edges(data=True):
        l = data["label"]
        for v in {p.head.value for p in term_productions if p.body[0].value == l}:
            matrices[v][i, j] = True

    for i in range(nodes_num):
        for v in epsilon_prod:
            matrices[v][i, i] = True

    changed = True
    while changed:
        changed = False
        for p in var_productions:
            old_nnz = matrices[p.head.value].nnz
            matrices[p.head.value] += (
                matrices[p.body[0].value] @ matrices[p.body[1].value]
            )
            new_nnz = matrices[p.head.value].nnz
            changed = changed or old_nnz != new_nnz

    return {
        (u, variable, v)
        for variable, matrix in matrices.items()
        for u, v in zip(*matrix.nonzero())
    }


def query_matrix(
    graph: nx.MultiDiGraph,
    cfg: CFG,
    start_vertices: Iterable,
    final_vertices: Iterable,
    nonterminals: Variable,
) -> Dict[int, int]:
    result = {u: set() for u in start_vertices}
    hell = matrix_based(graph, cfg)
    for u, nt, v in hell:
        if nt == nonterminals and u in start_vertices and v in final_vertices:
            result[u].add(v)
    return result


def from_text_matrix(graph: nx.MultiDiGraph, cfg: str):
    return matrix_based(graph, CFG.from_text(cfg))


def from_file_matrix(graph: nx.MultiDiGraph, filename: str) -> Set[Tuple]:
    with open(filename) as file:
        return from_text_matrix(graph, file.read())
