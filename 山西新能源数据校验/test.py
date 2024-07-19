from 山西新能源数据校验.common import CommonClass
import requests

businessType = [
            {
                "name": "风电",
                "id": "1"
            },
            {
                "name": "光伏",
                "id": "2"
            },
            {
                "name": "水电",
                "id": "3"
            },
            {
                "name": "火电",
                "id": "4"
            },
            {
                "name": "核电",
                "id": "5"
            },
            {
                "name": "生物质",
                "id": "6"
            },
            {
                "name": "虚拟电厂",
                "id": "7"
            },
            {
                "name": "其他",
                "id": "8"
            },
            {
                "name": "太阳能",
                "id": "9"
            }
        ]

dataItemDic = {
    "001":  {
        "name" : "原始短期功率预测",
        "type" : "场站发电数据"
    },
    "101":  {
        "name" : "申报短期功率预测",
        "type" : "场站发电数据"
    },

    "401":  {
        "name" : "中长期总加曲线",
        "type" : "省内现货交易"
    },
    "402":  {
        "name" : "日前出力计划",
        "type" : "省内现货交易"
    },
    "403":  {
        "name" : "日内出力计划",
        "type" : "省内现货交易"
    },
    "405":  {
        "name" : "日内出力计划",
        "type" : "省内现货交易"
    },
    "406":  {
        "name" : "日内节点电价",
        "type" : "省内现货交易"
    },
    "1001":  {
        "name" : "中长期基数电量",
        "type" : "省内现货交易"
    },
    "301": {
        "name": "省间日前结算电价",
        "type": "省间现货交易"
    },
    "302": {
        "name": "省间日前结算电量",
        "type": "省间现货交易"
    },
    "304": {
        "name": "省间日内结算电价",
        "type": "省间现货交易"
    },
    "305": {
        "name": "省间日内结算电量",
        "type": "省间现货交易"
    },
}

def getBusinessTypeStr(businessTypeId):

    for b in businessType:
        if businessTypeId == b["id"]:
            return b["name"]
    return None


class Shanxi:

    def __init__(self,session, info):
        self.domain = None
        self.loginInfo = None
        self.session = session
        self.domain = info['url_domain']
        self.loginInfo = info['logininfo']


    def login(self):
        CommonClass.login(self.session, self.domain, self.loginInfo)

    def getUnit(self):
        url = self.domain + "/sxAdss/api/common/user/list"
        method = "GET"

        res = CommonClass.execRequest(self.session, method=method, url=url).json()['data'][0]["orgOsDetailDTOS"]
        unitsInfo = []

        for r in res:
            unitsInfo.append(
                {
                    "unitId" : r['osOrgId'],
                    "unitName" : r['osOrgName'],
                    "businessType" : getBusinessTypeStr(r['businessType']),
                }
            )
        return unitsInfo

if __name__ == '__main__':


    info = {
        "url_domain" :  "https://adssx-test-gzdevops3.tsintergy.com",
        "logininfo" : {
            "publicKey_url" :  None,
            "login_url" :  "/usercenter/web/login",
            "switch_url" :  "/usercenter/web/switchTenant?tenantId=8280818779cb82450179cb8422a30000" ,
            "username" :  "zhanzw_czc",
            "password" :  "passwd123@",
            "loginMode" :  2,
        },
    }


    testSession = requests.Session()
    sx = Shanxi(testSession,info)
    sx.login()

    pass

