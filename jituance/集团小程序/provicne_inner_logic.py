from jituance.集团小程序.common_calculation import CommonCal


class ProInLogic:

    # 变动成本
    @staticmethod
    def otherInComeProcess(dataList, lenght=96):
        needKeys = [
            "mlt_ele",
            "change_cost",
        ]

        getNeedKeyData = CommonCal.filterNeedKeyFromDbData(dataList, needKeys)

        change_cost_weightedmean = CommonCal.weightedMean(
            numeratorList=[getNeedKeyData["mlt_ele"], getNeedKeyData["change_cost"]],
            denominatorList=[getNeedKeyData["mlt_ele"]],
            lenght=lenght
        )

        # 变动成本
        change_cost_list = change_cost_weightedmean["divideList"]
        change_cost_sum = change_cost_weightedmean["divideSum"]

        return {
            "change_cost_list": change_cost_list,
            "change_cost_sum": change_cost_sum,
        }


    # 中长期电量、电价、费用
    @staticmethod
    def otherMltProcess(dataList, lenght=96):

        # mlt_ele = [None for i in range(0,lenght)]
        # mlt_price = [None for i in range(0,lenght)]
        # mlt_fee = [None for i in range(0,lenght)]
        # change_cost = [None for i in range(0,lenght)]

        needKeys = [
            "mlt_ele",
            "mlt_price",
            "change_cost",
        ]
        getNeedKeyData = CommonCal.filterNeedKeyFromDbData(dataList, needKeys)

        mlt_ele_price_weightedmean = CommonCal.weightedMean(
            numeratorList=[getNeedKeyData["mlt_ele"], getNeedKeyData["mlt_price"]],
            denominatorList=[getNeedKeyData["mlt_ele"]],
            lenght=lenght
        )

        # 获取偏差电价
        mlt_diffPrice = []
        for i in range(len(0, getNeedKeyData["mlt_ele"])):
            diffPrice = CommonCal.conductSubtract(getNeedKeyData["mlt_price"][i], getNeedKeyData["change_cost"][i],
                                                  B_NoneToZero=True)
            mlt_diffPrice.append(diffPrice["diff"])
        mlt_diff_weightedmean = CommonCal.weightedMean(
            numeratorList=[getNeedKeyData["mlt_ele"], mlt_diffPrice],
            denominatorList=[getNeedKeyData["mlt_ele"]],
            lenght=lenght
        )

        # 中长期收入
        mlt_ele_list = mlt_ele_price_weightedmean["denominatorResList"]
        mlt_ele_sum = mlt_ele_price_weightedmean["denominatorSum"]
        mlt_price_list = mlt_ele_price_weightedmean["divideList"]
        mlt_price_sum = mlt_ele_price_weightedmean["divideSum"]
        mlt_fee_list = mlt_ele_price_weightedmean["numeratorList"]
        mlt_fee_sum = mlt_ele_price_weightedmean["numeratorSum"]
        # mlt_change_cost_list = mlt_ele_cost_weightedmean["divideList"]
        # mlt_change_cost_sum = mlt_ele_cost_weightedmean["divideSum"]

        # 中长期收益
        mlt_diff_fee_sum = mlt_diff_weightedmean["numeratorSum"]

        return {
            "mlt_ele_list": mlt_ele_list,
            "mlt_ele_sum": mlt_ele_sum,
            "mlt_price_list": mlt_price_list,
            "mlt_price_sum": mlt_price_sum,
            "mlt_fee_list": mlt_fee_list,
            "mlt_fee_sum": mlt_fee_sum,
            # "mlt_change_cost_list" :  mlt_change_cost_list,
            # "mlt_change_cost_sum" :  mlt_change_cost_sum,
            "mlt_diff_fee_sum": mlt_diff_fee_sum,
        }

    # 日前结算电量、日前结算电价、日前结算费用
    @staticmethod
    def otherDayAheadProcess(dataList, lenght=96):

        needKeys = [
            "mlt_ele",
            "day_ahead_ele",
            "day_ahead_price",
            "change_cost",
        ]
        getNeedKeyData = CommonCal.filterNeedKeyFromDbData(dataList, needKeys)

        # 获取日前结算量价费
        dayAhead_ele_price_weightedmean = CommonCal.weightedMean(
            numeratorList=[getNeedKeyData["day_ahead_ele"], getNeedKeyData["day_ahead_price"]],
            denominatorList=[getNeedKeyData["day_ahead_ele"]],
            lenght=lenght
        )

        # 获取日前偏差电量
        dayAhead_diffEle = []
        dayAhead_positive_diffEle = []
        dayAhead_negative_diffEle = []
        dayAhead_price_sub_cost = []

        for i in range(len(0, getNeedKeyData["day_ahead_ele"])):
            diffEle = CommonCal.conductSubtract(getNeedKeyData["day_ahead_ele"][i], getNeedKeyData["mlt_ele"][i])
            dayAhead_diffEle.append(diffEle["diff"])
            dayAhead_positive_diffEle.append(diffEle["positive_diff"])
            dayAhead_negative_diffEle.append(diffEle["negative_diff"])

            diffPrice = CommonCal.conductSubtract(getNeedKeyData["day_ahead_price"][i],
                                                  getNeedKeyData["change_cost"][i], B_NoneToZero=True)
            dayAhead_price_sub_cost.append(diffPrice["diff"])

        # 获取日前正偏差收益
        dayAhead_positive_weightedmean = CommonCal.weightedMean(
            numeratorList=[dayAhead_positive_diffEle, dayAhead_price_sub_cost],
            denominatorList=[dayAhead_positive_diffEle],
            lenght=lenght
        )

        # 获取日前正偏差电量*日期偏差电价
        dayAhead_positive_diff = CommonCal.weightedMean(
            numeratorList=[dayAhead_positive_diffEle, getNeedKeyData["day_ahead_price"]],
            denominatorList=[dayAhead_positive_diffEle],
            lenght=lenght
        )


        # 获取日前负偏差收益
        dayAhead_negative_weightedmean = CommonCal.weightedMean(
            numeratorList=[dayAhead_negative_diffEle, dayAhead_price_sub_cost],
            denominatorList=[dayAhead_negative_diffEle],
            lenght=lenght
        )

        # 获取日前负偏差电量*日期偏差电价
        dayAhead_negative_diff = CommonCal.weightedMean(
            numeratorList=[dayAhead_negative_diffEle, getNeedKeyData["day_ahead_price"]],
            denominatorList=[dayAhead_negative_diffEle],
            lenght=lenght
        )

        # 日前费用
        dayAhead_ele_list = dayAhead_ele_price_weightedmean["denominatorResList"]
        dayAhead_ele_sum = dayAhead_ele_price_weightedmean["denominatorSum"]
        dayAhead_price_list = dayAhead_ele_price_weightedmean["divideList"]
        dayAhead_price_sum = dayAhead_ele_price_weightedmean["divideSum"]
        dayAhead_fee_list = dayAhead_ele_price_weightedmean["numeratorList"]
        dayAhead_fee_sum = dayAhead_ele_price_weightedmean["numeratorSum"]

        # 日前正偏差
        dayAhead_positive_ele_list = dayAhead_positive_weightedmean["denominatorResList"]
        dayAhead_positive_ele_sum = dayAhead_positive_weightedmean["denominatorSum"]
        dayAhead_positive_price_sub_cost_list = dayAhead_positive_weightedmean["divideList"]
        dayAhead_positive_price_sub_cost_sum = dayAhead_positive_weightedmean["divideSum"]
        dayAhead_positive_fee_list = dayAhead_positive_weightedmean["numeratorList"]
        dayAhead_positive_fee_sum = dayAhead_positive_weightedmean["numeratorSum"]
        dayAhead_positive_diff_fee_list = dayAhead_positive_diff["numeratorSum"]

        # 日前负偏差
        dayAhead_negative_ele_list = dayAhead_negative_weightedmean["denominatorResList"]
        dayAhead_negative_ele_sum = dayAhead_negative_weightedmean["denominatorSum"]
        dayAhead_negative_price_sub_cost_list = dayAhead_negative_weightedmean["divideList"]
        dayAhead_negative_price_sub_cost_sum = dayAhead_negative_weightedmean["divideSum"]
        dayAhead_negative_fee_list = dayAhead_negative_weightedmean["numeratorList"]
        dayAhead_negative_fee_sum = dayAhead_negative_weightedmean["numeratorSum"]
        dayAhead_negative_diff_fee_list = dayAhead_negative_diff["numeratorSum"]

        # 日前偏差电量*日期偏差电价



        return {
            "dayAhead_ele_list": dayAhead_ele_list,
            "dayAhead_ele_sum": dayAhead_ele_sum,
            "dayAhead_price_list": dayAhead_price_list,
            "dayAhead_price_sum": dayAhead_price_sum,
            "dayAhead_fee_list": dayAhead_fee_list,
            "dayAhead_fee_sum": dayAhead_fee_sum,
            "dayAhead_positive_ele_list": dayAhead_positive_ele_list,
            "dayAhead_positive_ele_sum": dayAhead_positive_ele_sum,
            "dayAhead_positive_price_sub_cost_list": dayAhead_positive_price_sub_cost_list,
            "dayAhead_positive_price_sub_cost_sum": dayAhead_positive_price_sub_cost_sum,
            "dayAhead_positive_fee_list": dayAhead_positive_fee_list,
            "dayAhead_positive_fee_sum": dayAhead_positive_fee_sum,
            "dayAhead_negative_ele_list": dayAhead_negative_ele_list,
            "dayAhead_negative_ele_sum": dayAhead_negative_ele_sum,
            "dayAhead_negative_price_sub_cost_list": dayAhead_negative_price_sub_cost_list,
            "dayAhead_negative_price_sub_cost_sum": dayAhead_negative_price_sub_cost_sum,
            "dayAhead_negative_fee_list": dayAhead_negative_fee_list,
            "dayAhead_negative_fee_sum": dayAhead_negative_fee_sum,
            "dayAhead_positive_diff_fee_list": dayAhead_positive_diff_fee_list,
            "dayAhead_negative_diff_fee_list": dayAhead_negative_diff_fee_list,
        }

    # 实时结算电量、日前结算电价、日前结算费用
    @staticmethod
    def otherRealTimeProcess(dataList, lenght=96):

        needKeys = [
            "day_ahead_ele",
            "real_time_ele",
            "real_time_price",
            "change_cost",
        ]
        getNeedKeyData = CommonCal.filterNeedKeyFromDbData(dataList, needKeys)

        # 获取日前结算量价费
        realTime_ele_price_weightedmean = CommonCal.weightedMean(
            numeratorList=[getNeedKeyData["real_time_ele"], getNeedKeyData["real_time_price"]],
            denominatorList=[getNeedKeyData["real_time_ele"]],
            lenght=lenght
        )

        # 获取日前偏差电量
        realTime_diffEle = []
        realTime_positive_diffEle = []
        realTime_negative_diffEle = []
        realTime_price_sub_cost = []

        for i in range(len(0, getNeedKeyData["real_time_ele"])):
            diffEle = CommonCal.conductSubtract(getNeedKeyData["real_time_ele"][i], getNeedKeyData["day_ahead_ele"][i])
            realTime_diffEle.append(diffEle["diff"])
            realTime_positive_diffEle.append(diffEle["positive_diff"])
            realTime_negative_diffEle.append(diffEle["negative_diff"])

            diffPrice = CommonCal.conductSubtract(getNeedKeyData["real_time_price"][i],
                                                  getNeedKeyData["change_cost"][i], B_NoneToZero=True)
            realTime_price_sub_cost.append(diffPrice["diff"])

        # 获取日前正偏差量价费
        realTime_positive_weightedmean = CommonCal.weightedMean(
            numeratorList=[realTime_positive_diffEle, realTime_price_sub_cost],
            denominatorList=[realTime_positive_diffEle],
            lenght=lenght
        )
        # 获取日前负偏差量价费
        realTime_negative_weightedmean = CommonCal.weightedMean(
            numeratorList=[realTime_negative_diffEle, realTime_price_sub_cost],
            denominatorList=[realTime_negative_diffEle],
            lenght=lenght
        )

        # 获取实时正偏差电量*日期偏差电价
        realTime_positive_diff = CommonCal.weightedMean(
            numeratorList=[realTime_positive_diffEle, getNeedKeyData["real_time_price"]],
            denominatorList=[realTime_positive_diffEle],
            lenght=lenght
        )


        # 获取实时负偏差电量*日期偏差电价
        realTime_negative_diff = CommonCal.weightedMean(
            numeratorList=[realTime_negative_diffEle, getNeedKeyData["real_time_price"]],
            denominatorList=[realTime_negative_diffEle],
            lenght=lenght
        )

        # 日前结算
        realTime_ele_list = realTime_ele_price_weightedmean["denominatorResList"]
        realTime_ele_sum = realTime_ele_price_weightedmean["denominatorSum"]
        realTime_price_list = realTime_ele_price_weightedmean["divideList"]
        realTime_price_sum = realTime_ele_price_weightedmean["divideSum"]
        realTime_fee_list = realTime_ele_price_weightedmean["numeratorList"]
        realTime_fee_sum = realTime_ele_price_weightedmean["numeratorSum"]

        # 实时正偏差
        realTime_positive_ele_list = realTime_positive_weightedmean["denominatorResList"]
        realTime_positive_ele_sum = realTime_positive_weightedmean["denominatorSum"]
        realTime_positive_price_sub_cost_list = realTime_positive_weightedmean["divideList"]
        realTime_positive_price_sub_cost_sum = realTime_positive_weightedmean["divideSum"]
        realTime_positive_fee_list = realTime_positive_weightedmean["numeratorList"]
        realTime_positive_fee_sum = realTime_positive_weightedmean["numeratorSum"]
        realTime_positive_diff_fee_list = realTime_positive_diff["numeratorSum"]

        # 实时负偏差
        realTime_negative_ele_list = realTime_negative_weightedmean["denominatorResList"]
        realTime_negative_ele_sum = realTime_negative_weightedmean["denominatorSum"]
        realTime_negative_price_sub_cost_list = realTime_negative_weightedmean["divideList"]
        realTime_negative_price_sub_cost_sum = realTime_negative_weightedmean["divideSum"]
        realTime_negative_fee_list = realTime_negative_weightedmean["numeratorList"]
        realTime_negative_fee_sum = realTime_negative_weightedmean["numeratorSum"]
        realTime_negative_diff_fee_list = realTime_negative_diff["numeratorSum"]

        return {
            "realTime_ele_list": realTime_ele_list,
            "realTime_ele_sum": realTime_ele_sum,
            "realTime_price_list": realTime_price_list,
            "realTime_price_sum": realTime_price_sum,
            "realTime_fee_list": realTime_fee_list,
            "realTime_fee_sum": realTime_fee_sum,
            "realTime_positive_ele_list": realTime_positive_ele_list,
            "realTime_positive_ele_sum": realTime_positive_ele_sum,
            "realTime_positive_price_sub_cost_list": realTime_positive_price_sub_cost_list,
            "realTime_positive_price_sub_cost_sum": realTime_positive_price_sub_cost_sum,
            "realTime_positive_fee_list": realTime_positive_fee_list,
            "realTime_positive_fee_sum": realTime_positive_fee_sum,
            "realTime_negative_ele_list": realTime_negative_ele_list,
            "realTime_negative_ele_sum": realTime_negative_ele_sum,
            "realTime_negative_price_sub_cost_list": realTime_negative_price_sub_cost_list,
            "realTime_negative_price_sub_cost_sum": realTime_negative_price_sub_cost_sum,
            "realTime_negative_fee_list": realTime_negative_fee_list,
            "realTime_negative_fee_sum": realTime_negative_fee_sum,
            "realTime_positive_diff_fee_list": realTime_positive_diff_fee_list,
            "realTime_negative_diff_fee_list": realTime_negative_diff_fee_list,
        }

    # 收益、综合价
    @staticmethod
    def otherInComeProcess(dataList):

        mlt = ProInLogic.otherMltProcess(dataList)
        dayAhead = ProInLogic.otherDayAheadProcess(dataList)
        realTime = ProInLogic.otherRealTimeProcess(dataList)

        # 中长期收益
        mltIncomeList = mlt["mlt_diff_fee_sum"]
        # 中长期收入
        mltFeeList = mlt["mlt_fee_sum"]

        # 日前正偏差收益
        dayAheadPositiveIncomeList = dayAhead["dayAhead_positive_fee_list"]
        # 日前负偏差收益
        dayAheadNegativeIncomeList = dayAhead["dayAhead_negative_fee_list"]
        # 日前结算收益
        dayAheadSettlementIncomeList = CommonCal.conductAdd([dayAheadPositiveIncomeList, dayAheadNegativeIncomeList,] )
        # 日前收益
        dayAheadIncomeList = CommonCal.conductAdd( [dayAheadSettlementIncomeList, mltIncomeList] )
        # 日前正偏差电量*正偏差电价
        dayAheadPositiveFeeList = dayAhead["dayAhead_positive_diff_fee_list"]
        # 日前负偏差电量*负偏差电价
        dayAheadNegativeFeeList = dayAhead["dayAhead_negative_diff_fee_list"]

        # 实时出清电量
        realTimeEleList = realTime["realTime_ele_list"]
        # 实时正偏差收益
        realTimePositiveIncomeList = realTime["realTime_positive_fee_list"]
        # 实时负偏差收益
        realTimeNegativeIncomeList = realTime["realTime_negative_fee_list"]
        # 实时结算收益
        realTimeSettlementIncomeList = CommonCal.conductAdd( [realTimePositiveIncomeList, realTimeNegativeIncomeList] )
        # 实时收益
        realTimeIncomeList = CommonCal.conductAdd( [dayAheadIncomeList, realTimeSettlementIncomeList] )
        # 实时正偏差电量*正偏差电价
        realTimePositiveFeeList = dayAhead["realTime_positive_diff_fee_list"]
        # 实时负偏差电量*负偏差电价
        realTimeNegativeFeeList = dayAhead["realTime_negative_diff_fee_list"]


        # 综合收入
        comprehensiveIncomeList =  CommonCal.conductAdd(
            [
                dayAheadPositiveFeeList,
                dayAheadNegativeFeeList,
                realTimePositiveFeeList,
                realTimeNegativeFeeList,
                mltFeeList,
            ]
        )


        # 综合收入/实时出清电量
        comprehensive = CommonCal.weightedMean([comprehensiveIncomeList],[realTimeEleList])
        # 综合电价
        comprehensivePriceList = comprehensive["divideList"]

        # 现货增收
        SpotIncomeIncreaseLsit = CommonCal.conductAdd( [dayAheadSettlementIncomeList, realTimeSettlementIncomeList] )

        return {

            "realTime_negative_fee_sum": 1,
        }


if __name__ == '__main__':


    a = CommonCal.conductAdd(
        [[1,2],[3,None],None,[4,5]],
        lenght=2
    )
    print(a)

