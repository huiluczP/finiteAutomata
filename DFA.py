"""
实现确定有穷自动机
包括功能：
输入五元组，创建DFA(c)
输入字符串进行验证(c)
DFA最小化(c)
将NFA转化为DFA(c)
DFA转RL(c)
"""
import copy
import NFA
from collections import deque
import itertools


def trans_NFA(nfa=NFA.NFA):
    # 转换NFA为DFA
    # 利用itertools的combinations方法生成表项，同时计算表头状态集合
    # 字母表直接copy
    input_symbols = list(nfa.input_symbols.copy())
    state_list = list(nfa.states)
    state_num = len(nfa.states)
    # 计算表头
    table_state_list = create_table_head(state_list)
    table_state_list.insert(0, ('blank',))  # 增加空状态集
    table_state_num = len(table_state_list)
    print(table_state_list)
    # 计算每个状态的闭包
    closures = cal_closure(state_list, nfa.trans)
    print(closures)
    # 初始化并计算table
    table = cal_table(input_symbols, table_state_num, table_state_list, nfa.trans, state_list, closures)

    # 为了转换，要先获取初始状态和终结状态，并生成转换规则
    # 初始状态为开始状态的闭包
    start_closure = sorted(cal_single_closure(nfa.start_state, nfa.trans))
    start_combine_state = tuple(start_closure)
    start_state_index = get_combine_state_index(table_state_list, start_combine_state)
    dfa_start_state = "q" + str(start_state_index)
    # 获取所有终结状态的序号
    final_state_index = get_dfa_final_state(table_state_list, nfa.final_states)
    dfa_final_state = index_into_state(final_state_index)
    # 将table转换成index表示
    index_table = trans_table(table, table_state_list)
    # 从初始状态开始把转换规则整理完
    dfa_trans, dfa_states_index = create_dfa_trans(index_table, start_state_index, input_symbols)
    dfa_states = index_into_state(dfa_states_index)
    d_final_state = []
    for f in dfa_final_state:
        if f in dfa_states:
            d_final_state.append(f)
    new_dfa = DFA(dfa_states, input_symbols, dfa_trans, dfa_start_state, d_final_state)
    return new_dfa


def index_into_state(index_list):
    # 将序号前面加上q表示状态
    state_list = index_list.copy()
    for i in range(len(state_list)):
        state_list[i] = "q" + str(state_list[i])
    return state_list


def combine_equal(combine1, combine2):
    # 判断组合状态是否相同
    if len(combine1) != len(combine2):
        return False
    for c in combine1:
        if c not in combine2:
            return False
    return True


def get_combine_state_index(combine_list, combine):
    # 工具方法，由于组合状态由tuple构成，所以需要确定index比较麻烦，要一个个元素对照
    for i in range(len(combine_list)):
        if combine_equal(combine_list[i], combine):
            return i
    return -1


def create_table_head(states):
    table_state_list = []
    # 计算表头
    state_num = len(states)
    for i in range(state_num):
        head_list = list(itertools.combinations(states, i + 1))
        table_state_list.extend(head_list)
    return table_state_list


def cal_single_closure(s, trans):
    # 计算单一状态闭包
    closure = []
    middle_state = deque()
    closure.append(s)
    middle_state.append(s)
    while len(middle_state) > 0:
        if middle_state[0] not in trans.keys():
            # 非确定可能不是所有状态都有转换规则
            middle_state.popleft()
            break
        if dict(trans[middle_state[0]]).keys().__contains__("e"):
            next_states = dict(trans[middle_state[0]])["e"]
            for next_state in next_states:
                if next_state not in closure:
                    closure.append(next_state)
                    middle_state.append(next_state)
        middle_state.popleft()
    return closure


def cal_closure(states, trans):
    # 计算常规状态闭包,包括本身与直接利用e规则到达的状态
    closures = []
    for s in states:
        closure = cal_single_closure(s, trans)
        closures.append(closure)
    return closures


def cal_table_state_closure(table_states, states, normal_closures, trans):
    # 计算table状态闭包
    closures = []
    for ss in table_states:
        closure = []
        for s in ss:
            c_l = normal_closures[list(states).index(s)]
            for c in list(c_l):
                if c not in closure:
                    closure.append(c)
        closures.append(closure)
    return closures


def cal_table(input_symbols, table_state_num, table_state_list, trans, state_list, closures):
    # table大小为表头*字母表长度,方便起见把所有项目都算上
    table = []
    for i in range(table_state_num):
        simple_list = [0] * len(input_symbols)
        # 空集合直接放入空结果
        if 'blank' in table_state_list[i]:
            for j in range(len(input_symbols)):
                simple_list[j] = ('blank', )
            table.append(simple_list)
            continue
        # 每个项目为转移规则结果的闭包的并集
        # 获得转移结果
        for j in range(len(input_symbols)):
            simple_trans_result = []
            for c in table_state_list[i]:
                if c in trans.keys():
                    if input_symbols[j] in dict(trans)[c].keys():
                        next_states = dict(trans)[c][input_symbols[j]]
                        for next_state in next_states:
                            if next_state not in simple_trans_result:
                                simple_trans_result.append(next_state)
            # 计算闭包并集
            simple_closures_list = []
            for k in simple_trans_result:
                for c in closures[state_list.index(k)]:
                    if c not in simple_closures_list:
                        simple_closures_list.append(c)

            # 直接利用顺序tuple进行对应
            simple_closures_list = sorted(simple_closures_list)
            if len(simple_closures_list) > 0:
                simple_list[j] = tuple(simple_closures_list)
            else:
                simple_list[j] = tuple(["blank"])
        table.append(simple_list)
    print_table(table, table_state_list, input_symbols)
    return table


def print_table(table, table_head, input_symbols):
    # 将表表示出来，方便观看
    print("  ".join(input_symbols))
    for i in range(len(table_head)):
        print(",".join(table_head[i]) + "   ", end="")
        print(table[i])


def trans_table(table, table_head):
    # 为了计算方便，将状态combine转换为对应的index
    index_table = copy.deepcopy(table)
    for i in range(len(index_table)):
        for k in range(len(index_table[i])):
            combine = index_table[i][k]
            c_index = get_combine_state_index(table_head, combine)
            index_table[i][k] = c_index
    return index_table


def create_dfa_trans(table, start_index, symbols_list):
    # 利用table构造dfa转换结果
    trans = {}
    states = []
    middle_state = deque()
    middle_state.append(start_index)
    while len(middle_state) > 0:  # 注意还要加上对e兜底的判断
        current_state = middle_state[0]
        states.append(current_state)
        simple_rule = {}
        for i in range(len(symbols_list)):
            # 状态名用q+index表示
            simple_rule[symbols_list[i]] = "q"+str(table[current_state][i])
            if table[current_state][i] not in states:
                middle_state.append(table[current_state][i])
        trans["q"+str(current_state)] = simple_rule
        middle_state.popleft()
    return trans, states


def get_dfa_final_state(combine_list, final_states):
    # 将combine_list中包含原终结状态的作为终结状态
    final_combines = []
    final_index = []
    for c in combine_list:
        for f in final_states:
            if f in c:
                final_combines.append(c)
                break
    for fc in final_combines:
        f_index = get_combine_state_index(combine_list, fc)
        final_index.append(f_index)
    return final_index


class DFA:
    states = []  # 所有状态
    input_symbols = []  # 字母表
    start_state = "q0"  # 初始状态，仅有一个
    final_states = []  # 终结状态
    trans = {}  # 转移函数，字典，包括启示状态，字符与终点{'q1':{'a':'q2', 'b':'q3'}}

    def __init__(self, states, input_symbols, trans, start_state, final_states):
        self.states = states.copy()
        self.input_symbols = input_symbols.copy()
        self.trans = copy.deepcopy(trans)
        self.start_state = start_state
        self.final_states = final_states.copy()

    def read_input(self, input_str):
        # 遍历输入字符串字符，进行状态转移，若最终状态为终结状态，输出接收，否则输出错误
        current_state = self.start_state
        # 确认字符可靠性
        for c in input_str:
            if c not in self.input_symbols:
                print("输入字符串包括非法字符")
                return False
        # 遍历
        for c in input_str:
            current_state = self._get_next(current_state, c)
        if current_state in self.final_states:
            print("被接受")
            return True
        else:
            print("不被接受")
            return False

    def _get_next(self, current_state, input_char):
        # current_state为当前状态，input_char为读入字符
        current_trans = self.trans[current_state]
        next_state = current_trans[input_char]
        print("{}-{}-{}".format(current_state, input_char, next_state))
        return next_state

    def minimize(self):
        # 最小化DFA
        # 先弄个新的DFA出来，免得出事
        new_dfa = DFA(self.states, self.input_symbols, self.trans, self.start_state, self.final_states)
        # 先删除不可达
        new_dfa._delete_unreachable_node()
        # 利用方法，判断每个点的相同规则的结果是否在同一组里，直到全部满足, 以此判断同类状态
        state_combine_after_divide = new_dfa._divide_states()
        # 利用现有的状态，整出转换条件
        new_trans = new_dfa._build_trans(state_combine_after_divide)
        # 更新start和end
        new_start_state = "q0"
        for i in range(len(state_combine_after_divide)):
            if new_dfa.start_state in state_combine_after_divide[i]:
                new_start_state = "q" + str(i)
                break
        new_final_state = []
        for f in new_dfa.final_states:
            for i in range(len(state_combine_after_divide)):
                if f in state_combine_after_divide[i]:
                    n_f_state = "q" + str(i)
                    if n_f_state not in new_final_state:
                        new_final_state.append(n_f_state)
        # 新状态，其实就是算下divide的数量
        new_states = []
        for i in range(len(state_combine_after_divide)):
            new_states.append("q"+str(i))
        new_dfa.start_state = new_start_state
        new_dfa.final_states = new_final_state
        new_dfa.trans = new_trans
        new_dfa.states = new_states
        return new_dfa

    def _delete_unreachable_node(self):
        # 删除不可达节点
        # 所以先求可达节点
        reachable_node = [self.start_state]
        middle_state = deque()
        middle_state.append(self.start_state)
        while len(middle_state) > 0:
            current_state = middle_state[0]
            for s in self.input_symbols:
                state = self.trans[current_state][s]
                if state not in reachable_node:
                    reachable_node.append(state)
                    middle_state.append(state)
            middle_state.popleft()
        # 删除不可达与对应转换规则
        unreachable_node = []
        for s in self.states:
            if s not in reachable_node:
                unreachable_node.append(s)
        for un in unreachable_node:
            self.states.remove(un)
            del self.trans[un]

    def _divide_states(self):
        # 划分类
        # 先初始化
        first = self.final_states.copy()
        second = []
        for s in self.states:
            if s not in first:
                second.append(s)
        divide = [first, second]
        print(divide)
        while True:
            new_divide = self._cal_divide(divide)
            print(new_divide)
            if len(new_divide) > len(divide):
                divide = new_divide
            else:
                break
        return divide

    def _cal_divide(self, divide):
        # 计算分离相关矩阵
        whole_new_divide = []
        for d in divide:
            # 把归属都放在矩阵里
            d_end = []
            for char in self.input_symbols:
                simple_d_end = []
                for s in d:
                    end = self.trans[s][char]
                    # 找到end归哪组
                    for i in range(len(divide)):
                        if end in divide[i]:
                            simple_d_end.append(i)
                            break
                d_end.append(simple_d_end)
            print(d_end)
            # 展开新divide
            new_divide = []
            symbol_num = len(self.input_symbols)
            for i in range(len(d_end[0])):
                # 先把第一个放进去,先放序号
                if len(new_divide) == 0:
                    new_divide.append([i])
                else:
                    # 遍历已有新分组，放进去，不然就整个新的
                    is_in_old = False
                    for n_d in new_divide:
                        is_this = True
                        for j in range(symbol_num):
                            if d_end[j][n_d[0]] != d_end[j][i]:
                                is_this = False
                                break
                        # 为true，分为该类
                        if is_this:
                            n_d.append(i)
                            is_in_old = True
                            break
                    # 整个新的
                    if not is_in_old:
                        new_divide.append([i])
            # 此时新divide中全是index，变为对应状态
            for n_d in new_divide:
                for n_d_d_index in range(len(n_d)):
                    n_d[n_d_d_index] = d[n_d[n_d_d_index]]
            for n_d in new_divide:
                whole_new_divide.append(n_d)
        return whole_new_divide

    def _build_trans(self, divide):
        # 利用新状态建成新转换
        trans = {}
        for i in range(len(divide)):
            # 因为等价，所以用第一个状态即可
            simple_rule = {}
            state = divide[i][0]
            for s in self.input_symbols:
                end_state = self.trans[state][s]
                after_end_state = ""
                for j in range(len(divide)):
                    if end_state in divide[j]:
                        after_end_state = "q" + str(j)
                        break
                simple_rule[s] = after_end_state
            after_state = "q" + str(i)
            trans[after_state] = simple_rule
        return trans

    def trans_to_RL(self):
        # 将DFA转为RL
        # 思路大概就是把要消去的状态有关的规则（头和尾）都处理成还在的状态
        trans = copy.deepcopy(self.trans)
        # 增加假头和假尾
        start_state = self.start_state
        trans["qs"] = {"e": start_state}
        for f_s in self.final_states:
            trans[f_s]["e"] = "qe"
        # 依次消除状态
        states = self.states.copy()
        for state in states:
            # 先把自交的归成一个
            state_trans = trans[state]  # 当前状态为头
            self_str = self._make_self_rule_into_one(state, state_trans)
            # 计算每一条到达的规则和所有离开的规则的笛卡尔积
            for k in trans.keys():
                out_list = []
                del_q = []
                for q in dict(trans[k]).keys():
                    if trans[k][q] == state:
                        del_q.append(q)
                        # 找到所有出去的规则, (起点，入符号，出符号，终点)
                        for out_q in trans[state].keys():
                            out_list.append((k, q, out_q, trans[state][out_q]))
                # 为了不破坏key，先删除，后添加
                for q in del_q:
                    del trans[k][q]
                for ol in out_list:
                    if len(self_str) > 1:
                        trans[k][ol[1] + "({})*".format(self_str) + ol[2]] = ol[3]
                    elif len(self_str) == 1:
                        trans[k][ol[1] + "{}*".format(self_str) + ol[2]] = ol[3]
            # 删除自身规则
            del trans[state]
        # 规则中qs到qe的中间状态取出，除去e字符即可
        rl = ""
        for t in trans["qs"].keys():
            rl = t
        rl = rl.replace('e', "")
        return rl

    @staticmethod
    def _make_self_rule_into_one(state, state_trans):
        self_str = ""
        self_rule_list = []
        for t in dict(state_trans).keys():
            # 自交为并
            if state_trans[t] == state:
                self_rule_list.append(t)
                del state_trans[t]
        # 数量大于1，则增加并符
        if len(self_rule_list) == 1:
            # state_trans[self_rule_list[0]] = state
            self_str = self_rule_list[0]
        elif len(self_rule_list) > 1:
            self_to_self = "∪".join(self_rule_list)
            # state_trans[self_to_self] = state
            self_str = self_to_self
        # 返回对应要放到星号中的符号串
        return self_str


if __name__ == "__main__":
    """
    t_start = "q5"
    t_final = ['q4', 'q7']
    t_states = ["q5", "q2", "q6", "q3", "q7", "q0"]
    t_symbols = ['a', 'b']
    t_trans = {'q5': {'a': 'q5', 'b': 'q2'}, 'q2': {'a': 'q6', 'b': 'q3'}, 'q6': {'a': 'q7', 'b': 'q3'}, 'q3': {'a': 'q5', 'b': 'q0'}, 'q7': {'a': 'q7', 'b': 'q6'}, 'q0': {'a': 'q0', 'b': 'q0'}}
-
    t_dfa = DFA(t_states, t_symbols, t_trans, t_start, t_final)
    input_s = "baaabab"
    t_dfa.read_input(input_s)
    """

    """
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
    t_dfa = DFA(t_states, t_symbols, t_trans, t_start, t_final)
    min_dfa = t_dfa.minimize()
    print(min_dfa.start_state)
    print(min_dfa.final_states)
    print(min_dfa.states)
    print(min_dfa.trans)
    """
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
    t_dfa = DFA(t_states, t_symbols, t_trans, t_start, t_final)
    t_rl = t_dfa.trans_to_RL()
    print(t_rl)

