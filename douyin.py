import json
import os
import sys
import time
import urllib.request
import datetime
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
db1=MysqlHelper(DB_CONFIG1)

def handle1():
    folder_path = "D:/douyin_data/douyin/license/"
    file_names = os.listdir(folder_path)
    today = datetime.datetime.today()
    date = today.date()
    date = str(date)
    date = date.replace("-", "")
    for file_name in file_names:
        try:
            str1 = '_'
            index = file_name.index(str1)
            id = file_name[0:index]
            cret_name = 'douyin/%s/%s' % (date, file_name)
            upload_minio('license', cret_name, folder_path + file_name)
            sql1 = "update amp_shop_marketentity t set t.certpath='%s' where t.id='%s' " % (
                cret_name, id)
            db1.execute_sql(sql1)

            # sql3 = "SELECT t.shopcompany FROM amp_shop_marketentity t where t.id='%s'" % (id)
            # result = db1.select(sql3)
            # for ob in result:
            #     shopcompany = ob[0]
            #     if shopcompany is None:
            #         company = bdocrUtil(folder_path + file_name)
            #         if company != '':
            #             sql2 = "update amp_shop_marketentity t set t.shopcompany='%s',t.marketentityid=1 where t.id='%s' " % (
            #                 company, id)
            #             db1.execute_sql(sql2)
        except:
            continue

def handle2():
    folder_path = "D:/douyin_data/douyin/710logo/"
    file_names = os.listdir(folder_path)
    for file_name in file_names:
        str1 = '_'
        index = file_name.index(str1)
        shop_id = file_name[0:index]
        cret_name = 'douyin/%s' % (file_name)
        upload_minio('logo',cret_name,folder_path+file_name)
        sql1 = "update amp_shop_marketentity t set t.logopath='%s' where t.id='%s' " % (
            cret_name, shop_id)
        db1.execute_sql(sql1)

def main1():
    d = u2.connect('A48B9X2A20W12786')
    sql = "SELECT t.id,t.sec_shop_id,t.shopname FROM amp_shop_marketentity t where t.id>=146400" \
          " and t.sec_shop_id is not null and t.shopcompany is null and t.medianame='抖音短视频'"
    result = db1.select(sql)
    pathlicense = 'D:/douyin_data/douyin/license/'
    for ob in result:
        try:
            id = ob[0]
            shop_id = ob[1]
            shopname = ob[2]
            time.sleep(5)
            url = 'snssdk1128://goods/store?sec_shop_id=%s' % shop_id
            d.open_url(url)
            time.sleep(1)

            dsr_text = ''
            # dsr = d.xpath('//*[@resource-id="com.ss.android.ugc.aweme:id/twq"]').wait(timeout=2)
            # if not dsr is None:
            #     dsr_text = dsr.text

            xq = d.xpath('//*[@resource-id="com.ss.android.ugc.aweme:id/fvh"]')

            for i in range(5):
                if xq.exists:
                    break
                else:
                    time.sleep(1)
                    xq = d.xpath('//*[@resource-id="com.ss.android.ugc.aweme:id/fvh"]')
            # d.xpath('//*[@resource-id="com.ss.android.ugc.aweme:id/erp"]').click()
            xq.click()
            time.sleep(1)
            fan = d.xpath('//*[contains(@text,"粉丝")]').wait(timeout=2)
            fans_text = ""
            volstr = ""
            if not fan is None:
                fans = fan.text
                fans_text = fans[3:]

            vol = d.xpath('//*[contains(@text,"销量")]')
            if vol.exists:
                voltext = vol.get_text()
                volstr = voltext[3:]
                if '量' in volstr:
                    index = volstr.index('量')
                    volstr = volstr[index + 2:]
            if fans_text != "" or volstr != "":
                sql1 = 'update amp_shop_marketentity t set t.fans="%s", t.sales_volume="%s" where t.id=%s' % (
                    fans_text, volstr, id)
                db1.execute_sql(sql1)
            if '海外' not in shopname:
                zizhi = d.xpath('//*[contains(@text,"查看资质")]')
                for i in range(3):
                    if zizhi.exists:
                        break
                    else:
                        time.sleep(1)
                        zizhi = d.xpath('//*[contains(@text,"查看资质")]')
                zizhi.click()
                time.sleep(1)

                shangjia = d.xpath('//*[@text="营业执照"]')
                for i in range(10):
                    if shangjia.exists:
                        break
                    else:
                        time.sleep(1)
                img = d.xpath('//*[@resource-id="com.ss.android.ugc.aweme:id/i_a"]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/com.lynx.tasm.ui.image.FlattenUIImage[3]')
                for i in range(5):
                    if img.exists:
                        break
                    else:
                        time.sleep(1)
                d.click(364, 633)
                time.sleep(1)
                for i in range(5):
                    if img.exists:
                        img.click()
                        time.sleep(1)
                    else:
                        break
                img_scr = d.screenshot()
                cert_name = '%s_certificate.png' % (id)
                img_scr.crop((0, 550, 720, 1050)).save(pathlicense + cert_name)
                # img.screenshot().save(pathlicense + cert_name)

                front = 0
                bake = os.path.getsize(pathlicense + cert_name)
                while front != bake:
                    front = bake
                    time.sleep(1)
                    img_scr = d.screenshot()
                    cert_name = '%s_certificate.png' % (id)
                    img_scr.crop((0, 550, 720, 1050)).save(pathlicense + cert_name)
                    # img.screenshot().save(pathlicense + cert_name)
                    bake = os.path.getsize(pathlicense + cert_name)
        except:
            print("Error")

def main2():
    d = u2.connect('HMQNW19B08001936')
    # d = u2.connect('A48B9X2A20W12786')
    sql = "SELECT t.id,t.sec_shop_id,t.shopname FROM amp_shop_marketentity t where t.id>=149015" \
          " and t.sec_shop_id is not null and t.shopcompany is null and t.medianame='抖音短视频'"

    result = db1.select(sql)
    pathlicense = 'D:/douyin_data/douyin/license/'

    for ob in result:
        try:
            id = ob[0]
            shop_id = ob[1]
            shopname=ob[2]
            time.sleep(2)
            url = 'snssdk1128://goods/store?sec_shop_id=%s' % shop_id
            d.open_url(url)
            time.sleep(1)

            dsr_text = ''
            # dsr = d.xpath('//*[@resource-id="com.ss.android.ugc.aweme:id/twq"]').wait(timeout=2)
            # if not dsr is None:
            #     dsr_text = dsr.text

            xq=d.xpath('//*[@resource-id="com.ss.android.ugc.aweme:id/fv="]')

            for i in range(5):
                if xq.exists:
                    break
                else:
                    time.sleep(1)
                    xq = d.xpath('//*[@resource-id="com.ss.android.ugc.aweme:id/fv="]')
            # d.xpath('//*[@resource-id="com.ss.android.ugc.aweme:id/erp"]').click()
            isFans=d.xpath('//*[@text="粉丝"]')
            fans_text=""
            if isFans.exists:
                fan = d.xpath('//*[@resource-id="com.ss.android.ugc.aweme:id/fy+"]')
                wan=d.xpath('//*[@resource-id="com.ss.android.ugc.aweme:id/fza"]')
                fans_text = fan.get_text()
                if wan.exists:
                    wantext=wan.get_text()
                    fans_text=fans_text+wantext

            xq.click()
            time.sleep(1)

            volstr = ""
            vol = d.xpath('//*[contains(@text,"销量")]')
            if vol.exists:
                voltext = vol.get_text()
                volstr = voltext[3:]
                if '量' in volstr:
                    index = volstr.index('量')
                    volstr = volstr[index + 2:]
            if fans_text!="" or volstr !="":
                sql1 = 'update amp_shop_marketentity t set t.fans="%s",t.sales_volume="%s" where t.id=%s' % (
                     fans_text,volstr, id)
                db1.execute_sql(sql1)
            if '海外' not in shopname:
                zizhi = d.xpath('//*[contains(@text,"查看资质")]')
                for i in range(3):
                    if zizhi.exists:
                        break
                    else:
                        time.sleep(1)
                        zizhi = d.xpath('//*[contains(@text,"查看资质")]')
                time.sleep(3)
                zizhi.click()
                time.sleep(1)

                shangjia = d.xpath('//*[@text="营业执照"]')
                for i in range(10):
                    if shangjia.exists:
                        break
                    else:
                        time.sleep(1)
                img = d.xpath('/hierarchy/android.widget.FrameLayout[1]/android.widget.LinearLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.view.ViewGroup[1]/android.widget.FrameLayout[2]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/com.lynx.tasm.behavior.ui.LynxFlattenUI[5] | /hierarchy/android.widget.FrameLayout[2]/android.widget.LinearLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.view.ViewGroup[1]/android.widget.FrameLayout[2]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/com.lynx.tasm.behavior.ui.LynxFlattenUI[5]')
                for i in range(5):
                    if img.exists:
                        break
                    else:
                        img = d.xpath(
                            '/hierarchy/android.widget.FrameLayout[1]/android.widget.LinearLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.view.ViewGroup[1]/android.widget.FrameLayout[2]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/com.lynx.tasm.behavior.ui.LynxFlattenUI[5] | /hierarchy/android.widget.FrameLayout[2]/android.widget.LinearLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.view.ViewGroup[1]/android.widget.FrameLayout[2]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/com.lynx.tasm.behavior.ui.LynxFlattenUI[5]')
                        time.sleep(1)

                img_scr = d.screenshot()
                cert_name = '%s_certificate.png' % (id)
                # img_scr.crop((0, 665, 1075, 1740)).save(pathlicense + cert_name)
                img.screenshot().save(pathlicense + cert_name)

                # front = 0
                # bake = os.path.getsize(pathlicense + cert_name)
                # while front != bake:
                #     front = bake
                #     time.sleep(1)
                #     img_scr = d.screenshot()
                #     cert_name = '%s_certificate.png' % (id)
                #     # img_scr.crop((0, 820, 1075, 1580)).save(pathlicense + cert_name)
                #     img.screenshot().save(pathlicense + cert_name)
                #     bake = os.path.getsize(pathlicense + cert_name)
                maId=d.xpath("//com.lynx.tasm.behavior.ui.text.FlattenUIText[starts-with(@text, '营业执照编号')][1]")
                company=d.xpath("//com.lynx.tasm.behavior.ui.text.FlattenUIText[starts-with(@text, '企业名称')][1]")
                matext=maId.get_text()
                matext=matext[9:]
                companytext=company.get_text()
                companytext=companytext[7:]
                sql2 = 'update amp_shop_marketentity t set t.shopcompany="%s",t.marketentityid="%s" where t.id=%s' % (
                    companytext, matext, id)
                db1.execute_sql(sql2)

        except:
            print("Error")

def text():
    path = 'D:/douyin_data/douyin_shopinfo.txt'
    path_log = 'D:/douyin_data/douyin/logo/'
    if not os.path.exists(path_log):
        os.makedirs(path_log)
    file = open(path, 'r', encoding='utf-16')
    for line in file.readlines():
        try:
            if line != '':
                dic = json.loads(line)
                shop_info = dic['data']
                dsr = shop_info['score']
                mall_id = shop_info['shopId']
                mall_name = shop_info['desc']
                mall_logo = shop_info['cover']

                # print(count, mall_id, mall_name, mall_logo, mall_star)
                sql1 = "SELECT t.id,t.shopname FROM amp_shop_marketentity t where t.shopname ='%s' and t.medianame='抖音短视频' and t.id>=53434" % (
                    mall_name)
                result = db1.select(sql1)
                if len(result) < 1:
                    continue
                for ob in result:
                    id = ob[0]
                file_name = '%s_logo.png' % (id)
                # path_logo = download_img(mall_logo, path_log, file_name)
                path = path_log + file_name
                opener = urllib.request.build_opener()
                opener.addheaders = [('User-agent',
                                      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36')]
                urllib.request.install_opener(opener)
                urllib.request.urlretrieve(mall_logo, path)
                cret_name = 'douyin/20230904/%s' % (file_name)
                upload_minio('logo', cret_name, path)
                sql = 'update amp_shop_marketentity t set t.sec_shop_id="%s",t.logopath="%s",t.dsr_score="%s" where t.id="%s"' % (
                    mall_id, cret_name,dsr,id)
                db1.execute_sql(sql)
        except:
            print("Error")
    file.close()
#快手
#https://app.kwaixiaodian.com/merchant/shop/list?id=

if __name__ == "__main__":
    # sys.exit(mainks3(35236))
    sys.exit(handle1())
    # main1()
