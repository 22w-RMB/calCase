
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
            if l == None:
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
                "diff" : [],
                "positive_diff": [],
                "negative_diff": [],
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
            if dataList[i] == None and noneToZero[i] ==1  :
                dataList[i] = [0 for i in range(0,lenght)]

        isAllList = True
        for i in range(0, len(dataList)):
            if isinstance(dataList[i], list) == False:
                isAllList = False
                break

        if isAllList:
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
                "sumList": [],
            }


        # if listA == None and A_NoneToZero:
        #     listA = [0 for i in range(0,lenght)]
        #
        # if listB == None and B_NoneToZero:
        #     listB = [0 for i in range(0,lenght)]
        #
        #
        # if isinstance(listA,list) and isinstance(listB,list):
        #
        #     sumList = [None for i in range(0,lenght)]
        #
        #     for i in range(0,lenght):
        #
        #         if listA[i] == None and A_NoneToZero:
        #             listA[i] = 0
        #
        #         if listB[i] == None and B_NoneToZero:
        #             listB[i] = 0
        #
        #         if listA[i] == None or listB[i] == None:
        #             pass
        #         else:
        #             sumList[i] = listA[i] - listB[i]
        #
        #
        #     return {
        #         "sumList" : sumList,
        #     }
        #
        # else:
        #     print("A、B中存在非列表，无法进行相加")
        #     return {
        #         "sumList" : [],
        #     }


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
        for i in range(0, lenght):
            for l in range(0,len(numeratorList)):
                if numeratorList[l] == None:
                    continue
                # 如果分子存在任意一项为空，则结果为空

                if numeratorList[l][i] == None:
                    numeratorResList[i] = None
                    continue

                numeratorResList[i] = (1 if numeratorResList[i]==None else numeratorResList[i])*numeratorList[l][i]

            for l in range(0, len(denominatorList)):
                if denominatorList[l] == None:
                    continue
                # 如果分母存在任意一项为空，则结果为空
                if denominatorList[l][i] == None:
                    denominatorResList[i] = None
                    continue

                denominatorResList[i] = (0 if denominatorResList[i] == None else denominatorResList[i]) + denominatorList[l][i]

            if numeratorResList[i] == None or denominatorResList[i]==None or denominatorResList[i]==0:
                numeratorDividedenominatorResList[i] = None
            else:
                numeratorDividedenominatorResList[i] = numeratorResList[i]/denominatorResList[i]

        numeratorSum = None
        denominatorSum = None
        divideSum = None
        for i in range(0, lenght):
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
            print(numeratorSum)
            print(denominatorSum)
            divideSum = numeratorSum/denominatorSum

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
