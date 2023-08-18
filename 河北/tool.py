



class Tool:

    @staticmethod
    def data96To24list(dataList):


        data24List = [0 for i in range(0,24) ]

        if dataList == None:
            return data24List

        for i in range(0,24):

            tempL =  dataList[i*4:(i+1)*4]

            data24List[i] = sum( tempL)/len(tempL)


        return data24List

    @staticmethod
    def time96To24list(timeList):


        time24List = [0 for i in range(0,24) ]
        count = 0

        if timeList == None:
            return {
                "time24List": time24List,
                "count": count
            }

        # 处理00:00 开始的，如00:00-00:45

        for d in timeList:
            tempList = d.split("-")

            begin = int(tempList[0][:2])
            end = int(tempList[1][:2])


            while begin<=end:
                time24List[begin] = 1
                begin += 1
                count += 1

        return {
            "time24List": time24List,
            "count": count
        }


    @staticmethod
    def time24o24list(timeList):

        time24List = [0 for i in range(0,24) ]
        count = 0

        # 处理00:00 开始的，如00:00-01:00
        if time24List == None:
            return {
                "time24List": time24List,
                "count": count
            }


        for d in timeList:
            tempList = d.split("-")

            begin = int(tempList[0][:2])
            end = int(tempList[1][:2])-1


            while begin<=end:
                time24List[begin] = 1
                begin += 1
                count += 1

        return {

            "time24List":time24List,
            "count" : count
        }


if __name__ == '__main__':

    # test = ["00:00-00:45","20:00-23:45"]
    #
    # print(Tool.time96To24list(test))

    # test1 = ["17:00-19:00"]
    # a = str(test1)

    # print(Tool.time24o24list(test1))

    # print(a)
    # print(type(eval(a)))

    print(str(None))
    pass