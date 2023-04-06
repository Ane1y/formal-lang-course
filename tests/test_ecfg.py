import pytest
from pyformlang.cfg import CFG, Variable
from pyformlang.regular_expression import Regex

from project.fsm import regex_to_dfa
from project.task7.ecfg import ExtendedContextFreeGrammatic as ECFG
import os
import tempfile


def test_from_file():
    fd, path = tempfile.mkstemp()
    try:
        with os.fdopen(fd, "w") as tmp:
            tmp.write("""S -> (a | b) c | $""")

        ecfg = ECFG.from_file(path)
        expected = {
            Variable("S"): Regex("(a | b) c | $"),
        }
        assert len(ecfg.productions) == len(expected) and all(
            regex_to_dfa(p.body).is_equivalent_to(regex_to_dfa(expected[p.head]))
            for p in ecfg.productions
        )
    finally:
        os.remove(path)


@pytest.mark.parametrize(
    "text, expected",
    [
        ("""""", []),
        (
            """S -> (a | b) c | $""",
            {
                Variable("S"): Regex("(a | b) c | $"),
            },
        ),
        ("""S -> a b c""", {Variable("S"): Regex("a b c")}),
        (
            """
        S -> $
        C -> a b c
             """,
            {
                Variable("S"): Regex("$"),
                Variable("C"): Regex("a b c"),
            },
        ),
    ],
)
def test_from_text(text, expected):
    ecfg = ECFG.from_text(text)
    assert len(ecfg.productions) == len(expected) and all(
        regex_to_dfa(p.body).is_equivalent_to(regex_to_dfa(expected[p.head]))
        for p in ecfg.productions
    )


@pytest.mark.parametrize(
    "cfg, expected_cfg",
    [
        (
            """
                S -> epsilon
                """,
            {Variable("S"): Regex("$")},
        ),
        (
            """
                S -> S a S
                S -> a H a
                S -> epsilon
                H -> S
                """,
            {Variable("S"): Regex("S a S | a H a | $"), Variable("H"): Regex("S")},
        ),
    ],
)
def test_from_cfg(cfg, expected_cfg):
    ecfg = ECFG.from_cfg(CFG.from_text(cfg))
    ecfg_productions = ecfg.productions
    assert all(
        regex_to_dfa(p.body).is_equivalent_to(regex_to_dfa(expected_cfg[p.head]))
        for p in ecfg_productions
    ) and len(ecfg_productions) == len(expected_cfg)
