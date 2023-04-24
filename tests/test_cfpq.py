import pytest
from pyformlang.cfg import CFG

from project.cfpq import *
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
            {(1, "S", 1), (0, "S", 0)},
        ),
        (
            """
                S -> a | b
                """,
            labeled_cycle_graph(4, "a"),
            {(1, "S", 2), (0, "S", 1), (3, "S", 0), (2, "S", 3)},
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
            {
                (0, "A", 1),
                (0, "B", 3),
                (0, "S", 0),
                (0, "S", 3),
                (0, "S", 4),
                (1, "A", 2),
                (1, "S", 1),
                (2, "A", 0),
                (2, "S", 0),
                (2, "S", 2),
                (2, "S", 3),
                (2, "S", 4),
                (3, "B", 4),
                (3, "S", 0),
                (3, "S", 3),
                (3, "S", 4),
                (4, "B", 0),
                (4, "S", 0),
                (4, "S", 3),
                (4, "S", 4),
            },
        ),
    ],
)
class TestReachability:
    def test_hellings(self, cfg, graph, expected):
        assert hellings(graph, CFG.from_text(cfg)) == expected

    def test_matrix_based(self, cfg, graph, expected):
        assert matrix_based(graph, CFG.from_text(cfg)) == expected


@pytest.mark.parametrize(
    "cfg, graph, start_vertices, end_vertices, nonterminal, expected",
    [
        (
            """
                S -> A B
                S -> epsilon
                S1 -> S B
                A -> a
                S -> S1 
                B -> b
                """,
            build_two_cycle_graph(3, 2, ("a", "b")),
            [0, 1, 2],
            [2, 3, 4],
            Variable("S"),
            {0: {4}, 1: set(), 2: {2}},
        )
    ],
)
class TestQueries:
    def test_hellings_query_to_cfg(
        self, cfg, graph, start_vertices, end_vertices, nonterminal, expected
    ):
        assert (
            query_hellings(
                graph, CFG.from_text(cfg), start_vertices, end_vertices, nonterminal
            )
            == expected
        )

    def test_matrix_query_to_cfg(
        self, cfg, graph, start_vertices, end_vertices, nonterminal, expected
    ):
        assert (
            query_matrix(
                graph, CFG.from_text(cfg), start_vertices, end_vertices, nonterminal
            )
            == expected
        )
