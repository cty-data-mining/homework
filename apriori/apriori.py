import sys

from itertools import chain, combinations
from collections import defaultdict
from optparse import OptionParser

def subsets(arr):
    return chain(*[combinations(arr, i + 1) for i, a in enumerate(arr)])

def returnItemsWithMinSupport(itemSet, transactionList, minSupport, freqSet):
        _itemSet = set()
        localSet = defaultdict(int)

        for item in itemSet:
                for transaction in transactionList:
                        if item.issubset(transaction):
                                freqSet[item] += 1
                                localSet[item] += 1

        for item, count in list(localSet.items()):
                support = float(count)/len(transactionList)

                if support >= minSupport:
                        _itemSet.add(item)

        return _itemSet


def joinSet(itemSet, length):
        return set([i.union(j) for i in itemSet for j in itemSet if len(i.union(j)) == length])

def getItemSetTransactionList(data_iterator):
    transactionList = list()
    itemSet = set()
    for record in data_iterator:
        transaction = frozenset(record)
        transactionList.append(transaction)
        for item in transaction:
            itemSet.add(frozenset([item]))
    return itemSet, transactionList

def runApriori(data_iter, minSupport, minConfidence):
    itemSet, transactionList = getItemSetTransactionList(data_iter)

    freqSet = defaultdict(int)
    largeSet = dict()

    assocRules = dict()

    oneCSet = returnItemsWithMinSupport(itemSet,
                                        transactionList,
                                        minSupport,
                                        freqSet)

    currentLSet = oneCSet
    k = 2
    while(currentLSet != set([])):
        largeSet[k-1] = currentLSet
        currentLSet = joinSet(currentLSet, k)
        currentCSet = returnItemsWithMinSupport(currentLSet,
                                                transactionList,
                                                minSupport,
                                                freqSet)
        currentLSet = currentCSet
        k = k + 1

    def getSupport(item):
            return float(freqSet[item])/len(transactionList)
    toRetItems = []
    for key, value in list(largeSet.items()):
        toRetItems.extend([(tuple(item), getSupport(item))
                           for item in value])

    toRetRules = []
    for key, value in list(largeSet.items())[1:]:
        for item in value:
            _subsets = map(frozenset, [x for x in subsets(item)])
            for element in _subsets:
                remain = item.difference(element)
                if len(remain) > 0:
                    confidence = getSupport(item)/getSupport(element)
                    if confidence >= minConfidence:
                        toRetRules.append(((tuple(element), tuple(remain)),
                                           confidence))
    return toRetItems, toRetRules


def printResults(items, rules):
    for item, support in sorted(items):
        print ("item: %s , %.3f" % (str(item), support))
    print ("\n------------------------ RULES:")
    for rule, confidence in sorted(rules):
        pre, post = rule
        print( "Rule: %s ==> %s , %.3f" % (str(pre), str(post), confidence))


def dataFromFile(fname,extra = False):
    if not extra:
        file_iter = open(fname, encoding = 'utf-8')
        for line in file_iter:
            line = line.strip().rstrip(',')
            record = frozenset(line.split(','))
            yield record
    else:
        for n in range(len(fname)):
            record = frozenset(fname.ix[n,:])
            yield record

if __name__ == "__main__":
    inFile = dataFromFile('iris.csv',extra = False)
    minSupport = 0.15
    minConfidence = 0.6
    items, rules = runApriori(inFile, minSupport, minConfidence)

    print('--------items number is: %s , rules number is : %s--------'%(len(items),len(rules)))

    printResults(items, rules)
