import json
import os
import sys
import time
import pandas as pd
import requests
import ddddocr,time
from util.MysqlHelper import MysqlHelper
from util.min_io import upload_minio
from urllib.parse import urlparse
import uiautomator2 as u2
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from util.MysqlHelper import MysqlHelper
from PIL import Image
import threading
import sched
import urllib.request
from lxml import etree
import urllib.request
from lxml import etree
import time
import requests
import datetime
import os
from urllib import request

DB_CONFIG = {
    "host": '127.0.0.1',
    "port": 3306,
    "user": 'root',
    "password": 'root',
    "db": 'byquick',
    "charset": 'utf8'
}

db = MysqlHelper(DB_CONFIG)

def main():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.63'
    }
    sql ="SELECT t.sec_shop_id,t.shopname,t.id FROM amp_shop_marketentity t where t.medianame='京东' and t.sec_shop_id IS NOT NULL and t.id>=149042"
    result = db.select(sql)
    for ob in result:
        try:
            shop_id = ob[0]
            shop_name = ob[1]
            id=ob[2]
            url = "https://mall.jd.com/index-%s.html" % (shop_id)
            # 先创建request
            request = urllib.request.Request(url=url, headers=headers)
            # 返回HttpResponse类型
            response = urllib.request.urlopen(request)
            content = response.read().decode('utf-8')
            tree = etree.HTML(content, parser=etree.HTMLParser(encoding='utf8'))
            # logo地址
            result3 = tree.xpath("//body/img[1]/@src")

            path_log = 'D:/douyin_data/jingdong/logo/'
            if not os.path.exists(path_log):
                os.makedirs(path_log)
            file_name = '%s_logo.png' % (id)
            if len(result3)==0:
                continue
            url1 = str(result3[0])
            type=url1[-3:]
            if type == 'gif':
                file_name = '%s_logo.gif' % (id)
                print(file_name)
            path = path_log + file_name
            url2 = 'https:%s' % (url1)
            opener = urllib.request.build_opener()
            opener.addheaders = [('User-agent',
                                  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36')]
            urllib.request.install_opener(opener)
            urllib.request.urlretrieve(url2, path)

        except:
            print("Error!")

def handle2():
    folder_path = "D:/douyin_data/jingdong/logo/"
    file_names = os.listdir(folder_path)
    for file_name in file_names:
        str1 = '_'
        index = file_name.index(str1)
        shop_id = file_name[0:index]
        cret_name = 'jingdong/%s' % (file_name)
        upload_minio('logo', cret_name, folder_path + file_name)
        sql1 = "update amp_shop_marketentity t set t.logopath='%s' where t.id='%s'" % (
            cret_name, shop_id)
        db.execute_sql(sql1)

def handle1():
    folder_path = "D:/douyin_data/jingdong/license/"
    file_names = os.listdir(folder_path)
    today = datetime.datetime.today()
    date = today.date()
    date = str(date)
    date = date.replace("-", "")
    for file_name in file_names:
        try:
            str1 = '_'
            index = file_name.index(str1)
            shop_id = file_name[0:index]
            cret_name = 'jingdong/%s/%s' % (date,file_name)
            upload_minio('license', cret_name, folder_path + file_name)
            sql1 = "update amp_shop_marketentity t set t.certpath='%s' where t.id='%s'" % (
                cret_name, shop_id)
            db.execute_sql(sql1)
        except:
            print("error")

def se():
    wd = webdriver.Edge(service=Service(r'D:/douyin_data/msedgedriver.exe'))
    wd.get('https://www.jd.com/')
    wd.implicitly_wait(3)
    sql = "SELECT t.shopname,t.id FROM amp_shop_marketentity t WHERE t.id>=149042 AND t.medianame='京东' and t.sec_shop_id IS NULL"
    sql1= "SELECT t.liveroomname,t.id FROM amp_illege_liveroom t WHERE t.medianame='京东' AND  t.certpath IS NULL and t.liveroomcompany is null"
    result = db.select(sql)
    time.sleep(25)
    for ob in result:
        try:
            shop_name = ob[0]
            id = ob[1]
            inpu = wd.find_element(By.XPATH, "//input[@id='key']")
            inpu.clear()
            inpu.send_keys(shop_name)
            button = wd.find_element(By.XPATH,
                                "//button[contains(text(),'搜索')]")
            button.click()
            time.sleep(2)

            name_path = wd.find_element(By.XPATH,
                                        "//div[@id='J_goodsList']/ul/li[1]//div[@class='p-shop']/span[1]/a[1]")
            name = name_path.get_attribute('title')
            if name != shop_name:
                name_path = wd.find_element(By.XPATH,
                                            "//div[@id='J_goodsList']/ul/li[2]//div[@class='p-shop']/span[1]/a[1]")
                name = name_path.get_attribute('title')

            shop_herf_ele = name_path.get_attribute('href')
            shop_herf = str(shop_herf_ele)
            if name == shop_name:
                str1 = 'index-'
                str2 = '.html'
                index1 = shop_herf.index(str1)
                index2 = shop_herf.index(str2)
                shop_id = shop_herf[index1 + 6:index2]
                # sql = 'update amp_shop_marketentity t set t.sec_shop_id="%s" where t.id="%s"' % (
                #     shop_id, id)
                # db.execute_sql(sql)
                sql1 = 'update amp_shop_marketentity t set t.sec_shop_id="%s" where t.id="%s"' % (
                    shop_id, id)
                db.execute_sql(sql1)
            else:
                print('名称不一致')
                continue

        except:
            try:
                name_path = wd.find_element(By.XPATH,
                                            "//div[@id='J_goodsList']/ul/li[2]//div[@class='p-shopnum']/a[1]")
                name = name_path.get_attribute('title')
                if name != shop_name:
                    name_path = wd.find_element(By.XPATH,
                                                "//div[@id='J_goodsList']/ul/li[2]//div[@class='p-shopnum']/a[1]")
                    name = name_path.get_attribute('title')

                shop_herf_ele = name_path.get_attribute('href')
                shop_herf = str(shop_herf_ele)
                if name == shop_name:
                    str1 = 'index-'
                    str2 = '.html'
                    index1 = shop_herf.index(str1)
                    index2 = shop_herf.index(str2)
                    shop_id = shop_herf[index1 + 6:index2]
                    # sql = 'update amp_shop_marketentity t set t.sec_shop_id="%s" where t.id="%s"' % (
                    #     shop_id, id)
                    # db.execute_sql(sql)
                    sql1 = 'update amp_shop_marketentity t set t.sec_shop_id="%s" where t.id="%s"' % (
                        shop_id, id)
                    db.execute_sql(sql1)
                else:
                    print('名称不一致')
                    continue
            except:
                print('error')

def selic():
    wd = webdriver.Edge(service=Service(r'D:/douyin_data/msedgedriver.exe'))
    wd.implicitly_wait(3)
    pathorc='D:/douyin_data/jingdong/orc/'
    pathlicense = 'D:/douyin_data/jingdong/license/'
    sql = "SELECT t.shopname,t.id,t.sec_shop_id FROM amp_shop_marketentity t WHERE t.id>=149044 AND t.sec_shop_id IS not NULL" \
          " and t.shopname NOT LIKE '%海外%' AND t.shopname NOT LIKE '%自营%' and t.shopcompany is null"
    result = db.select(sql)
    for ob in result:
        try:
            shop_name = ob[0]
            id = ob[1]
            secid = ob[2]
            url = 'https://mall.jd.com/showLicence-%s.html' % (secid)
            wd.get(url)
            inpu = wd.find_element(By.XPATH, "//input[@id='verifyCode']")
            flag = isExist(wd)
            num=0
            while flag:
                if num>5:
                    break
                img = wd.find_element(By.XPATH, "//img[@id='verifyCodeImg']")
                orcname = '%s_ocr.png' % (id)
                img.screenshot(pathorc + orcname)
                time.sleep(1)
                with open(pathorc + orcname, 'rb') as file:
                    img = file.read()
                ocr = ddddocr.DdddOcr()
                text = ocr.classification(img)
                inpu.click()
                inpu.clear()
                inpu.send_keys(text)
                button = wd.find_element(By.XPATH, "//button[contains(text(),'确定')]")
                button.click()
                time.sleep(1)
                flag = isExist(wd)
                if not flag:
                    break
                num+=1
                inpu = wd.find_element(By.XPATH, "//input[@id='verifyCode']")
            #证照图
            lic = wd.find_element(By.XPATH, "//img[@class='qualification-img']").get_attribute('src')
            lictext = str(lic)
            licname = '%s_certificate.png' % (id)
            opener = urllib.request.build_opener()
            opener.addheaders = [('User-agent',
                                  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36')]
            urllib.request.install_opener(opener)
            urllib.request.urlretrieve(lictext, pathlicense+licname)
            #公司名
            company = wd.find_element(By.XPATH,
                                      "/html[1]/body[1]/div[3]/div[2]/div[1]/div[2]/div[1]/ul[1]/li[2]/span[1]").text
            mar=wd.find_element(By.XPATH,
                                      "/html[1]/body[1]/div[3]/div[2]/div[1]/div[2]/div[1]/ul[1]/li[3]/span[1]").text
            sql1 = "update amp_shop_marketentity t set t.shopcompany='%s',t.marketentityid='%s' where t.id='%s'" % (
                company, mar,id)
            db.execute_sql(sql1)
        except:
            print('error')

def selive():
    wd = webdriver.Edge(service=Service(r'D:/douyin_data/msedgedriver.exe'))
    wd.implicitly_wait(3)
    pathorc = 'D:/douyin_data/jingdong/orc/'
    sql = "SELECT t.certpath,t.id FROM amp_illege_liveroom t WHERE t.medianame='京东' and t.certpath IS not NULL" \
          " and t.liveroomcompany is null "
    result = db.select(sql)
    for ob in result:
        try:
            certpath=ob[0]
            sql1 = "SELECT t.sec_shop_id FROM amp_shop_marketentity t where t.certpath ='%s'" % (
                certpath)
            result = db.select(sql1)
            for ob in result:
                secid = ob[0]
            url = 'https://mall.jd.com/showLicence-%s.html' % (secid)
            wd.get(url)
            inpu = wd.find_element(By.XPATH, "//input[@id='verifyCode']")
            flag = isExist(wd)
            while flag:
                img = wd.find_element(By.XPATH, "//img[@id='verifyCodeImg']")
                orcname = '%s_ocr.png' % (secid)
                img.screenshot(pathorc + orcname)
                time.sleep(1)
                with open(pathorc + orcname, 'rb') as file:
                    img = file.read()
                ocr = ddddocr.DdddOcr()
                text = ocr.classification(img)
                inpu.click()
                inpu.clear()
                inpu.send_keys(text)
                button = wd.find_element(By.XPATH, "//button[contains(text(),'确定')]")
                button.click()
                time.sleep(1)
                flag = isExist(wd)
                if not flag:
                    break
                inpu = wd.find_element(By.XPATH, "//input[@id='verifyCode']")

            company = wd.find_element(By.XPATH, "/html[1]/body[1]/div[3]/div[2]/div[1]/div[2]/div[1]/ul[1]/li[2]/span[1]").text
            sql2 = "update amp_illege_liveroom t set t.liveroomcompany='%s' where t.certpath='%s'" % (
                company, certpath)
            db.execute_sql(sql2)
        except:
            print('error')

def isExist(wd):
    try:
        wd.find_element(By.XPATH, "//input[@id='verifyCode']")
        return True
    except:
        return False

#goods表淘宝根据url补goodsid
def test():
    sql = "SELECT t.id,t.landingurl FROM amp_goods t where t.medianame='淘宝' " \
          "and t.createtime>'2023-12-11 00:00:00' and t.createtime<'2023-12-12 00:00:00' and t.landingurl is not null and t.landingurl!= ''"
    result = db.select(sql)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.63'
    }
    for ob in result:
        try:
            time.sleep(1)
            id = ob[0]
            url = ob[1]
            request = urllib.request.Request(url=url, headers=headers)
            response = urllib.request.urlopen(request)
            content = response.read().decode('utf-8')
            str1 = 'https://item.taobao.com/item.htm?id='
            index1 = str(content).find(str1)
            str2 = content[index1:index1 + 60]
            str3 = 'id='
            str4 = '&'
            index2 = str2.find(str3)
            index3 = str2.find(str4)
            str5 = str2[index2 + 3:index3]
            if str5!='':
                sql1 = "update amp_goods t set t.goodsid='%s' where t.id='%s'" % (
                    str5, id)
                db.execute_sql(sql1)
        except:
            'error'

def test1():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.63'
    }
    url = 'https://app.kwaixiaodian.com/page/kwaishop-buyer-qulification?sellerId=96884777'
    request = urllib.request.Request(url=url, headers=headers)
    response = urllib.request.urlopen(request)
    content = response.read()
    print(content)


if __name__ == '__main__':
    handle1()