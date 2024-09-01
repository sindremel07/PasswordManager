# newwordList = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

#for i in range(0, 10):
#    oldwordList = []
#    print(newwordList)
#    for i in range(0, 11):
#        oldwordList.append(i)
#        newwordList[i - 1] = newwordList[i -1] + oldwordList[i]

numberList = [7, 3, 11, 1, 19, 4, 3, 17]
highestNumber = numberList[0]

for i in range(len(numberList)):
    if len(numberList) == i + 1:
        print(highestNumber)
    else:
        if highestNumber > numberList[i + 1]:
            highestNumber = numberList[i + 1]    