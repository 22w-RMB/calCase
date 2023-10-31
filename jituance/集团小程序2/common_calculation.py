
class CommonCal:

    @staticmethod
    def transformYi( dataList):

        for key in dataList:
            if dataList[key] == None:
                continue

            if "price" in key:
                continue
            if isinstance(dataList[key], list):
                tempList = []
                for d in dataList[key]:
                    if d == None:
                        tempList.append(None)
                    else:
                        if "ele" in key:
                            tempList.append(round(d / 100000,2))
                        elif ("fee" in key) or ("income" in key):
                            tempList.append(round(d / 100000000,2)   )

                dataList[key] = tempList
                continue

            if "ele" in key:
                dataList[key] = round(dataList[key] / 100000,2)
            elif ("fee" in key) or ("income" in key):
                dataList[key] = round(dataList[key] / 100000000,2)



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
            sumRes = sum(filterNoneRes)

        return sumRes

    @staticmethod
    def conductSubtract( listA , listB , A_NoneToZero=False, B_NoneToZero=False,length=96 ):
        '''
        lsitA - listB
        :param listA:
        :param listB:
        :param A_Zero:  A 为空时是否当0处理
        :param B_Zero:  B 为空时是否当0处理
        :param length:
        :return:
        '''
        if listA == None and A_NoneToZero:
            listA = [0 for i in range(0,length)]

        if listB == None and B_NoneToZero:
            listB = [0 for i in range(0,length)]


        if isinstance(listA,list) and isinstance(listB,list):
            # 偏差
            diff = [None for i in range(0,length)]
            # 正偏差
            positive_diff = [None for i in range(0,length)]
            # 负偏差
            negative_diff = [None for i in range(0,length)]

            for i in range(0,length):

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
                "diff" : [None for i in range(0,length)],
                "positive_diff": [None for i in range(0,length)],
                "negative_diff": [None for i in range(0,length)],
            }

    @staticmethod
    def conductDivide( listA , listB , A_NoneToZero=False, B_NoneToZero=False,length=96 ):
        '''
        lsitA - listB
        :param listA:
        :param listB:
        :param A_Zero:  A 为空时是否当0处理
        :param B_Zero:  B 为空时是否当0处理
        :param length:
        :return:
        '''
        divideList = [None for i in range(0, length)]
        numeratorSum = None
        denominatorSum = None
        divideSum = None


        for i in range(0, length):

            if isinstance(listA,list) == False or  isinstance(listB,list) == False:
                print("分子或分母存在None")
                break

            if len(listA) != length or len(listB) != length:
                print("分子或分母存在长度与期望不一致")
                break

            if listA[i] == None or listB[i] == None or listB[i]== 0:
                continue
            divideList[i] = listA[i] / listB[i]

        numeratorSum = CommonCal.getSum(listA)
        denominatorSum = CommonCal.getSum(listB)
        if denominatorSum == None or denominatorSum == 0 or numeratorSum == None:
            pass
        else:
            divideSum = numeratorSum / denominatorSum

        return {
            "divideList": divideList,
            "numeratorSum": numeratorSum,
            "denominatorSum": denominatorSum,
            "divideSum": divideSum,
        }


    @staticmethod
    def conductAdd(dataList,noneToZero=[],length=96 ):
        '''
        lsitA + listB
        :param listA:
        :param listB:
        :param A_Zero:  A 为空时是否当0处理
        :param B_Zero:  B 为空时是否当0处理
        :param length:
        :return:
        '''


        if noneToZero == []:
            noneToZero = [1 for i in range(0,len(dataList))]


        for i in range(0,len(noneToZero)):
            if dataList[i] == None and noneToZero[i] == 1  :
                dataList[i] = [None for i in range(0,length)]

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
            sumList = [None for i in range(0, length)]

            for i in range(0, length):
                for j in range(0, len(dataList)):


                    if dataList[j][i] == None and noneToZero[j] == 1:
                        dataList[j][i] = 0

                    if dataList[j][i] == None:
                        pass
                    else:
                        sumList[i] = (0 if sumList[i]==None else sumList[i]) + dataList[j][i]


            return sumList
        else:
            print("A、B中存在非列表，无法进行相加")
            return [None for i in range(0,length)]

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
    def weightedMean( numeratorList ,denominatorList,length=96):
        '''
        加权平均，只适用于两个数据项
        :param numerator:  分子
        :param denominator: 分母
        :param length: 数组长度
        :return:
        '''

        numeratorResList = [None for i in range(0,length)]
        denominatorResList = [None for i in range(0,length)]
        numeratorDividedenominatorResList = [None for i in range(0,length)]
        numeratorSum = None
        denominatorSum = None
        divideSum = None

        isNumOrDenNotNone = True
        if numeratorList == None or numeratorList == [] or denominatorList == None or denominatorList == []:
            isNumOrDenNotNone == False


        if isNumOrDenNotNone:
            for i in range(0,length):
                if isinstance(numeratorList[0], list) == False or isinstance(numeratorList[1], list) == False:
                    break
                if len(numeratorList[0]) != length or len(numeratorList[1]) != length:
                    print("分子长度与期望的长度不一致")
                    break
                if numeratorList[0][i] == None or numeratorList[1][i] == None:
                    continue
                numeratorResList[i] = numeratorList[0][i] * numeratorList[1][i]

            for i in range(0, length):
                if isinstance(denominatorList[0], list) == False:
                    break
                if len(denominatorList[0]) != length :
                    print("分母长度与期望的长度不一致")
                    break
                if denominatorList[0][i] == None or numeratorResList[i] == None:
                    continue
                denominatorResList[i] = denominatorList[0][i]
                if denominatorResList[i]==0:
                    continue
                numeratorDividedenominatorResList[i] = numeratorResList[i]/denominatorResList[i]

            numeratorSum = CommonCal.getSum(numeratorResList)
            denominatorSum = CommonCal.getSum(denominatorResList)
            if denominatorSum == None  or denominatorSum == 0  or numeratorSum==None:
                pass
            else:
                divideSum = numeratorSum/denominatorSum


        return {
            "numeratorList": numeratorResList,
            "denominatorList": denominatorResList,
            "divideList": numeratorDividedenominatorResList,
            "numeratorSum": numeratorSum,
            "denominatorSum": denominatorSum,
            "divideSum": divideSum,
        }

    #  暂不用这个加权计算逻辑
    # @staticmethod
    # def weightedMean( numeratorList ,denominatorList,length=96):
    #     '''
    #     加权平均
    #     :param numerator:  分子
    #     :param denominator: 分母
    #     :param length: 数组长度
    #     :return:
    #     '''
    #
    #
    #     numeratorResList = [None for i in range(0,length)]
    #     denominatorResList = [None for i in range(0,length)]
    #     numeratorDividedenominatorResList = [None for i in range(0,length)]
    #     numeratorSum = None
    #     denominatorSum = None
    #     divideSum = None
    #
    #     isNumOrDenNotNone = True
    #     if numeratorList == None or numeratorList == [] or denominatorList == None or denominatorList == []:
    #         isNumOrDenNotNone == False
    #
    #     if isNumOrDenNotNone:
    #
    #         isNumNotError = True
    #
    #
    #         for l in range(0, len(numeratorList)):
    #
    #             if isinstance(numeratorList[l] ,list) == False:
    #                 isNumNotError = False
    #                 break
    #             if len(numeratorList[l])!=length  :
    #                 isNumNotError = False
    #                 break
    #
    #         if isNumNotError == True:
    #             for i in range(0,length):
    #                 iIsNone = False
    #
    #                 for l in range(0, len(numeratorList)):
    #
    #                     if numeratorList[l][i] == None :
    #                         iIsNone = True
    #                         continue
    #
    #                     numeratorResList[i] = (1 if numeratorResList[i]==None else numeratorResList[i])*numeratorList[l][i]
    #                 if iIsNone:
    #                     numeratorResList[i] = None
    #
    #         isDenNotError = True
    #         for l in range(0, len(denominatorList)):
    #             if isinstance(denominatorList[l], list) == False:
    #                 isDenNotError = False
    #                 break
    #             if len(denominatorList[l]) != length:
    #                 isDenNotError = False
    #                 break
    #             for i in range(0, length):
    #                 if denominatorList[l][i] == None:
    #                     continue
    #                 denominatorResList[i] = (0 if denominatorResList[i] == None else denominatorResList[i]) + denominatorList[l][i]
    #
    #         if isNumNotError == True and isDenNotError == True:
    #
    #             for i in range(0, length):
    #                 if numeratorResList[i] == None or denominatorResList[i]==None or denominatorResList[i]==0:
    #                     numeratorDividedenominatorResList[i] = None
    #                 else:
    #                     numeratorDividedenominatorResList[i] = numeratorResList[i]/denominatorResList[i]
    #
    #                 # if numeratorResList[i] != None:
    #                 #     if numeratorSum == None:
    #                 #         numeratorSum = numeratorResList[i]
    #                 #     else:
    #                 #         numeratorSum += numeratorResList[i]
    #                 #
    #                 # if denominatorResList[i] != None:
    #                 #     if denominatorSum == None:
    #                 #         denominatorSum = denominatorResList[i]
    #                 #     else:
    #                 #         denominatorSum += denominatorResList[i]
    #
    #             numeratorSum = CommonCal.getSum(numeratorResList)
    #             denominatorSum = CommonCal.getSum(denominatorResList)
    #
    #             if denominatorSum == None  or denominatorSum == 0  or numeratorSum==None:
    #                 pass
    #             else:
    #                 divideSum = numeratorSum/denominatorSum
    #         if isNumNotError == False or isDenNotError == False:
    #             numeratorResList = [None for i in range(0,length)]
    #             denominatorResList = [None for i in range(0,length)]
    #
    #     return {
    #         "numeratorList": numeratorResList,
    #         "denominatorList": denominatorResList,
    #         "divideList": numeratorDividedenominatorResList,
    #         "numeratorSum": numeratorSum,
    #         "denominatorSum": denominatorSum,
    #         "divideSum": divideSum,
    #     }


    @staticmethod
    def conductAddMulField(fieldNameList, dataList, length=96):

        fieldDataDict = {}

        for field in fieldNameList:
            fieldDataDict[field] = []

        for data in dataList:
            for field in fieldNameList:
                # if field in data.keys():
                fieldDataDict[field].append(data[field])

        for field in fieldNameList:
            fieldDataDict[field] = CommonCal.conductAdd(fieldDataDict[field], length=length)

        return fieldDataDict

if __name__ == '__main__':
    print(CommonCal.weightedMean(
        [[1, 2], [3, 4]],
        [[1, 2]]
        , 2
    ))