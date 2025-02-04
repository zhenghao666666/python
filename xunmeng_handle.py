#!/home/byquick/anaconda3/envs/bqlive_env/bin/python
import json
import os
import sys
import time
import urllib.request
from io import BytesIO
from util.test import shuiyin
import datetime
import cv2
import numpy as np
from PIL import Image
from util import paddle_ocr
from util.MysqlHelper import MysqlHelper
from util.min_io import upload_minio
from aip import AipOcr

DB_CONFIG1 = {
    "host": '127.0.0.1',
    "port": 3306,
    "user": 'root',
    "password": 'root',
    "db": 'byquick',
    "charset": 'utf8'
}
db = MysqlHelper(DB_CONFIG3)
db1= MysqlHelper(DB_CONFIG4)
db2= MysqlHelper(DB_CONFIG1)

APP_ID = ''
API_KEY = ''
SECRET_KEY = ''

def handle1():
    path = 'D:/douyin_data/response_pinduoduo_shop_20230301.txt'
    path_log = 'D:/douyin_data/pinduoduo/logo/'
    if not os.path.exists(path_log):
        os.makedirs(path_log)
    file = open(path, 'r', encoding='utf-16')
    for line in file.readlines():
        try:
            if line != '':
                dic = json.loads(line)
                shop_info = dic['mall_basic_info']
                dsr = dic['dsr']
                mall_id = shop_info['mall_id']
                mall_name = shop_info['mall_name']
                mall_logo = shop_info['mall_logo']
                mall_star = ''
                if 'mall_star' in dsr:
                    mall_star = dsr['mall_star']
                licenseinfo=dic['mall_licence_info']
                is_certificated=licenseinfo['is_certificated']
                # print(count, mall_id, mall_name, mall_logo, mall_star)
                sql1 = "SELECT t.id,t.shopname FROM amp_shop_marketentity t where t.sec_shop_id ='%s' and t.medianame='拼多多'" % (mall_id)
                result =db.select(sql1)
                if len(result) < 1:
                    continue
                for ob in result:
                    id=ob[0]
                file_name = '%s_%s_logo.png' % (mall_id, mall_name)
                # path_logo = download_img(mall_logo, path_log, file_name)
                path=path_log+file_name
                opener = urllib.request.build_opener()
                opener.addheaders = [('User-agent',
                                      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36')]
                urllib.request.install_opener(opener)
                urllib.request.urlretrieve(mall_logo, path)
                cret_name = 'pinduoduo/20230730/%s' % (file_name)
                upload_minio('logo', cret_name, path)
                sql = 'update amp_shop_marketentity t set t.sec_shop_id="%s",t.logopath="%s",t.dsr_score="%s",t.shopname="%s" ' % (
                    mall_id,cret_name, mall_star,mall_name)
                #四平台区分个人企业店铺新字段shoptype
                if is_certificated:
                    sql+=',t.shoptype="%s" ' % '企业'
                else:
                    sql += ',t.shoptype="%s" ' % '个人'
                sql+='where t.id="%s"' % id
                db.execute_sql(sql)
        except:
            print("Error")
    file.close()

def handle1wulin():
    path = 'D:/douyin_data/response_pinduoduo_shop_20230301.txt'
    path_log = 'D:/douyin_data/pinduoduo/logo/'
    if not os.path.exists(path_log):
        os.makedirs(path_log)
    file = open(path, 'r', encoding='utf-16')
    for line in file.readlines():
        try:
            if line != '':
                dic = json.loads(line)
                shop_info = dic['mall_basic_info']
                dsr = dic['dsr']
                mall_id = shop_info['mall_id']
                mall_name = shop_info['mall_name']
                mall_logo = shop_info['mall_logo']
                mall_star = ''
                if 'mall_star' in dsr:
                    mall_star = dsr['mall_star']
                licenseinfo = dic['mall_licence_info']
                is_certificated = licenseinfo['is_certificated']
                # print(count, mall_id, mall_name, mall_logo, mall_star)
                sql1 = "SELECT t.id FROM amp_shop_marketentity t where t.shopname ='%s' and t.medianame='拼多多'" % (
                    mall_name)
                result = db2.select(sql1)
                if len(result) < 1:
                    continue
                for ob in result:
                    id = ob[0]
                file_name = '%s_logo.png' % (mall_id)
                # path_logo = download_img(mall_logo, path_log, file_name)
                path = path_log + file_name
                opener = urllib.request.build_opener()
                opener.addheaders = [('User-agent',
                                      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36')]
                urllib.request.install_opener(opener)
                urllib.request.urlretrieve(mall_logo, path)
                cret_name = 'pinduoduo/wulin/%s' % (file_name)
                upload_minio('logo', cret_name, path)
                sql = 'update amp_shop_marketentity t set t.sec_shop_id="%s",t.logopath="%s",t.dsr_score="%s" ' % (
                    mall_id, cret_name, mall_star)
                # 四平台区分个人企业店铺新字段shoptype
                if is_certificated:
                    sql += ',t.certpath=1 '
                sql += 'where t.id="%s"' % id
                db2.execute_sql(sql)
        except:
            print("Error")
    file.close()

def handle2hyg():
    folder_path = "D:/douyin_data/pinduoduo/license/"
    file_names = os.listdir(folder_path)
    today = datetime.datetime.today()
    date = today.date()
    date = str(date)
    date = date.replace("-", "")
    date = date[:-2]
    for file_name in file_names:
        try:
            str1 = '.'
            index = file_name.index(str1)
            shop_id = file_name[0:index]
            new_name = '%s_certificate.png' % (shop_id)
            cret_name = 'pinduoduo/%s/%s' % (date,new_name)
            upload_minio('license', cret_name, folder_path + file_name)
            sql1 = "update amp_shop_marketentity t set t.certpath='%s' where t.id='%s'" % (
                cret_name, shop_id)
            db.execute_sql(sql1)
            company = ''
            if file_name[-3:]=='jpg':
                img = cv2.imread(folder_path+file_name, cv2.IMREAD_UNCHANGED)
                a = shuiyin.ocr(img)
                for word in a:
                    dic = dict(word)
                    value = dic['text']
                    if '企业名称：' in value:
                        str2 = '企业名称：'
                        index = value.index(str2)
                        text = value[index + 5:]
                        company = text
                        if '白货' in company:
                            company = company.replace('白货', '百货')
                        if '公巨' in company:
                            company = company.replace('公巨', '公司')
                        break
                    else:
                        continue

            else:
                company=bdocrUtil(folder_path + file_name)
            if company !='':
                sql2 = "update amp_shop_marketentity t set t.status='2',t.shopcompany='%s' where t.id='%s' " % (
                    company, shop_id)
                db.execute_sql(sql2)
        except:
            continue

def handle2grxx():
    folder_path = "D:/douyin_data/pinduoduo/wulin/"
    file_names = os.listdir(folder_path)
    for file_name in file_names:
        try:
            str1 = '.'
            index = file_name.index(str1)
            shop_id = file_name[0:index]

            a = paddle_ocr.get_text(folder_path + file_name)
            str = '店主姓名'
            str1 = '联系方式'
            str2 = '经营地址'
            index = a.index(str)
            index1 = a.index(str1)
            index2 = a.index(str2)
            name=a[index+4:index1]
            contactinfo=a[index1+4:index2]
            businessaddress = a[index2 + 4:]
            name1=name.replace(' ','')
            contactinfo1=contactinfo.replace(' ','')
            businessaddress1=businessaddress.replace(' ','')

            sql2 = "update amp_shop_marketentity t set t.name='%s',t.contactinfo='%s',t.businessaddress='%s' where t.id='%s' " % (
                name1, contactinfo1,businessaddress1,shop_id)
            db.execute_sql(sql2)
        except:
            continue

def handle2wulin():
    folder_path = "D:/douyin_data/pinduoduo/license/"
    file_names = os.listdir(folder_path)
    today = datetime.datetime.today()
    date = today.date()
    date = str(date)
    date = date.replace("-", "")
    date = date[:-2]
    for file_name in file_names:
        try:
            str1 = '.'
            index = file_name.index(str1)
            shop_id = file_name[0:index]
            new_name = '%s_certificate.png' % (shop_id)
            cret_name = 'pinduoduo/%s/%s' % (date,new_name)
            upload_minio('license', cret_name, folder_path + file_name)
            sql1 = "update amp_shop_marketentity t set t.certpath='%s' where t.id='%s'" % (
                cret_name, shop_id)
            db2.execute_sql(sql1)
            company = ''
            if file_name[-3:]=='jpg':
                img = cv2.imread(folder_path+file_name, cv2.IMREAD_UNCHANGED)
                a = shuiyin.ocr(img)
                for word in a:
                    dic = dict(word)
                    value = dic['text']
                    if '企业名称：' in value:
                        str2 = '企业名称：'
                        index = value.index(str2)
                        text = value[index + 5:]
                        company = text
                        if '白货' in company:
                            company = company.replace('白货', '百货')
                        if '公巨' in company:
                            company = company.replace('公巨', '公司')
                        break
                    else:
                        continue

            else:
                company=bdocrUtil(folder_path + file_name)
            if company !='':
                sql2 = "update amp_shop_marketentity t set t.shopcompany='%s' where t.id='%s' " % (
                    company, shop_id)
                db2.execute_sql(sql2)
        except:
            continue

def ocr():
    sql = "SELECT t.id,t.certpath FROM amp_shop_marketentity t where t.id>=112524 and t.certpath is not null and t.shopcompany is null and t.medianame='小红书'"
    result = db2.select(sql)
    path_orc = 'D:/douyin_data/xhs/license/'
    for ob in result:
        try:
            id = ob[0]
            certpath = ob[1]
            word = urllib.parse.quote(certpath)
            url = 'http://222.222.99.153:30004/license/%s' %(word)
            url.encode('UTF-8', 'ignore').decode('UTF-8')
            filename='%s.png' %(id)
            path = path_orc + filename
            opener = urllib.request.build_opener()
            opener.addheaders = [('User-agent',
                                  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36')]
            urllib.request.install_opener(opener)
            urllib.request.urlretrieve(url, path)

            # sql1 = "update amp_shop_marketentity t set t.status='6' where t.id='%s' " % (id)
            # db.execute_sql(sql1)
            #
            #
            # #百度OCR
            # company=bdocrUtil(path)
            # if company !='':
            #     #修改大库
            #     sql2 = "update amp_shop_marketentity t set t.shopcompany='%s' where t.id='%s' " % (
            #         company, id)
            #     db.execute_sql(sql2)

        except:
            continue

def bdocrUtil(path):
    client = AipOcr(APP_ID, API_KEY, SECRET_KEY)
    with open(path, 'rb') as file:
        img = file.read()
    size = os.path.getsize(path) / 1024 / 1024
    if size>7:
        return ''
    result = client.basicAccurate(img)
    print(result)
    words = result.get('words_result')
    list1 = list(words)
    company = ''
    num = 0
    for i in list1:
        word = dict(i)
        value = word['words']
        if value == '公司名称：' or value == '名称' or value == '称' or value == '名':
            num = 1
            continue
        elif '企业名称：' in value or num == 1 or '有限公司' in value or '商行' in value or '公司名称：' in value:
            if len(value) < 6:
                continue
            if '天猫入驻' in value or '统一社会' in value or '公示专用' in value or '9' in value or '元整' in value or '无效' in value or '仅限' in value:
                continue
            company = value
            company = str(company)
            if '企业名称：' in company or '公司名称：' in company:
                company = company[5:]
            if company[0:2]=='名称':
                company = company[2:]
            if company[0:1]=='称':
                company = company[1:]
            company =company.replace('(', '（')
            company =company.replace(')', '）')
            break
    return company
#

#如果fiddler弹“不是私密链接”，鼠标点击空白处输入：thisisunsafe即可
if __name__ == "__main__":
    sys.exit(handle2wulin())
    # sys.exit(handle2dzdp())
    # sys.exit(meituan_shop_new())
    # sys.exit(ocr())
    # sys.exit(test())