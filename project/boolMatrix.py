from abc import ABC, abstractmethod
from pyformlang.finite_automaton import State, NondeterministicFiniteAutomaton
from pyformlang.cfg import Variable
from scipy import sparse

from task7.RecursiveFA import RecursiveFA


class BoolMatrix(ABC):
    def __init__(self):
        self.num_states = 0
        self.start_states = set()
        self.final_states = set()
        self.bool_matrices = {}
        self.state_indices = {}
        self.states_to_box_variable = {}

    def get_states(self):
        return self.state_indices.keys()

    def get_start_states(self):
        return self.start_states.copy()

    def get_final_states(self):
        return self.final_states.copy()


    @classmethod
    def from_rfa(cls, rfa: RecursiveFA):
        bm = cls()
        bm.num_states = sum(len(box.dfa.states) for box in rfa.boxes)
        box_idx = 0

        for box in rfa.boxes:
            for idx, state in enumerate(box.dfa.states):
                new_name = bm._rename_rsm_box_state(state, box.variable)
                bm.state_indices[new_name] = idx + box_idx
                if state in box.dfa.start_states:
                    bm.start_states.add(bm.state_indices[new_name])
                if state in box.dfa.final_states:
                    bm.final_states.add(bm.state_indices[new_name])
            bm.states_to_box_variable.update(
                {
                    (
                        bm.state_indices[
                            bm._rename_rsm_box_state(box.dfa.start_state, box.variable)
                        ],
                        bm.state_indices[bm._rename_rsm_box_state(state, box.variable)],
                    ): box.variable.value
                    for state in box.dfa.final_states
                }
            )
            bm.bool_matrices.update(bm._create_box_bool_matrices(box))
            box_idx += len(box.dfa.states)
        return bm

    def get_nonterminals(self, s_from, s_to):
        return self.states_to_box_variable.get((s_from, s_to))

    def _rename_rsm_box_state(self, state: State, box_var: Variable):
        return State(f"{state.value}#{box_var.value}")

    def _create_box_bool_matrices(self, box: RecursiveFA.Box):

        bool_matrices = {}

        for s_from, trans in box.dfa.to_dict().items():
            for label, states_to in trans.items():
                if not isinstance(states_to, set):
                    states_to = {states_to}
                for s_to in states_to:
                    idx_from = self.state_indices[
                        self._rename_rsm_box_state(s_from, box.variable)
                    ]
                    idx_to = self.state_indices[
                        self._rename_rsm_box_state(s_to, box.variable)
                    ]
                    label = str(label)
                    if label in self.bool_matrices:
                        self.bool_matrices[label][idx_from, idx_to] = True
                        continue
                    if label not in bool_matrices:
                        bool_matrices[label] = self._create_bool_matrix(
                            (self.num_states, self.num_states)
                        )
                    bool_matrices[label][idx_from, idx_to] = True

        return bool_matrices

    def _create_bool_matrices(self, automaton):
        bool_matrices = {}
        for s_from, trans in automaton.to_dict().items():
            for label, states_to in trans.items():
                if not isinstance(states_to, set):
                    states_to = {states_to}
                for s_to in states_to:
                    idx_from = self.state_indices[s_from]
                    idx_to = self.state_indices[s_to]
                    label = str(label)
                    if label not in bool_matrices:
                        bool_matrices[label] = self._create_bool_matrix(
                            (self.num_states, self.num_states)
                        )
                    bool_matrices[label][idx_from, idx_to] = True
        return bool_matrices

    @staticmethod
    def _create_bool_matrix(shape):
        return sparse.dok_matrix(shape, dtype=bool)

