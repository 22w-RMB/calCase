

class ProInLogic:


    @staticmethod
    def weightedMean( numeratorList ,denominatorList,lenght=96):
        '''
        加权平均
        :param numerator:  分子
        :param denominator: 分母
        :param lenght: 数组长度
        :return:
        '''
        numeratorRes = [None for i in range(0,lenght)]
        denominatorRes = [None for i in range(0,lenght)]
        numeratorDividedenominatorRes = [None for i in range(0,lenght)]
        for i in range(0, lenght):
            for l in range(0,len(numeratorList)):
                # 如果分子存在任意一项为空，则结果为空
                if numeratorList[l][i] == None:
                    numeratorRes[i] = None
                    continue

                numeratorRes[i] = (1 if numeratorRes[i]==None else numeratorRes[i])*numeratorList[l][i]

            for l in range(0, len(denominatorList)):
                # 如果分母存在任意一项为空，则结果为空
                if denominatorList[l][i] == None:
                    denominatorRes[i] = None
                    continue

                denominatorRes[i] = (0 if denominatorRes[i] == None else denominatorRes[i]) + denominatorList[l][i]

            if numeratorRes[i] == None or denominatorRes[i]==None or denominatorRes[i]==0:
                numeratorDividedenominatorRes[i] = None
            else:
                numeratorDividedenominatorRes[i] = numeratorRes[i]/denominatorRes[i]

        return {
            "numerator": numeratorRes,
            "denominator": denominatorRes,
            "divide": numeratorDividedenominatorRes,
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


    # 中长期
    @staticmethod
    def mltProcess(dataList,lenght=96):

        mlt_ele = [None for i in range(0,lenght)]
        mlt_price = [None for i in range(0,lenght)]
        mlt_fee = [None for i in range(0,lenght)]
        change_cost = [None for i in range(0,lenght)]

        needKeys = [
            "mlt_ele",
            "mlt_price",
            "mlt_fee",
            "change_cost",
        ]
        getNeedKeyData = ProInLogic.filterNeedKeyFromDbData(dataList,needKeys)

        for data in dataList:
            pass
        pass