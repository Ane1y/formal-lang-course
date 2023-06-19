from grammar.antlr.GrammarVisitor import GrammarVisitor
from grammar.antlr.GrammarLexer import GrammarLexer
from grammar.antlr.GrammarParser import GrammarParser
from grammar.antlr.GrammarListener import GrammarListener

from antlr4 import *
from antlr4.tree.Tree import TerminalNodeImpl
from pydot import Dot, Node, Edge


def parse_stream(stream: InputStream = None):
    lexer = GrammarLexer(stream)
    lexer.removeErrorListeners()
    stream = CommonTokenStream(lexer)
    parser = GrammarParser(stream)
    parser.removeErrorListeners()
    return parser.prog()


def parse(inputFile: str = None, text: str = None):
    if inputFile and text:
        raise ValueError("Can not decide which stream to use")

    if inputFile:
        stream = FileStream(inputFile)
    elif text:
        stream = InputStream(text)
    else:
        stream = StdinStream()

    return parse_stream(stream)


def check(inputFile: str = None, text: str = None):
    tree = parse(inputFile=inputFile, text=text)
    visitor = ErrorVisitor()
    visitor.visit(tree)
    return not visitor.has_error


def generate_dot_description(text: str, filename: str):
    if not check(text=text):
        raise ValueError("Text is not match grammar")
    ast = parse(text=text)
    tree = Dot("tree", graph_type="digraph")
    ParseTreeWalker().walk(
        DotTreeListener(tree, GrammarParser.ruleNames, GrammarLexer.symbolicNames), ast
    )
    tree.write(filename)


class DotTreeListener(GrammarListener):
    def __init__(self, tree: Dot, rules: list, symbols: list):
        self.tree = tree
        self.num_nodes = 0
        self.nodes = {}
        self.rules = rules
        self.symbols = symbols
        super(DotTreeListener, self).__init__()

    def enterEveryRule(self, ctx: ParserRuleContext):
        if ctx not in self.nodes:
            self.num_nodes += 1
            self.nodes[ctx] = self.num_nodes
        if ctx.parentCtx:
            self.tree.add_edge(Edge(self.nodes[ctx.parentCtx], self.nodes[ctx]))
        label = self.rules[ctx.getRuleIndex()]
        self.tree.add_node(Node(self.nodes[ctx], label=label))

    def visitTerminal(self, node: TerminalNodeImpl):
        self.num_nodes += 1
        self.tree.add_edge(Edge(self.nodes[node.parentCtx], self.num_nodes))
        if self.symbols[node.symbol.type - 1].lower() != node.getText().lower():
            self.tree.add_node(
                Node(
                    self.num_nodes,
                    label=f"{self.symbols[node.symbol.type - 1]}: {node.getText()}",
                )
            )
        else:
            self.tree.add_node(
                Node(self.num_nodes, label=f"{self.symbols[node.symbol.type - 1]}")
            )


class ErrorVisitor(GrammarVisitor):
    def __init__(self):
        self.has_error = False

    def visitErrorNode(self, node):
        self.has_error = True
