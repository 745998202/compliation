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
    if len(stack)==1:
        catchLink = stack.pop()
    else:
        print('你的后缀表达式有问题哦')
    return catchLink

def print_catch_link(node,queue):
    node.setvalue(len(queue))
    queue.append(node)
    for i in range(len(node.nextlist)):
        if node.nextlist[i] not in queue:
            print_catch_link(node.nextlist[i],queue)
def NFA_relation(queue):
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













if __name__ == '__main__':
    str = input("输入对应的正规式")
    print("你输入的正规式为: ",str)
    wordlist = getWord(str)
    print('你的转化的输入串列表为:', wordlist)
    str = reserve.reserve(str)
    print('正规式转化成为的后缀式为：',str)
    #建造NFA
    NFA = make_NFA(str,wordlist)
    #打印NFA
    queue = [] #状态队列
    print_catch_link(NFA.getfirstNode(),queue)
    NFA_relation(queue)
    #得到初始状态
    print('初始状态为：')
    state = set()#存放初始状态
    getbegin(NFA.getfirstNode(),state)
    print(state)
    #通过初始状态生成DFA（没有化简的版本）
    statelist = [state] #初始的生成DFA只有一个状态
    DFA = getDFA(queue,statelist,wordlist)#获得DFA
    print('DFA的一共有',len(statelist),'个状态')
    print('DFA状态为:',statelist)
    print('DFA转换表为',DFA)


