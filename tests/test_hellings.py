import pytest
from pyformlang.cfg import CFG

from project.hellings import *
from project.graph_utils import build_two_cycle_graph
from cfpq_data import labeled_cycle_graph


@pytest.mark.parametrize(
    "cfg, graph, expected",
    [
        (
            """
            S -> epsilon
            """,
            labeled_cycle_graph(2, "a"),
            {(1, 'S', 1), (0, 'S', 0)}
        ),
        (
            """
                S -> a | b
                """,
            labeled_cycle_graph(4, "a"),
            {(1, 'S', 2), (0, 'S', 1), (3, 'S', 0), (2, 'S', 3)}
        ),
        (
            """
                S -> A B
                S -> epsilon
                S -> S B
                A -> a
                B -> b
                """,
            build_two_cycle_graph(2, 2, ("a", "b")),
            {(0, 'A', 1),
             (0, 'B', 3),
             (0, 'S', 0),
             (0, 'S', 3),
             (0, 'S', 4),
             (1, 'A', 2),
             (1, 'S', 1),
             (2, 'A', 0),
             (2, 'S', 0),
             (2, 'S', 2),
             (2, 'S', 3),
             (2, 'S', 4),
             (3, 'B', 4),
             (3, 'S', 0),
             (3, 'S', 3),
             (3, 'S', 4),
             (4, 'B', 0),
             (4, 'S', 0),
             (4, 'S', 3),
             (4, 'S', 4)}

        ),
    ],
)
def test_hellings(cfg, graph, expected):
    assert hellings(graph, CFG.from_text(cfg)) == expected

def test_query_to_cfg():
    cfg = """
            S -> A B
            S -> epsilon
            S1 -> S B
            A -> a
            S -> S1 
            B -> b
            """
    graph = build_two_cycle_graph(3, 2, ("a", "b"))
    expected = { 0 : {4},
                 1 : set(),
                 2 : {2}}
    assert query_to_graph(graph, CFG.from_text(cfg), [0, 1, 2], [2, 3, 4], Variable("S")) == expected
