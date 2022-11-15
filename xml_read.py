#!/usr/bin/evn python
# coding:utf-8

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
import sys

def get_xml_root(file):
    try:
        tree = ET.parse(file)  # 打开xml文档
        # root = ET.fromstring(country_string) #从字符串传递xml
        root = tree.getroot()  # 获得root节点
    except Exception as e:
        print("Error:cannot parse file:%s"%file +str(e))
        root = ''
        # sys.exit(1)
    return root

root = get_xml_root(file='testjian.xml')

print(root.tag, "---", root.attrib)
for child in root:
    print(    child.tag, "---", child.attrib)

print("*" * 10)
print(root[0][1].text   )# 通过下标访问
print(root[0].tag, root[0].text)

print("*" * 10)

for country in root.findall('country'):  # 找到root节点下的所有country节点
    rank = country.find('rank').text  # 子节点下节点rank的值
    name = country.get('name')  # 子节点下属性name的值
    print( name, rank )
root[2][0][0].tag+str(root[2][0][0].attrib)