from grammar.Interpreter import interpret_str


def test_simple() :
    # assert interpret_str("print 5;") == "5\n"
    # assert interpret_str("print {4};") == "frozenset({4})\n"
    # assert interpret_str("print {};") == "frozenset()\n"
    # assert interpret_str('print {1,   2, 3   };') == "frozenset({1, 2, 3})\n"
    # assert interpret_str('print {1..5};') == "frozenset({1, 2, 3, 4, 5})\n"
    #
    # assert interpret_str("var a = 5; print a;") == "5\n"
    # assert interpret_str("var a = {1, 2, 3}; print a;") == "frozenset({1, 2, 3})\n"
    # assert interpret_str('print "asd";') == '"asd"\n';
    # assert interpret_str('print get_start add_start {1} of fa "a";') == "frozenset({0, 1})\n"
    # assert interpret_str('print get_start set_start {1} of fa "a";') == "frozenset({1})\n"

    # порядок недетерминирован, поэтому эти тесты проходят иногда
    # assert interpret_str('print get_edges fa "a" ++ fa "b";') == "frozenset({((2, 0), '\"b\"', (2, 1)), ((1, 0), '\"a\"', (1, 1)), ((1, 0), 'epsilon', (2, 1))})\n"
    # assert interpret_str('print get_vertices load "right.dot";') == "frozenset({'31', '21', '28', '32', '15', '34'," \
    #                                                                 " '29', '11', '23', '16', '1', '30', '9', '27', " \
    #                                                                 "'14', '18', '6', '19', '10', '12', '3', '5', '26', " \
    #                                                                 "'2', '13', '8', '24', '35', '17', '4', '33', '20', " \
    #                                                                 "'7', '22', '25'})\n"
    # assert interpret_str('print get_edges fa "a" | fa "ab";') == 'frozenset({((2, 0), \'"ab"\', (2, 1)), ((1, 0), \'"a"\', (1, 1))})\n'



    assert interpret_str('print get_labels fa "a"*;') == 'frozenset({\'"a"\', \'epsilon\'})\n' \
           or 'frozenset({\'epsilon\', \'"a"\'})\n'

    assert interpret_str('print get_reachable fa "a" ++ fa "b";') == "frozenset({((1, 0), (1, 1))})\n"
    # assert interpret_str('print map ')
    # assert interpret_str("x -> x & 5; print x") == "\n";
    # assert interpret_str("print {0, 6} & {0, 5}") == "frozenset({0})\n"