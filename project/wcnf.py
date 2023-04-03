#  Используя возможности pyformlang для работы с контекстно-свободными грамматиками реализовать функцию преобразования
#  контекстно-свободной грамматики в ослабленную нормальную форму Хомского (ОНФХ), но не классическую нормальную форму
#  Хомского (НФХ). НФХ является частным случаем ОНФХ, а значит можно утверждать, что грамматика, находящаяся в НФХ
#  находится и в ОНФХ. Но в данной задаче нас интересует максимально слабая форма, то есть ОНФХ, но не НФХ.
from pyformlang.cfg import CFG


# Алгоритм:
#     \item Замена неодиночных терминалов
#     \item Удаление длинных правил
#     \item Удаление $\varepsilon$-правил
#     \item Удаление цепных правил
#     \item Удаление бесполезных нетерминалов


def cfg_to_wcnf(cfg: CFG) -> CFG:
    cleaned_cfg = cfg.eliminate_unit_productions().remove_useless_symbols()
    nonsolitary_cfg = cleaned_cfg._get_productions_with_only_single_terminals()
    new_rules = cleaned_cfg._decompose_productions(nonsolitary_cfg)
    return CFG(start_symbol=cleaned_cfg.start_symbol, productions=set(new_rules))


# Предусмотреть возможность чтения грамматики из файла. Формат файла определяется возможностями pyformalng.
# Например, можно использовать эту функцию.


def read_from_file(filename: str):
    with open(filename) as file:
        return CFG.from_text(file.read())
