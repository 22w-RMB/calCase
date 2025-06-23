import requests

from datetime import datetime, timedelta


from 江苏.国电投江苏.刘锐接口数据校验.common import CommonClass



class SystemInterface:

    def __init__(self,session, info):
        self.domain = None
        self.loginInfo = None
        self.session = session
        self.domain = info['url_domain']
        self.loginInfo = info['logininfo']
        self.tenantId = info['tenantId']
        self.loginInfo["switch_url"] += self.tenantId


    def login(self):
        CommonClass.login(self.session, self.domain, self.loginInfo)

    def get_public_data(self,start_date,end_date):

        public_data_dict = {}

        #  市场行情看板请求
        market_method = "POST"
        market_url = self.domain +"/PublicDataManage-Gdt/032/api/spot/market/info"
        market_json = {
            "dateMerge": {
                "aggregateType": "AVG",
                "mergeType": "NONE"
            },
            "dateRanges": [{
                "start": start_date,
                "end": end_date
            }],
            "marketType": None,
            "provinceAreaId": "032",
            "timeSegment": {
                "aggregateType": None,
                "filterPoints": None,
                "segmentType": "SEG_96"
            },
            "statistics": {
                "groupType": "RANGE"
            }
        }
        market_response = CommonClass.execRequest(self.session,url=market_url,method=market_method,json=market_json,)
        # print(market_response.json()["data"])
        public_data_dict.update(market_response.json()["data"])

        # 系统备用
        sparedemand_method = "POST"
        sparedemand_url = self.domain +"/PublicDataManage-Gdt/032/api/spot/spareDemand/query/latest"
        sparedemand_json = {
            "dateRanges":[
                {
                    "start":start_date,
                    "end":end_date
                }
            ],
            "provinceAreaId":"032",
            "timeSegment":{
                "filterPoints":None,
                "segmentType":"SEG_96"
            }
        }
        sparedemand_response = CommonClass.execRequest(self.session,url=sparedemand_url,method=sparedemand_method,json=sparedemand_json,)
        # print(sparedemand_response.json()["data"]["dataList"])
        public_data_dict.update({
            "spareDemand": sparedemand_response.json()["data"]["dataList"]
        })

        # 输变电检修计划
        overhaulplan_method = "POST"
        overhaulplan_url = self.domain +"/PublicDataManage-Gdt/032/api/spot/device/overhaulPlan/query/latest"

        # 稳定限额
        transsection_method = "POST"
        transsection_url = self.domain +"/PublicDataManage-Gdt/032/api/spot/transSection/bound/query/latest"

        overhaulplan_dict={}
        transsection_dict={}

        sd = datetime.strptime(start_date, "%Y-%m-%d")
        ed = datetime.strptime(end_date, "%Y-%m-%d")
        while sd <= ed:
            date_str = datetime.strftime(sd, "%Y-%m-%d")
            sd += timedelta(days=1)

            overhaulplan_json = {"dateRanges": [{"start": date_str, "end": date_str}], "provinceAreaId": "032"}
            transsection_json = {"dateRanges": [{"start": date_str, "end": date_str}], "provinceAreaId": "032"}

            overhaulplan_response = CommonClass.execRequest(self.session, url=overhaulplan_url,
                                                            method=overhaulplan_method, json=overhaulplan_json, )
            transsection_response = CommonClass.execRequest(self.session, url=transsection_url,
                                                            method=transsection_method, json=transsection_json, )

            overhaulplan_response_data_list = overhaulplan_response.json()["data"]["dataList"]
            transsection_response_data_list = transsection_response.json()["data"]["dataList"]

            overhaulplan_response_data_dict = {item['deviceName']: {'planStartTime': item['planStartTime'], 'planEndTime': item['planEndTime'],
                                      'areaName': item['areaName']} for item in overhaulplan_response_data_list}
            transsection_response_data_dict = {item['sectionName']:{'stablePowerLimit': item['stablePowerLimit']} for item in transsection_response_data_list}



            overhaulplan_dict[date_str] = overhaulplan_response_data_dict
            transsection_dict[date_str] = transsection_response_data_dict

        public_data_dict.update({"overhaulPlan":overhaulplan_dict})
        public_data_dict.update({"bound":transsection_dict})

        # print(public_data_dict)
        return public_data_dict




if __name__ == '__main__':
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
    js.get_public_data("2025-04-01","2025-04-01")