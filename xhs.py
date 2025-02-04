import json
import os
import sys
import time
import urllib.request
import pandas as pd
import requests
import uiautomator2 as u2
import ddddocr,time
from tqdm import trange
from util.MysqlHelper import MysqlHelper
from util.min_io import upload_minio
from util.xunmeng_handle import bdocrUtil
from util import utils, paddle_ocr, const_wulin, text_handling, rtmp, sql_live_wulin


DB_CONFIG1 = {
    "host": '127.0.0.1',
    "port": 3306,
    "user": 'root',
    "password": 'root',
    "db": 'byquick',
    "charset": 'utf8'
}
db = MysqlHelper(DB_CONFIG1)
# d = u2.connect('A48B9X2A20W12786')

#小红书店铺链接：https://www.xiaohongshu.com/vendor/shopid
def handle1():
    folder_path = "D:/douyin_data/xhs/license/"
    file_names = os.listdir(folder_path)
    for file_name in file_names:
        str1 = '.'
        index = file_name.index(str1)
        shop_id = file_name[0:index]
        newname='%s_xhs_certificate.png' % (shop_id)
        cret_name = 'xiaohongshu/%s' % (newname)
        upload_minio('license',cret_name,folder_path+file_name)
        sql1 = "update amp_shop_marketentity t set t.certpath='%s' where t.id='%s'" % (
            cret_name, shop_id)
        db.execute_sql(sql1)

        sql3 = "SELECT t.shopcompany FROM amp_shop_marketentity t where t.id='%s'" % (shop_id)
        result = db.select(sql3)
        for ob in result:
            shopcompany = ob[0]
            if shopcompany is None:
                company = bdocrUtil(folder_path + file_name)
                if company != '':
                    sql2 = "update amp_shop_marketentity t set t.shopcompany='%s',t.marketentityid=1 where t.id='%s' " % (
                        company, shop_id)
                    db.execute_sql(sql2)

def handle2():
    folder_path = "D:/douyin_data/xhs/logo/"
    file_names = os.listdir(folder_path)
    for file_name in file_names:
        str1 = '_'
        index = file_name.index(str1)
        shop_id = file_name[0:index]
        newname='%s_xhs_logo.png' % (shop_id)
        cret_name = 'xiaohongshu/%s' % (newname)
        upload_minio('logo',cret_name,folder_path+file_name)
        sql1 = "update amp_shop_marketentity t set t.logopath='%s' where t.id='%s'" % (
            cret_name, shop_id)
        db.execute_sql(sql1)

def main():
    d = u2.connect('HMQNW19B08001936')
    sql = "SELECT t.shopname,t.id FROM amp_shop_marketentity t where  t.id>=150525 and t.medianame='小红书' and t.shopcompany is null"
    result = db.select(sql)
    pathlogo = 'D:/douyin_data/xhs/logo/'
    pathlicense = 'D:/douyin_data/xhs/license/'
    pathocr='D:/douyin_data/xhs/ocr/'
    for ob in result:
        try:
            shop_name = ob[0]
            id = ob[1]
            search=d.xpath('//*[@resource-id="com.xingin.xhs:id/f_h"]')
            search.click()
            d.send_keys(shop_name, clear=True)
            sousuo=d.xpath('//*[@resource-id="com.xingin.xhs:id/f_m"]')
            sousuo.click()
            time.sleep(1)
            # goods=d.xpath('//*[@text="商品"]').wait(timeout=3)
            # goods.click()
            # time.sleep(1)
            name=d.xpath('//*[@resource-id="com.xingin.xhs:id/f_2"]/android.widget.LinearLayout[1]/android.widget.LinearLayout[1]/android.widget.TextView[1]')
            text=name.text
            shopnamespace=shop_name.replace(" ", "")
            textspace=text.replace(" ", "")
            if textspace!=shopnamespace:
                while not search.exists:
                    d.press('back')
                    d.sleep(1)
                continue
            while name.exists:
                name.click()
                d.sleep(1)
            time.sleep(1)
            hao = d.xpath('//*[contains(@text,"小红书号")]')

            haotext=hao.get_text()
            num=haotext[5:]
            sql1 = 'update amp_shop_marketentity t set t.sec_shop_id="%s" where t.id=%s' % (
                num, id)
            db.execute_sql(sql1)

            d.xpath('//*[@resource-id="com.xingin.xhs:id/gux"]').click()
            time.sleep(1)
            d.xpath('//*[@text="店铺详情"]').click()

            dsr1=d.xpath('//*[contains(@text,"卖家口碑")]/following-sibling::android.view.View[1]')
            fen=dsr1.text
            if len(fen)>5:
                fen =None
            xiaoliang = d.xpath('//*[contains(@text,"已售")]').get_text()
            vol=xiaoliang[:-2]
            guanzhu= d.xpath('//*[contains(@text,"关注")]').get_text()
            fans=guanzhu[:-2]
            sql2 = 'update amp_shop_marketentity t set t.sales_volume="%s",t.fans="%s"' % (
                 vol, fans)
            if fen is not None:
                sql2+=', t.dsr_score="%s"' % fen
            sql2+= 'where t.id="%s"' % id
            db.execute_sql(sql2)
            logoexist=d.xpath('//*[@resource-id="app"]/android.view.View[1]')
            if logoexist.exists:
                logourl = d.xpath('//*[@resource-id="app"]/android.view.View[1]/*[1]').get_text()
                url = 'https://sns-avatar-qc.xhscdn.com/avatar/%s.jpg' % (logourl)
                logo_name = '%s_xhs_logo.png' % (id)
                opener = urllib.request.build_opener()
                opener.addheaders = [('User-agent',
                                      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36')]
                urllib.request.install_opener(opener)
                try:
                    urllib.request.urlretrieve(url, pathlogo + logo_name)
                except:
                    print('LogoError')
            if '海外' not in shop_name:
                d.xpath('//*[@text="查看详情"]').click()

                ocrsearch = d.xpath('//android.widget.EditText')

                for i in range(9):
                    if ocrsearch.exists:
                        break
                    else:
                        time.sleep(1)

                while ocrsearch.exists:
                    img_scr = d.screenshot()
                    ocrname = '%s_xhs_ocr.png' % (id)
                    # img_scr.crop((85, 375, 315, 430)).save(pathocr + ocrname)
                    imgocr=d.xpath('//android.widget.Image')
                    imgocr.screenshot().save(pathocr + ocrname)
                    time.sleep(1)
                    with open(pathocr + ocrname, 'rb') as file:
                        img = file.read()
                    ocr = ddddocr.DdddOcr()
                    text = ocr.classification(img)
                    ocrsearch.click()
                    d.send_keys(text, clear=True)
                    d.xpath('//*[@text="确定"]').click()
                    time.sleep(1)
                time.sleep(1)
                licen = d.xpath('//*[@resource-id="app"]/android.view.View[3]')
                if licen.exists:
                    front=0
                    licname = '%s.png' % (id)
                    licen.screenshot().save(pathlicense + licname)
                    bake=os.path.getsize(pathlicense + licname)
                    while front!=bake:
                        front=bake
                        time.sleep(1)
                        licname = '%s.png' % (id)
                        licen.screenshot().save(pathlicense + licname)
                        bake=os.path.getsize(pathlicense + licname)
            while not search.exists:
                d.press('back')
                d.sleep(1)
            continue

        except:
            print('Error')
            while not search.exists:
                d.press('back')
                d.sleep(1)
            continue

def updateId():
    sql = "SELECT t.certpath,t.sec_shop_id FROM amp_illege_liveroom t where t.certpath is not null and t.liveroomcompany is null and t.medianame='小红书' "
    result = db.select(sql)
    path_orc = 'D:/douyin_data/xhs/test/'
    for ob in result:
        try:
            certpath = ob[0]
            shopid = ob[1]
            word = urllib.parse.quote(certpath)
            url = 'http://222.222.99.153:30004/license/%s' % (word)
            url.encode('UTF-8', 'ignore').decode('UTF-8')
            filename = '%s.png' % (shopid)
            path = path_orc + filename
            opener = urllib.request.build_opener()
            opener.addheaders = [('User-agent',
                                  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36')]
            urllib.request.install_opener(opener)
            urllib.request.urlretrieve(url, path)
        except:
            continue

def xhslive():
    d = u2.connect('HMQNW19B08001936')
    sql = "SELECT t.liveroomname,t.id,t.sec_shop_id FROM amp_illege_liveroom t where t.sec_shop_id is not null and t.certpath is null and t.medianame='小红书' and id>'DCE0A20D8C1A45D9A9145AD4EA9B50E7'"
    result = db.select(sql)
    pathlicense = 'D:/douyin_data/xhs/test/'
    pathocr = 'D:/douyin_data/xhs/ocr/'
    for ob in result:
        try:
            shop_name = ob[0]
            id = ob[1]
            shopid=ob[2]
            if '海外' in shop_name:
                continue
            search=d.xpath('//*[@resource-id="com.xingin.xhs:id/dlx"]')
            while not search.exists:
                d.press('back')
                d.sleep(1)
            search.click()
            d.send_keys(shopid, clear=True)
            sousuo=d.xpath('//*[@resource-id="com.xingin.xhs:id/dm2"]')
            sousuo.click()
            time.sleep(1)
            goods=d.xpath('//*[@text="用户"]').wait(timeout=3)
            goods.click()
            first=d.xpath('//*[@resource-id="com.xingin.xhs:id/dlg"]/android.widget.RelativeLayout[1]')
            if not first.exists:
                continue
            numtext=d.xpath('//*[@resource-id="com.xingin.xhs:id/dlg"]/android.widget.RelativeLayout[1]//*[@resource-id="com.xingin.xhs:id/dm7"]').get_text()
            num=numtext[5:]
            print(num)
            if num!=shopid:
                continue
            first.click()
            time.sleep(1)

            d.xpath('//*[@resource-id="com.xingin.xhs:id/eqv"]').click()
            time.sleep(1)
            dpxq=d.xpath('//*[@text="店铺详情"]')
            if not dpxq.exists:
                continue
            dpxq.click()
            dsr = d.xpath('//*[@resource-id="app"]/android.view.View[6]')
            for i in range(9):
                if dsr.exists:
                    break
                else:
                    time.sleep(1)

            if '海外' not in shop_name:
                d.xpath('//*[@text="查看详情"]').click()

                ocrsearch = d.xpath('//android.widget.EditText')

                for i in range(9):
                    if ocrsearch.exists:
                        break
                    else:
                        time.sleep(1)

                while ocrsearch.exists:
                    img_scr = d.screenshot()
                    ocrname = '%s_xhs_ocr.png' % (shopid)
                    img_scr.crop((85, 375, 315, 430)).save(pathocr + ocrname)
                    time.sleep(1)
                    with open(pathocr + ocrname, 'rb') as file:
                        img = file.read()
                    ocr = ddddocr.DdddOcr()
                    text = ocr.classification(img)
                    ocrsearch.click()
                    d.send_keys(text, clear=True)
                    d.xpath('//*[@text="确定"]').click()
                    time.sleep(1)
                time.sleep(1)
                licen = d.xpath('//*[@resource-id="app"]/android.view.View[3]')
                grxx = d.xpath('//*[@resource-id="app"]/android.view.View[4]')
                if grxx.exists:
                    img_scr1 = d.screenshot()
                    licname = '%s_xhs_certificate.png' % (id)
                    img_scr1.crop((55, 585, 661, 803)).save(pathlicense + licname)
                elif licen.exists:
                    front = 0
                    licname = '%s_xhs_certificate.png' % (id)
                    licen.screenshot().save(pathlicense + licname)
                    bake = os.path.getsize(pathlicense + licname)
                    while front != bake:
                        front = bake
                        time.sleep(1)
                        licname = '%s_xhs_certificate.png' % (id)
                        licen.screenshot().save(pathlicense + licname)
                        bake = os.path.getsize(pathlicense + licname)
            sql1 = 'update amp_illege_liveroom t set t.certpath=1 where t.id="%s"' %  (id)
            db.execute_sql(sql1)
            while not search.exists:
                d.press('back')
                d.sleep(1)
            continue

        except:
            print('Error')
            while not search.exists:
                d.press('back')
                d.sleep(1)
            continue

def change():
    folder_path = "D:/douyin_data/xhs/test/"
    file_names = os.listdir(folder_path)
    for file_name in file_names:
        str1 = '_'
        index = file_name.index(str1)
        shop_id = file_name[0:index]
        cret_name = 'illege/xiaohongshu/20230821/%s' % (file_name)
        upload_minio('license', cret_name, folder_path + file_name)
        sql1 = "update amp_illege_liveroom t set t.certpath='%s' where t.id='%s'" % (
            cret_name, shop_id)
        db.execute_sql(sql1)

if __name__ == "__main__":
    sys.exit(handle1())
    # sys.exit(updateId1())
    # sys.exit(handle1())