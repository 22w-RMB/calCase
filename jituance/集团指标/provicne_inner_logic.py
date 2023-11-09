import copy

from jituance.集团指标.common_calculation import CommonCal


class ProInLogic:

    @staticmethod
    def getFrontPageRunCapacity(dataList):

        if dataList == None:
            return 0

        run_capacity_sum = 0

        for data in dataList:

            unit_run_capacity_sum = CommonCal.getSum(data["run_capacity"])
            if unit_run_capacity_sum == None:
                continue
            run_capacity_sum = run_capacity_sum + unit_run_capacity_sum

        return run_capacity_sum/960

    # 其他省份中长期计算
    @staticmethod
    def otherProvinceMlt(data, length=96):

        # 计算中长期费用
        mlt_res = CommonCal.weightedMean(
            numeratorList=[data["mlt_ele"], data["mlt_price"]],
            denominatorList=[data["mlt_ele"]],
            length=length
        )
        # 中长期电价-变动成本，中长期为空时，结果为空，变动成本为空时，变动成本当0计算
        mlt_diff_price = CommonCal.conductSubtract(data["mlt_price"], data["change_cost"], B_NoneToZero=True)["diff"]
        # 计算中长期收益
        mlt_income_res = CommonCal.weightedMean(
            numeratorList=[data["mlt_ele"], mlt_diff_price],
            denominatorList=[data["mlt_ele"]],
            length=length
        )
        # 中长期电量
        mlt_ele_list = copy.deepcopy(data["mlt_ele"])
        # 中长期均价
        mlt_price_list = mlt_res["divideList"]
        # 中长期费用
        mlt_fee_list = mlt_res["numeratorList"]
        # 中长期收益
        mlt_income_list = mlt_income_res["numeratorList"]

        data["mlt_ele_list"] = mlt_ele_list
        data["mlt_fee_list"] = mlt_fee_list
        data["mlt_income_list"] = mlt_income_list

    # 其他省份变动成本计算
    @staticmethod
    def otherProvinceCost(data, length=96):
        change_cost_ele_list = [None for i in range(0,length)]
        change_cost_fee_list = [None for i in range(0,length)]
        if data["business_type"] == "1":
            # 变动成本计算
            cost = CommonCal.weightedMean(
                numeratorList=[data["mlt_ele"], data["change_cost"]],
                denominatorList=[data["mlt_ele"]],
                length=length
            )
            change_cost_ele_list = copy.deepcopy(data["mlt_ele"])
            change_cost_fee_list = cost["numeratorList"]
        data["change_cost_ele_list"] = change_cost_ele_list
        data["change_cost_fee_list"] = change_cost_fee_list

    # 其他省份日前数据计算
    @staticmethod
    def otherProvinceDayAhead(data, length=96):
        # 计算日前费用
        dayAhead_res = CommonCal.weightedMean(
            numeratorList=[data["day_ahead_ele"], data["day_ahead_price"]],
            denominatorList=[data["day_ahead_ele"]],
            length=length
        )
        # 日前电量
        dayAhead_ele_list = copy.deepcopy(data["day_ahead_ele"])
        # 日前均价
        dayAhead_price_list = dayAhead_res["divideList"]
        # 日前费用
        dayAhead_fee_list = dayAhead_res["numeratorList"]

        # 计算日前偏差电量，日前-中长期，任意一个为空，则结果为空
        dayAhead_diffEle_cal_res = CommonCal.conductSubtract(data["day_ahead_ele"], data["mlt_ele"])
        # 计算日前电价-变动成本，日前电价为空时，结果为空，变动成本为空时，变动成本当0计算
        dayAhead_diffPrice_cal_res = \
        CommonCal.conductSubtract(data["day_ahead_price"], data["change_cost"], B_NoneToZero=True)["diff"]

        # 日前偏差电量
        dayAhead_diff_ele_list = dayAhead_diffEle_cal_res["diff"]
        # 日前正偏差电量
        dayAhead_positive_ele_list = dayAhead_diffEle_cal_res["positive_diff"]
        # 日前负偏差电量
        dayAhead_negative_ele_list = dayAhead_diffEle_cal_res["negative_diff"]


        dayAhead_diff_fee_res = CommonCal.weightedMean(
            numeratorList=[dayAhead_diff_ele_list, dayAhead_diffPrice_cal_res],
            denominatorList=[dayAhead_diff_ele_list],
            length=length
        )
        dayAhead_positive_diff_res = CommonCal.weightedMean(
            numeratorList=[dayAhead_positive_ele_list, dayAhead_diffPrice_cal_res],
            denominatorList=[dayAhead_positive_ele_list],
            length=length
        )
        dayAhead_negative_diff_res = CommonCal.weightedMean(
            numeratorList=[dayAhead_negative_ele_list, dayAhead_diffPrice_cal_res],
            denominatorList=[dayAhead_negative_ele_list],
            length=length
        )


        # 日前正偏差收益
        dayAhead_positive_diff_income_list = dayAhead_positive_diff_res["numeratorList"]
        # 日前负偏差收益
        dayAhead_negative_diff_income_list = dayAhead_negative_diff_res["numeratorList"]
        # 日前结算收益
        dayAhead_settlement_income_list = CommonCal.conductAdd(
            [dayAhead_positive_diff_income_list, dayAhead_negative_diff_income_list])
        # 日前收益
        dayAhead_income_list = CommonCal.conductAdd([dayAhead_settlement_income_list, data["mlt_income_list"]])

        # 日前正偏差电量*日前出清电价计算
        dayAhead_positive_diffeleMulPrice_res = CommonCal.weightedMean(
            numeratorList=[dayAhead_positive_ele_list, data["day_ahead_price"]],
            denominatorList=[dayAhead_positive_ele_list],
            length=length
        )
        # 日前负偏差电量*日前出清电价计算
        dayAhead_negative_diffeleMulPrice_res = CommonCal.weightedMean(
            numeratorList=[dayAhead_negative_ele_list, data["day_ahead_price"]],
            denominatorList=[dayAhead_negative_ele_list],
            length=length
        )

        # 日前正偏差电量*日前出清电价
        dayAhead_positive_diff_fee_list = dayAhead_positive_diffeleMulPrice_res["numeratorList"]
        # 日前负偏差电量*日前出清电价
        dayAhead_negative_diff_fee_list = dayAhead_negative_diffeleMulPrice_res["numeratorList"]

        data["dayAhead_ele_list"] = dayAhead_ele_list
        data["dayAhead_fee_list"] = dayAhead_fee_list
        data["dayAhead_positive_ele_list"] = dayAhead_positive_ele_list
        data["dayAhead_negative_ele_list"] = dayAhead_negative_ele_list
        data["dayAhead_settlement_income_list"] = dayAhead_settlement_income_list
        data["dayAhead_income_list"] = dayAhead_income_list

        data["dayAhead_positive_diff_fee_list"] = dayAhead_positive_diff_fee_list
        data["dayAhead_negative_diff_fee_list"] = dayAhead_negative_diff_fee_list

    # 其他省份实时数据计算
    @staticmethod
    def otherProvinceRealTime(data, length=96):
        # 计算实时费用
        realTime_res = CommonCal.weightedMean(
            numeratorList=[data["real_time_ele"], data["real_time_price"]],
            denominatorList=[data["real_time_ele"]],
            length=length
        )
        # 实时电量
        realTime_ele_list = copy.deepcopy(data["real_time_ele"])
        # 实时均价
        realTime_price_list = realTime_res["divideList"]
        # 实时费用
        realTime_fee_list = realTime_res["numeratorList"]

        # 计算实时偏差电量，实时-日前，任意一个为空，则结果为空
        realTime_diffEle_cal_res = CommonCal.conductSubtract(data["real_time_ele"], data["day_ahead_ele"])
        # 计算实时电价-变动成本，实时电价为空时，结果为空，变动成本为空时，变动成本当0计算
        realTime_diffPrice_cal_res = \
        CommonCal.conductSubtract(data["real_time_price"], data["change_cost"], B_NoneToZero=True)["diff"]

        # 实时偏差电量
        realTime_diff_ele_list = realTime_diffEle_cal_res["diff"]
        # 实时正偏差电量
        realTime_positive_ele_list = realTime_diffEle_cal_res["positive_diff"]
        # 实时负偏差电量
        realTime_negative_ele_list = realTime_diffEle_cal_res["negative_diff"]

        realTime_diff_fee_res = CommonCal.weightedMean(
            numeratorList=[realTime_diff_ele_list, realTime_diffPrice_cal_res],
            denominatorList=[realTime_diff_ele_list],
            length=length
        )
        realTime_positive_diff_res = CommonCal.weightedMean(
            numeratorList=[realTime_positive_ele_list, realTime_diffPrice_cal_res],
            denominatorList=[realTime_positive_ele_list],
            length=length
        )
        realTime_negative_diff_res = CommonCal.weightedMean(
            numeratorList=[realTime_negative_ele_list, realTime_diffPrice_cal_res],
            denominatorList=[realTime_negative_ele_list],
            length=length
        )


        # 实时正偏差收益
        realTime_positive_diff_income_list = realTime_positive_diff_res["numeratorList"]
        # 实时负偏差收益
        realTime_negative_diff_income_list = realTime_negative_diff_res["numeratorList"]
        # 实时结算收益
        realTime_settlement_income_list = CommonCal.conductAdd(
            [realTime_positive_diff_income_list, realTime_negative_diff_income_list])
        # 实时收益
        realTime_income_list = CommonCal.conductAdd([realTime_settlement_income_list, data["dayAhead_income_list"]])

        # 实时偏差电量*实时出清电价计算
        realTime_positive_diffeleMulPrice_res = CommonCal.weightedMean(
            numeratorList=[realTime_positive_ele_list, data["real_time_price"]],
            denominatorList=[realTime_positive_ele_list],
            length=length
        )
        realTime_negative_diffeleMulPrice_res = CommonCal.weightedMean(
            numeratorList=[realTime_negative_ele_list, data["real_time_price"]],
            denominatorList=[realTime_negative_ele_list],
            length=length
        )

        # 实时正偏差电量*实时出清电价
        realTime_positive_diff_fee_list = realTime_positive_diffeleMulPrice_res["numeratorList"]
        # 实时负偏差电量*实时出清电价
        realTime_negative_diff_fee_list = realTime_negative_diffeleMulPrice_res["numeratorList"]


        data["realTime_ele_list"] = realTime_ele_list
        data["realTime_fee_list"] = realTime_fee_list
        data["realTime_positive_ele_list"] = realTime_positive_ele_list
        data["realTime_negative_ele_list"] = realTime_negative_ele_list
        data["realTime_settlement_income_list"] = realTime_settlement_income_list
        data["realTime_income_list"] = realTime_income_list

        data["realTime_positive_diff_fee_list"] = realTime_positive_diff_fee_list
        data["realTime_negative_diff_fee_list"] = realTime_negative_diff_fee_list

    # 其他省份综合电价时数据计算
    @staticmethod
    def otherProvinceComprehensive(data, length=96):
        # 计算综合价的费用
        comprehensive_income_list = CommonCal.conductAdd(
            [
                data["dayAhead_positive_diff_fee_list"],
                data["dayAhead_negative_diff_fee_list"],
                data["realTime_positive_diff_fee_list"],
                data["realTime_negative_diff_fee_list"],
                data["mlt_fee_list"],
            ]
        )
        # 计算综合价的费用的实时出清电量
        comprehensive_ele_list = copy.deepcopy(data["real_time_ele"])

        # 计算综合价的费用/实时出清电量
        comprehensive = CommonCal.conductDivide(
            listA=comprehensive_income_list,
            listB=comprehensive_ele_list,
            length=length
        )
        # 综合电价
        comprehensive_price_list = comprehensive["divideList"]

        # 现货增收
        spot_incomeIncrease_list = CommonCal.conductAdd(
            [data["dayAhead_settlement_income_list"], data["realTime_settlement_income_list"]]
        )

        data["comprehensive_ele_list"] = comprehensive_ele_list
        data["comprehensive_income_list"] = comprehensive_income_list
        data["spot_incomeIncrease_list"] = spot_incomeIncrease_list

    @staticmethod
    def otherProvinceCal(data, length=96):

        ProInLogic.otherProvinceCost(data,length)
        ProInLogic.otherProvinceMlt(data,length)
        ProInLogic.otherProvinceDayAhead(data,length)
        ProInLogic.otherProvinceRealTime(data,length)
        ProInLogic.otherProvinceComprehensive(data,length)

    # 蒙西中长期计算
    @staticmethod
    def MXProvinceMlt(data, length=96):

        # 计算中长期费用
        mlt_res = CommonCal.weightedMean(
            numeratorList=[data["mlt_ele"], data["mlt_price"]],
            denominatorList=[data["mlt_ele"]],
            length=length
        )

        # 中长期电量
        mlt_ele_list = copy.deepcopy(data["mlt_ele"])
        # 中长期均价
        mlt_price_list = mlt_res["divideList"]
        # 中长期费用
        mlt_fee_list = mlt_res["numeratorList"]

        data["mlt_ele_list"] = mlt_ele_list
        data["mlt_fee_list"] = mlt_fee_list

    # 蒙西变动成本计算
    @staticmethod
    def MXProvinceCost(data, length=96):
        change_cost_ele_list = [None for i in range(0, length)]
        change_cost_fee_list = [None for i in range(0, length)]
        if data["business_type"] == "1":
            # 变动成本计算
            cost = CommonCal.weightedMean(
                numeratorList=[data["mlt_ele"], data["change_cost"]],
                denominatorList=[data["mlt_ele"]],
                length=length
            )
            change_cost_ele_list = copy.deepcopy(data["mlt_ele"])
            change_cost_fee_list = cost["numeratorList"]
        data["change_cost_ele_list"] = change_cost_ele_list
        data["change_cost_fee_list"] = change_cost_fee_list

    # 蒙西日前数据计算
    @staticmethod
    def MXProvinceDayAhead(data, length=96):

        data["dayAhead_ele_list"] = [None for i in range(0,length)]
        data["dayAhead_fee_list"] = [None for i in range(0,length)]
        data["dayAhead_positive_ele_list"] = [None for i in range(0,length)]
        data["dayAhead_negative_ele_list"] = [None for i in range(0,length)]
        data["dayAhead_settlement_income_list"] = [None for i in range(0,length)]
        data["dayAhead_income_list"] = [None for i in range(0,length)]

        data["dayAhead_positive_diff_fee_list"] = [None for i in range(0,length)]
        data["dayAhead_negative_diff_fee_list"] = [None for i in range(0,length)]

    # 蒙西实时数据计算
    @staticmethod
    def MXProvinceRealTime(data, length=96):
        # 计算实时费用
        realTime_res = CommonCal.weightedMean(
            numeratorList=[data["real_time_ele"], data["real_time_price"]],
            denominatorList=[data["real_time_ele"]],
            length=length
        )
        # 实时电量
        realTime_ele_list = copy.deepcopy(data["real_time_ele"])
        # 实时均价
        realTime_price_list = realTime_res["divideList"]
        # 实时费用
        realTime_fee_list = realTime_res["numeratorList"]

        # 计算实时偏差电量，实时-中长期，任意一个为空，则结果为空
        realTime_diffEle_cal_res = CommonCal.conductSubtract(data["real_time_ele"], data["mlt_ele"])
        # 计算实时电价-变动成本，实时电价为空时，结果为空，变动成本为空时，变动成本当0计算
        realTime_diffPrice_cal_res = \
            CommonCal.conductSubtract(data["real_time_price"], data["change_cost"], B_NoneToZero=True)["diff"]

        # 实时偏差电量
        realTime_diff_ele_list = realTime_diffEle_cal_res["diff"]
        # 实时正偏差电量
        realTime_positive_ele_list = realTime_diffEle_cal_res["positive_diff"]
        # 实时负偏差电量
        realTime_negative_ele_list = realTime_diffEle_cal_res["negative_diff"]

        realTime_diff_fee_res = CommonCal.weightedMean(
            numeratorList=[realTime_diff_ele_list, realTime_diffPrice_cal_res],
            denominatorList=[realTime_diff_ele_list],
            length=length
        )
        realTime_positive_diff_res = CommonCal.weightedMean(
            numeratorList=[realTime_positive_ele_list, realTime_diffPrice_cal_res],
            denominatorList=[realTime_positive_ele_list],
            length=length
        )
        realTime_negative_diff_res = CommonCal.weightedMean(
            numeratorList=[realTime_negative_ele_list, realTime_diffPrice_cal_res],
            denominatorList=[realTime_negative_ele_list],
            length=length
        )


        # 实时正偏差收益
        realTime_positive_diff_income_list = realTime_positive_diff_res["numeratorList"]
        # 实时负偏差收益
        realTime_negative_diff_income_list = realTime_negative_diff_res["numeratorList"]
        # 实时结算收益
        realTime_settlement_income_list = CommonCal.conductAdd(
            [realTime_positive_diff_income_list, realTime_negative_diff_income_list])


        # 机组ntn时刻的中长期合同价-tn时刻的全省统一出清价
        mlt_diff_clearing_price_list = \
            CommonCal.conductSubtract(data["mlt_price"], data["clearing_price"], B_NoneToZero=True)["diff"]

        # 机组ntn时刻的中长期电量*机组ntn时刻的中长期合同价-tn时刻的全省统一出清价
        mlt_diff_clearing_cal_res = CommonCal.weightedMean(
            numeratorList=[data["mlt_ele"], mlt_diff_clearing_price_list],
            denominatorList=[data["mlt_ele"]],
            length=length
        )


        mlt_diff_clearing_fee_list = mlt_diff_clearing_cal_res["numeratorList"]

        # 机组ntn时刻的中长期电量*机组ntn时刻的中长期合同价-tn时刻的全省统一出清价+机组ntn时刻的实时出清电量*机组ntn时刻的实时出清电价
        # 即计算综合电价所需的费用
        temp_income_list = CommonCal.conductAdd([mlt_diff_clearing_fee_list,realTime_fee_list])

        # 实时收益
        realTime_income_list = \
            CommonCal.conductSubtract(temp_income_list, data["change_cost_fee_list"], B_NoneToZero=True)["diff"]


        # 中长期收益
        mlt_income_list = \
            CommonCal.conductSubtract(realTime_income_list, realTime_settlement_income_list, B_NoneToZero=True)["diff"]

        data["mlt_income_list"] = mlt_income_list

        data["realTime_ele_list"] = realTime_ele_list
        data["realTime_fee_list"] = realTime_fee_list
        data["realTime_positive_ele_list"] = realTime_positive_ele_list
        data["realTime_negative_ele_list"] = realTime_negative_ele_list
        data["realTime_settlement_income_list"] = realTime_settlement_income_list
        data["realTime_income_list"] = realTime_income_list

        data["temp_income_list"] = temp_income_list


    # 蒙西综合电价时数据计算
    @staticmethod
    def MXProvinceComprehensive(data, length=96):
        # 计算综合价的费用
        comprehensive_income_list = copy.deepcopy(data["temp_income_list"])
        # 计算综合价的费用的实时出清电量
        comprehensive_ele_list = copy.deepcopy(data["real_time_ele"])

        # 计算综合价的费用/实时出清电量
        comprehensive = CommonCal.conductDivide(
            listA=comprehensive_income_list,
            listB=comprehensive_ele_list,
            length=length
        )
        # 综合电价
        comprehensive_price_list = comprehensive["divideList"]

        # 现货增收
        spot_incomeIncrease_list = copy.deepcopy(data["realTime_settlement_income_list"])

        data["comprehensive_ele_list"] = comprehensive_ele_list
        data["comprehensive_income_list"] = comprehensive_income_list
        data["spot_incomeIncrease_list"] = spot_incomeIncrease_list

    @staticmethod
    def MxProvinceCal(data, length=96):
        ProInLogic.MXProvinceCost(data,length)
        ProInLogic.MXProvinceMlt(data,length)
        ProInLogic.MXProvinceDayAhead(data,length)
        ProInLogic.MXProvinceRealTime(data,length)
        ProInLogic.MXProvinceComprehensive(data,length)


    @staticmethod
    def amalgamateDataList(dataList, length=96):

        fieldNameList = [
            "change_cost_ele_list",
            "change_cost_fee_list",
            "mlt_ele_list",
            "mlt_fee_list",
            "mlt_income_list",
            "dayAhead_ele_list",
            "dayAhead_fee_list",
            "dayAhead_positive_ele_list",
            "dayAhead_negative_ele_list",
            "dayAhead_settlement_income_list",
            "dayAhead_income_list",
            "realTime_ele_list",
            "realTime_fee_list",
            "realTime_positive_ele_list",
            "realTime_negative_ele_list",
            "realTime_settlement_income_list",
            "realTime_income_list",
            "comprehensive_ele_list",
            "comprehensive_income_list",
            "spot_incomeIncrease_list",
        ]

        fieldDataDict = CommonCal.conductAddMulField(fieldNameList,dataList)


        # 变动成本计算
        cost_res = CommonCal.conductDivide(
            listA=fieldDataDict["change_cost_fee_list"],
            listB=fieldDataDict["change_cost_ele_list"],
            length=length
        )
        change_cost_price_list = cost_res["divideList"]
        change_cost_price_sum = cost_res["divideSum"]
        change_cost_fee_sum = cost_res["numeratorSum"]


        # 中长期计算
        mlt_res = CommonCal.conductDivide(
            listA=fieldDataDict["mlt_fee_list"],
            listB=fieldDataDict["mlt_ele_list"],
            length=length
        )
        mlt_price_list = mlt_res["divideList"]
        mlt_price_sum = mlt_res["divideSum"]
        mlt_fee_sum = mlt_res["numeratorSum"]


        # 日前计算
        dayAhead_res = CommonCal.conductDivide(
            listA=fieldDataDict["dayAhead_fee_list"],
            listB=fieldDataDict["dayAhead_ele_list"],
            length=length
        )
        dayAhead_price_list = dayAhead_res["divideList"]
        dayAhead_price_sum = dayAhead_res["divideSum"]
        dayAhead_fee_sum = dayAhead_res["numeratorSum"]


        # 实时计算
        realTime_res = CommonCal.conductDivide(
            listA=fieldDataDict["realTime_fee_list"],
            listB=fieldDataDict["realTime_ele_list"],
            length=length
        )
        realTime_price_list = realTime_res["divideList"]
        realTime_price_sum = realTime_res["divideSum"]
        realTime_fee_sum = realTime_res["numeratorSum"]


        # 综合收入计算
        comprehensive_res = CommonCal.conductDivide(
            listA=fieldDataDict["comprehensive_income_list"],
            listB=fieldDataDict["comprehensive_ele_list"],
            length=length
        )
        comprehensive_price_list = comprehensive_res["divideList"]
        comprehensive_price_sum = comprehensive_res["divideSum"]
        comprehensive_fee_sum = comprehensive_res["numeratorSum"]

        # 中长期收益
        mlt_income_sum = CommonCal.getSum(fieldDataDict["mlt_income_list"])
        # 日前收益
        dayAhead_income_sum = CommonCal.getSum(fieldDataDict["dayAhead_income_list"])
        # 日前偏差收益
        dayAhead_settlement_income = CommonCal.getSum(fieldDataDict["dayAhead_settlement_income_list"])
        # 实时收益
        realTime_income_sum= CommonCal.getSum(fieldDataDict["realTime_income_list"])
        # 实时偏差收益
        realTime_settlement_income = CommonCal.getSum(fieldDataDict["realTime_settlement_income_list"])
        # 现货增收合计
        spot_incomeIncrease_sum = CommonCal.getSum(fieldDataDict["spot_incomeIncrease_list"])
        
        mlt_ele_sum = CommonCal.getSum(fieldDataDict["mlt_ele_list"])
        dayAhead_ele_sum = CommonCal.getSum(fieldDataDict["dayAhead_ele_list"])
        realTime_ele_sum = CommonCal.getSum(fieldDataDict["realTime_ele_list"])

        # fieldDataDict["change_cost_price_list"] = change_cost_price_list
        # fieldDataDict["mlt_price_list"] = mlt_price_list
        # fieldDataDict["dayAhead_price_list"] = dayAhead_price_list
        # fieldDataDict["realTime_price_list"] = realTime_price_list
        # fieldDataDict["comprehensive_price_list"] = comprehensive_price_list


        return {
                "change_cost_ele_list": fieldDataDict["change_cost_ele_list"],
                "change_cost_price_list": change_cost_price_list,
                "change_cost_fee_list": fieldDataDict["change_cost_ele_list"],
                "mlt_ele_list": fieldDataDict["mlt_ele_list"],
                "mlt_price_list": mlt_price_list,
                "mlt_fee_list": fieldDataDict["mlt_fee_list"],
                "mlt_income_list": fieldDataDict["mlt_income_list"],
                "dayAhead_ele_list": fieldDataDict["dayAhead_ele_list"],
                "dayAhead_price_list": dayAhead_price_list,
                "dayAhead_fee_list": fieldDataDict["dayAhead_fee_list"],
                "dayAhead_settlement_income_list": fieldDataDict["dayAhead_settlement_income_list"],
                "dayAhead_income_list": fieldDataDict["dayAhead_income_list"],
                "realTime_ele_list": fieldDataDict["realTime_ele_list"],
                "realTime_price_list": realTime_price_list,
                "realTime_fee_list": fieldDataDict["realTime_fee_list"],
                "realTime_settlement_income_list": fieldDataDict["realTime_settlement_income_list"],
                "realTime_income_list": fieldDataDict["realTime_income_list"],
                "comprehensive_ele_list": fieldDataDict["comprehensive_ele_list"],
                "comprehensive_price_list": comprehensive_price_list,
                "comprehensive_income_list": fieldDataDict["comprehensive_income_list"],
                "spot_incomeIncrease_list": fieldDataDict["spot_incomeIncrease_list"],

                "change_cost_price_sum" :  change_cost_price_sum,
                "change_cost_fee_sum" :  change_cost_fee_sum,

                "mlt_ele_sum": mlt_ele_sum,
                "mlt_price_sum" :  mlt_price_sum,
                "mlt_fee_sum" :  mlt_fee_sum,

                "dayAhead_ele_sum": dayAhead_ele_sum,
                "dayAhead_price_sum" :  dayAhead_price_sum,
                "dayAhead_fee_sum" :  dayAhead_fee_sum,

                "realTime_ele_sum": realTime_ele_sum,
                "realTime_price_sum" :  realTime_price_sum,
                "realTime_fee_sum" :  realTime_fee_sum,
                "comprehensive_price_sum" :  comprehensive_price_sum,
                "comprehensive_fee_sum" :  comprehensive_fee_sum,
                "mlt_income_sum" :  mlt_income_sum,
                "dayAhead_income_sum" :  dayAhead_income_sum,
                "dayAhead_settlement_income" :  dayAhead_settlement_income,
                "realTime_income_sum" :  realTime_income_sum,
                "realTime_settlement_income" :  realTime_settlement_income,
                "spot_incomeIncrease_sum" :  spot_incomeIncrease_sum,
        }


    # 针对山西电厂的特殊处理
    @staticmethod
    def ShanxiSpecialHandling(data):

        # 左权电厂
        list1 = [ "15ef155062154794a525f07ceedc1391","687a146555f84d56ad0f732c676500c2"]
        list1Proportion = 0.9331

        # 榆社电厂
        list2 = [ "18bbb5d806144438a21a7b7bac26490b","d0e75f2bec85454aa58a908437f27758"]
        list2Proportion = 0.9

        proportion = 1

        if data["org_id"] in list1:
            proportion = list1Proportion
        if data["org_id"] in list2:
            proportion = list2Proportion

        if proportion == 1:
            return

        keyNameList = [
            "mlt_ele",
            "day_ahead_ele",
            "real_time_ele",
        ]

        for keyName in keyNameList:
            if keyName not in data.keys():
                continue

            if isinstance(data[keyName],list) == False:
                continue

            for i in range(0,len(data[keyName])):
                if data[keyName][i] == None:
                    continue
                data[keyName][i] = data[keyName][i]*proportion

    @staticmethod
    def execEntry(dataList, length=96):


        proInFieldEnum = {
                         "change_cost_ele_list" : "计算变动成本用的电量96点数据",
                "change_cost_price_list" : "变动成本96点数据",
                "change_cost_fee_list" : "计算变动成本用的费用96点数据",
                "mlt_ele_list" : "中长期电量96点数据",
                "mlt_price_list" : "中长期电价96点数据",
                "mlt_fee_list" : "中长期费用96点数据",
                "mlt_income_list" : "中长期收益96点数据",
                "dayAhead_ele_list" :  "日前电量96点数据",
                "dayAhead_price_list" : "日前电价96点数据",
                "dayAhead_fee_list" : "日前费用96点数据",
                "dayAhead_settlement_income_list" : "日前偏差收益96点数据",
                "dayAhead_income_list" : "日前收益96点数据",
                "realTime_ele_list" : "实时电量96点数据",
                "realTime_price_list" : "实时电价96点数据",
                "realTime_fee_list" : "实时费用96点数据",
                "realTime_settlement_income_list" : "实时偏差收益96点数据",
                "realTime_income_list" : "实时收益96点数据",
                "comprehensive_ele_list" : "计算综合电价用的电量96点数据",
                "comprehensive_price_list" : "综合电价96点数据",
                "comprehensive_income_list" : "计算综合电价用的费用96点数据",
                "spot_incomeIncrease_list" : "现货增收96点数据",

                "change_cost_price_sum" : "变动成本",
                "change_cost_fee_sum" : "总成本",

                "mlt_ele_sum" : "中长期总电量",
                "mlt_price_sum" : "中长期均价",
                "mlt_fee_sum" : "中长期总费用",

                "dayAhead_ele_sum" :  "日前总电量",
                "dayAhead_price_sum" : "日前总均价",
                "dayAhead_fee_sum" : "日前总费用",

                "realTime_ele_sum" :  "实时总电量",
                "realTime_price_sum" : "实时均价",
                "realTime_fee_sum" : "实时总费用",
                "comprehensive_price_sum" : "综合电价",
                "comprehensive_fee_sum" : "计算综合电价用的总费用",
                "mlt_income_sum" : "中长期总收益",
                "dayAhead_income_sum" : "日前总收益",
                "dayAhead_settlement_income": "日前偏差总收益",
                "realTime_income_sum" : "实时总收益",
                "realTime_settlement_income" : "实时偏差总收益",
                "spot_incomeIncrease_sum" : "现货增收",

        }

        for data in dataList:
            if data["province_id"] == "14":
                ProInLogic.ShanxiSpecialHandling(data)

            if data["province_id"] == "15":
                ProInLogic.MxProvinceCal(data, length)
            else:
                ProInLogic.otherProvinceCal(data, length)

        res = ProInLogic.amalgamateDataList(dataList, length=length)


        for r in res:
            print(proInFieldEnum[r]," ：",res[r])
        # return d


if __name__ == '__main__':


    x = ["a","ab"]
    d = copy.deepcopy(x)
    print(d )
