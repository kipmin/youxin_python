#!/usr/bin/python
# -*- coding: utf-8 -*-
import os, sys
import pymongo, time, random, re
from pymongo import MongoClient
from datetime import datetime
import requests as rq
from bs4 import BeautifulSoup as bs

# 代理隧道验证信息
proxyUser = 'HWH57XR1O2G9V9UD'
proxyPass = 'D117C2F74F3EF341'

proxyMeta = 'http://%(user)s:%(pass)s@proxy.abuyun.com:9020' % {
    'host': proxyHost,
    'port': proxyPort,
}

proxies = {
    'http': proxyMeta,
    'https': proxyMeta,
}
# 筛选出的优信超过2000车源的城市124个
city_list = ['baoding', 'baoji', 'baotou', 'beijing', 'bengbu', 'binzhou', 'cangzhou', 'changchun', 'changde', 'changsha', 'changzhi', 'changzhou', 'chengde', 'chengdu', 'chongqing', 'dalian', 'daqing', 'datong', 'dazhou', 'deyang', 'dezhou', 'dongguan', 'dongying', 'eerduosi', 'foshan', 'fushun', 'fuzhou', 'ganzhou', 'guangzhou', 'guilin', 'guiyang', 'haerbin', 'handan', 'hangzhou', 'hefei', 'hengshui', 'hengyang', 'heze', 'huaibei', 'huainan', 'huhehaote', 'huizhou', 'huzhou', 'jiamusi', 'jian', 'jiangmen', 'jiaxing', 'jilin', 'jinan', 'jingzhou', 'jinhua', 'jinzhou', 'kunming', 'langfang', 'lanzhou', 'leshan', 'lianyungang', 'liaocheng', 'linfen', 'linyi', 'liuzhou', 'luan', 'luoyang', 'luzhou', 'mianyang', 'nanchang', 'nanchong', 'nanjing', 'nanning', 'nantong', 'ningbo', 'qingdao', 'qinhuangdao', 'qiqihaer', 'quanzhou', 'rizhao', 'shanghai', 'shangqiu', 'shantou', 'shaoxing', 'shenyang', 'shenzhen', 'shijiazhuang', 'shiyan', 'songyuan', 'suqian', 'suzhou', 'suzhouah', 'taian', 'taiyuan', 'taizhouzj', 'taizhou', 'tangshan', 'tianjin', 'weifang', 'wenzhou', 'wuhan', 'wuhu', 'wulumuqi', 'wuxi', 'xiamen', 'xian', 'xiangyang', 'xingtai', 'xinxiang', 'xinyang', 'xuchang', 'xuzhou', 'yancheng', 'yangzhou', 'yantai', 'yibin', 'yichang', 'yinchuan', 'yueyang', 'yuncheng', 'yongchuan', 'zaozhuang', 'zhengzhou', 'zhenjiang', 'zhongshan', 'zhuhai', 'zhuzhou', 'zibo']

# 获取网页
def requestPage(page):
    head = {    #Cookie信息每次用都要重新从浏览器获取.
        'cookie': 'RELEASE_KEY=; XIN_UID_CK=eedda47f-1739-6dbd-6ef4-45d30f98ac92; uid=rBAKE1rjIOl1EXs/BPRnAg==; Hm_lvt_ae57612a280420ca44598b857c8a9712=1524834539,1524920174,1525007001; Hm_lpvt_ae57612a280420ca44598b857c8a9712=1525246116; XIN_anti_uid=5A3B88F0-F0C6-E444-F74A-434146F85610; XIN_LOCATION_CITY=%7B%22cityid%22%3A%221015%22%2C%22areaid%22%3A%226%22%2C%22big_areaid%22%3A%222%22%2C%22provinceid%22%3A%2221%22%2C%22cityname%22%3A%22%5Cu5fb7%5Cu5dde%22%2C%22ename%22%3A%22dezhou%22%2C%22shortname%22%3A%22DZ%22%2C%22service%22%3A%221%22%2C%22near%22%3A%222101%22%2C%22tianrun_code%22%3A%220534%22%2C%22zhigou%22%3A%221%22%2C%22longitude%22%3A%22116.3574640%22%2C%22latitude%22%3A%2237.4340920%22%2C%22direct_rent_support%22%3A%221%22%7D',        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0'    }
    r = rq.get(page, headers=head, timeout=3)
        # , proxies = proxies)
    r.encoding = r.apparent_encoding
    return bs(r.text, 'lxml')

# 连接Mongod
def set_mongodb(dict_car):
    client = MongoClient('localhost', 27017)
    db = client.car
    youxin = db.youxin
    # car_id可以在需要的时候返回
    car_id = youxin.insert_one(dict_car).inserted_id



# 获得单个数据dict
def  get_info_from(car_page, city):
    carsoup = requestPage(car_page)
    title = carsoup.find('span', class_='cd_m_h_tit')
    info = carsoup.select('.cd_m_desc_val')
    infokey = carsoup.select('.cd_m_desc_key')
    pris = carsoup.select('b')
    more_title = carsoup.select('.cd_m_i_pz_tit')
    more_value = carsoup.select('.cd_m_i_pz_val')

    name = title.get_text().replace('\n','')
    price = pris[0].get_text().replace('￥', '').replace('万', '').replace('\n','')
    new_price = pris[1].get_text().replace('\r\n','').replace(' ','').replace('新车含税', '').replace('万', '')
    reg_date = infokey[0].get_text().replace(' ','').replace('\n','')
    mileage = info[1].get_text().replace(' ','').replace('\n','').replace('万公里', '')
    effluent = info[2].get_text().replace(' ','').replace('\n','')
    # speed = info[3].get_text().replace(' ','').replace('\n','')
    det_title = []
    det_value = []
    for k in more_title:
        det_title.append(k.get_text().replace('\n','').replace(' ',''))
    for v in more_value:
        det_value.append(v.get_text().replace('\n','').replace(' ',''))

    youxin = re.split(r'\s+', name)
    if youxin[4].find('T') == -1:
        speed = youxin[4]+'L'
    else:
        speed = youxin[4]
    speedbox = youxin[5]
    detail = youxin[6]
    reg = datetime.strptime(reg_date, '%Y年%m月上牌')
    njdate = datetime.strptime(det_value[3], '%Y-%m-%d')
    bxdate = datetime.strptime(det_value[4], '%Y-%m-%d')

    car = {
    '品牌':youxin[1],
    '名称':youxin[2],
    '款式':youxin[3],
    '现价' :float(price),
    '全新价':float(new_price),
    '上牌年月':reg,
    '已开里程':float(mileage),
    '排放标准':effluent,
    '排放量':speed,
    '变速箱':speedbox,
    '详细信息':detail,
    det_title[2]:det_value[2],
    det_title[3]:njdate,
    det_title[4]:bxdate,
    det_title[5]:det_value[5],
    det_title[12]:det_value[12],
    det_title[13]:det_value[13],
    det_title[15]:det_value[15],
    det_title[16]:det_value[16],
    det_title[17]:det_value[17],
    '城市':city,
    '页面':car_page,
    }
    print("OK")
    return car
    # print (car,'\n')          #调试打印用
    # extra = carsoup.select('ul.basic-eleven li div')[6:-1]
    # for ele in extra:
    #     print(ele)     #这是附加信息。

# 单目录数据循环获取
def get_cars_in_Page(page):
    host = 'https:'
    try:
        soup = requestPage(page)
    except Exception as e:
        try:
            soup = requestPage(page)
        except Exception as e:
            try:
                soup = requestPage(page)
            except Exception as e:
                try:
                    soup = requestPage(page)
                except Exception as e:
                    try:
                        soup = requestPage(page)
                    except Exception as e:
                        # print("pageError") 调试用
                        # 如果这都获取不到就放到错误页里吧
                        with open('/root/youxin/err_page1', 'a', encoding='utf8') as f:
                            f.write(page + '\n')
    cars = soup.select('.aimg')
    online_city = soup.select('dt#current_city_id')[0].get_text()
    car_count = 0;
    for car in cars:
        carpage = host+car.get('href')
        try:
            # print(host + car.get('href'))
            # carsoup = requestPage(host + car.get('href'))
            # time.sleep(random.uniform(1.2,2.5))
            dict_car = get_info_from(carpage, online_city)
            # 保存数据库或文件
            set_mongodb(dict_car)
            # car_count += 1
        except Exception as e:
            # print("Exception1")
            try:
                dict_car = get_info_from(carpage, online_city)
                set_mongodb(dict_car)
                # car_count += 1
            except Exception as e:
                # print("Exception2")
                try:
                    dict_car = get_info_from(carpage, online_city)
                    set_mongodb(dict_car)
                    # car_count += 1
                except Exception as e:
                    # print("Exception3")
                    # 输出到错误页
                    with open('/root/youxin/err_list1', 'a', encoding='utf8') as f:
                        f.write(carpage + ' ' + online_city + '\n')
    # print('\n本页获取车辆数：', car_count)

def get_error_list(page):
    try:
        # print(host + car.get('href'))
        # carsoup = requestPage(host + car.get('href'))
        dict_car = get_info_from(page)
        # 保存数据库或文件
        set_mongodb(dict_car)
    except Exception as e:
        print("eRR Exception1")
        try:
            dict_car = get_info_from(page)
            set_mongodb(dict_car)
        except Exception as e:
            print("eRR Exception2")

#页码列表
pageList = ['https://www.xin.com/{}/i{}'.format(city, str(n)) for city in city_list for n in range(1, 51)]
# 读取错误页码和车辆页面
# io_list = []
# io_page = []
# with open('f:/intercar/youxin/err_list1', 'r') as f:
#     io_list = f.readlines()
# with open('f:/intercar/youxin/err_page1', 'r') as f:
#     io_page = f.readlines()

#批量获取车辆详情页的url，用页码列表循环，得到一个城市所有车辆数据。

for page in pageList:           
    get_cars_in_Page(page)
# 循环获取失败的车辆页面
# for error in io_list:
#     get_error_list(error)
# 循环获取失败的车辆目录页面
# for page in io_page:
#     get_cars_in_Page(page)

#从单个页码进去，获得40条URL。
# get_cars_in_Page(pageList[0])


# 单个车辆页面信息获取
# one_car = 'https://www.xin.com/yrek41mkmg/che43674507.html'
# get_info_from(one_car)



