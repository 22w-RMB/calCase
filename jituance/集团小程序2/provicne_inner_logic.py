import copy

from jituance.集团小程序2.common_calculation import CommonCal


class ProInLogic:


    @staticmethod
    def getFrontPageRunCapacity(dataList):

        run_capacity_sum = 0

        for data in dataList:

            unit_run_capacity_sum = CommonCal.getSum(data["run_capacity"])
            if unit_run_capacity_sum == None:
                continue
            run_capacity_sum = run_capacity_sum + unit_run_capacity_sum

        return run_capacity_sum/96


    @staticmethod
    def otherProvinceCal(data, length=96):

        # 变动成本计算
        cost = CommonCal.weightedMean(
            numeratorList=[data["mlt_ele"], data["change_cost"]],
            denominatorList=[data["mlt_ele"]],
            length=length
        )
        change_cost_ele_list = cost["denominatorList"]
        change_cost_fee_list = cost["numeratorList"]

        # 计算中长期费用
        mlt_res = CommonCal.weightedMean(
            numeratorList=[data["mlt_ele"], data["mlt_price"]],
            denominatorList=[data["mlt_ele"]],
            length=length
        )
        # 中长期电价-变动成本，中长期为空时，结果为空，变动成本为空时，变动成本当0计算
        mlt_diff_price = CommonCal.conductSubtract(data["mlt_price"],data["change_cost"],B_NoneToZero=True)["diff"]
        # 计算中长期收益
        mlt_income_res = CommonCal.weightedMean(
            numeratorList=[data["mlt_ele"], mlt_diff_price],
            denominatorList=[data["mlt_ele"]],
            length=length
        )
        # 中长期电量
        mlt_ele_list =  copy.deepcopy(data["mlt_ele"])
        # 中长期均价
        mlt_price_list =  mlt_res["divideList"]
        # 中长期费用
        mlt_fee_list = mlt_res["numeratorList"]

        # 中长期收益
        mlt_income_list = mlt_income_res["numeratorList"]

        # 计算日前费用
        dayAhead_res = CommonCal.weightedMean(
            numeratorList=[data["day_ahead_ele"], data["day_ahead_price"]],
            denominatorList=[data["day_ahead_ele"]],
            length=length
        )
        # 日前电量
        dayAhead_ele_list =  copy.deepcopy(data["day_ahead_ele"])
        # 日前均价
        dayAhead_price_list =  dayAhead_res["divideList"]
        # 日前费用
        dayAhead_fee_list = dayAhead_res["numeratorList"]

        # 计算日前偏差电量，日前-中长期，任意一个为空，则结果为空
        dayAhead_diffEle_cal_res = CommonCal.conductSubtract(data["day_ahead_ele"],data["mlt_ele"])
        # 计算日前电价-变动成本，日前电价为空时，结果为空，变动成本为空时，变动成本当0计算
        dayAhead_diffPrice_cal_res = CommonCal.conductSubtract(data["day_ahead_price"],data["change_cost"],B_NoneToZero=True)["diff"]

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

        # 日前偏差收益
        dayAhead_diff_income_list = dayAhead_diff_fee_res["numeratorList"]
        # 日前正偏差收益
        dayAhead_positive_diff_income_list = dayAhead_positive_diff_res["numeratorList"]
        # 日前负偏差收益
        dayAhead_negative_diff_income_list = dayAhead_negative_diff_res["numeratorList"]
        # 日前结算收益
        dayAhead_settlement_income_list = CommonCal.conductAdd([dayAhead_positive_diff_income_list,dayAhead_negative_diff_income_list])
        # 日前收益
        dayAhead_income_list = CommonCal.conductAdd([dayAhead_settlement_income_list,mlt_income_list])



        # 日前偏差电量*日前出清电价计算
        dayAhead_positive_diffeleMulPrice_res = CommonCal.weightedMean(
            numeratorList=[dayAhead_positive_ele_list, data["day_ahead_price"]],
            denominatorList=[dayAhead_positive_ele_list],
            length=length
        )
        dayAhead_negative_diffeleMulPrice_res = CommonCal.weightedMean(
            numeratorList=[dayAhead_negative_ele_list, data["day_ahead_price"]],
            denominatorList=[dayAhead_negative_ele_list],
            length=length
        )

        # 日前正偏差电量*日前出清电价
        dayAhead_positive_diff_fee_list = dayAhead_positive_diffeleMulPrice_res["numeratorList"]
        # 日前负偏差电量*日前出清电价
        dayAhead_negative_diff_fee_list = dayAhead_negative_diffeleMulPrice_res["numeratorList"]

        # 计算实时费用
        realTime_res = CommonCal.weightedMean(
            numeratorList=[data["real_time_ele"], data["real_time_price"]],
            denominatorList=[data["real_time_ele"]],
            length=length
        )
        # 实时电量
        realTime_ele_list =  copy.deepcopy(data["real_time_ele"])
        # 实时均价
        realTime_price_list =  realTime_res["divideList"]
        # 实时费用
        realTime_fee_list = realTime_res["numeratorList"]

        # 计算实时偏差电量，实时-中长期，任意一个为空，则结果为空
        realTime_diffEle_cal_res = CommonCal.conductSubtract(data["real_time_ele"],data["day_ahead_ele"])
        # 计算实时电价-变动成本，实时电价为空时，结果为空，变动成本为空时，变动成本当0计算
        realTime_diffPrice_cal_res = CommonCal.conductSubtract(data["real_time_price"],data["change_cost"],B_NoneToZero=True)["diff"]

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

        # 实时偏差收益
        realTime_diff_income_list = realTime_diff_fee_res["numeratorList"]
        # 实时正偏差收益
        realTime_positive_diff_income_list = realTime_positive_diff_res["numeratorList"]
        # 实时负偏差收益
        realTime_negative_diff_income_list = realTime_negative_diff_res["numeratorList"]
        # 实时结算收益
        realTime_settlement_income_list = CommonCal.conductAdd([realTime_positive_diff_income_list,realTime_negative_diff_income_list])
        # 实时收益
        realTime_income_list = CommonCal.conductAdd([realTime_settlement_income_list,dayAhead_income_list])

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


        # 计算综合价的费用
        comprehensive_income_list = CommonCal.conductAdd(
            [
                dayAhead_positive_diff_fee_list,
                dayAhead_negative_diff_fee_list,
                realTime_positive_diff_fee_list,
                realTime_negative_diff_fee_list,
                mlt_fee_list,
            ]
        )
        # 计算综合价的费用的实时出清电量
        comprehensive_ele_list = copy.deepcopy(data["real_time_ele"])

        # 计算综合价的费用/实时出清电量
        comprehensive = CommonCal.conductDivide(
            listA=[comprehensive_income_list],
            listB=[comprehensive_ele_list],
            length=length
        )
        # 综合电价
        comprehensive_price_list = comprehensive["divideList"]

        # 现货增收
        spot_incomeIncrease_list = CommonCal.conductAdd(
            [dayAhead_settlement_income_list, realTime_settlement_income_list]
        )

        data["change_cost_ele_list"] = change_cost_ele_list
        data["change_cost_fee_list"] = change_cost_fee_list
        data["mlt_ele_list"] = mlt_ele_list
        data["mlt_fee_list"] = mlt_fee_list
        data["mlt_income_list"] = mlt_income_list
        data["dayAhead_ele_list"] = dayAhead_ele_list
        data["dayAhead_fee_list"] = dayAhead_fee_list
        data["dayAhead_settlement_income_list"] = dayAhead_settlement_income_list
        data["dayAhead_income_list"] = dayAhead_income_list
        data["realTime_ele_list"] = realTime_ele_list
        data["realTime_fee_list"] = realTime_fee_list
        data["realTime_settlement_income_list"] = realTime_settlement_income_list
        data["realTime_income_list"] = realTime_income_list
        data["comprehensive_ele_list"] = comprehensive_ele_list
        data["comprehensive_income_list"] = comprehensive_income_list
        data["spot_incomeIncrease_list"] = spot_incomeIncrease_list


    @staticmethod
    def MxProvinceCal(data, length=96):




        pass

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
            "dayAhead_settlement_income_list",
            "dayAhead_income_list",
            "realTime_ele_list",
            "realTime_fee_list",
            "realTime_settlement_income_list",
            "realTime_income_list",
            "comprehensive_ele_list",
            "comprehensive_income_list",
            "spot_incomeIncrease_list",
        ]
        fieldDataDict = {}

        for field in fieldNameList:
            fieldDataDict[field] = []

        for data in dataList:
            for field in fieldNameList:
                # if field in data.keys():
                fieldDataDict[field].append(data[field])

        for field in fieldNameList:
            fieldDataDict[field] = CommonCal.conductAdd(fieldDataDict[field])



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
        # 实时收益
        realTime_income_sum = CommonCal.getSum(fieldDataDict["realTime_income_list"])
        # 现货增收合计
        spot_incomeIncrease_sum = CommonCal.getSum(fieldDataDict["spot_incomeIncrease_list"])
        
        mlt_ele_sum = CommonCal.getSum(fieldDataDict["mlt_ele_list"])
        dayAhead_ele_sum = CommonCal.getSum(fieldDataDict["dayAhead_ele_list"])
        realTime_ele_sum = CommonCal.getSum(fieldDataDict["realTime_ele_list"])
        
        
        
        
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
                "realTime_income_sum" :  realTime_income_sum,
                "spot_incomeIncrease_sum" :  spot_incomeIncrease_sum,
        }




    @staticmethod
    def execEntry(dataList, length=96):
        for data in dataList:
            if data["province_id"] == "15":
                ProInLogic.MxProvinceCal(data, length)
            else:
                ProInLogic.otherProvinceCal(data, length)


        d = ProInLogic.amalgamateDataList(dataList, length=length)

        return d


if __name__ == '__main__':


    x = ["a","ab"]
    d = copy.deepcopy(x)
    print(d )
