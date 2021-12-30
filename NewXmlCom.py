import difflib
a='E:\\XMLCompare\\FT\\A\\DV57833_CP1_PHN_Release_20210220112021.xml'
b='E:\\XMLCompare\\FT\\B\\DV57833_CP1_PHN_Release_20210220112111.xml'

a=open(a,'r',encoding='utf-8').readlines()
for each in a:
    if
b=open(b,'r',encoding='utf-8').readlines()



r=difflib.HtmlDiff().make_file(fromlines=a,tolines=b)
c=open('result11.html',mode='x',encoding='utf-8')
c.write(r)
c.close()