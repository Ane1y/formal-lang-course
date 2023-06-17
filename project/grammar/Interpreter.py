import io
from dataclasses import dataclass

import networkx as nx
from antlr4 import *
from typing import TextIO, Tuple

from pyformlang.finite_automaton import EpsilonNFA, State, Symbol

from fsm import graph_to_nfa
from grammar.antlr.GrammarParser import GrammarParser
from grammar.antlr.GrammarVisitor import GrammarVisitor
from grammar import Grammar
from grammar.Grammar import parse_stream
from regular_path_queries import intersect, union, concat, get_transitive_closure, find_reachable



class Interpreter(GrammarVisitor):
    def __init__(self, writer : TextIO):
        self.memory = {}
        self.writer = writer

    def visitBind(self, ctx):
        name = ctx.var().getText()
        value = self.visit(ctx.expr())
        self.memory[name] = value
        return value

    def visitPrint_expr(self, ctx):
        value = self.visit(ctx.expr())
        print(value, file=self.writer)
        return value

    def visitVar(self, ctx):
        name = ctx.IDENT().getText()
        if name in self.memory:
            return self.memory[name]
        return 0

    def visitLiteral(self, ctx:GrammarParser.LiteralContext) -> int | str:
        # ура управление на исключениях!!
        # хорошо, что я пишу на питоне
        try:
            return int(ctx.getText())
        except:
            return ctx.getText()

    def visitsetElemLiteral(self, ctx: GrammarParser.SetElemLiteralContext) -> int | str:
        return self.visit(ctx.children[0])

    def visitSetElemRange(self, ctx:GrammarParser.SetElemRangeContext) -> Tuple[int, int]:
        return self.visit(ctx.children[0]), self.visit(ctx.children[2])

    def visitSet(self, ctx: GrammarParser.SetContext) -> frozenset:
        vals = set()
        for child in ctx.children[1:-1:2]:
            x = self.visit(child)
            if isinstance(x, tuple):
                for i in range(x[0], x[1] + 1):
                    vals.add(i)
            else:
                vals.add(x)
        return frozenset(vals)
    def visitVal(self, ctx):
        if ctx.literal():
            return self.visit(ctx.literal())
        elif ctx.set_():
            return self.visit(ctx.set_())
        else:
            raise TypeError(f"Invalid type {type(ctx)}")



    def visitExprParenthesis(self, ctx):
        return self.visit(ctx.expr())

    def visitExprVar(self, ctx):
        return self.visit(ctx.var())

    def visitExprVal(self, ctx):
        return self.visit(ctx.val())

    def visitExprMap(self, ctx):
        # todo: todo
        func = self.visit(ctx.lambda_expr())
        lst = self.visit(ctx.expr())
        return list(map(func, lst))

    def visitExprFilter(self, ctx):
        # todo: todo
        func = self.visit(ctx.lambda_expr())
        lst = self.visit(ctx.expr())
        return list(filter(func, lst))

    def visitExprAnd(self, ctx):
        left = self.visit(ctx.expr(0))
        right = self.visit(ctx.expr(1))
        if not isinstance(left, EpsilonNFA) or not isinstance(right, EpsilonNFA):
            raise TypeError(f"Cannot intersect {type(left)} and {type(right)}")
        return intersect(left, right)

    def visitExprOr(self, ctx:GrammarParser.ExprConcatContext):
        left = self.visit(ctx.expr(0))
        right = self.visit(ctx.expr(1))
        if not isinstance(left, EpsilonNFA) or not isinstance(right, EpsilonNFA):
            raise TypeError(f"Cannot get union of {type(left)} and {type(right)}")
        return union(left, right)

    def visitExprConcat(self, ctx:GrammarParser.ExprConcatContext) -> EpsilonNFA:
        left = self.visit(ctx.expr(0))
        right = self.visit(ctx.expr(1))
        if not isinstance(left, EpsilonNFA) or not isinstance(right, EpsilonNFA):
            raise TypeError(f"Cannot concatenate {type(left)} and {type(right)}")
        return concat(left, right)

    def visitExprKleene(self, ctx):
        fa = self.visit(ctx.children[0])
        if isinstance(fa, EpsilonNFA):
            return get_transitive_closure(fa)
        else:
            raise TypeError(f"{type(fa)} is not a graph")

    def visitExprSetStart(self, ctx: GrammarParser.ExprSetStartContext) -> EpsilonNFA:
        vertices, graph = self._get_vertices_and_graph(ctx)
        for state in graph.start_states.copy():
            graph.remove_start_state(state)
        for vertex in vertices:
            graph.add_start_state(vertex)
        return graph

    def visitExprSetFinal(self, ctx: GrammarParser.ExprSetFinalContext) -> EpsilonNFA:
        vertices, graph = self._get_vertices_and_graph(ctx)
        for state in graph.final_states.copy():
            graph.remove_final_state(state)
        for vertex in vertices:
            graph.add_sfinal_state(vertex)
        return graph


    def visitExprAddStart(self, ctx: GrammarParser.ExprAddStartContext) -> EpsilonNFA:
        vertices, graph = self._get_vertices_and_graph(ctx)
        fa = graph.copy()
        for x in vertices:
            fa.add_start_state(x)
        return fa

    def visitExprAddFinals(self, ctx: GrammarParser.ExprAddFinalsContext) -> EpsilonNFA:
        vertices, graph = self._get_vertices_and_graph(ctx)
        fa = graph.copy()
        for x in vertices:
            fa.add_final_state(x)
        return fa

    def visitExprGetStart(self, ctx: GrammarParser.ExprGetStartContext) -> frozenset:
        val = self.visit(ctx.children[1])
        if isinstance(val, EpsilonNFA):
            return frozenset(x.value for x in val.start_states)
        else:
            raise TypeError(f"{type(val)} has not start nodes")

    def visitExprGetFinal(self, ctx: GrammarParser.ExprGetFinalContext) -> frozenset:
        val = self.visit(ctx.children[1])
        if isinstance(val, EpsilonNFA):
            return frozenset(x.value for x in val.final_states)
        else:
            raise TypeError(f"{type(val)} has not final nodes")


    def visitExprGerReachable(self, ctx:GrammarParser.ExprGerReachableContext) -> frozenset:
        val = self.visit(ctx.children[1])
        if not isinstance(val, EpsilonNFA):
            raise TypeError(f"Cannot get reachable of type {type(val)}")
        return frozenset(find_reachable(val))

    def visitExprGetVertices(self, ctx):
            val = self.visit(ctx.children[1])
            if isinstance(val, EpsilonNFA):
                vertices = set()
                for x in val.states:
                    assert isinstance(x, State)
                    vertices.add(x.value)
                return frozenset(vertices)
            else:
                raise TypeError(f"{type(val)} does not have vertices")


    def visitExprGetEdges(self, ctx:GrammarParser.ExprGetEdgesContext) -> frozenset:
        val = self.visit(ctx.children[1])
        if isinstance(val, EpsilonNFA):
            items = set()
            for fro, symb, to in val:
                assert isinstance(fro, State)
                assert isinstance(symb, Symbol)
                assert isinstance(to, State)
                assert isinstance(symb.value, str)
                items.add((fro.value, symb.value, to.value))
            return frozenset(items)
        else:
            raise TypeError(f"Cannot get edges of type {type(val)}")

    def visitExprGetLabels(self, ctx):
        val = self.visit(ctx.children[1])
        if isinstance(val, EpsilonNFA):
            items = set()
            for fro, symb, to in val:
                assert isinstance(symb.value, str)
                items.add(symb.value)
            return frozenset(items)
        else:
            raise TypeError(f"{type(val)} has not edges")


    def visitExprLoad(self, ctx):
        path = ctx.children[1].getText()[1:-1]
        if not isinstance(path, str):
            raise TypeError(f"{type(path)} is not a string")
        graph = nx.nx_pydot.read_dot(path)
        fa = graph_to_nfa(graph, graph.nodes, graph.nodes)
        return fa

    def visitExprFiniteAutomata(self, ctx):
        val = self.visit(ctx.children[1])
        if isinstance(val, str):
            fa = EpsilonNFA()
            fa.add_start_state(State(0))
            fa.add_final_state(State(1))
            fa.add_transition(State(0), Symbol(val), State(1))
            return fa
        else:
            raise TypeError(f"{type(val)} cannot be a symbol")



    def visitLambda_expr(self, ctx):
        if ctx.ARROW():
            params = [ctx.pattern().getText()]
            body = lambda x: x # TODO: implement lambda body evaluation
            return lambda x: body(x)

    def _get_vertices_and_graph(self, ctx) -> tuple:
        vertices = self.visit(ctx.children[1])

        if not isinstance(vertices, frozenset):
            raise TypeError(f"{type(vertices)} is not a set")

        graph = self.visit(ctx.children[3])
        if not isinstance(graph, EpsilonNFA):
            raise TypeError(f"{type(graph)} does not allow to add vertices")

        return vertices, graph

def interpret(program: GrammarParser.ProgContext, writer: TextIO):
    error_visitor = Grammar.ErrorVisitor()
    error_visitor.visit(program)
    if error_visitor.has_error:
        print("Error visitor find error", file=writer)
        return

    exec_visitor = Interpreter(writer)
    try:
        exec_visitor.visit(program)
    except Exception as e:
        print(e, file=writer)
        print("Error occurred", file=writer)
        return

def interpret_stream(reader: InputStream, writer: TextIO):
    tree = parse_stream(reader)
    interpret(tree, writer)


def interpret_to_writer(input: str, writer: TextIO):
    interpret_stream(InputStream(input), writer)


def interpret_str(input: str) -> str:
    with io.StringIO() as writer:
        interpret_to_writer(input, writer)
        return writer.getvalue()