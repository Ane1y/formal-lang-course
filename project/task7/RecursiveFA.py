from typing import Iterable

from pyformlang.cfg import Variable
from pyformlang.finite_automaton import DeterministicFiniteAutomaton as DFA

from project.fsm import regex_to_dfa
from task7.ecfg import ExtendedContextFreeGrammatic as ECFG


#     Реализовать тип для представления рекурсивных конечных автоматов. В качестве составных частей можно использовать
#     типы из pyformlang (например, конечные автоматы). При проектировании этого типа необходимо помнить, что
#     рекурсивные конечные автоматы будут использоваться в алгоритмах КС достижимости, основанных на линейной алгебре,
#     а значит необходимо будет строить матрицы смежности. Здесь могут быть полезны результаты домашних работ по
#     конечным автоматам.

class RecursiveFA:
    class Box:
        def __init__(self, variable: Variable = None, dfa: DFA = None):
            self.variable = variable
            self.dfa = dfa

        def minimize(self):
            self.dfa = self.dfa.minimize()

    def __init__(self, start_symbol: Variable, boxes: Iterable[Box],):
        self.start_symbol = start_symbol
        self.boxes = boxes

    def set_start_symbol(self, start_symbol: Variable):
        self.start_symbol = start_symbol

    def minimize(self):
        for box in self.boxes:
            box.minimize()
        return self

    @staticmethod
    def from_ecfg(ecfg: ECFG) -> "RecursiveFA":
        boxes = [RecursiveFA.Box(p.head, regex_to_dfa(p.body)) for p in ecfg.productions]
        return RecursiveFA(start_symbol=ecfg.start_symbol, boxes=boxes)

    @staticmethod
    def from_text(text: str, start_symbol: str) -> "RecursiveFA":
        ecfg = ECFG.from_text(text, start_symbol)
        return RecursiveFA.from_ecfg(ecfg)

    @staticmethod
    def from_file(path: str, start_symbol="S") -> "RecursiveFA":
        with open(path) as f:
            return RecursiveFA.from_text(f.read(),
                                               start_symbol=start_symbol)
