
word = 'abcdefghijklmnopqrstuvwxyz'
def push_some_add(str):             #正规式重写
    addstr = str
    before_add = 0 #已经插入的+号数量，用于切割字符串时进行后移
    str_len = len(str)
    for i in range(str_len):
        if str[i] in word:
            if i <= (str_len-1):
                if str[i+1] in word:
                    addstr = addstr[:i+before_add+1]+'+'+addstr[i+before_add+1:]
                    before_add = before_add + 1
    return addstr

def reserve(str):                   #正则式转后缀式
    str = push_some_add(str)
    print('将连接规则添加进正规式，重写之后为：',str)
    result = []   #结果集
    stack = []    #栈
    for i in str: #遍历每一个字符
        if i in word:         #如果是字母，直接导入结果集中
            result.append(i)
        else:                   #如果为其他操作符
            if len(stack) == 0 and i not in '()*': #如果当前栈为空，直接压入栈
                stack.append(i)
            elif i in '(':         #当是括号的时候直接忽略
                continue
            elif i in ')':
                while len(stack)!=0:
                    catch_pop_char = stack.pop()
                    result.append(catch_pop_char)
            elif i in '*':
                result.append(i)
            elif i in '+|':        #当时其他符号的时候
                while len(stack)!=0:
                    catch_pop_char = stack.pop()
                    result.append(catch_pop_char)
                stack.append(i)
    while len(stack)!=0:
        catch_pop_char = stack.pop()
        result.append(catch_pop_char)
    result_str = ''
    for i in result:
        result_str = result_str + i
    return result_str

if __name__ == '__main__':
    #正规式重写测试
    str = '(ab)*(a|b)*(abc)'
    # str = push_some_add(str)
    # print(str)
    str = reserve(str)   #正则式转后缀式

    print(str)
