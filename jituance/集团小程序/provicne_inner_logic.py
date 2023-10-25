from jituance.集团小程序.common_calculation import CommonCal


class ProInLogic:

    # 运行容量
    @staticmethod
    def runCapacityProcess(dataList, length=96):
        needKeys = [
            "run_capacity",
        ]

        getNeedKeyData = CommonCal.filterNeedKeyFromDbData(dataList, needKeys)

        run_capacity_list = CommonCal.conductAdd(getNeedKeyData["run_capacity"])["sumList"]

        return {
            "run_capacity_list": run_capacity_list,
        }

    # 变动成本
    @staticmethod
    def otherChangeCostProcess(dataList, length=96):
        needKeys = [
            "mlt_ele",
            "change_cost",
        ]

        getNeedKeyData = CommonCal.filterNeedKeyFromDbData(dataList, needKeys)
        # print(getNeedKeyData["change_cost"])

        change_cost_weightedmean = CommonCal.spitWeightedMeanData(
            numeratorList=[getNeedKeyData["mlt_ele"], getNeedKeyData["change_cost"]],
            denominatorList=[getNeedKeyData["mlt_ele"]],
            length=length
        )

        # 变动成本
        change_cost_ele_list = change_cost_weightedmean["denominatorList"]
        change_cost_price_list = change_cost_weightedmean["divideList"]
        change_cost_fee_list = change_cost_weightedmean["numeratorList"]

        return {
            "change_cost_ele_list": change_cost_ele_list,
            "change_cost_price_list": change_cost_price_list,
            "change_cost_fee_list": change_cost_fee_list,
        }

    # 中长期电量、电价、费用
    @staticmethod
    def otherMltProcess(dataList, length=96):

        needKeys = [
            "mlt_ele",
            "mlt_price",
            "change_cost",
        ]
        getNeedKeyData = CommonCal.filterNeedKeyFromDbData(dataList, needKeys)

        mlt_ele_price_weightedmean = CommonCal.spitWeightedMeanData(
            numeratorList=[getNeedKeyData["mlt_ele"], getNeedKeyData["mlt_price"]],
            denominatorList=[getNeedKeyData["mlt_ele"]],
            length=length
        )


        # 获取偏差电价
        mlt_diffPrice = []
        for i in range(0,len( getNeedKeyData["mlt_ele"])):
            diffPrice = CommonCal.conductSubtract(getNeedKeyData["mlt_price"][i], getNeedKeyData["change_cost"][i],
                                                  B_NoneToZero=True)
            mlt_diffPrice.append(diffPrice["diff"])

        mlt_diff_weightedmean = CommonCal.spitWeightedMeanData(
            numeratorList=[getNeedKeyData["mlt_ele"], mlt_diffPrice],
            denominatorList=[getNeedKeyData["mlt_ele"]],
            length=length
        )


        # 中长期收入
        mlt_ele_list = mlt_ele_price_weightedmean["denominatorList"]
        mlt_ele_sum = mlt_ele_price_weightedmean["denominatorSum"]
        mlt_price_list = mlt_ele_price_weightedmean["divideList"]
        mlt_price_sum = mlt_ele_price_weightedmean["divideSum"]
        mlt_fee_list = mlt_ele_price_weightedmean["numeratorList"]
        mlt_fee_sum = mlt_ele_price_weightedmean["numeratorSum"]

        # 中长期收益
        mlt_diff_fee_sum = mlt_diff_weightedmean["numeratorSum"]
        mlt_diff_fee_list = mlt_diff_weightedmean["numeratorList"]

        return {
            "mlt_ele_list": mlt_ele_list,
            "mlt_ele_sum": mlt_ele_sum,
            "mlt_price_list": mlt_price_list,
            "mlt_price_sum": mlt_price_sum,
            "mlt_fee_list": mlt_fee_list,
            "mlt_fee_sum": mlt_fee_sum,
            "mlt_diff_fee_sum": mlt_diff_fee_sum,
            "mlt_diff_fee_list": mlt_diff_fee_list,
        }

    # 日前结算电量、日前结算电价、日前结算费用
    @staticmethod
    def otherDayAheadProcess(dataList, length=96):

        needKeys = [
            "mlt_ele",
            "day_ahead_ele",
            "day_ahead_price",
            "change_cost",
        ]
        getNeedKeyData = CommonCal.filterNeedKeyFromDbData(dataList, needKeys)

        # 获取日前结算量价费
        dayAhead_ele_price_weightedmean = CommonCal.spitWeightedMeanData(
            numeratorList=[getNeedKeyData["day_ahead_ele"], getNeedKeyData["day_ahead_price"]],
            denominatorList=[getNeedKeyData["day_ahead_ele"]],
            length=length
        )

        # 获取日前偏差电量
        dayAhead_diffEle = []
        dayAhead_positive_diffEle = []
        dayAhead_negative_diffEle = []
        dayAhead_price_sub_cost = []

        for i in range(0,len( getNeedKeyData["day_ahead_ele"])):
            diffEle = CommonCal.conductSubtract(getNeedKeyData["day_ahead_ele"][i], getNeedKeyData["mlt_ele"][i])
            dayAhead_diffEle.append(diffEle["diff"])
            dayAhead_positive_diffEle.append(diffEle["positive_diff"])
            dayAhead_negative_diffEle.append(diffEle["negative_diff"])

            diffPrice = CommonCal.conductSubtract(getNeedKeyData["day_ahead_price"][i],
                                                  getNeedKeyData["change_cost"][i], B_NoneToZero=True)
            dayAhead_price_sub_cost.append(diffPrice["diff"])

        # 获取日前正偏差收益
        dayAhead_positive_weightedmean = CommonCal.spitWeightedMeanData(
            numeratorList=[dayAhead_positive_diffEle, dayAhead_price_sub_cost],
            denominatorList=[dayAhead_positive_diffEle],
            length=length
        )

        # 获取日前正偏差电量*日期偏差电价
        dayAhead_positive_diff = CommonCal.spitWeightedMeanData(
            numeratorList=[dayAhead_positive_diffEle, getNeedKeyData["day_ahead_price"]],
            denominatorList=[dayAhead_positive_diffEle],
            length=length
        )


        # 获取日前负偏差收益
        dayAhead_negative_weightedmean = CommonCal.spitWeightedMeanData(
            numeratorList=[dayAhead_negative_diffEle, dayAhead_price_sub_cost],
            denominatorList=[dayAhead_negative_diffEle],
            length=length
        )

        # 获取日前负偏差电量*日期偏差电价
        dayAhead_negative_diff = CommonCal.spitWeightedMeanData(
            numeratorList=[dayAhead_negative_diffEle, getNeedKeyData["day_ahead_price"]],
            denominatorList=[dayAhead_negative_diffEle],
            length=length
        )

        # 日前费用
        dayAhead_ele_list = dayAhead_ele_price_weightedmean["denominatorList"]
        dayAhead_ele_sum = dayAhead_ele_price_weightedmean["denominatorSum"]
        dayAhead_price_list = dayAhead_ele_price_weightedmean["divideList"]
        dayAhead_price_sum = dayAhead_ele_price_weightedmean["divideSum"]
        dayAhead_fee_list = dayAhead_ele_price_weightedmean["numeratorList"]
        dayAhead_fee_sum = dayAhead_ele_price_weightedmean["numeratorSum"]

        # 日前正偏差
        dayAhead_positive_ele_list = dayAhead_positive_weightedmean["denominatorList"]
        dayAhead_positive_ele_sum = dayAhead_positive_weightedmean["denominatorSum"]
        dayAhead_positive_price_sub_cost_list = dayAhead_positive_weightedmean["divideList"]
        dayAhead_positive_price_sub_cost_sum = dayAhead_positive_weightedmean["divideSum"]
        dayAhead_positive_fee_list = dayAhead_positive_weightedmean["numeratorList"]
        dayAhead_positive_fee_sum = dayAhead_positive_weightedmean["numeratorSum"]
        dayAhead_positive_diff_fee_list = dayAhead_positive_diff["numeratorSum"]

        # 日前负偏差
        dayAhead_negative_ele_list = dayAhead_negative_weightedmean["denominatorList"]
        dayAhead_negative_ele_sum = dayAhead_negative_weightedmean["denominatorSum"]
        dayAhead_negative_price_sub_cost_list = dayAhead_negative_weightedmean["divideList"]
        dayAhead_negative_price_sub_cost_sum = dayAhead_negative_weightedmean["divideSum"]
        dayAhead_negative_fee_list = dayAhead_negative_weightedmean["numeratorList"]
        dayAhead_negative_fee_sum = dayAhead_negative_weightedmean["numeratorSum"]
        dayAhead_negative_diff_fee_list = dayAhead_negative_diff["numeratorSum"]




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
    def otherRealTimeProcess(dataList, length=96):

        needKeys = [
            "day_ahead_ele",
            "real_time_ele",
            "real_time_price",
            "change_cost",
        ]
        getNeedKeyData = CommonCal.filterNeedKeyFromDbData(dataList, needKeys)

        # 获取实时结算量价费
        realTime_ele_price_weightedmean = CommonCal.spitWeightedMeanData(
            numeratorList=[getNeedKeyData["real_time_ele"], getNeedKeyData["real_time_price"]],
            denominatorList=[getNeedKeyData["real_time_ele"]],
            length=length
        )

        # 获取实时偏差电量
        realTime_diffEle = []
        realTime_positive_diffEle = []
        realTime_negative_diffEle = []
        realTime_price_sub_cost = []

        for i in range(0,len( getNeedKeyData["real_time_ele"])):
            diffEle = CommonCal.conductSubtract(getNeedKeyData["real_time_ele"][i], getNeedKeyData["day_ahead_ele"][i],)
            realTime_diffEle.append(diffEle["diff"])
            realTime_positive_diffEle.append(diffEle["positive_diff"])
            realTime_negative_diffEle.append(diffEle["negative_diff"])

            diffPrice = CommonCal.conductSubtract(getNeedKeyData["real_time_price"][i],
                                                  getNeedKeyData["change_cost"][i], B_NoneToZero=True)
            realTime_price_sub_cost.append(diffPrice["diff"])

        # 获取实时正偏差量价费
        realTime_positive_weightedmean = CommonCal.spitWeightedMeanData(
            numeratorList=[realTime_positive_diffEle, realTime_price_sub_cost],
            denominatorList=[realTime_positive_diffEle],
            length=length
        )
        # 获取实时负偏差量价费
        realTime_negative_weightedmean = CommonCal.spitWeightedMeanData(
            numeratorList=[realTime_negative_diffEle, realTime_price_sub_cost],
            denominatorList=[realTime_negative_diffEle],
            length=length
        )

        # 获取实时正偏差电量*日期偏差电价
        realTime_positive_diff = CommonCal.spitWeightedMeanData(
            numeratorList=[realTime_positive_diffEle, getNeedKeyData["real_time_price"]],
            denominatorList=[realTime_positive_diffEle],
            length=length
        )


        # 获取实时负偏差电量*日期偏差电价
        realTime_negative_diff = CommonCal.spitWeightedMeanData(
            numeratorList=[realTime_negative_diffEle, getNeedKeyData["real_time_price"]],
            denominatorList=[realTime_negative_diffEle],
            length=length
        )

        # 实时结算
        realTime_ele_list = realTime_ele_price_weightedmean["denominatorList"]
        realTime_ele_sum = realTime_ele_price_weightedmean["denominatorSum"]
        realTime_price_list = realTime_ele_price_weightedmean["divideList"]
        realTime_price_sum = realTime_ele_price_weightedmean["divideSum"]
        realTime_fee_list = realTime_ele_price_weightedmean["numeratorList"]
        realTime_fee_sum = realTime_ele_price_weightedmean["numeratorSum"]

        # 实时正偏差
        realTime_positive_ele_list = realTime_positive_weightedmean["denominatorList"]
        realTime_positive_ele_sum = realTime_positive_weightedmean["denominatorSum"]
        realTime_positive_price_sub_cost_list = realTime_positive_weightedmean["divideList"]
        realTime_positive_price_sub_cost_sum = realTime_positive_weightedmean["divideSum"]
        realTime_positive_fee_list = realTime_positive_weightedmean["numeratorList"]
        realTime_positive_fee_sum = realTime_positive_weightedmean["numeratorSum"]
        realTime_positive_diff_fee_list = realTime_positive_diff["numeratorSum"]

        # 实时负偏差
        realTime_negative_ele_list = realTime_negative_weightedmean["denominatorList"]
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
    def otherInComeProcess(dataList, length=96):
        runCapacity = ProInLogic.runCapacityProcess(dataList,length)
        changeCost = ProInLogic.otherChangeCostProcess(dataList,length)
        mlt = ProInLogic.otherMltProcess(dataList,length)
        dayAhead = ProInLogic.otherDayAheadProcess(dataList,length)
        realTime = ProInLogic.otherRealTimeProcess(dataList,length)

        # 中长期收益
        mlt_income_list = mlt["mlt_diff_fee_list"]
        # 中长期收入
        mlt_fee_list = mlt["mlt_fee_list"]

        # 日前正偏差收益
        dayAhead_positive_income_list = dayAhead["dayAhead_positive_fee_list"]
        # 日前负偏差收益
        dayAhead_negative_income_list = dayAhead["dayAhead_negative_fee_list"]

        # 日前结算收益
        dayAhead_settlement_income_list = CommonCal.conductAdd([dayAhead_positive_income_list, dayAhead_negative_income_list] )["sumList"]
        # 日前收益
        dayAhead_income_list = CommonCal.conductAdd( [dayAhead_settlement_income_list, mlt_income_list] )["sumList"]
        # 日前正偏差电量*正偏差电价
        dayAhead_positive_fee_list = dayAhead["dayAhead_positive_diff_fee_list"]
        # 日前负偏差电量*负偏差电价
        dayAhead_negative_fee_list = dayAhead["dayAhead_negative_diff_fee_list"]


        # 实时出清电量
        realTime_ele_list = realTime["realTime_ele_list"]
        # 实时正偏差收益
        realTime_positive_income_list = realTime["realTime_positive_fee_list"]
        # 实时负偏差收益
        realTime_negative_income_list = realTime["realTime_negative_fee_list"]
        # 实时结算收益
        realTime_settlement_income_list = CommonCal.conductAdd( [realTime_positive_income_list, realTime_negative_income_list] )["sumList"]
        # 实时收益
        realTime_income_list = CommonCal.conductAdd( [dayAhead_income_list, realTime_settlement_income_list] )["sumList"]
        # 实时正偏差电量*正偏差电价
        realTime_positive_fee_list = realTime["realTime_positive_diff_fee_list"]
        # 实时负偏差电量*负偏差电价
        realTime_negative_fee_list = realTime["realTime_negative_diff_fee_list"]


        # 计算综合价的费用
        comprehensive_income_list =  CommonCal.conductAdd(
            [
                dayAhead_positive_fee_list,
                dayAhead_negative_fee_list,
                realTime_positive_fee_list,
                realTime_negative_fee_list,
                mlt_fee_list,
            ]
        )["sumList"]


        # 计算综合价的费用/实时出清电量
        comprehensive = CommonCal.weightedMean([comprehensive_income_list],[realTime_ele_list])
        # 综合电价
        comprehensive_price_list = comprehensive["divideList"]

        # 现货增收
        spot_incomeIncrease_list = CommonCal.conductAdd( [dayAhead_settlement_income_list, realTime_settlement_income_list] )["sumList"]

        return {
            # 运行容量
            "run_capacity_list": runCapacity["run_capacity_list"],

            # 变动成本需要的电量
            "change_cost_ele_list": changeCost["change_cost_ele_list"],
            # 变动成本
            "change_cost_price_list": changeCost["change_cost_price_list"],
            # 变动成本费用
            "change_cost_fee_list": changeCost["change_cost_fee_list"],

            # 中长期电量
            "mlt_ele_list": mlt["mlt_ele_list"],
            # 中长期均价
            "mlt_price_list": mlt["mlt_price_list"],
            # 中长期费用
            "mlt_fee_list": mlt["mlt_fee_list"],
            # 中长期收益
            "mlt_income_list": mlt_income_list,

            # 日前出清电量
            "dayAhead_ele_list": dayAhead["dayAhead_ele_list"],
            # 日前出清均价
            "dayAhead_price_list": dayAhead["dayAhead_price_list"],
            # 日前出清费用
            "dayAhead_fee_list": dayAhead["dayAhead_fee_list"],
            # 日前偏差收益
            "dayAhead_settlement_income_list": dayAhead_settlement_income_list,
            # 日前总收益
            "dayAhead_income_list": dayAhead_income_list,

            # 实时出清电量
            "realTime_ele_list": realTime["realTime_ele_list"],
            # 实时出清均价
            "realTime_price_list": realTime["realTime_price_list"],
            # 实时出清费用
            "realTime_fee_list": realTime["realTime_fee_list"],
            # 实时偏差收益
            "realTime_settlement_income_list": realTime_settlement_income_list,
            # 实时总收益
            "realTime_income_list": realTime_income_list,

            # 计算综合价的费用
            "comprehensive_income_list": comprehensive_income_list,
            # 计算综合价的电量
            "comprehensive_ele_list": realTime_ele_list,
            # 综合价
            "comprehensive_price_list": comprehensive_price_list,
            # 现货增收
            "spot_incomeIncrease_list": spot_incomeIncrease_list,
        }

    # 蒙西中长期电量、电价、费用
    @staticmethod
    def MXMltProcess(dataList, length=96):

        needKeys = [
            "mlt_ele",
            "mlt_price",
            "clearing_price",
        ]
        getNeedKeyData = CommonCal.filterNeedKeyFromDbData(dataList, needKeys)

        mlt_ele_price_weightedmean = CommonCal.spitWeightedMeanData(
            numeratorList=[getNeedKeyData["mlt_ele"], getNeedKeyData["mlt_price"]],
            denominatorList=[getNeedKeyData["mlt_ele"]],
            length=length
        )


        # 中长期电量*（中长期均价-统一出清均价）
        mlt_price_sub_unifiedPrice = []

        for i in range(0,len( getNeedKeyData["mlt_ele"])):

            diffPrice = CommonCal.conductSubtract(getNeedKeyData["mlt_price"][i],
                                                  getNeedKeyData["clearing_price"][i], B_NoneToZero=True)
            mlt_price_sub_unifiedPrice.append(diffPrice["diff"])

        mlt_diff_weightedmean = CommonCal.spitWeightedMeanData(
            numeratorList=[getNeedKeyData["mlt_ele"], mlt_price_sub_unifiedPrice],
            denominatorList=[getNeedKeyData["mlt_ele"]],
            length=length
        )



        # 中长期收入
        mlt_ele_list = mlt_ele_price_weightedmean["denominatorList"]
        mlt_ele_sum = mlt_ele_price_weightedmean["denominatorSum"]
        mlt_price_list = mlt_ele_price_weightedmean["divideList"]
        mlt_price_sum = mlt_ele_price_weightedmean["divideSum"]
        mlt_fee_list = mlt_ele_price_weightedmean["numeratorList"]
        mlt_fee_sum = mlt_ele_price_weightedmean["numeratorSum"]

        # 中长期电量*（中长期均价-统一出清均价）
        mlt_diff_fee_list = mlt_diff_weightedmean["numeratorList"]

        return {
            "mlt_ele_list": mlt_ele_list,
            "mlt_ele_sum": mlt_ele_sum,
            "mlt_price_list": mlt_price_list,
            "mlt_price_sum": mlt_price_sum,
            "mlt_fee_list": mlt_fee_list,
            "mlt_fee_sum": mlt_fee_sum,

            "mlt_diff_fee_list": mlt_diff_fee_list,

        }

    # 蒙西实时
    @staticmethod
    def MXRealTimeProcess(dataList, length=96):

        needKeys = [
            "mlt_ele",
            "real_time_ele",
            "real_time_price",
            "change_cost",
        ]
        getNeedKeyData = CommonCal.filterNeedKeyFromDbData(dataList, needKeys)

        # 获取日前结算量价费
        realTime_ele_price_weightedmean = CommonCal.spitWeightedMeanData(
            numeratorList=[getNeedKeyData["real_time_ele"], getNeedKeyData["real_time_price"]],
            denominatorList=[getNeedKeyData["real_time_ele"]],
            length=length
        )

        # 获取日前偏差电量
        realTime_diffEle = []
        realTime_positive_diffEle = []
        realTime_negative_diffEle = []
        realTime_price_sub_cost = []

        for i in range(0,len( getNeedKeyData["real_time_ele"])):
            diffEle = CommonCal.conductSubtract(getNeedKeyData["real_time_ele"][i], getNeedKeyData["mlt_ele"][i])
            realTime_diffEle.append(diffEle["diff"])
            realTime_positive_diffEle.append(diffEle["positive_diff"])
            realTime_negative_diffEle.append(diffEle["negative_diff"])

            diffPrice = CommonCal.conductSubtract(getNeedKeyData["real_time_price"][i],
                                                  getNeedKeyData["change_cost"][i], B_NoneToZero=True)
            realTime_price_sub_cost.append(diffPrice["diff"])

        # 获取日前正偏差量价费
        realTime_positive_weightedmean = CommonCal.spitWeightedMeanData(
            numeratorList=[realTime_positive_diffEle, realTime_price_sub_cost],
            denominatorList=[realTime_positive_diffEle],
            length=length
        )
        # 获取日前负偏差量价费
        realTime_negative_weightedmean = CommonCal.spitWeightedMeanData(
            numeratorList=[realTime_negative_diffEle, realTime_price_sub_cost],
            denominatorList=[realTime_negative_diffEle],
            length=length
        )



        # 实时结算
        realTime_ele_list = realTime_ele_price_weightedmean["denominatorList"]
        realTime_ele_sum = realTime_ele_price_weightedmean["denominatorSum"]
        realTime_price_list = realTime_ele_price_weightedmean["divideList"]
        realTime_price_sum = realTime_ele_price_weightedmean["divideSum"]
        realTime_fee_list = realTime_ele_price_weightedmean["numeratorList"]
        realTime_fee_sum = realTime_ele_price_weightedmean["numeratorSum"]

        # 实时正偏差
        realTime_positive_ele_list = realTime_positive_weightedmean["denominatorList"]
        realTime_positive_ele_sum = realTime_positive_weightedmean["denominatorSum"]
        realTime_positive_price_sub_cost_list = realTime_positive_weightedmean["divideList"]
        realTime_positive_price_sub_cost_sum = realTime_positive_weightedmean["divideSum"]
        realTime_positive_fee_list = realTime_positive_weightedmean["numeratorList"]
        realTime_positive_fee_sum = realTime_positive_weightedmean["numeratorSum"]

        # 实时负偏差
        realTime_negative_ele_list = realTime_negative_weightedmean["denominatorList"]
        realTime_negative_ele_sum = realTime_negative_weightedmean["denominatorSum"]
        realTime_negative_price_sub_cost_list = realTime_negative_weightedmean["divideList"]
        realTime_negative_price_sub_cost_sum = realTime_negative_weightedmean["divideSum"]
        realTime_negative_fee_list = realTime_negative_weightedmean["numeratorList"]
        realTime_negative_fee_sum = realTime_negative_weightedmean["numeratorSum"]

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
        }

    # 蒙西收益、综合价
    @staticmethod
    def MXInComeProcess(dataList, length=96):
        runCapacity = ProInLogic.runCapacityProcess(dataList,length)
        changeCost = ProInLogic.otherChangeCostProcess(dataList,length)
        mlt = ProInLogic.MXMltProcess(dataList,length)
        realTime = ProInLogic.MXRealTimeProcess(dataList,length)

        # 中长期量*变动成本
        change_cost_fee_list = changeCost["change_cost_fee_list"]
        # 中长期量*（中长期价-统一出清价）费用
        mlt_diff_fee_list = mlt["mlt_diff_fee_list"]


        # 实时出清电量
        realTime_ele_list = realTime["realTime_ele_list"]
        # 实时出清费用
        realTime_fee_list = realTime["realTime_fee_list"]
        # 实时正偏差收益
        realTime_positive_income_list = realTime["realTime_positive_fee_list"]
        # 实时负偏差收益
        realTime_negative_income_list = realTime["realTime_negative_fee_list"]
        # 实时结算收益
        realTime_settlement_income_list = CommonCal.conductAdd( [realTime_positive_income_list, realTime_negative_income_list] )["sumList"]

        # 中长期量*（中长期价-统一出清价）费用 + 实时出清费用
        realTime_temp_list = CommonCal.conductAdd([mlt_diff_fee_list, realTime_fee_list])["sumList"]
        # 实时收益
        realTime_income_list = CommonCal.conductSubtract(realTime_temp_list,change_cost_fee_list,B_NoneToZero=True)["diff"]


        # 计算综合价的费用
        comprehensive_income_list = realTime_temp_list

        # 计算综合价的费用/实时出清电量
        comprehensive = CommonCal.weightedMean([comprehensive_income_list],[realTime_ele_list])
        # 综合电价
        comprehensive_price_list = comprehensive["divideList"]

        # 现货增收
        spot_incomeIncrease_list = realTime_settlement_income_list

        # 中长期收益
        mlt_income_list = CommonCal.conductSubtract(realTime_income_list,spot_incomeIncrease_list)["diff"]

        return {
            # 运行容量
            "run_capacity_list": runCapacity["run_capacity_list"],

            # 变动成本需要的电量
            "change_cost_ele_list": changeCost["change_cost_ele_list"],
            # 变动成本
            "change_cost_price_list": changeCost["change_cost_price_list"],
            # 变动成本费用
            "change_cost_fee_list": changeCost["change_cost_fee_list"],

            # 中长期电量
            "mlt_ele_list": mlt["mlt_ele_list"],
            # 中长期均价
            "mlt_price_list": mlt["mlt_price_list"],
            # 中长期费用
            "mlt_fee_list": mlt["mlt_fee_list"],
            # 中长期收益
            "mlt_income_list": mlt_income_list,

            # 日前出清电量
            "dayAhead_ele_list": [None for i in range(0,length)],
            # 日前出清均价
            "dayAhead_price_list": [None for i in range(0,length)],
            # 日前出清费用
            "dayAhead_fee_list": [None for i in range(0,length)],
            # 日前偏差收益
            "dayAhead_settlement_income_list": [None for i in range(0,length)],
            # 日前总收益
            "dayAhead_income_list": [None for i in range(0,length)],

            # 实时出清电量
            "realTime_ele_list": realTime["realTime_ele_list"],
            # 实时出清均价
            "realTime_price_list": realTime["realTime_price_list"],
            # 实时出清费用
            "realTime_fee_list": realTime["realTime_fee_list"],
            # 实时偏差收益
            "realTime_settlement_income_list": realTime_settlement_income_list,
            # 实时总收益
            "realTime_income_list": realTime_income_list,

            # 计算综合价的费用
            "comprehensive_income_list": comprehensive_income_list,
            # 计算综合价的电量
            "comprehensive_ele_list": realTime_ele_list,
            # 综合价
            "comprehensive_price_list": comprehensive_price_list,
            # 现货增收
            "spot_incomeIncrease_list": spot_incomeIncrease_list,
        }

    @staticmethod
    def addMultiIncome(inComeList,length):

        addEnumList = [
            "run_capacity_list",
            "change_cost_ele_list",
            "change_cost_fee_list",
            "mlt_ele_list",
            "mlt_fee_list",
            "mlt_income_list",
            "dayAhead_ele_list",
            "dayAhead_fee_list",
            "dayAhead_settlement_income_list",
            "dayAhead_income_list",
            "realTime_ele_list",
            "realTime_fee_list",
            "realTime_settlement_income_list",
            "realTime_income_list",
            "comprehensive_income_list",
            "comprehensive_ele_list",
            "spot_incomeIncrease_list",
        ]
        addEnumDict = {}

        for e in addEnumList:
            addEnumDict[e] = []

        for income in inComeList:
            for e in addEnumList:
                addEnumDict[e].append(income[e])

        for e in addEnumList:
            addEnumDict[e] = CommonCal.conductAdd(addEnumDict[e],length=length)["sumList"]

        cost = CommonCal.spitWeightedMeanData(
            numeratorList=addEnumDict["change_cost_fee_list"],
            denominatorList=addEnumDict["change_cost_ele_list"],
            isNeedSpit=False,
            length=length
        )


        mlt = CommonCal.spitWeightedMeanData(
            numeratorList=addEnumDict["mlt_fee_list"],
            denominatorList=addEnumDict["mlt_ele_list"],
            isNeedSpit=False,
            length=length
        )


        dayAhead = CommonCal.spitWeightedMeanData(
            numeratorList=addEnumDict["dayAhead_fee_list"],
            denominatorList=addEnumDict["dayAhead_ele_list"],
            isNeedSpit=False,
            length=length
        )

        realTime = CommonCal.spitWeightedMeanData(
            numeratorList=addEnumDict["realTime_fee_list"],
            denominatorList=addEnumDict["realTime_ele_list"],
            isNeedSpit=False,
            length=length
        )

        comprehensive = CommonCal.spitWeightedMeanData(
            numeratorList=addEnumDict["comprehensive_income_list"],
            denominatorList=addEnumDict["comprehensive_ele_list"],
            isNeedSpit=False,
            length=length
        )

        # 运行容量
        addEnumDict["run_capacity_sum"] = CommonCal.getSum(addEnumDict["run_capacity_list"])

        # 变动成本
        addEnumDict["change_cost_price_list"] = cost["divideList"]
        addEnumDict["change_cost_price_sum"] = cost["divideSum"]
        addEnumDict["change_cost_fee_sum"] = cost["numeratorSum"]
        #中长期
        addEnumDict["mlt_price_list"] = mlt["divideList"]
        addEnumDict["mlt_ele_sum"] = CommonCal.getSum(addEnumDict["mlt_ele_list"])
        addEnumDict["mlt_price_sum"] = mlt["divideSum"]
        addEnumDict["mlt_fee_sum"] = mlt["numeratorSum"]
        # 中长期收益
        addEnumDict["mlt_income_sum"] = CommonCal.getSum(addEnumDict["mlt_income_list"])
        #日前
        addEnumDict["dayAhead_price_list"] = dayAhead["divideList"]
        addEnumDict["dayAhead_ele_sum"] = CommonCal.getSum(addEnumDict["dayAhead_ele_list"])
        addEnumDict["dayAhead_price_sum"] = dayAhead["divideSum"]
        addEnumDict["dayAhead_fee_sum"] = dayAhead["numeratorSum"]
        addEnumDict["dayAhead_settlement_income_sum"] = CommonCal.getSum(addEnumDict["dayAhead_settlement_income_list"])
        addEnumDict["dayAhead_income_sum"] = CommonCal.getSum(addEnumDict["dayAhead_income_list"])

        #实时
        addEnumDict["realTime_price_list"] = realTime["divideList"]
        addEnumDict["realTime_ele_sum"] = CommonCal.getSum(addEnumDict["realTime_ele_list"])
        addEnumDict["realTime_price_sum"] = realTime["divideSum"]
        addEnumDict["realTime_fee_sum"] = realTime["numeratorSum"]
        addEnumDict["realTime_settlement_income_sum"] = CommonCal.getSum(addEnumDict["realTime_settlement_income_list"])
        addEnumDict["realTime_income_sum"] = CommonCal.getSum(addEnumDict["realTime_income_list"])

        #综合
        addEnumDict["comprehensive_price_list"] = comprehensive["divideList"]
        addEnumDict["comprehensive_price_sum"] = comprehensive["divideSum"]
        addEnumDict["comprehensive_ele_sum"] = CommonCal.getSum(addEnumDict["comprehensive_ele_list"])
        addEnumDict["spot_incomeIncrease_sum"] = CommonCal.getSum(addEnumDict["spot_incomeIncrease_list"])

        return {
            # 运行容量
            "run_capacity_list": addEnumDict["run_capacity_list"],
            "run_capacity_sum": addEnumDict["run_capacity_sum"],

            # 变动成本需要的电量
            "change_cost_ele_list": addEnumDict["change_cost_ele_list"],
            # 变动成本
            "change_cost_price_list": addEnumDict["change_cost_price_list"],
            "change_cost_price_sum": addEnumDict["change_cost_price_sum"],
            # 变动成本费用
            "change_cost_fee_list": addEnumDict["change_cost_fee_list"],
            "change_cost_fee_sum": addEnumDict["change_cost_price_sum"],

            # 中长期电量
            "mlt_ele_list": addEnumDict["mlt_ele_list"],
            "mlt_ele_sum": addEnumDict["mlt_ele_sum"],
            # 中长期均价
            "mlt_price_list": addEnumDict["mlt_price_list"],
            "mlt_price_sum": addEnumDict["mlt_price_sum"],
            # 中长期费用
            "mlt_fee_list": addEnumDict["mlt_fee_list"],
            "mlt_fee_sum": addEnumDict["mlt_fee_sum"],
            # 中长期收益
            "mlt_income_list": addEnumDict["mlt_income_list"],
            "mlt_income_sum": addEnumDict["mlt_income_sum"],

            # 日前出清电量
            "dayAhead_ele_list": addEnumDict["dayAhead_ele_list"],
            "dayAhead_ele_sum": addEnumDict["dayAhead_ele_sum"],
            # 日前出清均价
            "dayAhead_price_list": addEnumDict["dayAhead_price_list"],
            "dayAhead_price_sum": addEnumDict["dayAhead_price_sum"],
            # 日前出清费用
            "dayAhead_fee_list": addEnumDict["dayAhead_fee_list"],
            "dayAhead_fee_sum": addEnumDict["dayAhead_fee_sum"],
            # 日前偏差收益
            "dayAhead_settlement_income_list": addEnumDict["dayAhead_settlement_income_list"],
            "dayAhead_settlement_income_sum": addEnumDict["dayAhead_settlement_income_sum"],
            # 日前总收益
            "dayAhead_income_list": addEnumDict["dayAhead_income_list"],
            "dayAhead_income_sum": addEnumDict["dayAhead_income_sum"],

            # 实时出清电量
            "realTime_ele_list": addEnumDict["realTime_ele_list"],
            "realTime_ele_sum": addEnumDict["realTime_ele_sum"],
            # 实时出清均价
            "realTime_price_list": addEnumDict["realTime_price_list"],
            "realTime_price_sum": addEnumDict["realTime_price_sum"],
            # 实时出清费用
            "realTime_fee_list": addEnumDict["realTime_fee_list"],
            "realTime_fee_sum": addEnumDict["realTime_fee_sum"],
            # 实时偏差收益
            "realTime_settlement_income_list": addEnumDict["realTime_settlement_income_list"],
            "realTime_settlement_income_sum": addEnumDict["realTime_settlement_income_sum"],
            # 实时总收益
            "realTime_income_list": addEnumDict["realTime_income_list"],
            "realTime_income_sum": addEnumDict["realTime_income_sum"],

            # 计算综合价的费用
            "comprehensive_income_list": addEnumDict['comprehensive_income_list'],
            # 计算综合价的电量
            "comprehensive_ele_list": addEnumDict["comprehensive_ele_list"],
            "comprehensive_ele_sum": addEnumDict["comprehensive_ele_sum"],
            # 综合价
            "comprehensive_price_list": addEnumDict["comprehensive_price_list"],
            "comprehensive_price_sum": addEnumDict["comprehensive_price_sum"],
            # 现货增收
            "spot_incomeIncrease_list": addEnumDict["spot_incomeIncrease_list"],
            "spot_incomeIncrease_sum": addEnumDict["spot_incomeIncrease_sum"],
        }

    @staticmethod
    def execEntry(dataList,length=96):

        mxDataList = []
        otherDataList = []

        for data in dataList:
            if data["province_id"] == "15":
                mxDataList.append(data)
            else:
                otherDataList.append(data)

        mxRes = ProInLogic.MXInComeProcess(mxDataList,length)

        otherRes = ProInLogic.otherInComeProcess(otherDataList,length)
        return ProInLogic.addMultiIncome([mxRes,otherRes],length=length)

if __name__ == '__main__':


    a = CommonCal.spitWeightedMeanData(
        numeratorList = [ [[1,2],[3,4]] ,[[5,6],[7,8]]],
        denominatorList = [ [[9,10],[11,2]] ],
        length=2)
    print(a)

