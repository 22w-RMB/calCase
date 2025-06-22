import requests

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
        #  市场行情看板请求
        marketMethod = "POST"
        marketUrl = self.domain +"/PublicDataManage-Gdt/032/api/spot/market/info"
        marketJson = {
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
        market_response = CommonClass.execRequest(self.session,url=marketUrl,method=marketMethod,json=marketJson,)
        print(market_response.json()["data"])
        return market_response.json()["data"]



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
    js.get_public_data("2025-06-20","2025-06-21")