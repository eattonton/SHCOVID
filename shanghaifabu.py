# -*- coding: utf-8 -*-
import os, sys
import json
import requests
import time,datetime
import re
import codecs
from bs4 import BeautifulSoup
from pypinyin import lazy_pinyin
import zipfile

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
    if url:
        content = __getWebHtml(url)
        soup = BeautifulSoup(content, 'lxml')  # 使用lxml解析器
        divContent = soup.findAll('div',id='js_content')
        pItems = divContent[0].findAll('p')
        for pItem in pItems:
            #spanItem = pItem.findAll('span',{'style':'font-size: 16px;'})
            spanItems = pItem.findAll('span')
            if spanItems:
                for spanItem in spanItems:
                    if 'font-size: 16px;' in str(spanItem) and 'data-src' not in str(spanItem):
                        if spanItem and spanItem.string:
                            arr1.append(spanItem.string)
                        elif spanItem.contents and len(spanItem.contents) > 0:
                            str1=""
                            for sp1 in spanItem.contents:
                                if sp1.string:
                                    str1 = str1 + sp1.string
                            if str1:
                                arr1.append(str1)
    return arr1

def GetSpanLines2(url):
    arr1 = []
    if url:
        content = __getWebHtml(url)
        soup = BeautifulSoup(content, 'lxml')  # 使用lxml解析器
        divContent = soup.findAll('div',id='js_content')
        pItems = divContent[0].findAll('p')
        for pItem in pItems:
            spanItem = pItem.findAll('span')
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

#读取上海新冠数据
def GetSHCOVIDJSON(urls,file2):
    objResult = {}
    #读取原先的数据
    obj1 = _readJson(file2)
    if obj1:
        objResult = obj1
    childrens = objResult.get("childrens",[])
    zones=objResult.get("zones",["浦东新区","黄浦区","静安区","徐汇区","长宁区","普陀区","虹口区","杨浦区","宝山区","闵行区","嘉定区","金山区","松江区","青浦区","奉贤区","崇明区"])
    history= objResult.get("history",[])
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
        if "更多" in strArea or "消毒" in strArea:
            return
        for oArea in childrens:
            if oArea["area"] == strArea and oArea["zone"] == strZone:
                if strDate not in oArea["d"]:
                    oArea["d"].append(strDate)
                return oArea
        childrens.append({"d":[strDate],"zone":strZone,"area":strArea})
        return childrens[-1]

    zone1 = ""
    for oUrl in urls:
        #判断是否已经读取过
        if oUrl["d"] in history:
            continue
        history.append(oUrl["d"])
        arr2 = GetSpanLines(oUrl["url"])
        for str2 in arr2:
            if str2:
                zone2 = findzone(str2)
                if zone2 != "":
                    zone1 = zone2
                if zone1 != "" and isinstance(str2,str) and len(str2) < 20:
                    findarea(oUrl["d"], zone1, str2.replace(' ', '').replace('，', '').replace('。', '').replace('、', '').replace(',', '').replace('\u00a0',''))

    if childrens and len(childrens) > 0:
        #排序
        childrens.sort(key=lambda x: (lazy_pinyin(x["area"][0])[0],lazy_pinyin(x["area"][1])[0]))
        #输出
        objResult["zones"]=zones
        objResult["childrens"]=childrens
        objResult["history"]=history
        _write(file2, json.dumps(objResult, sort_keys=False, ensure_ascii=False, separators=(',', ':')))
    return file2

#根据各个发布平台的数据读取
def GetSHCOVIDJSONSByZone(urls2,file2):
    for oUrl2 in urls2:
        strDate0 = oUrl2["d"]
        for oUrl in oUrl2["urls"]:
            zone1 = oUrl["zone"]
            arr2 = GetSpanLines2(oUrl["url"])
            print(zone1,arr2)

def ZipJSON(file1):
    _name = os.path.join(os.path.basename(file1))
    _name2 = _name.split('.')[0]+".zip"
    file2 = "./"+_name2
    with zipfile.ZipFile(file2, "w", compression=zipfile.ZIP_DEFLATED) as zip:
        if (os.path.exists(file1)):
            zip.write(file1, arcname=_name)
        else:
            print("file not exist %s" % file1)
        zip.close()

if __name__ == "__main__":
    urls = []
    urls.append({"d":"2022-03-25","url":"https://mp.weixin.qq.com/s/XG03jIjQLLLjaJZ1DD-kAg"})
    urls.append({"d":"2022-03-26","url":"https://mp.weixin.qq.com/s/JwUn4sVxSvHQs5KoyFn-lw"})
    urls.append({"d":"2022-03-27","url":"https://mp.weixin.qq.com/s/MfBzdO0bG4fbokKTRCWuIw"})
    urls.append({"d":"2022-03-28","url":"https://mp.weixin.qq.com/s/656rotFOMeDScnKSt6OmyQ"})
    urls.append({"d":"2022-03-29","url":"https://mp.weixin.qq.com/s/K6jT1wRMSScBhvxcB2yV4g"})
    urls.append({"d":"2022-03-30","url":"https://mp.weixin.qq.com/s/SSFVzOSXPTj-aLzR1tdtxw"})
    urls.append({"d":"2022-03-31","url":"https://mp.weixin.qq.com/s/hnrGo4KvUvxhpjFyiE8-sQ"})
    urls.append({"d":"2022-04-01","url":"https://mp.weixin.qq.com/s/gQDyFLtdILP2NuSBgcjUxg"})
    urls.append({"d":"2022-04-02","url":"https://mp.weixin.qq.com/s/2VWTo6e9gmWJ0vxeZ4PhIw"})
    urls.append({"d":"2022-04-03","url":"https://mp.weixin.qq.com/s/uj4TYASUn2YJZQMg2aUvdw"})
    urls.append({"d":"2022-04-04","url":"https://mp.weixin.qq.com/s/MkKsQkgvUWbwj8z9jG_Zng"})
    urls.append({"d":"2022-04-05","url":"https://mp.weixin.qq.com/s/djwW3S9FUYBE2L5Hj94a3A"})
    urls.append({"d":"2022-04-06","url":"https://mp.weixin.qq.com/s/8bljTUplPh1q4MXb6wd_gg"})
    urls.append({"d":"2022-04-07","url":"https://mp.weixin.qq.com/s/HTM47mUp0GF-tWXkPeZJlg"})
    urls.append({"d":"2022-04-08","url":"https://mp.weixin.qq.com/s/79NsKhMHbg09Y0xaybTXjA"})
    urls.append({"d":"2022-04-09","url":"https://mp.weixin.qq.com/s/_Je5_5_HqBcs5chvH5SFfA"})
    urls.append({"d":"2022-04-10","url":"https://mp.weixin.qq.com/s/u0XfHF8dgfEp8vGjRtcwXA"})
    urls.append({"d":"2022-04-11","url":"https://mp.weixin.qq.com/s/vxFiV2HeSvByINUlTmFKZA"})
    file1 = GetSHCOVIDJSON(urls, "./sh.json")
    ZipJSON(file1)
    #arr1 = GetSpanLines("https://mp.weixin.qq.com/s/u0XfHF8dgfEp8vGjRtcwXA")
    #print(arr1)
    #2022-04-09
    urls2 = []
    urls2.append({"d":"2022-04-09","urls":[{"zone":"浦东新区","url":"https://mp.weixin.qq.com/s/RpjLh0WT7KONsniM1dMYZQ"}
                                        ,{"zone":"黄浦区","url":"https://mp.weixin.qq.com/s/mN33_Vz-KfkgF84htTQ8dw"}
                                        ,{"zone":"静安区","url":"https://mp.weixin.qq.com/s/1utEBCXRSfRByj9N26e_5Q"}
                                        ,{"zone":"徐汇区","url":"https://mp.weixin.qq.com/s/6rjFiePzmWK2Qukj0iuGZA"}
                                        ,{"zone":"长宁区","url":"https://mp.weixin.qq.com/s/DH9QDy6hBM93inLIfgHh4g"}
                                        ,{"zone":"普陀区","url":"https://mp.weixin.qq.com/s/pao19i6t--4NJLP4nDGFYg"}
                                        ,{"zone":"虹口区","url":"https://mp.weixin.qq.com/s/_3ClkLBV-BihWOdhnis23Q"}
                                        ,{"zone":"杨浦区","url":"https://mp.weixin.qq.com/s/6_Jjsr0JZfbBP4MTVCwmug"}
                                        ,{"zone":"宝山区","url":"https://mp.weixin.qq.com/s/NUBmVXRQEZUwCngi8nIZjQ"}
                                        ,{"zone":"闵行区","url":"https://mp.weixin.qq.com/s/skg1jQ4Yq4o16e1FnXPrug"}
                                        ,{"zone":"嘉定区","url":"https://mp.weixin.qq.com/s/bvs5rvv4fKaY3p4VPeqGIQ"}
                                        ,{"zone":"金山区","url":""}
                                        ,{"zone":"松江区","url":"https://mp.weixin.qq.com/s/w4sBIrT9jYpvNd4QwpHLYQ"}
                                        ,{"zone":"青浦区","url":"https://mp.weixin.qq.com/s/WYLeKd6sWJ6cd6a7a6nGqA"}
                                        ,{"zone":"奉贤区","url":"https://mp.weixin.qq.com/s/tWB5aXSayxWh763kPiSShw"}
                                        ,{"zone":"崇明区","url":"https://mp.weixin.qq.com/s/OtMHyuC9xT0pKj5m0yhiIA"}]
                })
    #GetSHCOVIDJSONSByZone(urls2, "")