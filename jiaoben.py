import uiautomator2 as u2
import json
from util.MysqlHelper import MysqlHelper
import time
import threading
import sched

DB_CONFIG = {
    "host": '127.0.0.1',
    "port": 3306,
    "user": 'root',
    "password": 'root',
    "db": 'byquick',
    "charset": 'utf8'
}

db = MysqlHelper(DB_CONFIG)
db1 = MysqlHelper(DB_CONFIG2)
d = u2.connect('A48B9X2A20W12786')
# url='https://mall.jd.com/index-10362165.html'
# data = {"category":"jump","des":"m","sourceValue":"babel-act","sourceType":"babel","url":url,"M_sourceFrom":"h5auto","msf_type":"auto"}
# jsonstr=json.dumps(data)
# d.open_url("openApp.jdMobile://virtual?params="+jsonstr)
#获取粘贴板
# url = d.clipboard

def main():
    sql="SELECT t.shopname,t.id FROM amp_shop_marketentity t where t.medianame='京东' and t.sec_shop_id is null"
    result = db.select(sql)
    d.app_start("com.jingdong.app.mall", wait=True)
    time.sleep(3)
    for ob in result:
        shop_name=ob[0]
        id=ob[1]
        sql = 'update amp_shop_marketentity t set t.sec_shop_id="1" where t.id="%s" ' % (id)
        db.execute_sql(sql)
        serch=d.xpath('//*[@resource-id="com.jingdong.app.mall:id/az_"]/android.widget.RelativeLayout[1]/android.widget.RelativeLayout[3]/android.widget.ViewFlipper[1]/android.widget.LinearLayout[1]')
        serch.click()
        time.sleep(1)
        # d.xpath('//*[@resource-id="com.jd.lib.search.feature:id/ya"]')
        d.send_keys(shop_name,clear=True)
        time.sleep(1)
        d(resourceId="com.jingdong.app.mall:id/a9b").click()
        time.sleep(2)
        dianpu=d(resourceId="com.jd.lib.search.feature:id/ade", text="店铺")
        if dianpu.exists:
            dianpu.click()
            time.sleep(1)
            jindian=d.xpath('//*[@resource-id="com.jd.lib.search.feature:id/c2"]')
            if jindian.exists:
                jindian.click()
            else:
                d.press('back')
                time.sleep(1)
                if not serch.exists:
                    d.press('back')
                    time.sleep(1)
                continue
        else:
            d3=d.xpath('//*[@resource-id="com.jd.lib.search.feature:id/xq"]/android.widget.RelativeLayout[1]/android.widget.LinearLayout[1]/android.widget.RelativeLayout[1]/android.widget.RelativeLayout[2]/android.widget.RelativeLayout[1]/android.widget.TextView[2]')
            d4=d.xpath('//*[@resource-id="com.jd.lib.search.feature:id/xq"]/android.widget.RelativeLayout[1]/android.widget.LinearLayout[1]/android.widget.RelativeLayout[1]/android.widget.RelativeLayout[2]/android.widget.RelativeLayout[2]/android.widget.TextView[2]')
            d1=d.xpath('//*[@resource-id="com.jd.lib.search.feature:id/a4"]')
            d2=d.xpath('//*[@text="进店"][1]')
            if d1.exists:
                d1.click()
            elif d2.exists:
                d2.click()
            elif d3.exists:
                d3.click()
            elif d4.exists:
                d4.click()
            else:
                d.press('back')
                time.sleep(1)
                if not serch.exists:
                    d.press('back')
                    time.sleep(1)
                continue
        time.sleep(1)
        text = d.xpath('//*[@resource-id="com.jd.lib.jshop.feature:id/nt"]').get_text()
        print(text)
        if text != shop_name:
            d.press('back')
            time.sleep(1)
            if not serch.exists:
                d.press('back')
                time.sleep(1)
            continue
        d.xpath('//*[@resource-id="com.jd.lib.jshop.feature:id/ox"]').click()
        time.sleep(1)
        d.xpath('//*[@text="分享"]').click()
        time.sleep(1)
        d.swipe(332,1320,48,1320)
        time.sleep(1)
        d.xpath(
            '//androidx.recyclerview.widget.RecyclerView/android.widget.RelativeLayout[5]/android.widget.ImageView[1]').click()
        shop_url= d.clipboard
        str1 = '='
        str2 = '&'
        index1 = shop_url.index(str1)
        index2 = shop_url.index(str2)
        shop_id=shop_url[index1+1:index2]
        print(shop_id)
        sql = 'update amp_shop_marketentity t set t.sec_shop_id="%s" where t.shopname="%s" and t.medianame="京东" '% (
            shop_id, text)
        db.execute_sql(sql)
        time.sleep(1)
        d.press('back')
        time.sleep(1)
        d.press('back')
        time.sleep(1)
        continue

def task():
    time.sleep(3)
    thread_num = len(threading.enumerate())
    print("主线程：线程数量是%d" % thread_num)
    if thread_num<3:
        d.app_stop_all()
        time.sleep(3)
        t1=threading.Thread(target=main)
        t1.start()
    loop_monitor()

def main1():
    sql="SELECT t.sec_shop_id,t.id FROM amp_shop_marketentity t WHERE t.medianame = '京东' AND t.status=4"
    result = db1.select(sql)
    for ob in result:
        try:
            shop_id = ob[0]
            id = ob[1]
            url='https://mall.jd.com/index-%s.html' %(shop_id)
            data = {"category":"jump","des":"m","sourceValue":"babel-act","sourceType":"babel","url":url,"M_sourceFrom":"h5auto","msf_type":"auto"}
            jsonstr=json.dumps(data)
            d.open_url("openApp.jdMobile://virtual?params="+jsonstr)
            time.sleep(1)
            shop=d.xpath('//*[@resource-id="com.jd.lib.jshop.feature:id/o7"]')
            shopname=shop.get_text()
            shop.click()
            time.sleep(1)
            fans_contains = d.xpath('//*[contains(@text,"人关注")]')
            fanstext=fans_contains.get_text()
            fanstext=fanstext[:-3]
            dsr=d.xpath('//*[contains(@text,"用户评价")]/following-sibling::android.widget.TextView[1]')
            dsrtext=dsr.get_text()
            print(shopname+fanstext+dsrtext)
            sql1 = 'update amp_shop_marketentity t set t.dsr_score="%s",t.shopname="%s",t.fans="%s",t.status=5 where t.id=%s' % (
                dsrtext, shopname, fanstext, id)
            db1.execute_sql(sql1)
        except:
            continue

def loop_monitor():
    s = sched.scheduler(time.time, time.sleep)  # 生成调度器
    s.enter(60, 1, task, ())
    s.run()

if __name__ == '__main__':
    # t1=threading.Thread(target=main, name='job1')
    # t2=threading.Thread(target=task, name='job2')
    # t1.start()
    # time.sleep(5)
    # t2.start()
    main1()


