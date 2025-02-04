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

DB_CONFIG1 = {
    "host": '127.0.0.1',
    "port": 3306,
    "user": 'root',
    "password": 'root',
    "db": 'byquick',
    "charset": 'utf8'
}
db = MysqlHelper(DB_CONFIG1)


#https://shop.suning.com/70173894/index.html
def main():
    d = u2.connect('A48B9X2A20W12786')
    sql = "SELECT t.shopname,t.id FROM amp_shop_marketentity t where t.medianame='苏宁易购' and t.sec_shop_id is null and t.id>149320"
    result = db.select(sql)
    d.app_start("com.suning.mobile.ebuy", wait=True)
    time.sleep(3)
    for ob in result:
        try:
            shop_name = ob[0]
            id = ob[1]
            serch = d.xpath('//*[@resource-id="com.suning.mobile.ebuy:id/home_fragment_search_view_flipper"]')
            serch.click()
            time.sleep(1)
            d.send_keys(shop_name, clear=True)
            time.sleep(1)
            d.xpath('//*[@resource-id="com.suning.mobile.ebuy:id/tv_search_input_btn"]').click()
            time.sleep(2)
            dianpu = d.xpath('//*[@resource-id="com.suning.mobile.ebuy:id/tv_new_search_shop_select"]')
            dianpu.click()
            time.sleep(1)
            d.xpath('//*[@resource-id="com.suning.mobile.ebuy:id/tv_shop_enter_shop"]').click()
            time.sleep(1)
            text = d.xpath('//*[@resource-id="com.suning.mobile.ebuy:id/shop_name"]').get_text()
            if text != shop_name:
                d.press('back')
                time.sleep(1)
                if not serch.exists:
                    d.press('back')
                    time.sleep(1)
                continue
            d.xpath('//*[@recom/source-id="com.suning.mobile.ebuy:id/btn_menu"]').click()
            time.sleep(1)
            d.xpath('//*[@text="分享"]').click()
            time.sleep(1)
            d.xpath('//*[@text="复制链接"]').click()
            shop_url = d.clipboard
            str1 = ''
            str2 = '.html'
            index1 = shop_url.index(str1)
            index2 = shop_url.index(str2)
            shop_id = shop_url[index1 + 4:index2]
            print(shop_id)
            sql = 'update amp_shop_marketentity t set t.sec_shop_id="%s" where t.shopname="%s" and t.medianame="苏宁易购" ' % (
                shop_id, text)
            db.execute_sql(sql)
            time.sleep(1)
            d.press('back')
            time.sleep(1)
            d.press('back')
            time.sleep(1)
            continue
        except:
            print("Error")

def main1():
    sql = "SELECT t.sec_shop_id FROM amp_shop_marketentity t where t.medianame='苏宁易购' and t.sec_shop_id is not null and t.id>=149320"
    result = db.select(sql)
    for ob in result:
        try:
            id = ob[0]
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.63'
            }
            url = 'https://shop.suning.com/%s/index.html' % (id)

            # 先创建request
            request = urllib.request.Request(url=url, headers=headers)
            # 返回HttpResponse类型
            response = urllib.request.urlopen(request)
            content = response.read().decode('utf-8')
            tree = etree.HTML(content, parser=etree.HTMLParser(encoding='utf8'))

            info = tree.xpath("//script[@type='application/ld+json']/text()")
            str1 = str(info[0])
            dic = json.loads(str1)
            logourl = dic["images"][0]
            path = 'D:/douyin_data/suning/logo/'
            filename = "%s_logo.png" % (id)
            type = logourl[-3:]
            if type == 'gif':
                filename = '%s_logo.gif' % (id)
                print(filename)
            opener = urllib.request.build_opener()
            opener.addheaders = [('User-agent',
                                  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36')]
            urllib.request.install_opener(opener)
            urllib.request.urlretrieve(logourl, path + filename)
        except:
            print("error")

def handle2():
    folder_path = "D:/douyin_data/suning/logo/"
    file_names = os.listdir(folder_path)
    for file_name in file_names:
        str1 = '_'
        index = file_name.index(str1)
        shop_id = file_name[0:index]
        cret_name = 'suning/%s' % (file_name)
        upload_minio('logo',cret_name,folder_path+file_name)
        sql1 = "update amp_shop_marketentity t set t.logopath='%s' where t.sec_shop_id='%s' and t.medianame='苏宁易购' " % (
            cret_name, shop_id)
        db.execute_sql(sql1)

def handle1():
    folder_path = "D:/douyin_data/suning/license/"
    file_names = os.listdir(folder_path)
    for file_name in file_names:
        str1 = '.'
        index = file_name.index(str1)
        shop_id = file_name[0:index]
        cret_name = 'suning/%s' % (file_name)
        upload_minio('license', cret_name, folder_path + file_name)
        sql1 = "update amp_shop_marketentity t set t.certpath='%s' where t.id='%s'" % (
            cret_name, shop_id)
        db.execute_sql(sql1)


if __name__ == '__main__':
    handle1()