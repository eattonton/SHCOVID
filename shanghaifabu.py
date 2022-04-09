# -*- coding: utf-8 -*-
import os, sys
import json
import requests
import time,datetime
import re
import codecs
from bs4 import BeautifulSoup
from pypinyin import lazy_pinyin

userAgent = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36"
rootUrl = "mp.weixin.qq.com"

header1 = {
    'Host':rootUrl,
    'Connection':'keep-alive',
    'User-Agent':userAgent
}

def __getWebHtml(url):
    if url:
        data = requests.get(url=url, headers = header1)
        return data.text
    return ""

def _write(fNa, data, fileCode='utf-8', startpos=0):
    bres = False
    try:  
        with codecs.open(fNa,'w+',fileCode) as f:
            if startpos != 0:
                f.seek(startpos)
            f.write(data)
            bres = True
    except:
        print("except")
        bres = False
    return bres

def _read(fNa, fileCode='utf-8'):
    try:  
        with codecs.open(fNa,'r',fileCode) as f:
            return f.read()
    except:
        return ''

def _readJson(fNa, fileCode='utf-8'):
    sdata = _read(fNa,fileCode)
    sdata = sdata.replace('\ufeff','').replace('\r\n','')
    if sdata:
        return json.loads(sdata)
    return {}

def GetSpanLines(url):
    arr1 = []
    content = __getWebHtml(url)
    soup = BeautifulSoup(content, 'lxml')  # 使用lxml解析器
    divContent = soup.findAll('div',id='js_content')
    pItems = divContent[0].findAll('p')
    for pItem in pItems:
        spanItem = pItem.findAll('span', style="font-size: 16px;")
        if spanItem:
            if spanItem and spanItem[0].string:
                arr1.append(spanItem[0].string)
            elif spanItem[0].contents and len(spanItem[0].contents) > 0:
                str1=""
                for sp1 in spanItem[0].contents:
                    if sp1.string:
                        str1 = str1 + sp1.string
                if str1:
                    arr1.append(str1)
    return arr1
 
if __name__ == "__main__":
    urls = []
    urls.append({"d":"2022-04-01","url":"https://mp.weixin.qq.com/s/gQDyFLtdILP2NuSBgcjUxg"})
    urls.append({"d":"2022-04-02","url":"https://mp.weixin.qq.com/s/2VWTo6e9gmWJ0vxeZ4PhIw"})
    urls.append({"d":"2022-04-03","url":"https://mp.weixin.qq.com/s/uj4TYASUn2YJZQMg2aUvdw"})
    urls.append({"d":"2022-04-04","url":"https://mp.weixin.qq.com/s/MkKsQkgvUWbwj8z9jG_Zng"})
    urls.append({"d":"2022-04-05","url":"https://mp.weixin.qq.com/s/djwW3S9FUYBE2L5Hj94a3A"})
    urls.append({"d":"2022-04-06","url":"https://mp.weixin.qq.com/s/8bljTUplPh1q4MXb6wd_gg"})
    urls.append({"d":"2022-04-07","url":"https://mp.weixin.qq.com/s/HTM47mUp0GF-tWXkPeZJlg"})
    urls.append({"d":"2022-04-08","url":"https://mp.weixin.qq.com/s/79NsKhMHbg09Y0xaybTXjA"})
    objResult = {}
    #读取原先的数据
    obj1 = _readJson("./example.json")
    if obj1:
        objResult = obj1
    childrens = objResult.get("childrens",[])
    zones=objResult.get("zones",["浦东新区","黄浦区","静安区","徐汇区","长宁区","普陀区","虹口区","杨浦区","宝山区","闵行区","嘉定区","金山区","松江区","青浦区","奉贤区","崇明区"])
    #检索区域
    def findzone(str1):
        for strZone in zones:
            if strZone in str1:
                return strZone
        return ""

    #检索是否存在原先的记录
    def findarea(strDate, strZone, strArea):
        if not strArea:
            return
        if "年" in strArea and "月" in strArea and "日" in strArea:
            return
        for oArea in childrens:
            if oArea["area"] == strArea:
                if strDate not in oArea["d"]:
                    oArea["d"].append(strDate)
                return oArea
        childrens.append({"d":[strDate],"zone":strZone,"area":strArea})
        return childrens[-1]

    zone1 = ""
    for oUrl in urls:
        arr2 = GetSpanLines(oUrl["url"])
        for str2 in arr2:
            if str2:
                zone2 = findzone(str2)
                if zone2 != "":
                    zone1 = zone2
                if zone1 != "" and isinstance(str2,str) and len(str2) < 20 and "落实终末消毒措施" not in str2:
                    findarea(oUrl["d"], zone1, str2.replace(' ', '').replace('，', '').replace('。', '').replace('、', '').replace(',', '').replace('\u00a0',''))

    if childrens and len(childrens) > 0:
        #排序
        childrens.sort(key=lambda x: (lazy_pinyin(x["area"][0])[0][0],lazy_pinyin(x["area"][1])[0][0]))
        #输出
        objResult["zones"]=zones
        objResult["childrens"]=childrens
        _write("./example.json", json.dumps(objResult, sort_keys=False, ensure_ascii=False, separators=(',', ':')))