
class CommonCal:
    @staticmethod
    def filterNone( dataList):
        '''
        对数据判空处理
        :param dataList:
        :return:
        '''

        resultList = []
        def processList(l):
            if l == None or l == []:
                return

            if isinstance(l, int) or isinstance(l, float):
                resultList.append(l)

            if isinstance(l, list):
                for data in l:
                    processList(data)

        processList(dataList)
        return resultList



    @staticmethod
    def getSum( dataList):
        '''
        求和
        :param dataList:
        :return:
        '''

        filterNoneRes = CommonCal.filterNone(dataList)

        sumRes = None

        if len(filterNoneRes) >0:
            sumRes = sum(sumRes)

        return sumRes

    @staticmethod
    def conductSubtract( listA , listB , A_NoneToZero=False, B_NoneToZero=False,lenght=96 ):
        '''
        lsitA - listB
        :param listA:
        :param listB:
        :param A_Zero:  A 为空时是否当0处理
        :param B_Zero:  B 为空时是否当0处理
        :param lenght:
        :return:
        '''
        if listA == None and A_NoneToZero:
            listA = [0 for i in range(0,lenght)]

        if listB == None and B_NoneToZero:
            listB = [0 for i in range(0,lenght)]


        if isinstance(listA,list) and isinstance(listB,list):
            # 偏差
            diff = [None for i in range(0,lenght)]
            # 正偏差
            positive_diff = [None for i in range(0,lenght)]
            # 负偏差
            negative_diff = [None for i in range(0,lenght)]

            for i in range(0,lenght):

                if listA[i] == None and A_NoneToZero:
                    listA[i] = 0

                if listB[i] == None and B_NoneToZero:
                    listB[i] = 0

                if listA[i] == None or listB[i] == None:
                    pass
                else:
                    diff[i] = listA[i] - listB[i]
                    if diff[i] > 0:
                        positive_diff[i] = diff[i]
                    elif diff[i] < 0:
                        negative_diff[i] = diff[i]

            return {
                "diff" : diff,
                "positive_diff": positive_diff,
                "negative_diff": negative_diff,
            }

        else:

            print("A、B中存在非列表，无法进行相减")
            return {
                "diff" : [None for i in range(0,lenght)],
                "positive_diff": [None for i in range(0,lenght)],
                "negative_diff": [None for i in range(0,lenght)],
            }

    @staticmethod
    def conductAdd(dataList,noneToZero=[],lenght=96 ):
        '''
        lsitA + listB
        :param listA:
        :param listB:
        :param A_Zero:  A 为空时是否当0处理
        :param B_Zero:  B 为空时是否当0处理
        :param lenght:
        :return:
        '''


        if noneToZero == []:
            noneToZero = [1 for i in range(0,len(dataList))]


        for i in range(0,len(noneToZero)):
            if dataList[i] == None and noneToZero[i] == 1  :
                dataList[i] = [None for i in range(0,lenght)]

        # 是否全部都是列表
        isAllList = True
        # 判断所有列表所有值是否都为None
        isAllNone = True
        for i in range(0, len(dataList)):
            if isinstance(dataList[i], list) == False:
                isAllList = False
            else:
                for j in dataList[i]:
                    if j != None:
                        isAllNone = False
                        break

        # 只有都是列表 且 且其中存在数据时
        if isAllList == True and isAllNone == False:
            sumList = [None for i in range(0, lenght)]

            for i in range(0, lenght):
                for j in range(0, len(dataList)):


                    if dataList[j][i] == None and noneToZero[j] == 1:
                        dataList[j][i] = 0

                    if dataList[j][i] == None:
                        pass
                    else:
                        sumList[i] = (0 if sumList[i]==None else sumList[i]) + dataList[j][i]


            return {
                "sumList": sumList,
            }
        else:

            print("A、B中存在非列表，无法进行相加")
            return {
                "sumList": [None for i in range(0,lenght)],
            }



    @staticmethod
    def getAverage(dataList):
        '''
        求和
        :param dataList:
        :return:
        '''

        filterNoneRes = CommonCal.filterNone(dataList)

        sumRes = None
        averageRes = None

        if len(filterNoneRes) > 0:
            averageRes = sum(sumRes)/len(sumRes)

        return averageRes



    @staticmethod
    def spitWeightedMeanData(numeratorList, denominatorList, lenght=96):

        numDicTemp = {}
        for num in numeratorList:
            for i in range(0,len(num)):
                if i not in numDicTemp.keys():
                    numDicTemp[i] = []
                numDicTemp[i].append(num[i])

        denDicTemp = {}
        for num in denominatorList:
            for i in range(0,len(num)):
                if i not in denDicTemp.keys():
                    denDicTemp[i] = []
                denDicTemp[i].append(num[i])

        numeratorResLists = []
        denominatorResLists = []
        for key in numDicTemp:
            tempRes = CommonCal.weightedMean(numDicTemp[key],denDicTemp[key],lenght)
            numeratorResLists.append(tempRes["numeratorList"])
            denominatorResLists.append(tempRes["denominatorList"])


        numerator = CommonCal.conductAdd(numeratorResLists,lenght=lenght)["sumList"]
        denominator = CommonCal.conductAdd(denominatorResLists,lenght=lenght)["sumList"]


        res = CommonCal.weightedMean([numerator], [denominator], lenght=lenght)


        return res





    @staticmethod
    def weightedMean( numeratorList ,denominatorList,lenght=96):
        '''
        加权平均
        :param numerator:  分子
        :param denominator: 分母
        :param lenght: 数组长度
        :return:
        '''


        numeratorResList = [None for i in range(0,lenght)]
        denominatorResList = [None for i in range(0,lenght)]
        numeratorDividedenominatorResList = [None for i in range(0,lenght)]
        numeratorSum = None
        denominatorSum = None
        divideSum = None

        isMul = [True for i in range(0,lenght)]
        # 判断分子或分母列表中是否存在None或[]
        isNumOrDenListExistNone = False
        for l in range(0, len(numeratorList)):
            # 如果分子存在任意一项为空，则结果为空
            if numeratorList[l] == None or numeratorList[l]==[]:
                isNumOrDenListExistNone = True
                break
            for i in range(0,lenght):
                if isMul[i] == False:
                    continue
                # 如果分子存在任意一项为空，则结果为空
                if numeratorList[l][i] == None :
                    isMul[i] = False
                    continue
                numeratorResList[i] = (1 if numeratorResList[i]==None else numeratorResList[i])*numeratorList[l][i]

        for l in range(0, len(denominatorList)):
            # 如果分子存在任意一项为空，则结果为空
            if denominatorList[l] == None or denominatorList[l]==[]:
                isNumOrDenListExistNone = True
                break
            for i in range(0,lenght):
                if isMul[i] == False:
                    continue
                # 如果分子存在任意一项为空，则结果为空
                if denominatorList[l][i] == None :
                    continue
                denominatorResList[i] = (0 if denominatorResList[i] == None else denominatorResList[i]) + denominatorList[l][i]



        for i in range(0, lenght):
            if numeratorResList[i] == None or denominatorResList[i]==None or denominatorResList[i]==0:
                numeratorDividedenominatorResList[i] = None
            else:
                numeratorDividedenominatorResList[i] = numeratorResList[i]/denominatorResList[i]

            if numeratorResList[i] != None:
                if numeratorSum == None:
                    numeratorSum = numeratorResList[i]
                else:
                    numeratorSum += numeratorResList[i]

            if denominatorResList[i] != None:
                if denominatorSum == None:
                    denominatorSum = denominatorResList[i]
                else:
                    denominatorSum += denominatorResList[i]

        if denominatorSum == None  or denominatorSum == 0  or numeratorSum==None:
            pass
        else:

            divideSum = numeratorSum/denominatorSum

        if isNumOrDenListExistNone:
            return {
                "numeratorList": [None for i in range(0,lenght)],
                "denominatorList": [None for i in range(0,lenght)],
                "divideList": [None for i in range(0,lenght)],
                "numeratorSum": None,
                "denominatorSum": None,
                "divideSum": None,
            }
        else:
            return {
                "numeratorList": numeratorResList,
                "denominatorList": denominatorResList,
                "divideList": numeratorDividedenominatorResList,
                "numeratorSum": numeratorSum,
                "denominatorSum": denominatorSum,
                "divideSum": divideSum,
            }

    @staticmethod
    def filterNeedKeyFromDbData(dataList,keys):

        keysList = []
        if isinstance(keys,list):
            keysList.extend(keys)
        else:
            keysList.append(keys)

        keyDict = {}

        for key in keys:
            keyDict[key] = []

        for data in dataList:
            for key in keyDict:
                if key in data.keys():
                    keyDict[key].append( data[key] )
                else:
                    print("数据库返回的不存在该",key,"字段")

            pass

        return keyDict
