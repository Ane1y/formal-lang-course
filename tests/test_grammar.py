import filecmp
import sys

import pytest

from project.grammar.Grammar import check, generate_dot_description


@pytest.mark.parametrize(
    "txt, accepted",
    [
        ("var abc = 6;", True),
        ("var 1 = a;", False),
        ("var 3;", False),
    ],
)
def test_bind(txt, accepted):
    assert check(text=txt) == accepted


@pytest.mark.parametrize(
    "txt, accepted",
    [
        ("print a;", True),
        ("print 7;", True),
    ],
)
def test_print(txt, accepted):
    assert check(text=txt) == accepted


@pytest.mark.parametrize(
    "txt, accepted",
    [
        ("x -> x & 5;", True),
        ("(x, y) -> x & y;", True),
        ("-> a;", False),
    ],
)
def test_lambda(txt, accepted):
    assert check(text=txt) == accepted


@pytest.mark.parametrize(
    "txt, accepted",
    [
        ("map (x -> x & 5) a;", True),
        ("map (x, y) -> x & y b;", True),
        ("map a a;", False),
        ("map x -> x y -> y;", False),
    ],
)
def test_map(txt, accepted):
    assert check(text=txt) == accepted


@pytest.mark.parametrize(
    "txt, accepted",
    [
        ("set_start {} of g;", True),
        ("set_start get_vertices g of g1;", True),
        ("set_start {1..30} of g;", True),
    ],
)
def test_set_start(txt, accepted):
    assert check(text=txt) == accepted


@pytest.mark.parametrize(
    "txt, accepted",
    [
        ('load "bip.dot";', True),
        ("load 5;", False),
    ],
)
def test_load(txt, accepted):
    assert check(text=txt) == accepted


def test_generate_dot_description():
    generate_dot_description("""set_start get_vertices g of g1;
    map x -> x | 5 g1;""", "tmp.dot")
    filecmp.cmp("tmp.dot", "right.dot")

