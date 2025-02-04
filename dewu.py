import uiautomator2 as u2
import json
from util.MysqlHelper import MysqlHelper
import time
import threading
import sched
import urllib.request
from lxml import etree
import urllib.request
from lxml import etree
import time
import requests
import os
from util.min_io import upload_minio

DB_CONFIG = {
    "host": '127.0.0.1',
    "port": 3306,
    "user": 'root',
    "password": 'root',
    "db": 'byquick',
    "charset": 'utf8'
}
db = MysqlHelper(DB_CONFIG)
d = u2.connect('A48B9X2A20W12786')

def main():
    sql = "SELECT t.shopname,t.id FROM amp_shop_marketentity t where t.medianame='得物'  and t.id>=149151"
    # and t.sec_shop_id is null
    # sql = "SELECT t.shopname,t.id FROM amp_shop_marketentity t where  t.id=93239"
    result = db.select(sql)
    path='D:/douyin_data/dewu/'
    d.app_start("com.shizhuang.duapp", wait=True)
    time.sleep(3)
    for ob in result:
        try:
            shop_name = ob[0]
            id = ob[1]
            serch=d.xpath('//*[@resource-id="com.shizhuang.duapp:id/flipperView"]')
            serch.click()
            time.sleep(1)
            d.send_keys(shop_name, clear=True)
            time.sleep(1)
            d.xpath('//*[@resource-id="com.shizhuang.duapp:id/tvSearch"]').click()
            time.sleep(1)
            d.xpath('//*[@text="商品"]').click()
            time.sleep(1)
            d.xpath('//*[@resource-id="com.shizhuang.duapp:id/recyclerView"]/android.view.ViewGroup[1]').click()
            brandname=d.xpath('//*[@resource-id="com.shizhuang.duapp:id/brandName"]')
            flag=False
            for i in range(5):
                if brandname.exists:
                    flag=True
                    break
                else:
                    d.swipe_ext('up',scale=1)
                    continue
            if not flag:
                while not serch.exists:
                    d.press('back')
                time.sleep(1)
                continue
            else:
                brandnametext=d.xpath('//*[@resource-id="com.shizhuang.duapp:id/brandName"]').get_text()
                if brandnametext !=shop_name:
                    while not serch.exists:
                        d.press('back')
                    time.sleep(1)
                    continue
                else:
                    brandname.click()
            time.sleep(1)
            logo=d.xpath('//*[@resource-id="com.shizhuang.duapp:id/brand_cover_person_logo_id"]')
            if logo.exists:
                logoname='%s.png' % (id)
                logo.screenshot().save(path+logoname)

            d.xpath('//*[@resource-id="com.shizhuang.duapp:id/brand_cover_toolbar_right_parent_id"]/android.widget.ImageView[2]').click()
            time.sleep(1)
            d.xpath('//*[@text="复制链接"]').click()
            shop_url = d.clipboard
            str='='
            index=shop_url.index(str)
            shopid=shop_url[index+1:]
            sql1 = "update amp_shop_marketentity t set t.sec_shop_id='%s' where t.id='%s'" % (
            shopid,id)
            db.execute_sql(sql1)
            logo.click()
            time.sleep(1)
            d.xpath('//*[@resource-id="com.shizhuang.duapp:id/userHeader"]').click()
            time.sleep(1)
            img_scr = d.screenshot()
            img_scr.crop((0, 440, 720, 1160)).save(path+logoname)
            time.sleep(1)
            d.xpath('//*[@text="品牌信息"]').click()
            time.sleep(1)
            shopCompany = d.xpath('//*[@resource-id="com.shizhuang.duapp:id/tvCompanyMainContent"]').get_text()
            mid = d.xpath('//*[@resource-id="com.shizhuang.duapp:id/tvCreditCodeContent"]').get_text()
            sql2 = "update amp_shop_marketentity t set t.shopcompany='%s',t.marketentityid='%s' where t.id='%s'" % (
                shopCompany, mid, id)
            db.execute_sql(sql2)
            time.sleep(1)
            while not serch.exists:
                d.press('back')
            time.sleep(1)
        except:
            print('Error')
            while not serch.exists:
                d.press('back')
            time.sleep(1)

def handle1():
    folder_path = "D:/douyin_data/dewu/"
    file_names = os.listdir(folder_path)
    for file_name in file_names:
        str1 = '.'
        index = file_name.index(str1)
        shop_id = file_name[0:index]
        new_name = '%s_logo.png' % (shop_id)
        cret_name = 'dewu/%s' % (new_name)
        upload_minio('logo', cret_name, folder_path + file_name)
        sql1 = "update amp_shop_marketentity t set t.logopath='%s' where t.id='%s' " % (
            cret_name, shop_id)
        db.execute_sql(sql1)


if __name__ == '__main__':
    handle1()