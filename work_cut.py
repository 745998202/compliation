import xlrd
import xlwt
import reserve

# 1. 输入正规式
# 2. 将正规式进行重写，将连接规则写入
# 3. 将重写之后的正规式转化为后缀表达式
# 4. 将转化之后的后缀表达式逐个读取生成对应的NFA
# 5. 根据NFA转化为DFA
# 6. 将DFA最小化

word = '+|*()'

def getWord(yourstr):   #获得该正则式的所有输入字符串（用于生成状态转换矩阵）
    wordlist = set()      #创建一个集合用于存放输入字符集
    for i in yourstr:
        if i not in word:
            wordlist.add(i)
    return wordlist

class Node:                             #节点类
    def __init__(self):
        self.nextlist = []          #指向下一个节点的指针
        self.tranlist = []         #转换条件
        self.value = -1
        self.isend = False
    def setnext(self,nextnode,translate):
        self.nextlist.append(nextnode)
        self.tranlist.append(translate)
    def setvalue(self,value):
        self.value = value
    def set_is_end(self):  #设置是终态
        self.isend = True
#节点包含指向下一个节点的列表和转换条件列表


class Link:                             #Link类
    def __init__(self,value='_'):
        self.last = Node()
        self.first = Node()
        if value != '_':
            self.first.setnext(self.last,value)
    def getfirstNode(self):
        return self.first
    def getlastNode(self):
        return self.last
    def add_two_Node(self,node1,node2):
        self.first.setnext(node1.getfirstNode(),'_')
        node1.getlastNode().setnext(node2.getfirstNode(),'_')
        node2.getlastNode().setnext(self.last,'_')
    def or_two_Node(self,node1,node2):
        self.first.setnext(node1.getfirstNode(),'_')
        self.first.setnext(node2.getfirstNode(),'_')
        node1.getlastNode().setnext(self.last,'_')
        node2.getlastNode().setnext(self.last,'_')
    def turn_around_self(self,node):
        self.first.setnext(node.getfirstNode(), '_')
        self.first.setnext(self.last,'_')
        node.getlastNode().setnext(node.getfirstNode(),'_')
        node.getlastNode().setnext(self.last,'_')



#Link类由一组节点构成，只保存Link的头指针和尾指针节点


def make_NFA(str,transword):
    stack = []  #Link栈
    for i in str:
        if i in transword:#如果是转换式如a\b\c等,入栈
            newLink = Link(i)  # make a Link and push back in stack
            stack.append(newLink)
        elif i == '*':                  # if trans == '*' it is a one calculate
            newLink = Link('_')
            catchLink = stack.pop()
            newLink.turn_around_self(catchLink)
            stack.append(newLink)
        elif i == '+':                 # if trans in '+|' it is two calculat
            newLink = Link('_')
            node2 = stack.pop()
            node1 = stack.pop()
            newLink.add_two_Node(node1,node2)
            stack.append(newLink)
        elif i == '|':
            newLink = Link('_')
            node2 = stack.pop()
            node1 = stack.pop()
            newLink.or_two_Node(node1,node2)
            stack.append(newLink)
    catchLink = 0
    if len(stack)!=0:
        catchLink = stack.pop()
        beforeNode = catchLink.getlastNode()
        behindNode = 0
        help_catch_link = 0
        while len(stack)!=0:
            help_catch_link = stack.pop()
            behindNode = help_catch_link.getfirstNode()
            beforeNode.setnext(behindNode,'_')
            beforeNode = behindNode

    return catchLink

def print_catch_link(node,queue):
    node.setvalue(len(queue))
    queue.append(node)
    for i in range(len(node.nextlist)):
        if node.nextlist[i] not in queue:
            print_catch_link(node.nextlist[i],queue)
def set_isend_inNFA(queue):
    for state in queue:
        if len(state.nextlist) == 0:
            state.set_is_end()
def NFA_relation(queue):  #打印NFA
    for node in queue:
        print('node:',node.value)
        for i in range(len(node.nextlist)):
            print(node.tranlist[i], '->', node.nextlist[i].value)
def getbegin(node,state):
    state.add(node.value)
    for i in range(len(node.nextlist)):
        if node.tranlist[i] == '_': # 如果目标转换路径为空
            if node.nextlist[i].value not in state:#而且这个状态没有加入此初始状态
                state.add(node.nextlist[i].value)
                getbegin(node.nextlist[i],state)
def getmid(node,tran,state):#输入转化字符，获得后续可能的状态列表
    for i in range(len(node.nextlist)):
        if node.tranlist[i] == tran:  #可以接收这个转化字符
            if node.nextlist[i].value not in state:#如果这个字符代表的状态没有被收入到状态中
                state.add(node.nextlist[i].value)
                getmid(node.nextlist[i],'_',state)
def getDFA(queue,statelist,wordlist): #传入状态与NFA状态集合，求DFA状态集合
    DFA = []
    for one_state in statelist:     #遍历状态
        one_dfa_state = {}
        for word in wordlist:       #对于每一个输入字符
            state = set()
            for number in one_state:#每一个状态接收每一个输入字符
                getmid(queue[number],word,state)
            if state not in statelist:#如果这个状态是新的状态
                statelist.append(state)
            one_dfa_state[word] = statelist.index(state)
        DFA.append(one_dfa_state)
    return DFA
def help_to_make_DFA_small(one_style_state,alltrans,words):#协助DFA最小化
    #传入一个状态数组，此时这个状态数组对应的状态已经是分好组的状态了
    #需要完成的任务是将相同的状态合并
    #遍历状态数组，从第一个开始到最后一个，如果第一个状态的转换状态与之后某个状态的转换状态相同
    #将这个状态加入到第一个状态数组中，并删除掉这个状态
    i = 0
    j = 0
    while i < len(one_style_state):
        j = i+1
        while j < len(one_style_state):
            the_same = True
            for word in words:
                if alltrans[one_style_state[i][0]] != alltrans[one_style_state[j][0]]:
                    the_same = False
            if the_same:
                one_style_state[i] = one_style_state[i] + one_style_state[j]
                del one_style_state[j]
            else:
                j = j+1
        i = i+1
    return one_style_state

def make_DFA_small(statelist,queue,alltrans,words):#DFA最小化
    not_end_states = [] #非终止状态暂存列表
    end_states = []      #终止状态暂存列表
    end_state_number = 0 #终止状态标号
    allstate = range(len(statelist))
    for i in range(len(queue)):#寻找终止状态
        if queue[i].isend:
            end_state_number = i
    for i in allstate:
        if end_state_number in statelist[i]:#如果当前状态含有终结状态的话，定义为DFA终结状态
            help_add_to_end = [i]
            end_states.append(help_add_to_end)
        else:
            help_add_to_end = [i]
            not_end_states.append(help_add_to_end)
    end_states = help_to_make_DFA_small(end_states,alltrans,words)
    not_end_states = help_to_make_DFA_small(not_end_states,alltrans,words)
    print('DFA的终结状态有：',end_states)
    print('DFA的非终结状态有:',not_end_states)

    states = not_end_states + end_states
    print('联合之后', states)
    for i in states:
        if len(i) > 1:             #需要剔除某几个状态
            keep_small_state = i[0] # 被替换成的目标状态
            help_states = i[:]
            help_states.remove(keep_small_state)
            for j in help_states:               #对于每个需要被剔除的状态
                for num in range(len(alltrans)):#遍历其他所有状态
                    for word in wordlist:       #遍历其他所有转换目标
                        if alltrans[num][word] == j:#如果是这个将要被剔除的状态
                            alltrans[num][word] = keep_small_state
    mark_old_state_list = []
    new_state_tran_list = []
    new_state_list = []
    saved_state = []#存储所有应当保留的状态编号
    for i in states:  #[states = [[0,1],[2,3]]]
        saved_state.append(i[0])
    print('化简之后的状态为',saved_state)
    for i in statelist:                     #对于每个状态来说
        if statelist.index(i) in saved_state:#如果是应当保存的编号
            new_state_list.append(i)
            new_state_tran_list.append(alltrans[statelist.index(i)])
            mark_old_state_list.append(statelist.index(i))
    print('新的状态列表',new_state_list)
    print('新的转化列表',new_state_tran_list)
    print('新的标记数组',mark_old_state_list)
    for new_tran in new_state_tran_list:
        for word in wordlist:
            new_tran[word] = mark_old_state_list.index(new_tran[word])

    print('#==============================#')
    print('DFA转换矩阵为：')
    for i in range(len(new_state_tran_list)):
        if end_state_number in statelist[statelist.index(new_state_list[i])]:
            print(i,new_state_tran_list[i],'<------终态')
        else:
            print(i,new_state_tran_list[i])













if __name__ == '__main__':
    str = input("输入对应的正规式")
    print("你输入的正规式为: ",str)

    #==========获取可能的输入串==========#
    wordlist = getWord(str)
    print('你的转化的输入串列表为:', wordlist)
    #==========将正则式变为后缀式========#
    str = reserve.reserve(str)
    print('正规式转化成为的后缀式为：',str)
    #==========建造NFA===================#
    NFA = make_NFA(str,wordlist)
    #==========打印NFA===================#
    queue = [] #NFA状态队列
    print_catch_link(NFA.getfirstNode(),queue)
    NFA_relation(queue)
    set_isend_inNFA(queue)
    #=========得到DFA初始状态============#
    print('DFA初始状态为：')
    state = set()#存放初始状态
    getbegin(NFA.getfirstNode(),state)
    print(state)
    #通过初始状态生成DFA（没有化简的版本）#
    statelist = [state] #初始的生成DFA只有一个状态
    DFA = getDFA(queue,statelist,wordlist)#获得DFA
    print('DFA的一共有',len(statelist),'个状态')
    print('分别为:',statelist)
    print('DFA转换表为',DFA)
    #============DFA最小化=====================#
    make_DFA_small(statelist,queue,DFA,wordlist)

