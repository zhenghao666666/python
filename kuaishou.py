import json
import os
import sys
import time
import urllib.request
import pandas as pd
import requests
import ddddocr
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from pip._internal.req.req_file import get_file_content
from tqdm import trange
import uiautomator2 as u2
from util import paddle_ocr
from util.MysqlHelper import MysqlHelper
from util.min_io import upload_minio
from aip import AipOcr
from util.xunmeng_handle import bdocrUtil

DB_CONFIG1 = {
    "host": '127.0.0.1',
    "port": 3306,
    "user": 'root',
    "password": 'root',
    "db": 'byquick',
    "charset": 'utf8'
}
db = MysqlHelper(DB_CONFIG1)
d = u2.connect('A48B9X2A20W12786')
d.wait_timeout=5
APP_ID = ''
API_KEY = ''
SECRET_KEY = ''

#快手证照链接：https://app.kwaixiaodian.com/page/kwaishop-buyer-qulification?sellerId=
#快手小店链接：https://app.kwaixiaodian.com/page/kwaishop-c-shop-detail?sellerId=
#快手证照链接：https://u1-204.ecukwai.com/ufile/adsocial/51476e19-6181-41f7-82d1-8563957c3f73.jpg   或png
#https://u2-253.fdleckwai.com/ksc2/PkKtY_O1aMUMKMhlmraJhRT4kqTNQgy4TFbGxmszjhXEWw02Q34GTPRgGgGLem_kyKMQYkPS18axw7ZaxTrZikQEZVlVu1QkAUDgxC6XOzg.jpeg?pkey=AAUcjXvATnOSJOkM_mnNNjUVT5pkt0636BSFUbvvY816ZLGBRuoD1R_VLQNj8UlsHIFFZOuGhMPHVYb8Ca8fgkE-llMF1jJ2PvEbfqlKLkw4tudRgljosw99SF3xbB-sLao
def handle1():
    path = 'D:/douyin_data/kuaishou_shopid.txt'
    logopath = 'D:/douyin_data/kuaishou/logo/'
    file = open(path, 'r', encoding='utf-16')
    for line in file.readlines():
        try:
            if line != '':
                dic = json.loads(line)
                data = dic['data']
                shopid = data['userId']
                shopName = data['shopName']
                acqTotalSalesVolumeStr = data['acqTotalSalesVolumeStr']
                shopScore = data['shopScore']
                headUrl = data['shopCoverUrl']

                file_name = '%s_kuaishou_logo.png' % (shopid)
                path = logopath + file_name
                opener = urllib.request.build_opener()
                opener.addheaders = [('User-agent',
                                      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36')]
                urllib.request.install_opener(opener)
                urllib.request.urlretrieve(headUrl, path)
                cret_name = 'gifmaker/%s' % (file_name)
                upload_minio('logo', cret_name, path)
                shopname = str(shopName)
                if '官方旗舰店' in shopname:
                    shopname1 = shopname[:-5]
                else:
                    shopname1 = shopname[:-3]

                sql1 = "update amp_shop_marketentity t set t.sec_shop_id='%s',t.logopath='%s',t.sales_volume='%s',t.dsr_score='%s' where t.medianame='快手' and (t.shopname='%s' or t.shopname='%s') " % (
                    shopid, cret_name, acqTotalSalesVolumeStr, shopScore, shopname, shopname1)
                db.execute_sql(sql1)
        except:
            print("error")
            continue

def se():
    wd = webdriver.Edge(service=Service(r'D:/douyin_data/msedgedriver.exe'))
    wd.implicitly_wait(3)
    pathlicense = 'D:/douyin_data/kuaishou/license/'
    sql = "SELECT t.sec_shop_id,t.id FROM amp_shop_marketentity t where t.id>=147303 and t.sec_shop_id is not null and t.certpath is null and t.medianame='快手'"
    sql1="SELECT t.sec_shop_id FROM amp_illege_liveroom t where t.sec_shop_id is not null and t.liveroomcompany is null and t.medianame='快手'"
    result = db.select(sql)
    for ob in result:
        try:
            shopid = ob[0]
            id=ob[1]
            # url='https://app.kwaixiaodian.com/page/kwaishop-buyer-qulification?sellerId=%s' % (shopid)
            # wd.get(url)
            # time.sleep(1)
            # img=wd.find_element(By.XPATH, "//img[@class='quli-img']").get_attribute('src')
            # imgurl=str(img)
            # filename="%s_kuaishou_certificate.png" % (id)
            # opener = urllib.request.build_opener()
            # opener.addheaders = [('User-agent',
            #                       'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36')]
            # urllib.request.install_opener(opener)
            # urllib.request.urlretrieve(imgurl, pathlicense + filename)
            url = 'https://app.kwaixiaodian.com/page/kwaishop-c-shop-detail?sellerId=%s' % (shopid)
            wd.get(url)
            time.sleep(60)
        except:
            print('error')

def main():
    sql = "SELECT t.shopname,t.id FROM amp_shop_marketentity t " \
          "where t.id>=127552 and t.sec_shop_id is null and t.certpath is null and t.medianame='快手'"
    result = db.select(sql)
    pathlicense = 'D:/douyin_data/kuaishou/license/'
    pathlogo = 'D:/douyin_data/kuaishou/logo/'
    for ob in result:
        try:
            shopid = ob[1]
            shopname = ob[0]
            if '海外'in shopname:
                continue

            search = d.xpath('//*[@resource-id="com.smile.gifmaker:id/editor"]')
            while not search.exists:
                d.press('back')
                d.sleep(1)
            search.click()
            d.send_keys(shopname, clear=True)
            sousuo = d.xpath('//*[@resource-id="com.smile.gifmaker:id/right_button"]')
            sousuo.click()
            time.sleep(3)
            str1='//*[@resource-id="com.smile.gifmaker:id/view_pager"]//*[contains(@text,"%s")]' %(shopname)
            shop=d.xpath(str1)
            if not shop.exists:
                continue
            shop.click()
            time.sleep(1)

            r1=d.xpath('//*[@resource-id="com.smile.gifmaker:id/search_result_text"]')

            if r1.exists:
                for i in range(5):
                    str1 = '//*[@resource-id="com.smile.gifmaker:id/view_pager"]//*[contains(@text,"%s")]' % (shopname)
                    if r1.exists:
                        shop = d.xpath(str1)
                        shop.click()
                        time.sleep(1)
                    else:
                        break

            # logo=d.xpath('//*[@resource-id="com.smile.gifmaker:id/root_recyclerView"]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.view.ViewGroup[1]/android.view.ViewGroup[1]/android.view.ViewGroup[1]/android.view.ViewGroup[1]/android.view.ViewGroup[1]/android.widget.ImageView[1]')
            # logo.click()
            # sectext=d.xpath('//*[contains(@text,"快手号")]')
            # textstr=sectext.get_text()
            # num = textstr[4:]
            # d.press('back')

            tiyan = d.xpath('//*[contains(@text,"店铺体验")]')
            dian = d.xpath('//*[@text="店铺"]')
            if not tiyan.exists and dian.exists:
                for i in range(5):
                    if not dian.exists:
                        break
                    else:
                        dian.click()
                        time.sleep(1)
            for i in range(5):
                if tiyan.exists:
                    break
                else:
                    tiyan = d.xpath('//*[contains(@text,"店铺体验")]')
                    time.sleep(1)
            tiyan.click()

            xltext=d.xpath('//*[contains(@text,"总销量")]')
            for i in range(5):
                if xltext.exists:
                    break
                else:
                    xltext = d.xpath('//*[contains(@text,"总销量")]')
                    time.sleep(1)
            xlstr=xltext.get_text()
            sale = xlstr[4:]
            sql1 = 'update amp_shop_marketentity t set t.sales_volume="%s" where t.id=%s' % (
                sale,shopid)
            db.execute_sql(sql1)

            zizhi = d.xpath('//*[contains(@text,"查看资质证明")]')
            for i in range(5):
                if zizhi.exists:
                    break
                else:
                    d.swipe_ext('up', scale=1)
                    zizhi = d.xpath('//*[contains(@text,"查看资质证明")]')
                    time.sleep(1)
            zizhi.click()
            time.sleep(3)
            pic1 = d.xpath('//*[@resource-id="com.smile.gifmaker:id/webView"]//android.widget.Image[1]')
            for i in range(9):
                if pic1.exists:
                    break
                else:
                    pic1 = d.xpath('//*[@resource-id="com.smile.gifmaker:id/webView"]//android.widget.Image[1]')
                    time.sleep(1)
            text1 = pic1.get_text()
            if "此图片未加标签" in text1:
                continue
            else:
                file_name = '%s_kuaishou.png' % (shopid)
                path = pathlicense + file_name
                url1 = 'https://u1-204.ecukwai.com/ufile/adsocial/%s.jpg' % (text1)
                opener = urllib.request.build_opener()
                opener.addheaders = [('User-agent',
                                      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36')]
                urllib.request.install_opener(opener)
                urllib.request.urlretrieve(url1, path)
                continue
        except:
            try:
                if url1 != '':
                    file_name = '%s_kuaishou.png' % (shopid)
                    path = pathlicense + file_name
                    url1 = 'https://u1-204.ecukwai.com/ufile/adsocial/%s.png' % (text1)
                    opener = urllib.request.build_opener()
                    opener.addheaders = [('User-agent',
                                          'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36')]
                    urllib.request.install_opener(opener)
                    urllib.request.urlretrieve(url1, path)
                    continue
            except:
                print('Error')
                while not search.exists:
                    d.press('back')
                    d.sleep(1)
                continue

def text():
    path = 'D:/douyin_data/kuaishou.txt'
    logopath = 'D:/douyin_data/kuaishou/license/'
    file = open(path, 'r', encoding='utf-16')
    for line in file.readlines():
        try:
            if line != '':
                dic = json.loads(line)
                data = dic['data']
                shopName = data['shopName']
                userShopBasicInfoView = data['userShopBasicInfoView']
                certificateUrlList=userShopBasicInfoView['certificateUrlList']
                url=certificateUrlList[0]
                if url is not None and url !=" ":
                    sql1 = "SELECT t.id FROM amp_shop_marketentity t where t.shopname ='%s' and t.medianame='快手' and t.id>=93621" % (
                        shopName)
                    result = db.select(sql1)
                    if len(result) < 1:
                        continue
                    for ob in result:
                        id = ob[0]
                        file_name = '%s_kuaishou.png' % (id)
                        path = logopath + file_name
                        opener = urllib.request.build_opener()
                        opener.addheaders = [('User-agent',
                                              'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36')]
                        urllib.request.install_opener(opener)
                        urllib.request.urlretrieve(url, path)

        except:
            print("error")
            continue

def handle2():
    path = 'D:/douyin_data/kuaishou/license/'
    file_names = os.listdir(path)
    for file_name in file_names:
        try:
            str1 = '_'
            index = file_name.index(str1)
            shop_id = file_name[0:index]
            cret_name = 'gifmaker/%s' % (file_name)
            upload_minio('license', cret_name, path + file_name)
            sql1 = "update amp_shop_marketentity t set t.certpath='%s' where t.id='%s' " % (
                cret_name, shop_id)
            db.execute_sql(sql1)

            sql3 = "SELECT t.shopcompany FROM amp_shop_marketentity t where t.id='%s'" % (shop_id)
            result = db.select(sql3)
            for ob in result:
                shopcompany = ob[0]
                if shopcompany is None:
                    company = bdocrUtil(path + file_name)
                    if company != '':
                        sql2 = "update amp_shop_marketentity t set t.shopcompany='%s',t.marketentityid=1 where t.id='%s' " % (
                            company, shop_id)
                        db.execute_sql(sql2)
        except:
            print('error')
            continue

def test():
    logopath = 'D:/douyin_data/kuaishou/license/'
    sql = "SELECT t.shopname,t.id,t.sec_shop_id FROM amp_shop_marketentity t " \
          "where t.medianame='快手' and t.id>=147579 and t.sec_shop_id is not null and t.shopcompany is null GROUP BY t.sec_shop_id ORDER BY t.id"
    result = db.select(sql)
    for ob in result:
        try:
            url1=''
            shopname=ob[0]
            id = ob[1]
            shop_id = ob[2]
            if '海外' in shopname:
                continue
            url = 'kwai://profile/%s' % (shop_id)
            d.open_url(url)
            dainpu = d.xpath('//*[@text="店铺"]').wait(timeout=3)
            dainpu.click()
            tiyan = d.xpath('//*[contains(@text,"总销量")]')
            for i in range(5):
                if tiyan.exists:
                    break
                else:
                    tiyan = d.xpath('//*[contains(@text,"总销量")]')
                    time.sleep(1)
            tiyan.click()
            zizhi = d.xpath('//*[contains(@text,"查看资质证明")]')
            for i in range(5):
                if zizhi.exists:
                    break
                else:
                    d.swipe_ext('up', scale=1)
                    zizhi = d.xpath('//*[contains(@text,"查看资质证明")]')
                    time.sleep(1)
            zizhi.click()
            time.sleep(3)
            pic1=d.xpath('//*[@resource-id="com.smile.gifmaker:id/webView"]//android.widget.Image[1]')
            for i in range(9):
                if pic1.exists:
                    break
                else:
                    pic1 = d.xpath('//*[@resource-id="com.smile.gifmaker:id/webView"]//android.widget.Image[1]')
                    time.sleep(1)
            file_name = '%s_kuaishou.png' % (id)
            text1 = pic1.get_text()
            path = logopath + file_name
            pic1.screenshot().save(path)
            bake = os.path.getsize(path)
            while front != bake:
                front = bake
                time.sleep(1)
                pic1.screenshot().save(path)
                bake = os.path.getsize(path)
            time.sleep(3)
            if "此图片未加标签" in text1:
                continue
            else:
                url1='https://u1-204.ecukwai.com/ufile/adsocial/%s.jpg' %(text1)
                print(text1)
                opener = urllib.request.build_opener()
                opener.addheaders = [('User-agent',
                                      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36')]
                urllib.request.install_opener(opener)
                urllib.request.urlretrieve(url1, path)
                time.sleep(3)

        except:
            try:
                if url1!='':
                    file_name = '%s_kuaishou.png' % (id)
                    path = logopath + file_name
                    url1 = 'https://u1-204.ecukwai.com/ufile/adsocial/%s.png' % (text1)
                    opener = urllib.request.build_opener()
                    opener.addheaders = [('User-agent',
                                          'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36')]
                    urllib.request.install_opener(opener)
                    urllib.request.urlretrieve(url1, path)
                    time.sleep(1)
            except:
                try:
                    if url1 != '':
                        file_name = '%s_kuaishou.png' % (id)
                        path = logopath + file_name
                        url1 = 'https://u1-204.ecukwai.com/ufile/adsocial/%s' % (text1)
                        opener = urllib.request.build_opener()
                        opener.addheaders = [('User-agent',
                                              'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36')]
                        urllib.request.install_opener(opener)
                        urllib.request.urlretrieve(url1, path)
                        time.sleep(1)
                except:
                    print('error')
                    continue
#快手重复
def test1():
    sql="SELECT count(t.sec_shop_id),MAX(t.id),t.sec_shop_id FROM amp_shop_marketentity t " \
        "WHERE t.medianame = '快手' AND t.sec_shop_id IS NOT NULL AND t.sec_shop_id != '' " \
        "GROUP BY t.sec_shop_id HAVING COUNT( t.sec_shop_id )>1 and MAX(t.id)>=147303 order by MAX(t.id)"
    result = db.select(sql)
    for ob in result:
        shopid = ob[2]
        sql1="SELECT t.shopcompany,t.certpath,t.marketentityid FROM amp_shop_marketentity t" \
             " WHERE t.medianame = '快手' AND t.sec_shop_id = '%s' and t.certpath is not null limit 1" % (shopid)
        result1 = db.select(sql1)
        for ob in result1:
            shopcompany = ob[0]
            certpath=ob[1]
            marketentityid=ob[2]
            if marketentityid is None:
                sql2="update amp_shop_marketentity t set t.shopcompany ='%s',t.certpath='%s' " \
                     "where t.sec_shop_id='%s' and t.medianame='快手'" % (shopcompany,certpath,shopid)
            else:
                sql2 = "update amp_shop_marketentity t set t.shopcompany ='%s',t.certpath='%s',t.marketentityid='%s' " \
                       "where t.sec_shop_id='%s' and t.medianame='快手'" % (
                shopcompany, certpath,marketentityid,shopid)
            db.execute_sql(sql2)

if __name__ == "__main__":
    handle2()