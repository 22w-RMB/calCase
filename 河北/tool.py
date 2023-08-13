



class tool:


    @staticmethod
    def time96To24list(timeList):

        time24List = [0 for i in range(0,24) ]

        # 处理00:00 开始的，如00:00-00:45

        for d in timeList:
            tempList = d.split("-")

            begin = int(tempList[0][:2])
            end = int(tempList[1][:2])


            while begin<=end:
                time24List[begin] = 1
                begin += 1

        return time24List


    @staticmethod
    def time24o24list(timeList):

        time24List = [0 for i in range(0,24) ]

        # 处理00:00 开始的，如00:00-01:00

        for d in timeList:
            tempList = d.split("-")

            begin = int(tempList[0][:2])
            end = int(tempList[1][:2])-1


            while begin<=end:
                time24List[begin] = 1
                begin += 1

        return time24List


if __name__ == '__main__':

    test = ["00:00-00:45","20:00-23:45"]

    print(tool.time96To24list(test))

    test1 = ["00:00-02:00","03:00-06:00"]

    print(tool.time24o24list(test1))
