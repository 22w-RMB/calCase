
from common.common import CommonClass


hn_private_data_path  = CommonClass.mkDir( *["hn" , "output","private_data"],isGetStr=True)

hn_tem_path  = CommonClass.mkDir( *["hn" , "template"],isGetStr=True)




def generateUnit(count,prefix=""):

    unitNames = []

    prefix = prefix + "#"

    for i in range(0,count):

        unitNames.append( prefix + str(i+1)  )

    return  unitNames


def outputPrivateData(units, startDate, endDate, templateInfo):


    for unit in units:

        filename = unit[unitName]



    pass




# print(hn_private_data_path)


if __name__ == '__main__':
    print(generateUnit(4, prefix="华苏"))




