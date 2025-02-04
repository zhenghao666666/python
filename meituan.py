#!/home/byquick/anaconda3/envs/bqlive_env/bin/python
import json
import os
import sys
import time
import urllib.request
import pandas as pd
import requests
import datetime
from tqdm import trange

from util import paddle_ocr
from util.MysqlHelper import MysqlHelper
from util.min_io import upload_minio
from util.xunmeng_handle import bdocrUtil

DB_CONFIG4 = {
    "host": '127.0.0.1',
    "port": 3306,
    "user": 'root',
    "password": 'root',
    "db": 'byquick',
    "charset": 'utf8'
}
db = MysqlHelper(DB_CONFIG4)
#美团餐饮
def meituan_shop_new():
    path = 'D:/douyin_data/response_meituan_shop_20230331.txt'
    # path_log = 'D:/douyin_data/pinduoduo/' + time.strftime("%Y%m%d", time.localtime()) + '/'
    path_log = 'D:/douyin_data/meituan/logo/'
    if not os.path.exists(path):
        return
    file = open(path, 'r', encoding='utf-16')
    for line in file.readlines():
        try:
            if line != '':
                dic = json.loads(line)
                data = dic['data']
                shop_info = data['baseInfo']
                shopid = shop_info['id']
                logo = shop_info['headIcon']
                mall_name = shop_info['name']
                mall_name1 = str(mall_name).replace("（", "(")
                mall_name1 = str(mall_name1).replace("）", ")")
                sql1 = "SELECT t.id FROM amp_shop_marketentity t where (t.shopname ='%s' or t.shopname='%s') and t.medianame='美团'" \
                       % (mall_name, mall_name1)
                result = db.select(sql1)
                for ob in result:
                    id = ob[0]
                    sql = 'update amp_shop_marketentity t set t.sec_shop_id="%s" where t.id="%s"' % (
                        shopid, id)
                    db.execute_sql(sql)
                    # print(count, mall_id, mall_name, mall_logo, mall_star)
                    if logo != '':
                        file_name = '%s_logo.png' % (id)
                        path_logo = path_log + file_name
                        opener = urllib.request.build_opener()
                        opener.addheaders = [('User-agent',
                                              'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36')]
                        urllib.request.install_opener(opener)
                        urllib.request.urlretrieve(logo, path_logo)
        except:
            continue
    file.close()

def meituan_shop_license():
    path = 'D:/douyin_data/response_meituan_shop_license_20230301.txt'
    # path_log = 'D:/douyin_data/pinduoduo/' + time.strftime("%Y%m%d", time.localtime()) + '/'
    path_log = 'D:/douyin_data/meituan/license/'
    if not os.path.exists(path):
        return
    file = open(path, 'r', encoding='utf-16')
    for line in file.readlines():
        try:
            if line != '':
                dic = json.loads(line)
                shop_info = dic['data']
                shopid = shop_info['poiId']
                yyzz_url = shop_info['yyzzPicUrl']
                sql1 = "SELECT t.id FROM amp_shop_marketentity t where t.sec_shop_id ='%s' and t.medianame='美团'" % (
                    shopid)
                result = db.select(sql1)
                for ob in result:
                    id = ob[0]
                    file_name = '%s_certificate.png' % (id)
                    # path_logo = download_img(mall_logo, path_log, file_name)
                    path_l = path_log + file_name
                    opener = urllib.request.build_opener()
                    opener.addheaders = [('User-agent',
                                          'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36')]
                    urllib.request.install_opener(opener)
                    yyzz = "https:%s" % (yyzz_url)
                    urllib.request.urlretrieve(yyzz, path_l)
        except:
            continue
    file.close()


def handle1():
    folder_path = "D:/douyin_data/meituan/license/"
    file_names = os.listdir(folder_path)
    today = datetime.datetime.today()
    date = today.date()
    date = str(date)
    date = date.replace("-", "")
    date = date[:-2]
    for file_name in file_names:
        try:
            str1 = '_'
            index = file_name.index(str1)
            id = file_name[0:index]
            cret_name = 'meituan/%s/%s' % (date, file_name)
            upload_minio('license', cret_name, folder_path + file_name)
            sql1 = "update amp_shop_marketentity t set t.certpath='%s' where t.id='%s' " % (
                cret_name, id)
            db.execute_sql(sql1)

            sql3 = "SELECT t.shopcompany FROM amp_shop_marketentity t where t.id='%s'" % (id)
            result = db.select(sql3)
            for ob in result:
                shopcompany = ob[0]
                if shopcompany is None:
                    company = bdocrUtil(folder_path + file_name)
                    if company != '':
                        sql2 = "update amp_shop_marketentity t set t.shopcompany='%s' where t.id='%s' " % (
                            company, id)
                        db.execute_sql(sql2)
        except:
            continue

def handle2():
    folder_path = "D:/douyin_data/meituan/logo/"
    file_names = os.listdir(folder_path)
    for file_name in file_names:
        str1 = '_'
        index = file_name.index(str1)
        shop_id = file_name[0:index]
        cret_name = 'meituan/20230718/%s' % (file_name)
        upload_minio('logo', cret_name, folder_path + file_name)
        sql1 = "update amp_shop_marketentity t set t.logopath='%s' where t.id='%s' " % (
            cret_name, shop_id)
        db.execute_sql(sql1)

#用美团小程序采大众点评餐饮
def dzdp1():
    path = 'D:/douyin_data/response_meituan_shop_20230331.txt'
    # path_log = 'D:/douyin_data/pinduoduo/' + time.strftime("%Y%m%d", time.localtime()) + '/'
    path_log = 'D:/douyin_data/meituan/logo/'
    if not os.path.exists(path):
        return
    file = open(path, 'r', encoding='utf-16')
    for line in file.readlines():
        try:
            if line != '':
                dic = json.loads(line)
                data=dic['data']
                shop_info = data['baseInfo']
                shopid= shop_info['id']
                logo= shop_info['headIcon']
                mall_name=shop_info['name']
                mall_name1=str(mall_name).replace("（","(")
                mall_name1 = str(mall_name1).replace("）", ")")
                sql1 = "SELECT t.id FROM amp_shop_marketentity t where (t.shopname ='%s' or t.shopname='%s') and t.medianame='大众点评'" \
                       % (mall_name,mall_name1)
                result = db.select(sql1)
                for ob in result:
                    id=ob[0]
                    sql = 'update amp_shop_marketentity t set t.sec_shop_id="%s" where t.id="%s"' % (
                    shopid, id)
                    db.execute_sql(sql)
                    # print(count, mall_id, mall_name, mall_logo, mall_star)
                    if logo != '':
                        file_name = '%s_logo.png' % (id)
                        path_logo = path_log + file_name
                        opener = urllib.request.build_opener()
                        opener.addheaders = [('User-agent',
                                              'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36')]
                        urllib.request.install_opener(opener)
                        urllib.request.urlretrieve(logo, path_logo)
        except:
            continue
    file.close()

def dzdp2():
    path = 'D:/douyin_data/response_meituan_shop_license_20230301.txt'
    # path_log = 'D:/douyin_data/pinduoduo/' + time.strftime("%Y%m%d", time.localtime()) + '/'
    path_log = 'D:/douyin_data/meituan/license/'
    if not os.path.exists(path):
        return
    file = open(path, 'r', encoding='utf-16')
    for line in file.readlines():
        try:
            if line != '':
                dic = json.loads(line)
                shop_info = dic['data']
                shopid=shop_info['poiId']
                yyzz_url = shop_info['yyzzPicUrl']
                sql1 = "SELECT t.id FROM amp_shop_marketentity t where t.sec_shop_id ='%s' and t.medianame='大众点评'" % (
                    shopid)
                result = db.select(sql1)
                for ob in result:
                    id=ob[0]
                    file_name = '%s_certificate.png' % (id)
                    # path_logo = download_img(mall_logo, path_log, file_name)
                    path_l = path_log + file_name
                    opener = urllib.request.build_opener()
                    opener.addheaders = [('User-agent',
                                          'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36')]
                    urllib.request.install_opener(opener)
                    yyzz="https:%s" %(yyzz_url)
                    urllib.request.urlretrieve(yyzz, path_l)
        except:
            continue
    file.close()
#大众点评上传
def dzdplicense():
    folder_path = "D:/douyin_data/meituan/license/"
    file_names = os.listdir(folder_path)
    today = datetime.datetime.today()
    date = today.date()
    date = str(date)
    date = date.replace("-", "")
    date = date[:-2]
    for file_name in file_names:
        try:
            str1 = '_'
            index = file_name.index(str1)
            id = file_name[0:index]
            cret_name = 'dazhongdianping/%s/%s' % (date, file_name)
            upload_minio('license', cret_name, folder_path + file_name)
            sql1 = "update amp_shop_marketentity t set t.certpath='%s' where t.id='%s' " % (
                cret_name, id)
            db.execute_sql(sql1)

            sql3 = "SELECT t.shopcompany FROM amp_shop_marketentity t where t.id='%s'" % (id)
            result = db.select(sql3)
            for ob in result:
                shopcompany = ob[0]
                if shopcompany is None:
                    company = bdocrUtil(folder_path + file_name)
                    if company != '':
                        sql2 = "update amp_shop_marketentity t set t.status='2',t.shopcompany='%s' where t.id='%s' " % (
                            company, id)
                        db.execute_sql(sql2)
        except:
            continue
#大众点评上传
def dzdplogo():
    folder_path = "D:/douyin_data/meituan/logo/"
    file_names = os.listdir(folder_path)
    for file_name in file_names:
        str1 = '_'
        index = file_name.index(str1)
        shop_id = file_name[0:index]
        cret_name = 'dazhongdianping/%s' % (file_name)
        upload_minio('logo', cret_name, folder_path + file_name)
        sql1 = "update amp_shop_marketentity t set t.logopath='%s' where t.id='%s' " % (
            cret_name, shop_id)
        db.execute_sql(sql1)

#美团/大众非餐饮
def yimei1(sid):
    path = 'D:/douyin_data/meituanyimei_logo.txt'
    # path_log = 'D:/douyin_data/pinduoduo/' + time.strftime("%Y%m%d", time.localtime()) + '/'
    path_log = 'D:/douyin_data/meituan/logo/'
    path1 = 'D:/douyin_data/meituanyimei_license.txt'
    path_log1 = 'D:/douyin_data/meituan/license/'

    file = open(path, 'r', encoding='utf-16')
    id=0
    for line in file.readlines():
        try:
            if line != '':
                dic = json.loads(line)
                shop_info = dic['baseInfo']
                mall_name=shop_info['shopName']

                # if 'brand' not in dic:
                storeShare = dic['headPic']
                list = storeShare['list']
                obj = list[0]
                logo = obj['url']
                # else:
                #     storeShare = dic['brand']
                #     logo = storeShare['logo']

                # mall_name1 = str(mall_name).replace("（", "(")
                # mall_name1 = str(mall_name1).replace("）", ")")
                # sql1 = "SELECT t.id FROM amp_shop_marketentity t where t.shopname ='%s' or t.shopname='%s'" % (mall_name,mall_name1)
                sql1 = "SELECT t.id FROM amp_shop_marketentity t where t.id='%s'" % (
                sid)
                result = db.select(sql1)
                for ob in result:
                    id=ob[0]

                    # print(count, mall_id, mall_name, mall_logo, mall_star)
                    if logo != '':
                        file_name = '%s_logo.png' % (sid)
                        path_logo = path_log + file_name
                        opener = urllib.request.build_opener()
                        opener.addheaders = [('User-agent',
                                              'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36')]
                        urllib.request.install_opener(opener)
                        urllib.request.urlretrieve(logo, path_logo)

        except :
            file.close()
    try:
        file1 = open(path1, 'r', encoding='utf-16')
        for line in file1.readlines():
            try:
                if line != '' and line != '\n':
                    dic = json.loads(line)
                    shop_info = dic['data']
                    certContent = shop_info['certContent']
                    list1 = certContent[0]
                    certPicture = list1['certPicture']
                    list = certPicture[0]
                    yyzz = list['picUrl']
                    file_name = '%s_certificate.png' % (id)
                    # path_logo = download_img(mall_logo, path_log, file_name)
                    path_l = path_log1 + file_name
                    opener = urllib.request.build_opener()
                    opener.addheaders = [('User-agent',
                                          'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36')]
                    urllib.request.install_opener(opener)
                    urllib.request.urlretrieve(yyzz, path_l)
            except:
                file.close()
    except:
        print("error")
    file.close()
    os.remove(path)
    try:
        file1.close()
        os.remove(path1)
    except:
        print("1")


#手动传ID用美团采饿了么（店铺名不完全匹配）
def meituan3(id):
    path = 'D:/douyin_data/response_meituan_shop_20230331.txt'
    # path_log = 'D:/douyin_data/pinduoduo/' + time.strftime("%Y%m%d", time.localtime()) + '/'
    path_log = 'D:/douyin_data/meituan/logo/'
    if not os.path.exists(path):
        return
    file = open(path, 'r', encoding='utf-16')
    for line in file.readlines():
        try:
            if line != '':
                dic = json.loads(line)
                data = dic['data']
                shop_info = data['baseInfo']
                shopid = shop_info['id']
                logo = shop_info['headIcon']

                sql = 'update amp_shop_marketentity t set t.sec_shop_id="%s" where t.id="%s"' % (
                    shopid, id)
                db.execute_sql(sql)
                # print(count, mall_id, mall_name, mall_logo, mall_star)
                if logo != '':
                    file_name = '%s_logo.png' % (id)
                    path_logo = path_log + file_name
                    opener = urllib.request.build_opener()
                    opener.addheaders = [('User-agent',
                                          'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36')]
                    urllib.request.install_opener(opener)
                    urllib.request.urlretrieve(logo, path_logo)
        except:
            continue
    file.close()
    os.remove(path)

#携程旅行
#证照页：https://dimg04.c-ctrip.com/images/03044120008e2c7qgD80A.png
#//div[@class='vcm-pop-full']//p[2]//img[1]/@src
def handleXC():
    folder_path = "D:/douyin_data/meituan/license/"
    file_names = os.listdir(folder_path)
    today = datetime.datetime.today()
    date = today.date()
    date = str(date)
    date = date.replace("-", "")
    for file_name in file_names:
        try:
            str1 = '.'
            index = file_name.index(str1)
            id = file_name[0:index]
            cret_name = 'xiecheng/%s/%s' % (date, file_name)
            upload_minio('license', cret_name, folder_path + file_name)
            sql1 = "update amp_shop_marketentity t set t.certpath='%s' where t.id='%s' " % (
                cret_name, id)
            db.execute_sql(sql1)

            sql3 = "SELECT t.shopcompany FROM amp_shop_marketentity t where t.id='%s'" % (id)
            result = db.select(sql3)
            for ob in result:
                shopcompany = ob[0]
                if shopcompany is None:
                    company = bdocrUtil(folder_path + file_name)
                    if company != '':
                        sql2 = "update amp_shop_marketentity t set t.shopcompany='%s',t.marketentityid=1 where t.id='%s' " % (
                            company, id)
                        db.execute_sql(sql2)
        except:
            continue

if __name__ == "__main__":
    sys.exit(handleXC())
    # sys.exit(meituan_shop_new())
