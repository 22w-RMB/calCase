import random

from common.common import CommonClass


hn_private_data_path  = CommonClass.mkDir( *["hn" , "output","private_data"],isGetStr=True)

hn_tem_path  = CommonClass.mkDir( *["hn" , "template"],isGetStr=True)



def generateUnit(count,prefix=""):

    unitList = []

    prefix = prefix + "#"

    for i in range(0,count):

        unitList.append(
            {
                "unitName" : prefix + str(i+1),
                "businessType" : CommonClass.randomBusinessType(),
            }
             )

    return  unitList


def outputPrivateData(units, startDate, endDate, templateInfo):


    for unit in units:

        # filename = unit[unitName]


        pass


    pass




# print(hn_private_data_path)


if __name__ == '__main__':
    print(generateUnit(4, prefix="华苏"))




