from grammar.Interpreter import interpret_str


def test_simple() :
    # assert interpret_str("print 5;") == "5\n"
    # assert interpret_str("print {4};") == "frozenset({4})\n"
    # assert interpret_str("print {};") == "frozenset()\n"
    # assert interpret_str("var a = 5; print a") == "5\n"
    # assert interpret_str("var a = {1,2,3}; print a;") == "frozenset({1, 2, 3})\n"
    # assert interpret_str('print "asd"') == '"asd"\n';
    assert interpret_str('print get_edges fa "a" | fa "ab";') == 'frozenset({((2, 0), \'"ab"\', (2, 1)), ((1, 0), \'"a"\', (1, 1))})\n'
    assert interpret_str('print')
    # assert interpret_str("x -> x & 5; print x") == "\n";
    # assert interpret_str("print {0, 6} & {0, 5}") == "frozenset({0})\n"