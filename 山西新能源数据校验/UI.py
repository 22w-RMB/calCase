import os
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from functools import partial
from 山西新能源数据校验.test import *
from threading import Thread


def getYaml():
    yamlPath = CommonClass.mkDir("山西新能源数据校验",  "config", "config.yaml", isGetStr=True)
    configData = CommonClass.readYaml(yamlPath)
    print(configData)
    return configData

def getConfigType(configData):


    return [i for i in configData.keys()]


def long_running_task(select,entry,but):
    # 模拟一个耗时的任务
    but.config(state=tk.DISABLED)
    try:
        configData = getYaml()
        selectV = select.get()
        domain = configData[selectV]["domain"]
        publicKey_url = None if configData[selectV]["public_key"] == "无" else "/usercenter/web/pf/login/info/publicKey"

        username = entry["账号"].get()
        password = entry["密码"].get()
        tenantId = entry["企业id"].get()
        startDate = entry["开始日期"].get()
        endDate = entry["结束日期"].get()

        info = {
            "url_domain": domain,
            "logininfo": {
                "publicKey_url": publicKey_url,
                "login_url": "/usercenter/web/login",
                "switch_url": "/usercenter/web/switchTenant?tenantId=",
                "username": username,
                "password": password,
                "loginMode": 2,
            },
            "tenantId": tenantId,
        }

        testSession = requests.Session()
        sx = Shanxi(testSession, info)
        sx.login()

        sx.execMain(startDate, endDate)
        messagebox.showinfo("提示", "执行成功！")
    except Exception as e:
        messagebox.showerror("错误", "执行出错，请查看参数是否正确！")
    finally:
        but.config(state=tk.ACTIVE)



def open_folder(savePath):
    try:
        os.startfile(savePath)  # 替换为你想打开的文件夹路径
    except Exception as e:
        messagebox.showerror('找不到指定目录')

def on_button_click(select,entry,but):


    a = Thread(target=long_running_task,args=(select,entry,but))
    a.start()


# 创建一行文本标签和输入框
def createLabelAndEntry(frame,row,describe,px,py):

    label1 = tk.Label(frame, text=describe+"：")
    label1.grid(row=row, column=0, sticky=tk.W, padx=px, pady=py)  # 文本标签靠左
    entry1 = tk.Entry(frame,)
    entry1.grid(row=row, column=1, sticky=tk.EW, padx=px, pady=py)  # 输入框水平扩展

    return entry1

#输入框设置数据
def setEntryValue(entry1,v):
    entry1.delete(0, tk.END)  # 清空原有内容
    entry1.insert(0, v)  # 插入新内容

# 创建下拉框
def setupCombobox(frame,row,describe,px,py,v):

    label1 = tk.Label(frame, text=describe + "：")
    label1.grid(row=row, column=0, sticky=tk.W, padx=px, pady=py)  # 文本标签靠左
    combobox = ttk.Combobox(frame, values=[],width=10, state='readonly', )
    combobox.grid(row=row, column=1, sticky=tk.EW, padx=px, pady=py)  # 输入框水平扩展


    combobox['values'] = v
    combobox.current(0)

    return combobox

def on_combo_change(event,param1,param2,param3):
    # 获取下拉框选中的值
    selected_value = param1.get()
    # 根据选中的值设置输入框的状态

    for data in param3.keys():

        if selected_value == data:
            setEntryValue(param2,param3[data]["tenantId"])
            return


def ini():
    configData = getYaml()

    # 创建主窗口
    root = tk.Tk()
    root.title("Tkinter Example")

    # 设置窗口大小为400x300像素
    root.geometry("400x300")

    px = 5
    py = 5


    # 创建一个框架来容纳所有控件，以便更容易地管理内边距和居中
    frame = tk.Frame(root, padx=20, pady=20)  # 设置内边距
    frame.grid(row=0, column=0, sticky=tk.NSEW)  # 框架填满整个窗口，并允许扩展
    frame.grid_rowconfigure(1, weight=1)  # 在输入框之间添加额外的空间（可选）

    com = setupCombobox(frame, 1, "下拉框", px, py,getConfigType(configData))

    entryDic = {
        "企业id" : createLabelAndEntry(frame, 2, "企业id", px, py),
        "账号" : createLabelAndEntry(frame, 3, "账号", px, py),
        "密码" : createLabelAndEntry(frame, 4, "密码", px, py),
        "开始日期" : createLabelAndEntry(frame, 5, "开始日期", px, py),
        "结束日期" : createLabelAndEntry(frame, 6, "结束日期", px, py),
    }

    # print(com.get())

    setEntryValue(entryDic["企业id"], configData[com.get()]["tenantId"])
    com.bind("<<ComboboxSelected>>", partial(on_combo_change, param1=com, param2=entryDic["企业id"],param3=configData))

    button = tk.Button(frame, text="开始执行")
    button.config(command=partial(on_button_click, com, entryDic,button))
    button.grid(row=7, column=0, columnspan=2, sticky=tk.EW, padx=px, pady=py)  # 跨两列并水平扩展

    button1 = tk.Button(frame, text="打开输入文件夹")
    savePath = CommonClass.mkDir("山西新能源数据校验",  "导出", isGetStr=True)

    button1.config(command=partial(open_folder, savePath))
    button1.grid(row=8, column=0, columnspan=2, sticky=tk.EW, padx=px, pady=py)  # 跨两列并水平扩展

    # 运行主事件循环
    root.mainloop()

if __name__ == '__main__':


   ini()
    # getYaml()