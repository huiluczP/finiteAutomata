import DFA
import NFA


def create_dfa_input_str():
    t_start = "q0"
    t_final = ['q2']
    t_states = ["q0", "q1", "q2"]
    t_symbols = ['a', 'b']
    t_trans = {
        'q0':
        {
            'a': 'q0',
            'b': 'q1'
        },
        'q1':
        {
            'a': 'q0',
            'b': 'q2'
        },
        'q2':
        {
            'a': 'q2',
            'b': 'q2'
        },
    }
    t_dfa = DFA.DFA(t_states, t_symbols, t_trans, t_start, t_final)
    input_s = "aba"
    t_dfa.read_input(input_s)


def NFA_to_DFA():
    t_start = "q1"
    t_final = ['q1']
    t_states = ["q1", "q2", "q3"]
    t_symbols = ['a', 'b']
    t_trans = {
        'q1':
            {
                'b': ['q2'],
                'e': ['q3']
            },
        'q2':
            {
                'a': ['q2', 'q3'],
                'b': ['q3']
            },
        'q3':
            {
                'a': ['q1'],
            },
    }
    t_nfa = NFA.NFA(t_states, t_symbols, t_trans, t_start, t_final)
    t_dfa = DFA.trans_NFA(t_nfa)
    print("start state:", end="")
    print(t_dfa.start_state)
    print("final states:", end="")
    print(t_dfa.final_states)
    print("states:", end="")
    print(t_dfa.states)
    print("trans:", end="")
    print(t_dfa.trans)


def dfa_min():
    t_start = "q1"
    t_final = ["q1", "q3"]
    t_states = ["q1", "q2", "q3", "q4", "q5", "q6", "q7"]
    t_symbols = ['a', 'b']
    t_trans = {
        "q1": {
            "a": "q2",
            "b": "q4"
        },
        "q2": {
            "a": "q5",
            "b": "q3"
        },
        "q3": {
            "a": "q2",
            "b": "q6"
        },
        "q4": {
            "a": "q1",
            "b": "q5"
        },
        "q5": {
            "a": "q5",
            "b": "q5"
        },
        "q6": {
            "a": "q3",
            "b": "q5"
        },
        "q7": {
            "a": "q3",
            "b": "q6"
        }
    }
    t_dfa = DFA.DFA(t_states, t_symbols, t_trans, t_start, t_final)
    min_dfa = t_dfa.minimize()
    print(min_dfa.start_state)
    print(min_dfa.final_states)
    print(min_dfa.states)
    print(min_dfa.trans)


def DFA_to_RL():
    t_start = "q1"
    t_final = ["q3"]
    t_states = ["q1", "q2", "q3"]
    t_symbols = ['a', 'b']
    t_trans = {
        "q1": {
            "a": "q1",
            "b": "q3"
        },
        "q2": {
            "a": "q2",
            "b": "q1"
        },
        "q3": {
            "a": "q3",
            "b": "q2"
        },
    }
    t_dfa = DFA.DFA(t_states, t_symbols, t_trans, t_start, t_final)
    t_rl = t_dfa.trans_to_RL()
    print(t_rl)


if __name__ == "__main__":
    # create_dfa_input_str()
    # NFA_to_DFA()
    # dfa_min()
    DFA_to_RL()
