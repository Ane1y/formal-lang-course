from typing import Set

import pyformlang.regular_expression as re
import pyformlang.finite_automaton as fa
import networkx as nx

# Используя возможности pyformlang реализовать функцию построения минимального ДКА по заданному регулярному выражению.


def regex_to_dfa(regex: re.Regex) -> fa.DeterministicFiniteAutomaton:
    """
    Build minimal DFA from Regex
    :param regex:
    :return: minimal DFA
    """
    return regex.to_epsilon_nfa().minimize()


def graph_to_nfa(
    graph: nx.Graph, start_states: Set = None, final_states: Set = None
) -> fa.NondeterministicFiniteAutomaton:
    """
    Build Nondeterministic finite automaton from graph
    If start or final states are not defined, every vertex of graph become start/final

    :param graph: The graph from which NFA will be built
    :param start_states: Set of start states of NFA
    :param final_states: Set of final states of NFA
    :return: Nondeterministic finite automaton from given graph
    """

    nfa = fa.NondeterministicFiniteAutomaton(graph)
    states = nfa.states

    if start_states is None:
        start_states = states

    if final_states is None:
        final_states = states

    for s in start_states:
        nfa.add_start_state(s)
    for s in final_states:
        nfa.add_final_state(s)

    return nfa
