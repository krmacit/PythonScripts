class Stack:
    def __init__(self):
        self.items = []
        self.length = 0

    def push(self, val):
        self.items.append(val)
        self.length += 1

    def pop(self):
        if self.isEmpty():
            return None
        self.length -= 1
        return self.items.pop()

    def size(self):
        return self.length

    def peek(self):
        if self.isEmpty():
            return None
        return self.items[0]

    def isEmpty(self):
        return self.length == 0

    def __str__(self):
        return str(self.items)


class Assembly:
    def __init__(self):
        self.lines = []
        self.operations = {
            "(": 1,
            "&": 2,
            "|": 3,
            "?": 4,
            ")": 5
        }
        self.variables = []
        self.assemblyCode = []
        self.questionOperationCount = 0
        self.assemblyCode.append("code segment")

    def addLine(self, line):
        if "=" in line:
            list = line.split(" = ")
            variable = list[0]
            if not variable in self.variables:
                self.variables.append(variable)
            postfixList = self.toPostfix(list[1])
            self.toAssembly(variable, postfixList)
        else:
            self.printOperation(line)

    def toPostfix(self, infix):
        opStack = Stack()
        postfixList = []
        tokenList = infix.split()
        for token in tokenList:
            if not token in self.operations:
                postfixList.append(token)
            elif token == "(":
                opStack.push(token)
            elif token == ")":
                topToken = opStack.pop()
                while topToken != '(':
                    postfixList.append(topToken)
                    topToken = opStack.pop()
            else:
                while (not opStack.isEmpty()) and (self.operations[opStack.peek()] >= self.operations[token]):
                    postfixList.append(opStack.pop())
                opStack.push(token)
        while not opStack.isEmpty():
            postfixList.append(opStack.pop())
        return postfixList

    def toAssembly(self, LHS, RHS):
        self.assemblyCode.append("\tpush offset {}".format(LHS))
        for token in RHS:
            if token in self.operations:
                if token == "&":
                    self.andOperation()
                elif token == "|":
                    self.orOperation()
                else:
                    self.questionOperation()
            else:
                self.assemblyCode.append("\tpush {}".format(token))
        self.assingmentOperation()

    def andOperation(self):
        self.assemblyCode.append("\tpop ax")
        self.assemblyCode.append("\tpop bx")
        self.assemblyCode.append("\tand ax, bx")
        self.assemblyCode.append("\tpush ax")

    def orOperation(self):
        self.assemblyCode.append("\tpop ax")
        self.assemblyCode.append("\tpop bx")
        self.assemblyCode.append("\tor ax, bx")
        self.assemblyCode.append("\tpush ax")

    def questionOperation(self):
        self.questionOperationCount += 1
        self.assemblyCode.append("\tpop ax")
        self.assemblyCode.append("\tpop bx")
        self.assemblyCode.append("\tcmp ax, 0")
        self.assemblyCode.append("\tjl zeroloop{}".format(self.questionOperationCount))
        self.assemblyCode.append("\tpush bx")
        self.assemblyCode.append("\tj endloop{}".format(self.questionOperationCount))
        self.assemblyCode.append("zeroloop{}:".format(self.questionOperationCount))
        self.assemblyCode.append("\tpush 0")
        self.assemblyCode.append("endloop{}:".format(self.questionOperationCount))

    def assingmentOperation(self):
        self.assemblyCode.append("\tpop ax")
        self.assemblyCode.append("\tpop bx")
        self.assemblyCode.append("\tmov [bx], ax")

    def printOperation(self, printValue):
        self.assemblyCode.append("\tmov dx, {}".format(printValue))
        self.assemblyCode.append("\tmov ah, 09h")
        self.assemblyCode.append("\tint 21h")

    def finishingAssembly(self):
        self.assemblyCode.append("\tint 20h")
        for var in self.variables:
            self.assemblyCode.append("va {} 0".format(var))
        self.assemblyCode.append("code ends")


file = "example.bit"
assembly = Assembly()
with open(file, "r") as fd:
    for line in fd:
        line = line.replace("\r", "").replace("\n", "")
        assembly.addLine(line)
    assembly.finishingAssembly()
print("\n".join(assembly.assemblyCode))

with open("swe.asm","w") as txt_file:
    for line in assembly.assemblyCode:
        txt_file.write("".join(line) + "\n")