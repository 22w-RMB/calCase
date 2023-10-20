from jituance.集团小程序.mysql_tool import MysqlTool

businessTypeDict = {
    "全能源类型" :  "energy",
    "火电" :  1,
    "水电" :  2,
    "风电" :  4,
    "光伏" :  3,
}

provinceId = {
	"天津":  12,
	"河北":  13,
	"山西":  14,
	"蒙西":  15,
	"蒙东":  150,
	"辽宁":  21,
	"吉林":  22,
	"黑龙江":  23,
	"福建":  35,
	"四川":  51,
	"西藏":  54,
	"陕西":  61,
	"甘肃":  62,
	"青海":  63,
	"宁夏":  64,
	"新疆":  65,
    "山西" :14,
    "广东": 44,
    "甘肃": 62,
    "山东": 37,
    "蒙西" :15,
    "全集团" :"group",
}



class XiaoChengXu:

    def __init__(self):

        db = MysqlTool()
        self.provicneBetweenPrivateData = db.queryProvicneBetweenPrivateData()
        self.provicneInnerPrivateData = db.queryProvicneInnerPrivateData()
        db.close()

    # 计算省内私有数据
    def calProvicneInnerPrivateData(self):

        pass


    # 转化数据
    def dataProcess(self):

        self.transformStringToList(self.provicneBetweenPrivateData)
        self.transformStringToList(self.provicneInnerPrivateData)

        pass

    # 将数据库取到的电量、电价字符串转换成python中的数据结果
    def transformStringToList(self,dataList):

        for data in dataList:
            # 需要转化的字段包含的字符
            needTransformString = ["ele" , "price","run_capacity","change_cost"]

            for key in data.keys():
                for i in needTransformString:
                    if i in "key" and data[key] != None:
                        # null替换成None后，python才能识别转化
                        data[key] = eval( data[key].replace("null","None") )


        pass

    def executeMain(self,province,energy,startDate,endDate):




        pass

