import pandas as pd

class ExcelHepler:


    def __init__(self , filePath=None,sheetName=0,header=None,**kwargs):

        if filePath != None:

            self.df = pd.read_excel(io=filePath,sheet_name=sheetName,index_col=None,header=None,names=header,keep_default_na=False,*kwargs)
            # print(self.df)
            # print(dataFrame["1-电量"])
            # for row in self.df.itertuples(index=False):
                # print(getattr(row,"1-电量"))
                # print(row)

    def getDayEleDetail(self):

        return self.df




    def close(self):
        pass


if __name__ == '__main__':
    path = r"D:\code\python\calCase\江西\导入文件\xx电厂-合同日电量明细-YYYY.xls"
    e = ExcelHepler(path, "合同分月查询结果")

    pass