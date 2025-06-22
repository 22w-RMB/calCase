
from datetime import datetime, timedelta

import requests

from 江苏.国电投江苏.刘锐接口数据校验.class_info import PublicData
from 江苏.国电投江苏.刘锐接口数据校验.interface_liurui import LiuRui
from 江苏.国电投江苏.刘锐接口数据校验.interface_sys import SystemInterface

def ini_public_data():

    dic = {
        "日前-系统负荷": PublicData(market_type='DAY_AHEAD'),
        "日前-受电计划-华东": PublicData(market_type='DAY_AHEAD'),
        "日前-新能源风电": PublicData(market_type='DAY_AHEAD'),
        "日前-新能源光伏": PublicData(market_type='DAY_AHEAD'),
        "日前-新能源江南风电": PublicData(market_type='DAY_AHEAD'),
        "日前-新能源江北风电": PublicData(market_type='DAY_AHEAD'),
        "日前-新能源江南光伏": PublicData(market_type='DAY_AHEAD'),
        "日前-新能源江北光伏": PublicData(market_type='DAY_AHEAD'),
        "日前-燃机汇总": PublicData(market_type='DAY_AHEAD'),
        "日前-燃机江南": PublicData(market_type='DAY_AHEAD'),
        "日前-燃机江北": PublicData(market_type='DAY_AHEAD'),
        "日前-系统备用需求-正备用": PublicData(market_type='DAY_AHEAD'),
        "日前-系统备用需求-负备用": PublicData(market_type='DAY_AHEAD'),
        "日前-重大设备检修": PublicData(market_type='DAY_AHEAD'),
        "日前-稳定限额": PublicData(market_type='DAY_AHEAD'),
        "实时-系统负荷": PublicData(market_type='REAL_TIME'),
        "实时-受电计划-华东": PublicData(market_type='REAL_TIME'),
        "实时-新能源风电": PublicData(market_type='REAL_TIME'),
        "实时-新能源光伏": PublicData(market_type='REAL_TIME'),
        "实时-新能源江南风电": PublicData(market_type='REAL_TIME'),
        "实时-新能源江北风电": PublicData(market_type='REAL_TIME'),
        "实时-新能源江南光伏": PublicData(market_type='REAL_TIME'),
        "实时-新能源江北光伏": PublicData(market_type='REAL_TIME'),
        "实时-燃机汇总": PublicData(market_type='REAL_TIME'),
        "实时-燃机江南": PublicData(market_type='REAL_TIME'),
        "实时-燃机江北": PublicData(market_type='REAL_TIME'),
        "日前-江南分区价格": PublicData(market_type='DAY_AHEAD'),
        "日前-江北分区价格": PublicData(market_type='DAY_AHEAD'),
        "实时-江南分区价格": PublicData(market_type='REAL_TIME'),
        "实时-江北分区价格": PublicData(market_type='REAL_TIME'),
    }

    return dic

def multi_liurui_day_resquest(startDate,endDate):
    lr = LiuRui()
    lr.update_token()

    sd = datetime.strptime(startDate, "%Y-%m-%d")
    ed = datetime.strptime(endDate, "%Y-%m-%d")
    public_data_dict = ini_public_data()
    while sd <= ed:
        date_str = datetime.strftime(sd, "%Y-%m-%d")
        sd += timedelta(days=1)

        dayahead_provincial_load_forecast = lr.get_dayahead_provincial_load_forecast(date_str)
        dayahead_tie_line_plan = lr.get_dayahead_tie_line_plan(date_str)
        dayahead_provincial_new_energy_forecast = lr.get_dayahead_provincial_new_energy_forecast(date_str)
        dayahead_fixed_power_forecast = lr.get_dayahead_fixed_power_forecast(date_str)
        dayahead_reserve_demand = lr.get_dayahead_reserve_demand(date_str)
        equipment_maintenance_plan = lr.get_equipment_maintenance_plan(date_str)
        section_constraint = lr.get_section_constraint(date_str)
        realtime_provincial_load_forecast = lr.get_realtime_provincial_load_forecast(date_str)
        realtime_tie_line_plan = lr.get_realtime_tie_line_plan(date_str)
        realtime_provincial_new_energy_forecast = lr.get_realtime_provincial_new_energy_forecast(date_str)
        realtime_fixed_power_forecast = lr.get_realtime_fixed_power_forecast(date_str)
        provincial_spot_regional_price = lr.get_provincial_spot_regional_price(date_str)

        public_data_dict["日前-系统负荷"].add_date_data(date_str, dayahead_provincial_load_forecast)
        public_data_dict["日前-受电计划-华东"].add_date_data(date_str, dayahead_tie_line_plan)
        public_data_dict["日前-新能源风电"].add_date_data(date_str, dayahead_provincial_new_energy_forecast['风电'])
        public_data_dict["日前-新能源光伏"].add_date_data(date_str, dayahead_provincial_new_energy_forecast['光伏'])
        public_data_dict["日前-新能源江南风电"].add_date_data(date_str, dayahead_provincial_new_energy_forecast['江南风电'])
        public_data_dict["日前-新能源江北风电"].add_date_data(date_str, dayahead_provincial_new_energy_forecast['江北风电'])
        public_data_dict["日前-新能源江南光伏"].add_date_data(date_str, dayahead_provincial_new_energy_forecast['江南光伏'])
        public_data_dict["日前-新能源江北光伏"].add_date_data(date_str, dayahead_provincial_new_energy_forecast['江北光伏'])
        public_data_dict["日前-燃机汇总"].add_date_data(date_str, dayahead_fixed_power_forecast['汇总'])
        public_data_dict["日前-燃机江南"].add_date_data(date_str, dayahead_fixed_power_forecast['江南'])
        public_data_dict["日前-燃机江北"].add_date_data(date_str, dayahead_fixed_power_forecast['江北'])
        public_data_dict["日前-系统备用需求-正备用"].add_date_data(date_str, dayahead_reserve_demand['正备用'])
        public_data_dict["日前-系统备用需求-负备用"].add_date_data(date_str, dayahead_reserve_demand['负备用'])
        public_data_dict["日前-重大设备检修"].add_date_data(date_str, equipment_maintenance_plan)
        public_data_dict["日前-稳定限额"].add_date_data(date_str, section_constraint)
        public_data_dict["实时-系统负荷"].add_date_data(date_str, realtime_provincial_load_forecast)
        public_data_dict["实时-受电计划-华东"].add_date_data(date_str, realtime_tie_line_plan)
        public_data_dict["实时-新能源风电"].add_date_data(date_str, realtime_provincial_new_energy_forecast['风电'])
        public_data_dict["实时-新能源光伏"].add_date_data(date_str, realtime_provincial_new_energy_forecast['光伏'])
        public_data_dict["实时-新能源江南风电"].add_date_data(date_str, realtime_provincial_new_energy_forecast['江南风电'])
        public_data_dict["实时-新能源江北风电"].add_date_data(date_str, realtime_provincial_new_energy_forecast['江北风电'])
        public_data_dict["实时-新能源江南光伏"].add_date_data(date_str, realtime_provincial_new_energy_forecast['江南光伏'])
        public_data_dict["实时-新能源江北光伏"].add_date_data(date_str, realtime_provincial_new_energy_forecast['江北光伏'])
        public_data_dict["实时-燃机汇总"].add_date_data(date_str, realtime_fixed_power_forecast['汇总'])
        public_data_dict["实时-燃机江南"].add_date_data(date_str, realtime_fixed_power_forecast['江南'])
        public_data_dict["实时-燃机江北"].add_date_data(date_str, realtime_fixed_power_forecast['江北'])
        public_data_dict["日前-江南分区价格"].add_date_data(date_str, provincial_spot_regional_price['江南分区价格-日前'])
        public_data_dict["日前-江北分区价格"].add_date_data(date_str, provincial_spot_regional_price['江南分区价格-实时'])
        public_data_dict["实时-江南分区价格"].add_date_data(date_str, provincial_spot_regional_price['江北分区价格-日前'])
        public_data_dict["实时-江北分区价格"].add_date_data(date_str, provincial_spot_regional_price['江北分区价格-实时'])

def system_public_data_process(info,startDate,endDate):
    public_data_dict = ini_public_data()
    info = {
        "url_domain" :  "http://gdt.test.gzdevops3.tsintergy.com",
        "logininfo" : {
            "publicKey_url" :  None,
            "login_url" :  "/usercenter/web/login",
            "switch_url" :  "/usercenter/web/switchTenant?tenantId=" ,
            "username" :  "zhanzw01",
            "password" :  "Qinghua123@",
            "loginMode" :  2,
        },
        "tenantId" : "e4d4ed6c8d63dc6a018dd3c1bb1212de",
    }

    testSession = requests.Session()
    js = SystemInterface(testSession,info)
    js.login()
    sys_response_data = js.get_public_data("2025-06-20","2025-06-21")

    public_item_info = {
        "日前-系统负荷":{
            'data_list_key': "systemLoad",
            'data_key': "power",
            'filter_type_list': [
                {'type': 'marketType','name': 'DAY_AHEAD' },
            ],
        },
        "日前-受电计划-华东": {
            'data_list_key': "callWirePower",
            'data_key': "power",
            'filter_type_list': [
                {'type': 'marketType','name': 'DAY_AHEAD' },
                {'type': 'type','name': '受电计划华东' },
                {'type': 'channelName','name': 'CALL_WIRE' },
            ],
        },
        "日前-新能源风电": {
            'data_list_key': "newEnergyPower",
            'data_key': "power",
            'filter_type_list': [
                {'type': 'marketType', 'name': 'DAY_AHEAD'},
                {'type': 'area', 'name': '汇总'},
                {'type': 'type', 'name': 'WIND'},
            ],
        },
        "日前-新能源光伏": {
            'data_list_key': "newEnergyPower",
            'data_key': "power",
            'filter_type_list': [
                {'type': 'marketType', 'name': 'DAY_AHEAD'},
                {'type': 'area', 'name': '汇总'},
                {'type': 'type', 'name': 'PHOTOVOLTAIC'},
            ],
        },
        "日前-新能源江南风电": {
            'data_list_key': "newEnergyPower",
            'data_key': "power",
            'filter_type_list': [
                {'type': 'marketType', 'name': 'DAY_AHEAD'},
                {'type': 'area', 'name': '江南'},
                {'type': 'type', 'name': 'WIND'},
            ],
        },
        "日前-新能源江北风电": {
            'data_list_key': "newEnergyPower",
            'data_key': "power",
            'filter_type_list': [
                {'type': 'marketType', 'name': 'DAY_AHEAD'},
                {'type': 'area', 'name': '江北'},
                {'type': 'type', 'name': 'WIND'},
            ],
        },
        "日前-新能源江南光伏": {
            'data_list_key': "newEnergyPower",
            'data_key': "power",
            'filter_type_list': [
                {'type': 'marketType', 'name': 'DAY_AHEAD'},
                {'type': 'area', 'name': '江南'},
                {'type': 'type', 'name': 'PHOTOVOLTAIC'},
            ],
        },
        "日前-新能源江北光伏": {
            'data_list_key': "newEnergyPower",
            'data_key': "power",
            'filter_type_list': [
                {'type': 'marketType', 'name': 'DAY_AHEAD'},
                {'type': 'area', 'name': '江北'},
                {'type': 'type', 'name': 'PHOTOVOLTAIC'},
            ],
        },
        "日前-燃机汇总": {
            'data_list_key': "nonMarketFireUnitPower",
            'data_key': "power",
            'filter_type_list': [
                {'type': 'marketType', 'name': 'DAY_AHEAD'},
                {'type': 'area', 'name': '汇总'},
            ],
        },
        "日前-燃机江南": {
            'data_list_key': "nonMarketFireUnitPower",
            'data_key': "power",
            'filter_type_list': [
                {'type': 'marketType', 'name': 'DAY_AHEAD'},
                {'type': 'area', 'name': '江南'},
            ],
        },
        "日前-燃机江北": {
            'data_list_key': "nonMarketFireUnitPower",
            'data_key': "power",
            'filter_type_list': [
                {'type': 'marketType', 'name': 'DAY_AHEAD'},
                {'type': 'area', 'name': '江北'},
            ],
        },
        "日前-系统备用需求-正备用": {
            'data_list_key': "spareDemand",
            'data_key': "positivePower",
            'filter_type_list': [
                {'type': 'marketType', 'name': 'DAY_AHEAD'},
            ],
        },
        "日前-系统备用需求-负备用": {
            'data_list_key': "spareDemand",
            'data_key': "negativePower",
            'filter_type_list': [
                {'type': 'marketType', 'name': 'DAY_AHEAD'},
            ],
        },
        "日前-重大设备检修": {
            'data_list_key': "overhaulPlan",
            'data_key': "dataList",
            'filter_type_list': [
            ],
        },
        "日前-稳定限额": {
            'data_list_key': "bound",
            'data_key': "dataList",
            'filter_type_list': [
            ],
        },
        "实时-系统负荷": {
            'data_list_key': "systemLoad",
            'data_key': "power",
            'filter_type_list': [
                {'type': 'marketType', 'name': 'REAL_TIME'},
            ],
        },
        "实时-受电计划-华东": {
            'data_list_key': "callWirePower",
            'data_key': "power",
            'filter_type_list': [
                {'type': 'marketType', 'name': 'REAL_TIME'},
                {'type': 'type', 'name': '受电计划华东'},
                {'type': 'channelName', 'name': 'CALL_WIRE'},
            ],
        },
        "实时-新能源风电": {
            'data_list_key': "newEnergyPower",
            'data_key': "power",
            'filter_type_list': [
                {'type': 'marketType', 'name': 'REAL_TIME'},
                {'type': 'area', 'name': '汇总'},
                {'type': 'type', 'name': 'WIND'},
            ],
        },
        "实时-新能源光伏": {
            'data_list_key': "newEnergyPower",
            'data_key': "power",
            'filter_type_list': [
                {'type': 'marketType', 'name': 'REAL_TIME'},
                {'type': 'area', 'name': '汇总'},
                {'type': 'type', 'name': 'PHOTOVOLTAIC'},
            ],
        },
        "实时-新能源江南风电": {
            'data_list_key': "newEnergyPower",
            'data_key': "power",
            'filter_type_list': [
                {'type': 'marketType', 'name': 'REAL_TIME'},
                {'type': 'area', 'name': '江南'},
                {'type': 'type', 'name': 'WIND'},
            ],
        },
        "实时-新能源江北风电": {
            'data_list_key': "newEnergyPower",
            'data_key': "power",
            'filter_type_list': [
                {'type': 'marketType', 'name': 'REAL_TIME'},
                {'type': 'area', 'name': '江北'},
                {'type': 'type', 'name': 'WIND'},
            ],
        },
        "实时-新能源江南光伏": {
            'data_list_key': "newEnergyPower",
            'data_key': "power",
            'filter_type_list': [
                {'type': 'marketType', 'name': 'REAL_TIME'},
                {'type': 'area', 'name': '江南'},
                {'type': 'type', 'name': 'PHOTOVOLTAIC'},
            ],
        },
        "实时-新能源江北光伏": {
            'data_list_key': "newEnergyPower",
            'data_key': "power",
            'filter_type_list': [
                {'type': 'marketType', 'name': 'REAL_TIME'},
                {'type': 'area', 'name': '江北'},
                {'type': 'type', 'name': 'PHOTOVOLTAIC'},
            ],
        },
        "实时-燃机汇总": {
            'data_list_key': "nonMarketFireUnitPower",
            'data_key': "power",
            'filter_type_list': [
                {'type': 'marketType', 'name': 'REAL_TIME'},
                {'type': 'area', 'name': '汇总'},
            ],
        },
        "实时-燃机江南": {
            'data_list_key': "nonMarketFireUnitPower",
            'data_key': "power",
            'filter_type_list': [
                {'type': 'marketType', 'name': 'REAL_TIME'},
                {'type': 'area', 'name': '江南'},
            ],
        },
        "实时-燃机江北": {
            'data_list_key': "nonMarketFireUnitPower",
            'data_key': "power",
            'filter_type_list': [
                {'type': 'marketType', 'name': 'REAL_TIME'},
                {'type': 'area', 'name': '江北'},
            ],
        },
        "日前-江南分区价格": {
            'data_list_key': "areaClearingPrice",
            'data_key': "price",
            'filter_type_list': [
                {'type': 'marketType', 'name': 'DAY_AHEAD'},
                {'type': 'area', 'name': '江南'},
            ],
        },
        "日前-江北分区价格": {
            'data_list_key': "areaClearingPrice",
            'data_key': "price",
            'filter_type_list': [
                {'type': 'marketType', 'name': 'DAY_AHEAD'},
                {'type': 'area', 'name': '江北'},
            ],
        },
        "实时-江南分区价格": {
            'data_list_key': "areaClearingPrice",
            'data_key': "price",
            'filter_type_list': [
                {'type': 'marketType', 'name': 'REAL_TIME'},
                {'type': 'area', 'name': '江南'},
            ],
        },
        "实时-江北分区价格": {
            'data_list_key': "areaClearingPrice",
            'data_key': "price",
            'filter_type_list': [
                {'type': 'marketType', 'name': 'REAL_TIME'},
                {'type': 'area', 'name': '江北'},
            ],
        },
    }

def filter_data(data_list,data_filter_info):

    d1 = data_list[data_filter_info['data_list_key']]

    # 过滤出日前或实时的数据
    filterList1 = list(filter(lambda x: x.get('marketType') == marketType, dataList))
    # 如果是联络线或者通道或新能源，那么
    if fieldType is not None:
        filterList1 = list(filter(lambda x: x[fieldType] == fieldName, filterList1))

    filterList2 = []

    if itemOtherInfo == None:
        # 进一步过滤出96点数据不为空的日期
        filterList2 = list(filter(lambda x: CommonClass.judgeListIsNone(x[itemName]) == False, filterList1))

    if itemOtherInfo is not None:
        if itemOtherInfo['itemDataType'] == "dict" :
            '''
                {itemDataType : "dict" , dictKeyLists : []}
            '''
            def filterDictValue(dictData,dictKeyLists):
                if dictData == None:
                    return  False
                filterTemp = list(filter(lambda x: dictData[x] == None,dictKeyLists))
                return True if filterTemp == [] else False

            # 进一步过滤出96点数据不为空的日期
            filterList2 = list(filter(lambda x: filterDictValue(x[itemName],itemOtherInfo['dictKeyLists']) == True, filterList1))

        if itemOtherInfo['itemDataType'] == "str" :
            '''
                {itemDataType : "str" }
            '''
            # 进一步过滤出96点数据不为空的日期
            filterList2 = list(filter(lambda x: (x[itemName] != None and x[itemName] != ""), filterList1))

    # 生成有数据的日期
    havaDataDate = [d['date'][:10] for d in filterList2]
    # 生成没有数据的日期
    noDataDate = list(set(allDateList) - set(havaDataDate))

    return {
        'noDataDate': noDataDate,
        'haveDataDate': list(set(havaDataDate)),
    }




if __name__ == '__main__':


