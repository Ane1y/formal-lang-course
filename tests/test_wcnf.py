import tempfile

from pyformlang.cfg import CFG

from wcnf import cfg_to_wcnf, read_from_file


def test_cfg_to_wcnf():
    gr = CFG.from_text(
        """S -> A B C
        A -> a
        B -> b
        C -> c"""
    )
    cfg_wcnf = cfg_to_wcnf(gr)
    expected = CFG.from_text(
        """
        B -> b
        A -> a
        C -> c
        S -> A C#CNF#1
        C#CNF#1 -> B C"""
    )

    assert set(cfg_wcnf.productions) == set(expected.productions)


def test_read_from_file():
    gr = read_from_file("test_grammar.txt")
    actual = gr.to_text()

    expected = """
S -> A b S
A -> 
A -> a b c"""

    actual_lines = set([l for l in actual.split("\n") if l != ""])
    expected_lines = set([l for l in expected.split("\n") if l != ""])

    assert actual_lines == expected_lines
