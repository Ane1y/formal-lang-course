from typing import Dict, Set, Tuple, Any

from pyformlang.finite_automaton import (
    NondeterministicFiniteAutomaton,
    Symbol,
    State,
    EpsilonNFA, Epsilon,
)
from scipy import sparse
from scipy.sparse import dok_matrix, kron, coo_matrix, csr_matrix


def decompose_fa(fa: EpsilonNFA) -> (Dict[str, dok_matrix], Dict[State, int]):
    """
    Decomposition of FA as a dictionary: key is symbol, value is transition matrix for x
    :param fa: finite automaton
    :return:
    """
    states = {state: idx for idx, state in enumerate(fa.states)}
    n_states = len(fa.states)

    result = {}

    for fr, label, to in fa:
        matrix = result.setdefault(
            label,
            sparse.dok_matrix((n_states, n_states), dtype=bool),
        )
        matrix[states[fr], states[to]] = True

    inds = list(fa.states)
    return result, states, inds


def intersect(fa1: EpsilonNFA, fa2: EpsilonNFA) -> EpsilonNFA:
    """
    Computes the intersection of two finite automata using tensor product

    Parameters
    ----------
    `fa1`: First finite automaton
    `fa2`: Second finite automaton

    Returns
    -------
    The intersection of two finite automatas
    """

    fa1_bool, fa1_states, inds1 = decompose_fa(fa1)
    fa2_bool, fa2_states, inds2 = decompose_fa(fa2)

    n_states1 = len(fa1_states)
    n_states2 = len(fa2_states)

    same_labels = set(fa1_bool.keys()).intersection(fa2_bool.keys())
    bool_decomposition = {
        label: dok_matrix(kron(fa1_bool[label], fa2_bool[label]))
        for label in same_labels
    }

    result = EpsilonNFA()

    result_states = [None] * (n_states1 * n_states2)

    for i in range(n_states1):
        for j in range(n_states2):
            result_states[i * n_states2 + j] = State((inds1[i], inds2[j]))

    for l, mat in bool_decomposition.items():
        for (fr, to), value in mat.items():
            if value:
                result.add_transition(result_states[fr], l, result_states[to])

    for s1 in fa1.start_states:
        for s2 in fa2.start_states:
            result.add_start_state(
                result_states[fa1_states[s1] * n_states2 + fa2_states[s2]]
            )

    for s1 in fa1.final_states:
        for s2 in fa2.final_states:
            result.add_final_state(
                result_states[fa1_states[s1] * n_states2 + fa2_states[s2]]
            )

    return result

def union(fa1: EpsilonNFA, fa2: EpsilonNFA) -> EpsilonNFA:
    """
    Computes the union of two finite automata

    `fa1`: First finite automaton
    `fa2`: Second finite automaton
    :return: The union of two finite automatas
    """
    fa = EpsilonNFA()

    for fro, symb, to in fa1:
        assert isinstance(fro, State)
        assert isinstance(to, State)
        fa.add_transition((1, fro.value), symb, (1, to.value))

    for fro, symb, to in fa2:
        assert isinstance(fro, State)
        assert isinstance(to, State)
        fa.add_transition((2, fro.value), symb, (2, to.value))

    for node in fa1.start_states:
        assert isinstance(node, State)
        fa.add_start_state((1, node.value))

    for node in fa2.start_states:
        assert isinstance(node, State)
        fa.add_start_state((2, node.value))

    for node in fa1.final_states:
        assert isinstance(node, State)
        fa.add_final_state((1, node.value))

    for node in fa2.final_states:
        assert isinstance(node, State)
        fa.add_final_state((2, node.value))

    return fa

def concat(fa1: EpsilonNFA, fa2: EpsilonNFA) -> EpsilonNFA:
    """
    Computes the concatenation of two finite automata

    `fa1`: First finite automaton
    `fa2`: Second finite automaton
    :return: The concatenation of two finite automatas
    """
    fa = EpsilonNFA()

    for fro, symb, to in fa1:
        assert isinstance(fro, State)
        assert isinstance(to, State)
        fa.add_transition((1, fro.value), symb, (1, to.value))

    for fro, symb, to in fa2:
        assert isinstance(fro, State)
        assert isinstance(to, State)
        fa.add_transition((2, fro.value), symb, (2, to.value))

    for node in fa1.start_states:
        assert isinstance(node, State)
        fa.add_start_state((1, node.value))

        for node2 in fa2.final_states:
            assert isinstance(node2, State)
            fa.add_transition((1, node.value), Epsilon(), (2, node2.value))

    for node in fa2.final_states:
        assert isinstance(node, State)
        fa.add_final_state((1, node.value))

    return fa


def get_transitive_closure(fa: EpsilonNFA) -> EpsilonNFA:
    """
    Computes the transitive closure of given automaton
    :param fa: finite automaton
    :return: the transitive closure of given automaton
    """
    for s in fa.start_states:
        for f in fa.final_states:
            fa.add_transition(f, Epsilon(), s)
    return fa


def find_reachable_mat(fa: EpsilonNFA, matrices: Dict[Any, dok_matrix]) -> Set[Tuple[Any, Any]]:
    flat = None
    for mat in matrices.values():
        if flat is None:
            flat = mat
            continue
        flat |= mat
    if flat is None:
        return set()

    prev = 0
    while flat.count_nonzero() != prev:
        prev = flat.count_nonzero()
        flat += flat @ flat

    from_idx, to_idx = flat.nonzero()
    return set(zip(from_idx, to_idx))


def find_reachable(fa: EpsilonNFA) -> Set[Tuple[Any, Any]]:
    matrices, state_idx, _ = decompose_fa(fa)
    reachable = find_reachable_mat(fa, matrices)
    rev_idx = {i: k for k, i in state_idx.items()}
    result = set()
    for fro, to in reachable:
        fro_id = rev_idx[fro]
        to_id = rev_idx[to]
        if fro_id in fa.start_states and to_id in fa.final_states:
            result.add((fro_id.value, to_id.value))
    return result
