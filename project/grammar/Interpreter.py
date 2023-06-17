import io

from antlr4 import *
from typing import TextIO

from pyformlang.finite_automaton import EpsilonNFA, State, Symbol

from grammar.antlr.GrammarParser import GrammarParser
from grammar.antlr.GrammarVisitor import GrammarVisitor
from grammar import Grammar
from grammar.Grammar import parse_stream
from regular_path_queries import intersect, union, concat


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

    def visitVal(self, ctx):
        if ctx.LITERAL():
            try:
                return int(ctx.LITERAL().getText())
            except:
                return ctx.LITERAL().getText()
        elif ctx.SET():
            tmp = set()
            split = ctx.SET().getText()[1:-1].split(',')
            if split[0] != "":
                for elem in split:
                    tmp.add(int(elem))
            return frozenset(tmp)

    def visitExprParenthesis(self, ctx):
        return self.visit(ctx.expr())

    def visitExprVar(self, ctx):
        return self.visit(ctx.var())

    def visitExprVal(self, ctx):
        return self.visit(ctx.val())

    def visitExprMap(self, ctx):
        func = self.visit(ctx.lambda_expr())
        lst = self.visit(ctx.expr())
        return list(map(func, lst))

    def visitExprFilter(self, ctx):
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
            raise TypeError(f"Cannot intersect {type(left)} and {type(right)}")
        return union(left, right)

    def visitExprConcat(self, ctx:GrammarParser.ExprConcatContext) -> EpsilonNFA:
        left = self.visit(ctx.expr(0))
        right = self.visit(ctx.expr(1))
        return concat(left, right)

    def visitExprKleene(self, ctx):
        pass  # TODO: implement Kleene star operation

    def visitExprTrans(self, ctx):
        pass  # TODO: implement transitive closure operation

    def visitExprSetStart(self, ctx):
        pass  # TODO: implement set start operation

    def visitExprSetFinal(self, ctx):
        pass  # TODO: implement set final operation

    def visitExprAddStart(self, ctx: GrammarParser.ExprAddStartContext) -> EpsilonNFA:
        vertices = self.visit(ctx.children[1])

        if not isinstance(vertices, frozenset):
            raise TypeError(f"{type(vertices)} is not a set")

        graph = self.visit(ctx.children[5])
        if isinstance(graph, EpsilonNFA):
            fa = graph.copy()
            for x in vertices:
                fa.add_start_state(x)
            return fa
        else:
            raise TypeError(f"{type(graph)} does not allow to add vertices")

    def visitExprAddFinals(self, ctx):
        pass  # TODO: implement add finals operation

    def visitExprGetStart(self, ctx):
        pass  # TODO: implement get start operation

    def visitExprGetFinal(self, ctx):
        pass  # TODO: implement get final operation

    def visitExprGerReachable(self, ctx):
        pass  # TODO: implement get reachable operation

    def visitExprGetVertices(self, ctx):
        pass  # TODO: implement get vertices operation

    def visitExprGetEdges(self, ctx:GrammarParser.ExprGetEdgesContext):
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
        pass  # TODO: implement get labels operation

    def visitExprLoad(self, ctx):
        pass  # TODO: implement load operation

    def visitExprFiniteAutomata(self, ctx):
        return self.visit(ctx.finite_automata())

    def visitFinite_automata(self, ctx):
        val = ctx.LITERAL().getText()
        if isinstance(val, str):
            fa = EpsilonNFA()
            fa.add_start_state(State(0))
            fa.add_final_state(State(1))
            fa.add_transition(State(0), Symbol(val), State(1))
            return fa
        # elif isinstance(val, EpsilonNFA):
        #     return RSM(val.backend)
        else:
            raise TypeError(f"{type(val)} cannot be a symbol")
    def visitLambda_expr(self, ctx):
        if ctx.ARROW():
            params = [ctx.pattern().getText()]
            body = lambda x: x # TODO: implement lambda body evaluation
            return lambda x: body(x)

def interpret(program: GrammarParser.ProgContext, writer: TextIO):
    # error_visitor = Grammar.ErrorVisitor()
    # error_visitor.visit(program)
    # if error_visitor.has_error:
    #     print("Error visitor find error", file=writer)
    #     return

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