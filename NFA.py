"""
实现NFA非确定有限自动机
包括四元组转NFA(c)
NFA输入验证
RL转DFA（待定，可能从NFA转过来方便一点）
"""
import copy
from collections import deque


class NFA:
    states = set()  # 所有状态
    input_symbols = set()  # 字母表
    start_state = "q0"  # 初始状态，仅有一个
    final_states = set()  # 终结状态
    trans = {}  # 转移函数，字典，包括启示状态，字符与终点{'q1':{'a':'q2', 'b':'q3'}}，NFA包括e转移规则

    def __init__(self, states, input_symbols, trans, start_state, final_states):
        self.states = states.copy()
        self.input_symbols = input_symbols.copy()
        self.trans = copy.deepcopy(trans)
        self.start_state = start_state
        self.final_states = final_states.copy()

    def read_input(self, input_str):
        # NFA读取要麻烦一点，得随时保存状态
        # 检验是否有不正当字符
        for c in input_str:
            if c not in self.input_symbols:
                return "包含非法字符，请检查输入字符串"
        current_states = [self.start_state]
        for c in input_str:
            current_states = self._get_next_states(current_states, c)
        if self._have_final_states(current_states):
            return "被接受"
        else:
            return "不被接受"

    def _cal_closure(self, state):
        # 计算状态state的空闭包
        closure_list = [state]
        middle_state = deque()
        middle_state.append(state)
        while len(middle_state) > 0:
            current_state = middle_state[0]
            if current_state in self.trans.keys():
                if "e" in self.trans[current_state].keys():
                    for s in self.trans[current_state]["e"]:
                        if s not in closure_list:
                            closure_list.append(s)
                            middle_state.append(s)
            middle_state.popleft()
        return closure_list

    def _get_next_states(self, current_states, input_char):
        # 由于nfa，则输入的状态和到达的状态都不唯一
        next_states = []
        for c_state in current_states:
            if c_state in self.trans.keys():
                if input_char in self.trans[c_state].keys():
                    end_states = self.trans[c_state][input_char]
                    for s in end_states:
                        s_closure = self._cal_closure(s)
                        for s_c in s_closure:
                            if s_c not in next_states:
                                next_states.append(s_c)
        print(current_states, end="")
        print(" -> ", end="")
        print(next_states)
        return next_states

    def _have_final_states(self, current_states):
        # 判断是否含有终结状态
        for c in current_states:
            if c in self.final_states:
                return True
        return False


if __name__ == "__main__":
    # states, input_symbols, trans, start_state, final_states
    t_states = ["q1", "q2", "q3"]
    t_input = ["a", "b"]
    t_trans = {
        "q1":
        {
            "e": ["q3"],
            "b": ["q2"]
        },
        "q2":
        {
            "a": ["q2", "q3"],
            "b": ["q3"]
        },
        "q3":
        {
            "a": ["q1"],
        },
    }
    t_start = "q1"
    t_final = ["q1"]
    nfa = NFA(t_states, t_input, t_trans, t_start, t_final)
    t_input_str = "babaab"
    print(nfa.read_input(t_input_str))



