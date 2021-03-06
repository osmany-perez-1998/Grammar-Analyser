import pydot
from cmp.utils import ContainerSet, DisjointSet


class NFA:
    def __init__(self, states, finals, transitions, start=0):
        self.states = states
        self.start = start
        self.finals = set(finals)
        self.map = transitions
        self.vocabulary = set()
        self.transitions = {state: {} for state in range(states)}

        for (origin, symbol), destinations in transitions.items():
            assert hasattr(destinations, '__iter__'), 'Invalid collection of states'
            self.transitions[origin][symbol] = destinations
            self.vocabulary.add(symbol)

        self.vocabulary.discard('')

    def epsilon_transitions(self, state):
        assert state in self.transitions, 'Invalid state'
        try:
            return self.transitions[state]['']
        except KeyError:
            return ()

    def graph(self):
        G = pydot.Dot(rankdir='LR', margin=0.1)
        G.add_node(pydot.Node('start', shape='plaintext', label='', width=0, height=0))

        for (start, tran), destinations in self.map.items():
            tran = 'ε' if tran == '' else tran
            G.add_node(pydot.Node(start, shape='circle', style='bold' if start in self.finals else ''))
            for end in destinations:
                G.add_node(pydot.Node(end, shape='circle', style='bold' if end in self.finals else ''))
                G.add_edge(pydot.Edge(start, end, label=tran, labeldistance=2))

        G.add_edge(pydot.Edge('start', self.start, label='', style='dashed'))
        return G

    def _repr_svg_(self):
        try:
            return self.graph().create_svg().decode('utf8')
        except:
            pass


class DFA(NFA):

    def __init__(self, states, finals, transitions, start=0):
        assert all(isinstance(value, int) for value in transitions.values())
        assert all(len(symbol) > 0 for origin, symbol in transitions)

        transitions = {key: [value] for key, value in transitions.items()}
        NFA.__init__(self, states, finals, transitions, start)
        self.current = start

    def _move(self, symbol):
        # Your code here
        try:
            self.current = self.transitions[self.current[0]][symbol]
            return True
        except KeyError:
            return False

    def _reset(self):
        self.current = self.start

    def recognize(self, string):
        # Your code here
        self.current = [self.current]
        for char in string:
            if not self._move(char):
                self._reset()
                return False
        tmp = self.current[0]
        self._reset()
        return tmp in self.finals


def move(automaton, states, symbol):
    moves = set()
    for state in states:
        # Your code here
        try:
            for new_state in automaton.transitions[state][symbol]:
                moves.add(new_state)
        except KeyError:
            pass
    return moves


def epsilon_closure(automaton, states):
    pending = [s for s in states]  # equivalente a list(states) pero me gusta así :p
    closure = {s for s in states}  # equivalente a  set(states) pero me gusta así :p

    while pending:
        state = pending.pop()
        # Your code here
        for new_state in automaton.epsilon_transitions(state):
            closure.add(new_state)
            pending.append(new_state)

    return ContainerSet(*closure)


def nfa_to_dfa(automaton):
    transitions = {}

    start = epsilon_closure(automaton, [automaton.start])
    start.id = 0
    start.is_final = any(s in automaton.finals for s in start)
    states = [start]

    pending = [start]
    while pending:
        state = pending.pop()

        for symbol in automaton.vocabulary:
            # Your code here
            # ...
            goto = move(automaton, state, symbol)
            new_state = epsilon_closure(automaton, goto)
            if len(new_state) == 0:
                continue
            new_state.is_final = any(s in automaton.finals for s in new_state)

            try:
                transitions[state.id, symbol]
                assert False, 'Invalid DFA!!!'
            except KeyError:
                # Your code here
                new_id = 0
                for i, item in enumerate(states, 0):
                    if item.set.issubset(new_state.set) and new_state.set.issubset(item.set):
                        new_state.id = item.id
                        new_id = item.id
                        break
                else:
                    new_state.id = i + 1
                    pending.append(new_state)
                    states.append(new_state)
                    new_id = i + 1

                transitions[state.id, symbol] = new_id

    finals = [state.id for state in states if state.is_final]
    dfa = DFA(len(states), finals, transitions)
    return dfa


def automata_union(a1, a2):
    transitions = {}

    start = 0
    d1 = 1
    d2 = a1.states + d1
    final = a2.states + d2

    for (origin, symbol), destinations in a1.map.items():
        transitions[origin + d1, symbol] = [i + d1 for i in destinations]

    for (origin, symbol), destinations in a2.map.items():
        transitions[origin + d2, symbol] = [i + d2 for i in destinations]

    transitions[start, ''] = [d1, d2]

    for final_a1 in a1.finals:
        transitions[final_a1 + d1, ''] = [final]
    for final_a2 in a2.finals:
        transitions[final_a2 + d2, ''] = [final]

    states = a1.states + a2.states + 2
    finals = {final}

    return NFA(states, finals, transitions, start)


def automata_concatenation(a1, a2):
    transitions = {}

    start = 0
    d1 = 0
    d2 = a1.states + d1
    final = a2.states + d2

    for (origin, symbol), destinations in a1.map.items():
        transitions[origin, symbol] = destinations

    for (origin, symbol), destinations in a2.map.items():
        transitions[origin + d2, symbol] = [i + d2 for i in destinations]

    for final_a1 in a1.finals:
        transitions[final_a1, ''] = [d2]
    for final_a2 in a2.finals:
        transitions[final_a2 + d2, ''] = [final]

    states = a1.states + a2.states + 1
    finals = {final}

    return NFA(states, finals, transitions, start)


# TODO: Automata Clausura
def automata_closure(a):
    pass


def distinguish_states(group, automaton, partition):
    split = {}
    vocabulary = tuple(automaton.vocabulary)

    for member in group:
        # Your code here
        for subgroup in split.keys():
            for symbol in vocabulary:
                try:
                    s_transition = automaton.transitions[member.value][symbol]
                except KeyError:
                    s_transition = -1
                try:
                    t_transition = automaton.transitions[subgroup][symbol]
                except KeyError:
                    t_transition = -1

                if s_transition == -1 and t_transition != -1:
                    break

                if t_transition != -1 and s_transition == -1:
                    break

                if t_transition == -1 and s_transition == -1:
                    continue

                if not partition[s_transition[0]].representative == partition[t_transition[0]].representative:
                    break
            else:
                a = split[subgroup]
                a.append(member.value)
                split[subgroup] = a
                break
        else:
            split[member.value] = [member.value]
        pass

    return [group for group in split.values()]


def state_minimization(automaton):
    partition = DisjointSet(*range(automaton.states))

    ## partition = { NON-FINALS | FINALS }
    # Your code here
    non_finals = [state for state in range(automaton.states) if state not in automaton.finals]
    finals = [state for state in automaton.finals]

    partition.merge(non_finals)
    partition.merge(finals)

    while True:
        new_partition = DisjointSet(*range(automaton.states))

        ## Split each group if needed (use distinguish_states(group, automaton, partition))
        # Your code here
        for group in partition.groups:
            if len(group) > 1:
                new_partition.merge([i.value for i in group])

        aux_partition = DisjointSet(*range(automaton.states))
        for group in new_partition.groups:
            new_groups = distinguish_states(group, automaton, new_partition)
            for i in new_groups:
                aux_partition.merge(i)
        new_partition = aux_partition

        if len(new_partition) == len(partition):
            break

        partition = new_partition

    return partition


def automata_minimization(automaton):
    partition = state_minimization(automaton)

    states = [s for s in partition.representatives]

    transitions = {}
    for i, state in enumerate(states):
        origin = state.value
        for symbol, destinations in automaton.transitions[origin].items():
            fixed_destinations = []
            for st in destinations:
                representative = partition[st].representative
                fixed_destinations.append(states.index(representative))
            try:
                transitions[i, symbol]
                assert False
            except KeyError:
                transitions[i, symbol] = fixed_destinations[0]

    finals = []
    start = 0

    for i, state_representative in enumerate(states):
        for group in partition.groups:
            if state_representative in group:
                for state in group:
                    if state.value in automaton.finals:
                        finals.append(i)
                        break
                    if state.value == automaton.start:
                        start = i

    return DFA(len(states), finals, transitions, start)
