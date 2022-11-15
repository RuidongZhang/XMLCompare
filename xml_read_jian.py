#!/usr/bin/evn python
# coding:utf-8
import os
import sys
import time
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

def get_xml_root(file):
    try:
        tree = ET.parse(file)  # 打开xml文档
        # root = ET.fromstring(country_string) #从字符串传递xml
        root = tree.getroot()  # 获得root节点
        dic1=dic2={}
        for child in root:
            if 'RequestReference' in child.tag:
                dic1= child.attrib
                dic1['Timestamp0'] = dic1['Timestamp'].split('.')[0]
            elif 'LotStatus' in child.tag:
                dic2= child.attrib
                break
        root = {**dic1, **dic2}
    except Exception as e:
        print("Error:cannot parse file:%s"%file +str(e))
        root = ''
        # sys.exit(1)
    return root

def readFolder(path):
    list = os.listdir(path.replace('\n', ''))
    return list

def main_work():
    path = os.getcwd()+'\\\\'
    files =  readFolder(path)
    files = [each for each in files if '.xml' in each]
    import pandas as pd
    lis = []
    df = pd.DataFrame()

    for file in files:
        dics={'File':file}
        try:
            dic = get_xml_root(file=file)
            dics.update(dic)
        except Exception as e:
            pass

        df = df.append(dics, ignore_index=True)
    times=time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())
    df.to_csv('result-%s.csv' % times)

    print("*" * 10)


seconds = 10
try:
    main_work()
    print('finish')
    time.sleep(seconds)

except Exception as e:
    print(e, 'Error:main')
    time.sleep(seconds)