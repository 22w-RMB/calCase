import requests

from 江苏.国电投江苏.刘锐接口数据校验.common import CommonClass
from 江苏.国电投江苏.刘锐接口数据校验.class_info import DispatchUnit,BusinessUnit

class LiuRui:

    def __init__(self):
        self.pre_url = "https://www.dljyfzjc.spic.com.cn:20280/pct1/tsintergy/centreFacade"
        self.session = requests.Session()
        self.market_id = "PHDJS"
        self.header = None

    def update_token(self):
        token = self.get_token()
        self.session.headers.update({"Authorization": "Bearer "+token})

    def get_token(self):

        url = self.pre_url + "/token"
        form_data = {
            "app_key": "26e6b839-4331-46f9-9898-b43e1a0d6ed3",
            "app_secret": "fQLi9FTZJvGzpsIYGpr0UJbXgdoKAhPZ9sUyCxOGlNU=",
        }

        response = CommonClass.execRequest(session=self.session,url=url,method="POST",data=form_data)
        return response.json()["data"]["access_token"]

    def get_dispatch_unit(self):
        '''
        调度单元基础信息
        :return: 返回机组列表
        '''
        url = self.pre_url + "/v1/base/dispatch_unit"
        params = {
            "market_id": self.market_id
        }

        response = CommonClass.execRequest(session=self.session,url=url,method="GET",params=params)
        unit_list = response.json()['data']['list']

        return [DispatchUnit(item['dispatch_unit_id'],item['dispatch_unit_name']) for item in unit_list]

    def get_business_unit(self):
        '''
        交易单元基础信息
        :return: 返回交易单元列表
        '''
        url = self.pre_url + "/v1/base/business_unit"
        params = {
            "market_id": self.market_id
        }

        response = CommonClass.execRequest(session=self.session,url=url,method="GET",params=params)

        unit_list = response.json()['data']['list']

        return [BusinessUnit(item['business_unit_id'],item['business_unit_name']) for item in unit_list]

    def get_provincial_spot_clearing_result(self, dispatch_unit_id, date):
        '''
        出清结果
        :return: 返回多天出清结果
        '''
        url = self.pre_url + "/v1/spot/provincial_spot_clearing_result"
        params = {
            "market_id": self.market_id,
            "dispatch_unit_id": self.market_id,
            "date": self.market_id,
        }

        response = CommonClass.execRequest(session=self.session,url=url,method="GET",params=params)

        unit_list = response.json()['data']['list']

        return [BusinessUnit(item['business_unit_id'],item['business_unit_name']) for item in unit_list]

    def get_contract_total_curve(self, business_unit_id, start_date, end_date):
        '''
        出清结果
        :return: 返回多天出清结果
        '''
        url = self.pre_url + "/v1/spot/provincial_spot_clearing_result"
        params = {
            "market_id": self.market_id,
            "dispatch_unit_id": self.market_id,
            "date": self.market_id,
        }

        response = CommonClass.execRequest(session=self.session,url=url,method="GET",params=params)

        unit_list = response.json()['data']['list']

        return [BusinessUnit(item['business_unit_id'],item['business_unit_name']) for item in unit_list]

    def get_dayahead_provincial_load_forecast(self, date):
        '''
        日前-系统负荷
        :return: 返回单天
        '''
        url = self.pre_url + "/v1/disclosure/dayahead_provincial_load_forecast"
        params = {
            "market_id": self.market_id,
            "date": date,
        }

        response = CommonClass.execRequest(session=self.session,url=url,method="GET",params=params)

        unit_list = response.json()['data']['list']

        return [item['dayahead_provincial_load_forecast'] for item in unit_list]

    def get_dayahead_tie_line_plan(self, date):
        '''
        日前-受电计划-华东
        :return: 返回单天
        '''
        url = self.pre_url + "/v1/disclosure/dayahead_tie_line_plan"
        params = {
            "market_id": self.market_id,
            "date": date,
        }

        response = CommonClass.execRequest(session=self.session,url=url,method="GET",params=params)

        unit_list = response.json()['data']['list']
        print(unit_list)

        return [item['dayahead_tie_line_plan'] for item in unit_list]

    def get_dayahead_provincial_new_energy_forecast(self, date):
        '''
        日前-统调风光功率预测
        :return: 返回单天
        '''
        url = self.pre_url + "/v1/disclosure/dayahead_provincial_new_energy_forecast"
        params = {
            "market_id": self.market_id,
            "date": date,
        }

        response = CommonClass.execRequest(session=self.session,url=url,method="GET",params=params)

        unit_list = response.json()['data']['list']
        south_data_list = list(filter(lambda u: u['region_name'] == "江南分区", unit_list))
        north_data_list = list(filter(lambda u: u['region_name'] == "江北分区", unit_list))
        all_data_list = list(filter(lambda u: u['region_name'] == "江苏", unit_list))

        return {
            "风电": [item['wind_forecast'] for item in all_data_list],
            "光伏": [item['photovoltaic_forecast'] for item in all_data_list],
            "江南风电": [item['wind_forecast'] for item in south_data_list],
            "江北风电": [item['wind_forecast'] for item in north_data_list],
            "江南光伏": [item['photovoltaic_forecast'] for item in south_data_list],
            "江北光伏": [item['photovoltaic_forecast'] for item in north_data_list],
        }

    def get_dayahead_fixed_power_forecast(self, date):
        '''
        日前-燃机固定出力总值
        :return: 返回单天
        '''
        url = self.pre_url + "/v1/disclosure/dayahead_fixed_power_forecast"
        params = {
            "market_id": self.market_id,
            "date": date,
        }

        response = CommonClass.execRequest(session=self.session,url=url,method="GET",params=params)

        unit_list = response.json()['data']['list']
        south_data_list = list(filter(lambda u: u['region_name'] == "江南分区", unit_list))
        north_data_list = list(filter(lambda u: u['region_name'] == "江北分区", unit_list))
        all_data_list = list(filter(lambda u: u['region_name'] == "江苏", unit_list))

        return {
            "汇总": [item['dayahead_fixed_power_forecast'] for item in all_data_list],
            "江南": [item['dayahead_fixed_power_forecast'] for item in south_data_list],
            "江北": [item['dayahead_fixed_power_forecast'] for item in north_data_list],
        }

    def get_dayahead_reserve_demand(self, date):
        '''
        日前-系统备用需求
        :return: 返回单天
        '''
        url = self.pre_url + "/v1/disclosure/dayahead_reserve_demand"
        params = {
            "market_id": self.market_id,
            "date": date,
        }

        response = CommonClass.execRequest(session=self.session,url=url,method="GET",params=params)

        unit_list = response.json()['data']['list']

        return {
            "正备用": [item['positive_reserve'] for item in unit_list],
            "负备用": [item['negative_reserve'] for item in unit_list],
        }

    def get_equipment_maintenance_plan(self, date):
        '''
        日前-重大设备检修计划
        :return: 返回单天
        '''
        url = self.pre_url + "/v1/disclosure/equipment_maintenance_plan"
        params = {
            "market_id": self.market_id,
            "date": date,
        }

        response = CommonClass.execRequest(session=self.session,url=url,method="GET",params=params)

        unit_list = response.json()['data']['list']

        return {item['equipment_name']:{'planStartTime': item['begin_time'], 'planEndTime': item['end_time'], 'areaName': item['region_name']} for item in unit_list}

    def get_section_constraint(self, date):
        '''
        日前-稳定限额
        :return: 返回单天
        '''
        url = self.pre_url + "/v1/disclosure/section_constraint"
        params = {
            "market_id": self.market_id,
            "date": date,
        }

        response = CommonClass.execRequest(session=self.session,url=url,method="GET",params=params)

        unit_list = response.json()['data']['list']

        return {item['section_name']:{'stablePowerLimit': item['constraint']} for item in unit_list}

    def get_realtime_provincial_load_forecast(self, date):
        '''
        实时-系统负荷
        :return: 返回单天
        '''
        url = self.pre_url + "/v1/disclosure/realtime_provincial_load_forecast"
        params = {
            "market_id": self.market_id,
            "date": date,
        }

        response = CommonClass.execRequest(session=self.session, url=url, method="GET", params=params)

        unit_list = response.json()['data']['list']

        return [item['realtime_provincial_load_forecast'] for item in unit_list]

    def get_realtime_tie_line_plan(self, date):
        '''
        实时-受电计划-华东
        :return: 返回单天
        '''
        url = self.pre_url + "/v1/disclosure/realtime_tie_line_plan"
        params = {
            "market_id": self.market_id,
            "date": date,
        }

        response = CommonClass.execRequest(session=self.session, url=url, method="GET", params=params)

        unit_list = response.json()['data']['list']

        return [item['realtime_tie_line_plan'] for item in unit_list]

    def get_realtime_provincial_new_energy_forecast(self, date):
        '''
        实时-统调风光功率
        :return: 返回单天
        '''
        url = self.pre_url + "/v1/disclosure/realtime_provincial_new_energy_forecast"
        params = {
            "market_id": self.market_id,
            "date": date,
        }

        response = CommonClass.execRequest(session=self.session, url=url, method="GET", params=params)

        unit_list = response.json()['data']['list']
        south_data_list = list(filter(lambda u: u['region_name'] == "江南分区", unit_list))
        north_data_list = list(filter(lambda u: u['region_name'] == "江北分区", unit_list))
        all_data_list = list(filter(lambda u: u['region_name'] == "江苏", unit_list))

        return {
            "风电": [item['wind_forecast'] for item in all_data_list],
            "光伏": [item['photovoltaic_forecast'] for item in all_data_list],
            "江南风电": [item['wind_forecast'] for item in south_data_list],
            "江北风电": [item['wind_forecast'] for item in north_data_list],
            "江南光伏": [item['photovoltaic_forecast'] for item in south_data_list],
            "江北光伏": [item['photovoltaic_forecast'] for item in north_data_list],
        }

    def get_realtime_fixed_power_forecast(self, date):
        '''
        实时-燃机固定出力总值
        :return: 返回单天
        '''
        url = self.pre_url + "/v1/disclosure/realtime_fixed_power_forecast"
        params = {
            "market_id": self.market_id,
            "date": date,
        }

        response = CommonClass.execRequest(session=self.session,url=url,method="GET",params=params)

        unit_list = response.json()['data']['list']
        south_data_list = list(filter(lambda u: u['region_name'] == "江南分区", unit_list))
        north_data_list = list(filter(lambda u: u['region_name'] == "江北分区", unit_list))
        all_data_list = list(filter(lambda u: u['region_name'] == "江苏", unit_list))

        return {
            "汇总": [item['realtime_fixed_power_forecast'] for item in all_data_list],
            "江南": [item['realtime_fixed_power_forecast'] for item in south_data_list],
            "江北": [item['realtime_fixed_power_forecast'] for item in north_data_list],
        }

    def get_provincial_spot_regional_price(self, date):
        '''
        分区价格
        :return: 返回单天
        '''
        url = self.pre_url + "/v1/spot/provincial_spot_regional_price"
        params = {
            "market_id": self.market_id,
            "date": date,
        }

        response = CommonClass.execRequest(session=self.session, url=url, method="GET", params=params)

        unit_list = response.json()['data']['list']
        south_dayahead_data_list = list(filter(lambda u: u['spot_type'] == "dayahead" and u['region_name'] == "江南分区", unit_list))
        south_realtime_data_list = list(filter(lambda u: u['spot_type'] == "realtime" and u['region_name'] == "江南分区", unit_list))
        north_dayahead_data_list = list(filter(lambda u: u['spot_type'] == "dayahead" and u['region_name'] == "江北分区", unit_list))
        north_realtime_data_list = list(filter(lambda u: u['spot_type'] == "realtime" and u['region_name'] == "江北分区", unit_list))

        return {
            "江南分区价格-日前": [item['clearing_price'] for item in south_dayahead_data_list],
            "江南分区价格-实时": [item['clearing_price'] for item in south_realtime_data_list],
            "江北分区价格-日前": [item['clearing_price'] for item in north_dayahead_data_list],
            "江北分区价格-实时": [item['clearing_price'] for item in north_realtime_data_list],
        }


if __name__ == '__main__':
    lr = LiuRui()
    lr.update_token()
    print(lr.get_equipment_maintenance_plan('2025-04-01'))
