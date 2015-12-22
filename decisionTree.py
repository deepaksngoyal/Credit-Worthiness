import sys
import math
import copy

class DecisionTree:
    def __init__(self):
        self.data = [[], []]
        self.test = [[], []]
        self.entropyX = 0.0
        self.attrVals = [[] for x in range(16)]
        self.attrs = ['A1','A2','A3','A4','A5','A6','A7','A8','A9','A10','A11','A12','A13','A14','A15','A16']

    # read the data from the input file
    def read_data(self, file):
        rawState = [line.rstrip('\n').split(',') for line in open(file)]
        validationSize = int(2/float(3)*len(rawState))
        self.data= rawState[0: validationSize]
        self.test = rawState[validationSize:]


    def calc_entropy(self, x, y):
        if x <=0 or y <=0:
            return 1
        sum = x + y
        if sum > 0:
            return (-1*(x/float(sum))*math.log(x/float(sum),2) -1*(y/float(sum))*math.log(y/float(sum),2))
        else:
            return 0

    def calcContinuousAttrInfoGain(self, attrVals, data):
        tp = 0
        tn = 0
        p = 0
        n = 0
        for sample in data:
            if sample[len(sample)-1] == '+':
                tp += 1
            elif sample[len(sample)-1] == '-':
                tn += 1
        entropyX = self.calc_entropy(tp,tn)
        maxGain  = - float('inf')
        index = 0
        attrSet = []
        for val in attrVals:
            if val not in attrSet:
                attrSet.append(val)

        for i in range(len(attrSet)):
            for sample in data:
                if attrSet[i] in sample and sample[len(sample)-1] == '+':
                    p += 1
                elif attrSet[i] in sample and sample[len(sample)-1] == '-':
                    n += 1
            x = (p+n)/len(data)*self.calc_entropy(p, n)

            y = ((tp-p)+(tn-n))/len(data) * self.calc_entropy(tp - p, tn - n)
            ig = entropyX -x - y
            if ig > maxGain:
                maxGain = ig
                value = attrSet[i]

        return (maxGain, value)

    def findNodeAttr(self, entropyX, attrValsList, data):
        maxGain = -float('inf')
        attrIndex = 0
        contSelected = False
        contIndex = 0

        for i  in range(len(attrValsList)-1):
            ig = entropyX
            if len(attrValsList[i]) > 15:
                (gain, v) = self.calcContinuousAttrInfoGain(attrValsList[i], data)
                if gain > maxGain:
                    maxGain = gain
                    attrIndex = i
                    contSelected = True
                    value = v

            else:
                for val in attrValsList[i]:
                    if val == '?':
                        continue
                    p = 0
                    n = 0
                    total = len(data)

                    for sample in data:
                        if sample[i] == '?': # avoid unknown vars
                            continue
                        if val == sample[i] and sample[len(sample)- 1] == '+':
                            p += 1
                        elif val == sample[i] and sample[len(sample)- 1] == '-':
                            n += 1
                    ig -= self.calc_entropy(p,n)*(p+n)/float(total)
                if ig > maxGain:
                        maxGain = ig
                        attrIndex = i
                        value = val
                        contSelected = False

        return (attrIndex, contSelected,  value)

    def createNode(self, attrValue, attrs, attrVals, data):
        p = 0
        n = 0

        for sample in data:
            if sample[len(sample)-1] == '+':
                p += 1
            else:
                n += 1

        entropyX = self.calc_entropy(p,n)

        if(entropyX == 1):
            if p == 0:
                node = Node(0, [attrValue],'-')
            else:
                node = Node(0,[attrValue],'+')
            return node
        else :
            (attrIndex, contSelected,  value) = self.findNodeAttr(entropyX, attrVals, data)
            node  = Node(attrIndex, attrs, copy.copy(data))
            newAttrVals = copy.copy(attrVals)
            newAttrVals.pop(attrIndex)
            for val in attrVals[attrIndex]:
                new_attrs = copy.copy(attrs)
                new_attrs.pop(attrIndex)
                nodeData = []
                for i in range(len(data)):
                    if val in data[i]:
                        row = copy.copy(data[i])
                        row.remove(val)
                        nodeData.append(row)
                if len(nodeData) > 0:
                    node.addChild(val, self.createNode(val, new_attrs, newAttrVals, nodeData))

            return node

    def createTree(self,attrLen):
        attrVals = [[] for x in range(attrLen)]

        for sample in self.data:
            for i in range(len(sample)):
                if i in [1,2,7,10,13,14] and sample[i] !='?' and sample[i] not in attrVals[i]:
                    attrVals[i].append(float(sample[i]))
                elif sample[i] !='?' and sample[i] not in attrVals[i]:
                    attrVals[i].append(sample[i])
        self.root = self.createNode('', self.attrs, attrVals, self.data)

    def testData(self):
        p = 0
        total = len(self.test)
        for sample in self.test:
            val = self.testSample(sample, self.root)
            if(val == sample[len(sample)-1]):
                p+=1
        return p*100/float(total)

    def  testSample(self,sample, node):
            if node.data == '+' or node.data == '-':
                return node.data
            attr = node.getAttr()
            index = node.getAttrList().index(attr)
            if index < len(sample) -1:
                map = node.getNode()
                if sample[index] not in map:
                    return '-'
                else:
                    childNode = map[sample[index]]
                    return self.testSample(sample, childNode)


class Node(object):
    def __init__(self, attrIndex, attrs, data):
        self.attrIndex = attrIndex
        self.attrList = attrs
        self.data = data
        self.node  = dict()

    def setAttr(self,attr):
        self.attr = attr

    def getAttrList(self):
        return self.attrList

    def getAttr(self):
        if len(self.attrList) > 0:
            return self.attrList[self.attrIndex]
        else :
            return ' '

    def getData(self):
        return self.data

    def addChild(self, attrVal, child):
        self.node[attrVal] = child

    def getNode(self):
        return self.node


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Layout or output file not specified.'
        exit(-1)
    dTree = DecisionTree()
    print "Reading Data..."
    dTree.read_data(sys.argv[1])
    print "Applying Decision Tree Classification..."
    dTree.createTree(16)
    print "Classification done."
    print "Root index = " + str(dTree.root.getAttr())
    print "Testing on validation data."
    accuracy = dTree.testData()
    print "Accuracy = " + str(accuracy)

