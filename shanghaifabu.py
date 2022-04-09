# coding:utf-8
import os, sys
import json
import requests
import time,datetime
import re
import codecs
from bs4 import BeautifulSoup

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
    return arr1
 
if __name__ == "__main__":
    urls = [{"d":"2022-04-07","url":"https://" +rootUrl+"/s/HTM47mUp0GF-tWXkPeZJlg"}]
    arr1 = []
    zones=["浦东新区","黄浦区","静安区","徐汇区","长宁区","普陀区","虹口区","杨浦区","宝山区","闵行区","嘉定区","金山区","松江区","青浦区","奉贤区","崇明区"]
    def findzone(str1):
        for strZone in zones:
            if strZone in str1:
                return strZone
        return ""

    zone1 = ""
    for oUrl in urls:
        arr2 = GetSpanLines(oUrl["url"])
        for str2 in arr2:
            if str2:
                zone2 = findzone(str2)
                if zone2 != "":
                    zone1 = zone2
                if zone1 != "":
                    arr1.append({"d":[oUrl["d"]],"zone":zone1,"area":str2})

    if arr1 and len(arr1) > 0:
        _write("./shcovid/example.json", json.dumps(arr1, sort_keys=True, ensure_ascii=False, separators=(',', ':')))