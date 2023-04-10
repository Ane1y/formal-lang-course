#     Реализовать внутреннее представление для ECFG, пригодное как для дальнейшей конвертации в рекурсивный
#     конечный автомат, так и для получения его из "внешних источников", таких, например, как преобразование из
#     стандартного внутреннего представления КС грамматик в pyformlang
# #
from typing import AbstractSet, Iterable

from pyformlang.cfg import Variable, CFG
from pyformlang.regular_expression import Regex


class ExtendedContextFreeGrammatic:

    class Production:
        """Store production for grammatic
            """
        def __init__(self, head: Variable, body: Regex):
            self.head = head
            self.body = body

        def __str__(self):
            return str(self.head) + " -> " + str(self.body)

    def __init__(
        self,
        variables: AbstractSet[Variable] = None,
        start_symbol: Variable = None,
        productions: Iterable[Production] = None,
    ):
        self.variables = variables if variables else set()
        self.start_symbol = start_symbol
        self.productions = productions if productions else set()

    def to_text(self) -> str:
        """String representation of ecfg
        """
        return "\n".join(str(p) for p in self.productions)

    @staticmethod
    def from_text(
        text: str, start_symbol=Variable("S")
    ) -> "ExtendedContextFreeGrammatic":
        """
        Creates grammatic from text of production
        :param text: should be formed as "S -> a b v"
        :param start_symbol: start symbol for ecfg
        :return: ecfg by given prodictions
        """

        variables = set()
        productions = set()

        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue

            production_objects = line.split("->")

            if len(production_objects) != 2:
                raise ValueError("There should only be one production per line.")

            head_text, body_text = production_objects
            head = Variable(head_text.strip())

            if head in variables:
                raise ValueError(
                    "There should only be one production for each variable."
                )

            variables.add(head)
            body = Regex(body_text.strip())
            productions.add(ExtendedContextFreeGrammatic.Production(head, body))

        return ExtendedContextFreeGrammatic(
            variables=variables, start_symbol=start_symbol, productions=productions
        )

    @staticmethod
    def from_file(path: str, start_symbol: str = "S") -> "ExtendedContextFreeGrammatic":
        """
        :param path: path to file with productions
        :param start_symbol: start symbol
        :return: ecfg from given productions
        """
        with open(path) as f:
            return ExtendedContextFreeGrammatic.from_text(
                f.read(), start_symbol=start_symbol
            )

    @staticmethod
    def from_cfg(cfg: CFG) -> "ExtendedContextFreeGrammatic":
        """
        Returns ecfg from cfg
        :param cfg:
        :return: ecfg from cfg
        """
        productions = {}

        for p in cfg.productions:
            body = Regex(
                " ".join(cfg_obj.value for cfg_obj in p.body) if p.body else "$"
            )
            if p.head not in productions:
                productions[p.head] = body
            else:
                productions[p.head] = productions.get(p.head).union(body)

        ecfg_productions = [
            ExtendedContextFreeGrammatic.Production(head, body)
            for head, body in productions.items()
        ]

        return ExtendedContextFreeGrammatic(
            variables=cfg.variables,
            start_symbol=cfg.start_symbol,
            productions=ecfg_productions,
        )
