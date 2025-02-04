from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
import json
import os
import sys
import time
import pandas as pd
import requests
from util.MysqlHelper import MysqlHelper
from util.min_io import upload_minio
import uiautomator2 as u2
from util.MysqlHelper import MysqlHelper
import datetime
import urllib.request
from util.xunmeng_handle import bdocrUtil
import urllib.request
from lxml import etree
import time
import requests

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
    wd = webdriver.Edge(service=Service(r'D:/douyin_data/msedgedriver.exe'))
    wd.get('https://tb.alicdn.com/')
    wd.implicitly_wait(3)

    sql = "SELECT t.shopname,t.id FROM amp_shop_marketentity t WHERE t.medianame = '手机淘宝' AND t.id>=149047 and t.sec_shop_id IS NULL"
    result = db.select(sql)
    path_log = 'D:/douyin_data/taobao/logo/'
    time.sleep(30)

    for ob in result:
        try:
            shop_name = ob[0]
            id=ob[1]
            inpu = wd.find_element(By.XPATH, "//input[@id='q']")
            inpu.clear()
            inpu.send_keys(shop_name)
            inpu.submit()
            name_path = wd.find_elements(By.XPATH,'//*[@id="srp_shopLayout_shopContentWrapper"]/a[1]/div[2]/div[1]/div[2]/div[1]/div[1]')
            if len(name_path) == 0:
                inpu = wd.find_element(By.XPATH, "//input[@id='q']")
                inpu.clear()
                inpu.send_keys(shop_name)
                inpu.submit()
                name_path = wd.find_elements(By.XPATH,
                                             '//*[@id="srp_shopLayout_shopContentWrapper"]/a[1]/div[2]/div[1]/div[2]/div[1]/div[1]')
                if len(name_path) == 0:
                    inpu = wd.find_element(By.XPATH, "//input[@id='q']")
                    inpu.clear()
                    inpu.send_keys(shop_name)
                    inpu.submit()
                    name_path = wd.find_elements(By.XPATH,
                                                 '//*[@id="srp_shopLayout_shopContentWrapper"]/a[1]/div[2]/div[1]/div[2]/div[1]/div[1]')
                    if len(name_path) == 0:
                        continue
            name_path = wd.find_element(By.XPATH,
                                        '//*[@id="srp_shopLayout_shopContentWrapper"]/a[1]/div[2]/div[1]/div[2]/div[1]/div[1]')
            name = name_path.text
            name1=name.replace(" ", "")
            shop_name1=shop_name.replace(" ", "")
            if name1 == shop_name1:
                name_path=wd.find_element(By.XPATH,
                                        '//*[@id="srp_shopLayout_shopContentWrapper"]/a[1]')
                shop_herf_ele = name_path.get_attribute('href')
                logo_path = wd.find_element(By.XPATH,
                                            '//*[@id="srp_shopLayout_shopContentWrapper"]/a[1]/div[2]/div[1]/div[1]/img[1]')
                shop_herf = str(shop_herf_ele)
                str2 = '.'
                index2 = shop_herf.index(str2)
                shop_id = shop_herf[12:index2]
                sql = 'update amp_shop_marketentity t set t.sec_shop_id="%s" where t.id="%s"' % (
                    shop_id, id)
                db.execute_sql(sql)
                logosrc = logo_path.get_attribute('src')
                logo = logosrc
                file_name='%s_%s_logo.png' % (shop_id,name)
                path = path_log + file_name
                logo_str=str(logo)
                opener = urllib.request.build_opener()
                opener.addheaders = [('User-agent',
                                      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36')]
                urllib.request.install_opener(opener)
                urllib.request.urlretrieve(logo_str, path)
                time.sleep(5)
            else:
                continue
        except:
            print("错误")

def main1():
    d = u2.connect('A48B9X2A20W12786')
    sql="SELECT t.sec_shop_id,t.id FROM amp_shop_marketentity t WHERE t.medianame = '手机淘宝' AND  t.sec_shop_id IS NOT NULL and t.id>14223"
    result = db.select(sql)
    for ob in result:
        try:
            shop_id = ob[0]
            id = ob[1]
            url = "shop%s.taobao.com" % (shop_id)
            d.open_url("taobao://" + url)
            time.sleep(2)
            d.xpath(
                '//*[@resource-id="com.taobao.taobao:id/new_shop_view_header_view_container"]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.LinearLayout[1]').click()
            time.sleep(3)

            fans_contains = d.xpath('//*[contains(@text,"粉丝数")]')
            shopname=d.xpath('//*[contains(@text,"店铺名称")]/following-sibling::android.view.View[1]')
            dsr=d.xpath('//*[contains(@text,"描述相符")]/following-sibling::android.view.View[2]')
            # if not shopname.exists or not fans_contains.exists or not dsr.exists:
            #     continue
            fanstext=fans_contains.get_text()
            fanstext=fanstext[3:]
            shopnametext=shopname.get_text()
            dsrtext=dsr.get_text()
            print(fanstext+" "+shopnametext+" "+dsrtext)
            sql1 = 'update amp_shop_marketentity t set t.dsr_score="%s",t.shopname="%s",t.fans="%s",t.status=5 where t.id=%s' % (
                dsrtext, shopnametext, fanstext, id)
            db.execute_sql(sql1)
        except:
            print("Error")

def mainlogo():
    wd = webdriver.Edge(service=Service(r'D:/douyin_data/msedgedriver.exe'))
    path = "D:/douyin_data/taobao/logo/"
    sql = "SELECT t.sec_shop_id FROM amp_shop_marketentity t WHERE t.medianame = '手机淘宝' " \
          "AND t.id>=133904 and t.sec_shop_id IS not NULL and t.logopath is null"
    result = db.select(sql)
    for ob in result:
        try:
            secid = ob[0]
            url = 'https://shop%s.taobao.com' % (secid)
            wd.get(url)
            logo = wd.find_element(By.XPATH, "//meta[@property='og:image']").get_attribute('content')
            logourl=str(logo)
            name="%s_logo.png" % secid
            opener = urllib.request.build_opener()
            opener.addheaders = [('User-agent',
                                  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36')]
            urllib.request.install_opener(opener)
            urllib.request.urlretrieve(logourl, path + name)
        except:
            print('error')

def handle1():
    folder_path = "D:/douyin_data/taobao/license/"
    file_names = os.listdir(folder_path)
    today = datetime.datetime.today()
    date = today.date()
    date = str(date)
    date = date.replace("-", "")
    # date = date[:-2]
    for file_name in file_names:
        try:
            str1 = '_'
            index = file_name.index(str1)
            id = file_name[0:index]
            cret_name = 'taobao/%s/%s' % (date, file_name)
            upload_minio('license', cret_name, folder_path + file_name)
            sql1 = "update amp_shop_marketentity t set t.certpath='%s' where t.id='%s' " % (
                cret_name, id)
            db.execute_sql(sql1)

            company = bdocrUtil(folder_path + file_name)
            if company != '':
                sql2 = "update amp_shop_marketentity t set t.shopcompany='%s' where t.id='%s' " % (
                    company, id)
                db.execute_sql(sql2)

        except:
            continue

def handle2():
    folder_path = "D:/douyin_data/taobao/logo/"
    file_names = os.listdir(folder_path)
    for file_name in file_names:
        str1 = '_'
        index = file_name.index(str1)
        shop_id = file_name[0:index]
        cret_name = 'taobao/%s' % (file_name)
        upload_minio('logo',cret_name,folder_path+file_name)
        sql1 = "update amp_shop_marketentity t set t.logopath='%s' where t.sec_shop_id='%s' and t.medianame = '手机淘宝'" % (
            cret_name, shop_id)
        db.execute_sql(sql1)

def alimain():
    d = u2.connect('A48B9X2A20W12786')
    sql = "SELECT t.shopname,t.id FROM amp_shop_marketentity t where  t.id>=149656 and t.medianame='阿里巴巴' and t.certpath is null"
    result = db.select(sql)
    pathlicense = 'D:/douyin_data/taobao/license/'
    for ob in result:
        try:
            shop_name = ob[0]
            id = ob[1]
            search = d.xpath('//*[@resource-id="com.alibaba.wireless:id/et_search_input_edit"]')
            search.click()
            d.send_keys(shop_name, clear=True)
            sousuo = d.xpath('//*[contains(@text,"搜索")]')
            sousuo.click()
            time.sleep(1)
            dianpu = d.xpath('//*[contains(@text,"搜到以下")]')
            time.sleep(1)

            if not dianpu.exists:
                first = d.xpath(
                    '//*[@resource-id="app"]/android.view.View[last()]/android.view.View[1]/android.view.View[2]/android.view.View[1]/android.widget.TextView[1]')
                name = first.text
                name3=first
                shop_name=shop_name.replace('(','')
                shop_name = shop_name.replace(')', '')
                name = name.replace('(', '')
                name = name.replace(')', '')
                shop_name = shop_name.replace('（', '')
                shop_name = shop_name.replace('）', '')
                name = name.replace('（', '')
                name = name.replace('）', '')
                if name != shop_name or name not in shop_name:
                    second = d.xpath(
                        '//*[@resource-id="app"]/android.view.View[last()]/android.view.View[1]/android.view.View[4]/android.view.View[1]/android.widget.TextView[1]')
                    name2 = second.text
                    name2 = name2.replace('(', '')
                    name2 = name2.replace(')', '')
                    name2 = name2.replace('（', '')
                    name2 = name2.replace('）', '')
                    if name2 == shop_name or name2 in shop_name:
                        name3=second
                    else:
                        while not search.exists:
                            d.press('back')
                            d.sleep(1)
                        continue
                name3.click()
                time.sleep(3)

            else:
                first1 = d.xpath(
                    '//*[@resource-id="app"]/android.view.View[last()]/android.view.View[1]/android.view.View[1]/android.view.View[2]/android.view.View[1]/android.widget.TextView[1]')
                name = first1.text
                shop_name = shop_name.replace('(', '')
                shop_name = shop_name.replace(')', '')
                name = name.replace('(', '')
                name = name.replace(')', '')
                shop_name = shop_name.replace('（', '')
                shop_name = shop_name.replace('）', '')
                name = name.replace('（', '')
                name = name.replace('）', '')
                if name != shop_name or name not in shop_name:
                    while not search.exists:
                        d.press('back')
                        d.sleep(1)
                    continue
                first1.click()
                time.sleep(1)
                dsr = d.xpath('//*[contains(@text,"服务")]').get_text()
                fans = d.xpath('//*[contains(@text,"粉丝")]').get_text()
                dsrtext = dsr[2:]
                fanstext = fans[:-2]
                sql1 = 'update amp_shop_marketentity t set t.fans="%s", t.dsr_score="%s" where t.id=%s' % (
                    fanstext, dsrtext, id)
                db.execute_sql(sql1)
                title = d.xpath(
                    '//*[@text="顶部二级Tabbar"]/android.view.View[1]/android.view.View[1]/android.view.View[1]/android.view.View[1]/android.view.View[1]/android.view.View[1]/android.view.View[1]/android.view.View[1]')
                title.click()
                time.sleep(3)

            gongshang = d.xpath('//*[contains(@text,"工商资质")]')
            zhuti = d.xpath('//*[contains(@text,"主体资质")]')
            flag = 0
            for i in range(5):
                if gongshang.exists:
                    flag = 1
                    time.sleep(1)
                    break
                elif zhuti.exists:
                    flag = 2
                    time.sleep(1)
                    break
                else:
                    time.sleep(1)
                    gongshang = d.xpath('//*[contains(@text,"工商资质")]')
                    zhuti = d.xpath('//*[contains(@text,"主体资质")]')
                    continue
            if flag == 1:
                gongshang.click()
                time.sleep(1)
                ele = d.xpath(
                    '//*[contains(@text,"名称:")]/parent::android.view.View[1]/parent::android.view.View[1]/parent::android.view.View[1]/parent::android.view.View[1]')
                # if not ele.exists:
                #     gongshang.click()
                file = "%s.png" % (id)
                path = pathlicense + file
                ele.screenshot().save(path)
            elif flag == 2:
                zhuti.click()
                time.sleep(1)
                ele = d.xpath(
                    '//android.webkit.WebView/android.view.View[1]/android.view.View[1]/android.view.View[2]/android.view.View[1]/android.view.View[1]/android.view.View[1]')
                # if not ele.exists:
                #     zhuti.click()
                file = "%s.png" % (id)
                path = pathlicense + file
                ele.screenshot().save(path)
            else:
                ele = d.xpath(
                    '//android.webkit.WebView/android.view.View[1]/android.view.View[1]/android.view.View[2]/android.view.View[1]/android.view.View[1]/android.view.View[1]')
                # if not ele.exists:
                #     zhuti.click()
                file = "%s.png" % (id)
                path = pathlicense + file
                ele.screenshot().save(path)
            while not search.exists:
                d.press('back')
                d.sleep(1)


        except:
            print('Error')
            while not search.exists:
                d.press('back')
                d.sleep(1)
            continue

def handleali():
    folder_path = "D:/douyin_data/taobao/license/"
    file_names = os.listdir(folder_path)
    today = datetime.datetime.today()
    date = today.date()
    date = str(date)
    date = date.replace("-", "")
    # date = date[:-2]
    for file_name in file_names:
        try:
            str1 = '.'
            index = file_name.index(str1)
            id = file_name[0:index]
            cret_name = 'alibaba/%s/%s' % (date, file_name)
            upload_minio('license', cret_name, folder_path + file_name)
            sql1 = "update amp_shop_marketentity t set t.certpath='%s' where t.id='%s' " % (
                cret_name, id)
            db.execute_sql(sql1)
        except:
            continue

if __name__ == '__main__':
    handleali()