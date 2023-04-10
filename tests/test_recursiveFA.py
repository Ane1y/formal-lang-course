import os
import tempfile

import pytest

from boolMatrix import BoolMatrix
from project.fsm import regex_to_dfa
from project.task7.ecfg import ExtendedContextFreeGrammatic as ECFG
from project.task7.RecursiveFA import RecursiveFA as RFA

@pytest.mark.parametrize(
    """text""",
    (
        """
        S -> $
        """,
        """
        S -> a b c
        A -> S
        B -> q w e
        """,
    ),
)
def test_from_text(text: str):
    ecfg = ECFG.from_text(text)
    expected_start_symbol = ecfg.start_symbol
    expected_boxes = [RFA.Box(p.head, regex_to_dfa(p.body)) for p in ecfg.productions]

    rfa = RFA.from_ecfg(ecfg)
    actual_start_symbol = rfa.start_symbol
    actual_boxes = rfa.boxes

    return (
        actual_start_symbol == expected_start_symbol and actual_boxes == expected_boxes
    )


def test_from_file():
    text = """
        S -> a b c
        A -> S
        B -> q w e
        """
    fd, path = tempfile.mkstemp()
    try:
        with os.fdopen(fd, "w") as tmp:
            tmp.write("""S -> (a | b) c | $""")

        ecfg = ECFG.from_text(text)
        expected_start_symbol = ecfg.start_symbol
        expected_boxes = [
            RFA.Box(p.head, regex_to_dfa(p.body)) for p in ecfg.productions
        ]

        rfa = RFA.from_ecfg(ecfg)
        actual_start_symbol = rfa.start_symbol
        actual_boxes = rfa.boxes

        return (
            actual_start_symbol == expected_start_symbol
            and actual_boxes == expected_boxes
        )

    finally:
        os.remove(path)

def test_bool_matrix():
    rfa = RFA.from_text("""S -> a b""", "S")
    mat = BoolMatrix.from_rfa(rfa)
    assert len(mat.bool_matrices) == 2
    assert 'b' in mat.bool_matrices
    assert 'a' in mat.bool_matrices
    print(mat)