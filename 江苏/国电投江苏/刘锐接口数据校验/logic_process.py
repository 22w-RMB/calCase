import copy
import json


import requests
import six
import numpy as np

from datetime import datetime, timedelta

from 江苏.国电投江苏.刘锐接口数据校验.class_info import PublicData,ContractCalResult
from 江苏.国电投江苏.刘锐接口数据校验.interface_liurui import LiuRui
from 江苏.国电投江苏.刘锐接口数据校验.interface_sys import SystemInterface
from 江苏.国电投江苏.刘锐接口数据校验.common import CommonClass
from 江苏.国电投江苏.刘锐接口数据校验.excel_handler import ExcelHeplerXlwing


LOGIN_INFO = {
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

def multi_liurui_day_resquest(start_date,end_date):
    lr = LiuRui()
    lr.update_token()

    sd = datetime.strptime(start_date, "%Y-%m-%d")
    ed = datetime.strptime(end_date, "%Y-%m-%d")
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
        public_data_dict["日前-江北分区价格"].add_date_data(date_str, provincial_spot_regional_price['江北分区价格-日前'])
        public_data_dict["实时-江南分区价格"].add_date_data(date_str, provincial_spot_regional_price['江南分区价格-实时'])
        public_data_dict["实时-江北分区价格"].add_date_data(date_str, provincial_spot_regional_price['江北分区价格-实时'])

    return public_data_dict

def system_public_data_process(start_date,end_date):
    public_data_dict = ini_public_data()

    testSession = requests.Session()
    js = SystemInterface(testSession,LOGIN_INFO)
    js.login()
    sys_response_data = js.get_public_data(start_date,end_date)

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
                {'type': 'type','name': 'CALL_WIRE' },
                {'type': 'channelName','name': '受电计划华东' },
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
            'data_key': None,
            'filter_type_list': [
            ],
        },
        "日前-稳定限额": {
            'data_list_key': "bound",
            'data_key': None,
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
                {'type': 'type', 'name': 'CALL_WIRE'},
                {'type': 'channelName', 'name': '受电计划华东'},
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

    for key,value in public_item_info.items():
        public_data_dict[key].add_date_dict_data(filter_data(sys_response_data,value))

    return public_data_dict

def filter_data(data_list,data_filter_info):

    d1 = data_list[data_filter_info['data_list_key']]
    if data_filter_info['data_key'] == None:
        return d1

    temp_list = d1
    for f in data_filter_info['filter_type_list']:
        temp_list = list(filter(lambda x: x.get(f['type']) == f['name'], temp_list))

    result_dict = {}
    for item in temp_list:
        item_date = item['date'][:10]
        item_value = item[data_filter_info['data_key']]
        result_dict[item_date] = item_value

    # print(result_dict)
    return result_dict

def compare_public_data(start_date,end_date):

    error_info= {

    }

    # 刘锐结果
    lr_result = multi_liurui_day_resquest(start_date,end_date)
    # 系统返回
    sys_result = system_public_data_process(start_date,end_date)



    for key,value in lr_result.items():
        if key not in error_info:
            error_info[key] ={}
        lr_dict_value = lr_result[key].date_data_dict
        sys_dict_value = sys_result[key].date_data_dict

        lr_dict_value_date = lr_dict_value.keys()
        sys_dict_value_date = sys_dict_value.keys()

        date_list = list(lr_dict_value_date|sys_dict_value_date)

        for date in date_list:
            if date not in lr_dict_value_date:
                if sys_dict_value[date] == {} or sys_dict_value[date]==[]:
                    pass
                else:
                    error_info[key].update({
                        "日期" : date,
                        "详情" : "刘锐没有，系统有",
                        # "刘锐数据" : lr_dict_value[date],
                        # "系统数据" : None,
                    })
                continue

            if date not in sys_dict_value_date:
                if lr_dict_value[date] =={} or lr_dict_value[date]==[]:
                    pass
                else:
                    error_info[key].update({
                        "日期": date,
                        "详情": "刘锐有，系统没有",
                        # "刘锐数据": None,
                        # "系统数据": sys_dict_value[date],
                    })
                continue

            lr_date_value = lr_dict_value[date]
            sys_date_value = sys_dict_value[date]

            if type(lr_date_value) == type(sys_date_value):

                # 列表比较
                if isinstance(lr_date_value, list):
                    if len(lr_date_value) == 0 and ( sum([0 if item is None else 1 for item in sys_date_value]) )==0:
                        error_info[key].update({
                            "日期": date,
                            "详情": "双方都没有数据",
                            # "刘锐数据": lr_date_value,
                            # "系统数据": sys_date_value,
                        })
                        continue

                    if len(lr_date_value) != len(sys_date_value):
                        error_info[key].update({
                            "日期": date,
                            "详情": "数据长度对不上",
                            # "刘锐数据": lr_date_value,
                            # "系统数据": sys_date_value,
                        })
                        continue

                    compare_list = [1 if lr_date_value[i]!=sys_date_value[i] else 0 for i in range(0,len(lr_date_value))]
                    res = sum(compare_list)
                    if res > 0:
                        error_info[key].update({
                            "日期": date,
                            "详情": "存在时刻点数据对不上",
                            # "刘锐数据": lr_date_value,
                            # "系统数据": sys_date_value,
                        })

                # 字典比较
                if isinstance(lr_date_value, dict):

                    temp_list = []
                    for k in lr_date_value.keys():  # 设备名称
                        for k1 in lr_date_value[k]: # 设备具体信息
                            if lr_date_value[k][k1] != sys_date_value[k][k1]:
                                temp_list.append("设备名称："+k+" 数据对不上")
                    if len(temp_list) > 0:
                        error_info[key].update({
                            "日期": date,
                            # "详情": str(temp_list),
                            "详情": "数据对不上",
                            # "刘锐数据": lr_date_value,
                            # "系统数据": sys_date_value,
                        })

                    pass


            else:
                error_info[key].update({
                    "日期": date,
                    "详情": "数据类型对不上",
                    # "刘锐数据": lr_date_value,
                    # "系统数据": sys_date_value,
                })

    return error_info


def get_unit_contract(start_date,end_date,sys_trade_unit_name_list):

    lr = LiuRui()
    lr.update_token()
    sys_trade_unit_name_list = sys_trade_unit_name_list
    lr_trade_unit_object_list = lr.get_business_unit()
    lr_trade_unit_name_dict = {item.business_unit_name:item.business_unit_id for item in lr_trade_unit_object_list}
    sys_in_lr_id_dict = {}
    for sys in sys_trade_unit_name_list:
        if sys not in lr_trade_unit_name_dict.keys():
            sys_in_lr_id_dict[sys] = None
        else:
            sys_in_lr_id_dict[sys] = lr_trade_unit_name_dict[sys]

    trade_unit_contract_list = []
    for k,v in sys_in_lr_id_dict.items():
        trade_unit_contract_list.extend( lr.get_contract_total_curve(v,start_date,end_date,k))

    # print(trade_unit_contract_dict)
    return trade_unit_contract_list

def filter_contract_data(trade_unit_contract_list):

    # 根据合同名称、日期过滤
    contract_name_list = list(set([item.contract_name for item in trade_unit_contract_list]))
    date_list = list(set([item.date for item in trade_unit_contract_list]))
    contract_name_result_list = []
    for contract_name in contract_name_list:
        for date in date_list:
            filter_temp_list = list(filter(lambda x: x.contract_name == contract_name and x.date== date, trade_unit_contract_list))
            cal_res_dict = cal_contract(filter_temp_list)
            ele = [contract_name,date,"电量",]
            price = [contract_name,date,"电价",]
            fee = [contract_name,date,"电费",]
            ele.append(cal_res_dict.total_ele)
            ele.extend(cal_res_dict.ele)
            price.append(cal_res_dict.total_price)
            price.extend(cal_res_dict.price)
            fee.append(cal_res_dict.total_fee)
            fee.extend(cal_res_dict.fee)
            contract_name_result_list.append(ele)
            contract_name_result_list.append(price)
            contract_name_result_list.append(fee)

    # 根据机组过滤
    trade_name_list = list(set([item.trade_name for item in trade_unit_contract_list]))
    trade_name_result_list = []
    for trade_name in trade_name_list:
        for date in date_list:
            filter_temp_list = list(filter(lambda x: x.trade_name == trade_name and x.date== date, trade_unit_contract_list))
            cal_res_dict = cal_contract(filter_temp_list)
            ele = [trade_name,date,"电量",]
            price = [trade_name,date,"电价",]
            fee = [trade_name,date,"电费",]
            ele.append(cal_res_dict.total_ele)
            ele.extend(cal_res_dict.ele)
            price.append(cal_res_dict.total_price)
            price.extend(cal_res_dict.price)
            fee.append(cal_res_dict.total_fee)
            fee.extend(cal_res_dict.fee)
            trade_name_result_list.append(ele)
            trade_name_result_list.append(price)
            trade_name_result_list.append(fee)

    # 根据日期过滤
    date_result_list = []
    for date in date_list:
        filter_temp_list = list(
            filter(lambda x: x.date == date, trade_unit_contract_list))
        cal_res_dict = cal_contract(filter_temp_list)
        ele = [ date, "电量", ]
        price = [ date, "电价", ]
        fee = [ date, "电费", ]
        ele.append(cal_res_dict.total_ele)
        ele.extend(cal_res_dict.ele)
        price.append(cal_res_dict.total_price)
        price.extend(cal_res_dict.price)
        fee.append(cal_res_dict.total_fee)
        fee.extend(cal_res_dict.fee)
        date_result_list.append(ele)
        date_result_list.append(price)
        date_result_list.append(fee)

    return {
        "合同名称":contract_name_result_list,
        "交易单元":trade_name_result_list,
        "日期":date_result_list,
    }

def cal_contract(contract_object_list):
    if contract_object_list == []:
        return ContractCalResult(None,None,None,[],[],[])
    total_ele = None
    total_price = None
    total_fee = None
    ele = []
    price = []
    fee = []

    for contract_object in contract_object_list:

        contract_object_fee = np.multiply(contract_object.ele, contract_object.price).tolist()
        if ele == []:
            ele = copy.deepcopy(contract_object.ele)
            price = copy.deepcopy(contract_object.price)
            fee = copy.deepcopy(contract_object_fee)
        else:
            ele = np.add(ele,contract_object.ele).tolist()
            fee = np.add(fee,contract_object_fee).tolist()
            price = np.divide(fee,ele).tolist()

        total_fee = sum(fee)
        total_ele = sum(ele)
        total_price = total_fee / total_ele

    return ContractCalResult(total_ele,total_price,total_fee,ele,price,fee)


def output_contract_file(filter_contract_data_res_dict):
    # print(outputList)
    try:
        print("获取模板")
        tempPath = CommonClass.mkDir("刘锐接口数据校验", "导出", "模板.xlsx", isGetStr=True)
        print(tempPath)

        savePath = CommonClass.mkDir( "刘锐接口数据校验", "导出",  "合同数据明细.xlsx", isGetStr=True)
        e = ExcelHeplerXlwing()

        print("开始导出")
        e.copySheet(tempPath, "合同名称","合同名称")
        e.copySheet(tempPath, "交易单元", "交易单元")
        e.copySheet(tempPath, "日期","日期")
        e.write_contract(savePath,filter_contract_data_res_dict)

        print("导出结束")
    finally:
        e.close()

def exec_contract_main(sys_trade_unit_name_list,start_date,end_date):

    data = get_unit_contract(start_date, end_date,sys_trade_unit_name_list)
    res = filter_contract_data(data)
    output_contract_file(res)

if __name__ == '__main__':

    # l = multi_liurui_day_resquest("2025-06-21","2025-06-21")
    #
    # for k,v in l.items():
    #     print(k,": ",v.date_data_dict)
    # a = json.dumps(data, indent=4, ensure_ascii=False)
    data = compare_public_data("2025-06-07", "2025-06-07")
    a = json.dumps(data, indent=4, ensure_ascii=False)
    print(a)

    # l = ["国家电投集团响水新能源有限公司(风电)", "中泗光伏五站", "中电滨海风电", "舜大宝应集中式光伏"]  # ,"中泗光伏五站","中电滨海风电","舜大宝应集中式光伏"
    # exec_contract_main(l,"2025-06-01",'2026-06-30')
    # a = json.dumps(data, indent=4, ensure_ascii=False)
    # print(res)


