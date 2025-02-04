import json
import os
import sys
import time
import urllib.request
import pandas as pd
import requests
import uiautomator2 as u2
from tqdm import trange
from util.MysqlHelper import MysqlHelper
from util.min_io import upload_minio
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

# 通过如下格式链接拼接shopid进入店铺首页
# https://m.mogu.com/v8/meili/shop?shopid=

def main():
    sql = "SELECT t.shopname,t.id FROM amp_shop_marketentity t where t.medianame='蘑菇街' and t.id>=149175 and t.sec_shop_id is null"
    result = db.select(sql)
    d.app_start("com.mogujie", wait=True)
    time.sleep(3)
    for ob in result:
        try:
            shop_name = ob[0]
            id = ob[1]
            serch1 = d.xpath('//*[@resource-id="com.mogujie:id/title_search_container"]')
            serch1.click()
            time.sleep(1)
            serch =d.xpath('//*[@resource-id="com.mogujie:id/search_et"]')
            d.send_keys(shop_name, clear=True)
            time.sleep(1)
            d.xpath('//*[@resource-id="com.mogujie:id/search_go_btn"]').click()
            time.sleep(1)
            d.xpath('//*[@text="店铺"]').click()
            time.sleep(1)
            firstshop = d.xpath('//androidx.recyclerview.widget.RecyclerView/android.widget.RelativeLayout[1]')
            if not firstshop.exists:
                while not serch1.exists:
                    d.press('back')
                time.sleep(1)
                continue
            getname = d.xpath('//*[@resource-id="com.mogujie:id/tv_name"]').get_text()
            if getname != shop_name:
                while not serch1.exists:
                    d.press('back')
                time.sleep(1)
                continue
            d.xpath('//*[@resource-id="com.mogujie:id/tv_name"]').click()
            time.sleep(1)
            d.xpath('//*[@resource-id="com.mogujie:id/contact_btn"]').click()
            d.xpath('//*[@text="分享"]').click()
            d.xpath('//*[@text="复制链接"]').click()
            time.sleep(1)
            url = d.clipboard
            str="http"
            index = url.index(str)
            urltext=url[index:]
            sql1="update amp_shop_marketentity t set t.sec_shop_id='%s' where t.id='%s'" % (urltext,id)
            db.execute_sql(sql1)
            while not serch1.exists:
                d.press('back')
            time.sleep(1)
            continue
        except:
            print('Error')
            while not serch1.exists:
                d.press('back')
            time.sleep(1)
            continue

def handle1():
    path = 'D:/douyin_data/response_mogujie_shop.txt'
    # path_log = 'D:/douyin_data/pinduoduo/' + time.strftime("%Y%m%d", time.localtime()) + '/'
    path_log = 'D:/douyin_data/mogujie/logo/'
    path_license = 'D:/douyin_data/mogujie/license/'
    if not os.path.exists(path_log):
        os.makedirs(path_log)
    file = open(path, 'r', encoding='utf-16')
    for line in file.readlines():
        try:
            if line != '':
                dic = json.loads(line)
                data=dic['data']
                shop_info=data['shopInfo']
                #店铺名
                shop_name=shop_info['name']
                #logo地址
                logo_url=shop_info['logo']
                identify=data['identify']
                #营业执照地址
                license_url=''
                if 'companyLicense' in identify:
                    license_url=identify['companyLicense']
                    str1='.jpg'
                    index=str(license_url).find(str1)
                    license_url1=license_url[:index+4]
                dsr=data['dsr']
                shopDsr=dsr['shopDsr']
                #评分
                dsr_num=shopDsr['desc']
                #粉丝数
                fans=data['shopFansTotal']
                #销量
                sales=data['shopSaleTotal']
                #链接id
                shopid=data['shopIdStr']

                #下载logo
                logo_name = '%s_logo.png' % (shopid)
                path1=path_log+logo_name
                opener = urllib.request.build_opener()
                opener.addheaders = [('User-agent',
                                      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36')]
                urllib.request.install_opener(opener)
                urllib.request.urlretrieve(logo_url, path1)
                # if path_logo != '':
                #     index = path_logo.find('pinduoduo')
                #     file_name = path_logo[index:]
                #     upload_minio('logo', file_name, path_logo)
                #     # sql = 'update amp_shop_marketentity t set t.logopath="%s",t.dsr_score="%s",t.sec_shop_id="%s" where t.shopname="%s"' % (
                #     # file_name, mall_star, mall_id, mall_name)
                cret_name = 'mogujie/%s' % (logo_name)
                sql = 'update amp_shop_marketentity t set t.sec_shop_id="%s",t.sales_volume="%s",t.dsr_score="%s",t.fans="%s" where t.shopname="%s" and t.medianame="蘑菇街" ' % (
                    shopid, sales,dsr_num, fans,shop_name)
                db.execute_sql(sql)

                #下载执照
                if license_url !='':
                    license_name = '%s_certificate.png' % (shopid)
                    path2 = path_license + license_name
                    opener = urllib.request.build_opener()
                    opener.addheaders = [('User-agent',
                                          'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36')]
                    urllib.request.install_opener(opener)
                    urllib.request.urlretrieve(license_url1, path2)
        except:
            print("Error")

    file.close()

def handle2():
    folder_path = "D:/douyin_data/mogujie/license/"
    file_names = os.listdir(folder_path)
    for file_name in file_names:
        try:
            str1 = '_'
            index = file_name.index(str1)
            shop_id = file_name[0:index]
            cret_name = 'mogujie/%s' % (file_name)
            upload_minio('license', cret_name, folder_path + file_name)
            sql1 = "update amp_shop_marketentity t set t.certpath='%s' where t.sec_shop_id='%s' and t.medianame='蘑菇街' " % (
                cret_name, shop_id)
            db.execute_sql(sql1)
            company = bdocrUtil(folder_path + file_name)
            if company != '':
                sql2 = "update amp_shop_marketentity t set t.shopcompany='%s' where t.sec_shop_id='%s' and t.medianame='蘑菇街' " % (
                    company, shop_id)
                db.execute_sql(sql2)
        except:
            print('error')

def handle3():
    folder_path = "D:/douyin_data/mogujie/logo/"
    file_names = os.listdir(folder_path)
    for file_name in file_names:
        str1 = '_'
        index = file_name.index(str1)
        shop_id = file_name[0:index]
        cret_name = 'mogujie/%s' % (file_name)
        upload_minio('logo', cret_name, folder_path + file_name)
        sql1 = "update amp_shop_marketentity t set t.logopath='%s' where t.sec_shop_id='%s' and t.medianame='蘑菇街'" % (
            cret_name, shop_id)
        db.execute_sql(sql1)

def handleBu():
    folder_path = "D:/douyin_data/mogujie/license/"
    file_names = os.listdir(folder_path)
    for file_name in file_names:
        try:
            str1 = '.'
            index = file_name.index(str1)
            shop_id = file_name[0:index]
            company = bdocrUtil(folder_path + file_name)
            if company != '':
                sql2 = "update amp_shop_marketentity t set t.shopcompany='%s' where t.id='%s' " % (
                    company, shop_id)
                db.execute_sql(sql2)
        except:
            print('error')

if __name__ == "__main__":
    sys.exit(handle3())
    # sys.exit(main())