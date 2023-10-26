import copy

from jituance.集团小程序2.common_calculation import CommonCal


class ProBeLogic:


    @staticmethod
    def calLogic(data, length=96):

        change_cost_ele_list = [None for i in range(0,length)]
        if data["business_type"] == 1:
            change_cost_ele_list = copy.deepcopy(data["day_ahead_ele"])


        # 变动成本
        cost = CommonCal.weightedMean(
            numeratorList=[data["day_ahead_ele"], data["change_cost"]],
            denominatorList=[data["day_ahead_ele"]],
            length=length
        )

        change_cost_price_list = cost["divideList"]
        change_cost_fee_list = cost["numeratorList"]

        # 日前费用计算
        dayAhead = CommonCal.weightedMean(
            numeratorList=[data["day_ahead_ele"], data["day_ahead_price"]],
            denominatorList=[data["day_ahead_ele"]],
            length=length
        )

        # 日前电价-变动成本
        dayAheadDiffPrice = CommonCal.conductSubtract(data["day_ahead_price"],data["change_cost"],B_NoneToZero=True)["diff"]
        # 计算日前收益
        dayAhead_income_res = CommonCal.weightedMean(
            numeratorList=[data["day_ahead_ele"], dayAheadDiffPrice],
            denominatorList=[data["day_ahead_ele"]],
            length=length
        )

        dayAhead_ele_list = copy.deepcopy(data["day_ahead_ele"])
        dayAhead_price_list = dayAhead["divideList"]
        dayAhead_fee_list = dayAhead["numeratorList"]
        dayAhead_income_list = dayAhead_income_res["numeratorList"]

        # 实时费用计算
        realTime = CommonCal.weightedMean(
            numeratorList=[data["real_time_ele"], data["real_time_price"]],
            denominatorList=[data["real_time_ele"]],
            length=length
        )

        # 实时电价-变动成本
        realTimeDiffPrice = CommonCal.conductSubtract(data["real_time_price"], data["change_cost"], B_NoneToZero=True)[
            "diff"]
        # 计算实时收益
        realTime_income_res = CommonCal.weightedMean(
            numeratorList=[data["real_time_ele"], realTimeDiffPrice],
            denominatorList=[data["real_time_ele"]],
            length=length
        )

        realTime_ele_list = copy.deepcopy(data["real_time_ele"])
        realTime_price_list = realTime["divideList"]
        realTime_fee_list = realTime["numeratorList"]
        realTime_income_list = realTime_income_res["numeratorList"]


        # 总收益
        total_income_list = CommonCal.conductAdd([dayAhead_income_list,realTime_income_list])
        # 综合费用
        comprehensive_income_list = CommonCal.conductAdd([dayAhead_fee_list,realTime_fee_list])
        # 发电量
        comprehensive_ele_list = CommonCal.conductAdd([dayAhead_ele_list,realTime_ele_list])


        return {
                "change_cost_ele_list": change_cost_ele_list,
                "change_cost_price_list": change_cost_price_list,
                "change_cost_fee_list": change_cost_fee_list,

                "dayAhead_ele_list": dayAhead_ele_list,
                "dayAhead_price_list": dayAhead_price_list,
                "dayAhead_fee_list": dayAhead_fee_list,
                "dayAhead_income_list": dayAhead_income_list,

                "realTime_ele_list": realTime_ele_list,
                "realTime_price_list": realTime_price_list,
                "realTime_fee_list": realTime_fee_list,
                "realTime_income_list": realTime_income_list,

                "total_income_list": total_income_list,
                "comprehensive_income_list": comprehensive_income_list,
                "comprehensive_ele_list": comprehensive_ele_list,

        }

    @staticmethod
    def calTarget(dataList, length=96):


        fieldNameList = [
            "change_cost_ele_list",
            "change_cost_fee_list",

            "dayAhead_ele_list",
            "dayAhead_fee_list",
            "dayAhead_income_list",

            "realTime_ele_list",
            "realTime_fee_list",
            "realTime_income_list",

            "total_income_list",
            "comprehensive_income_list",
            "comprehensive_ele_list",

        ]

        fieldDataDict = CommonCal.conductAddMulField(fieldNameList=fieldNameList,dataList=dataList,length=length)

        # 变动成本计算
        cost_res = CommonCal.weightedMean(
            numeratorList=[fieldDataDict["change_cost_fee_list"]],
            denominatorList=[fieldDataDict["change_cost_ele_list"]],
            length=length
        )
        change_cost_price_list = cost_res["divideList"]
        change_cost_price_sum = cost_res["divideSum"]
        change_cost_fee_sum = cost_res["numeratorSum"]


        # 日前计算
        dayAhead_res = CommonCal.weightedMean(
            numeratorList=[fieldDataDict["dayAhead_fee_list"]],
            denominatorList=[fieldDataDict["dayAhead_ele_list"]],
            length=length
        )
        dayAhead_price_list = dayAhead_res["divideList"]
        dayAhead_ele_sum = CommonCal.getSum(fieldDataDict["dayAhead_ele_list"])
        dayAhead_price_sum = dayAhead_res["divideSum"]
        dayAhead_fee_sum = dayAhead_res["numeratorSum"]
        # 日前收益
        dayAhead_income_sum = CommonCal.getSum(fieldDataDict["dayAhead_income_list"])

        # 实时计算
        realTime_res = CommonCal.weightedMean(
            numeratorList=[fieldDataDict["realTime_fee_list"]],
            denominatorList=[fieldDataDict["realTime_ele_list"]],
            length=length
        )
        realTime_price_list = realTime_res["divideList"]
        realTime_ele_sum = CommonCal.getSum(fieldDataDict["realTime_ele_list"])
        realTime_price_sum = realTime_res["divideSum"]
        realTime_fee_sum = realTime_res["numeratorSum"]
        # 实时收益
        realTime_income_sum = CommonCal.getSum(fieldDataDict["realTime_income_list"])

        # 总收益
        total_income_sum = CommonCal.getSum(fieldDataDict["total_income_list"])

        # 综合费用
        comprehensive_income_sum = CommonCal.getSum(fieldDataDict["comprehensive_income_list"])
        # 发电量
        comprehensive_ele_sum = CommonCal.getSum(fieldDataDict["comprehensive_ele_list"])
        # 综合电价
        comprehensive_price_sum = None
        if comprehensive_income_sum == None or comprehensive_ele_sum == None or comprehensive_ele_sum == 0:
            pass
        else:
            comprehensive_price_sum = comprehensive_income_sum/comprehensive_ele_sum

        return {
            "change_cost_price_list": change_cost_price_list,
            "change_cost_fee_list": fieldDataDict["change_cost_fee_list"],
            "change_cost_price_sum": change_cost_price_sum,
            "change_cost_fee_sum": change_cost_fee_sum,

            "dayAhead_ele_list": fieldDataDict["dayAhead_ele_list"],
            "dayAhead_price_list": dayAhead_price_list,
            "dayAhead_fee_list": fieldDataDict["dayAhead_fee_list"],
            "dayAhead_income_list": fieldDataDict["dayAhead_income_list"],
            "dayAhead_ele_sum": dayAhead_ele_sum,
            "dayAhead_price_sum": dayAhead_price_sum,
            "dayAhead_fee_sum": dayAhead_fee_sum,
            "dayAhead_income_sum": dayAhead_income_sum,

            "realTime_ele_list": fieldDataDict["realTime_ele_list"],
            "realTime_price_list": realTime_price_list,
            "realTime_fee_list": fieldDataDict["realTime_fee_list"],
            "realTime_income_list": fieldDataDict["realTime_income_list"],
            "realTime_ele_sum": realTime_ele_sum,
            "realTime_price_sum": realTime_price_sum,
            "realTime_fee_sum": realTime_fee_sum,
            "realTime_income_sum": realTime_income_sum,

            "comprehensive_ele_list": fieldDataDict["comprehensive_ele_list"],
            "comprehensive_income_list": fieldDataDict["comprehensive_income_list"],
            "comprehensive_ele_sum": comprehensive_ele_sum,
            "comprehensive_price_sum": comprehensive_price_sum,

            "total_income_list": fieldDataDict["total_income_list"],
            "total_income_sum": total_income_sum,

        }

    @staticmethod
    def execEntry(dataList, length=96):

        proBetweenFieldEnum = {
            "run_capacity": "运行容量",

            "change_cost_price_list": "分时变动成本",
            "change_cost_fee_list": "分时变动成本费用",
            "change_cost_price_sum": "变动成本",
            "change_cost_fee_sum": "总成本",

            "dayAhead_ele_list": "分时日前电量",
            "dayAhead_price_list": "分时日前均价",
            "dayAhead_fee_list": "分时日前费用",
            "dayAhead_income_list": "分时日前收益",
            "dayAhead_ele_sum": "日前电量",
            "dayAhead_price_sum": "日前均价",
            "dayAhead_fee_sum": "日前费用",
            "dayAhead_income_sum": "日前收益",

            "realTime_ele_list": "分时实时电量",
            "realTime_price_list": "分时实时均价",
            "realTime_fee_list": "分时实时费用",
            "realTime_income_list": "分时实时收益",
            "realTime_ele_sum": "实时电量",
            "realTime_price_sum": "实时均价",
            "realTime_fee_sum": "实时费用",
            "realTime_income_sum": "实时收益",

            "comprehensive_ele_list": "分时发电量",
            "comprehensive_income_list": "分时综合费用",
            "comprehensive_ele_sum": "发电量",
            "comprehensive_price_sum": "综合电价",

            "total_income_list": "分时总收益",
            "total_income_sum": "总收益",

        }

        for data in dataList:
            calLogicRes = ProBeLogic.calLogic(data,length)
            data.update(calLogicRes)

        res = ProBeLogic.calTarget(dataList, length=96)
        for r in res:
            print(proBetweenFieldEnum[r]," ：",res[r])



if __name__ == '__main__':


    x = ["a","ab"]
    d = copy.deepcopy(x)
    print(d )
