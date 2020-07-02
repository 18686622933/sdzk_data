#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from selenium import webdriver
import time
import pymysql


def traverse_province(wd, conn):
    """
    循环进入省份
    :return:
    """
    for province_id in range(1, 2):
        province_xpath = '//*[@id="div1"]/div/div[%s]/a' % province_id
        wd.find_element_by_xpath(province_xpath).click()  # 点击进入省份
        time.sleep(1)
        traverse_school(wd, conn)  # 遍历省份内的高校
    wd.quit()
    conn.close()


def traverse_school(wd, conn):
    """
    遍历高校信息
    :return:
    """
    school_id = 10
    while True:
        school_info = []
        try:
            # 获取高校信息
            for i in [1, 2, 3, 4, 6]:
                school_xpath = '//*[@id="div4"]/table/tbody/tr[%s]/td[%s]' % (school_id, i)
                text = wd.find_element_by_xpath(school_xpath).text
                school_info.append(text)

            # 进入高校子页
            wd.find_element_by_xpath('//*[@id="div4"]/table/tbody/tr[%s]/td[5]/a' % school_id).click()
            wd.switch_to.window(wd.window_handles[-1])  # 切换到最后一个页面
            traverse_major(school_info, wd, conn)  # 遍历专业
            wd.close()  # 关闭当前页
            wd.switch_to.window(wd.window_handles[-1])  # 重新定位一次页面
            school_id += 1
        except:
            break
        conn.commit()  # 每个高校提交一次


def traverse_major(school_info, wd, conn):
    """
    遍历专业信息，最后结合高校信息一并输出
    :param school_info: 上层函数传递进来的高校信息
    :return:
    """
    major_id = 1
    cursor = conn.cursor()
    while True:
        major_info = []
        try:
            for i in range(1, 5):
                major_xpath = '//*[@id="ccc"]/div/table/tbody/tr[%s]/td[%s]' % (major_id, i)
                text = wd.find_element_by_xpath(major_xpath).text
                major_info.append(text)

            print(school_info + major_info)

            # 写入mysql
            insert_sql = '''
                        insert into sdzk_data
                        (school_id,province,school_code,school_name,school_home,major_id,cc,major_name,subject_ask) 
                        values('%s','%s','%s','%s','%s','%s','%s','%s','%s')   
                        ''' % (school_info[0], school_info[1], school_info[2], school_info[3], school_info[4],
                               major_info[0], major_info[1], major_info[2], major_info[3])
            cursor.execute(insert_sql)

            major_id += 1
        except:
            break
    cursor.close()  # 每个高校都重新开启一次游标


def connect_mysql(config):
    """
    连接数据库，并创建表，如果表已存在则先删除
    :param config: mysql数据库信息
    :return: 返回连接成功的connect对象
    """

    create_sql = '''
                    CREATE table if NOT EXISTS sdzk_data
                    (school_id int(3),province varchar(20), school_code varchar(5), 
                    school_name varchar(50), school_home varchar(100), major_id int(3), 
                    cc varchar(5), major_name varchar(100), subject_ask varchar(50))
                 '''

    # 判断表是否存在，存在则删除，然后创建
    conn = pymysql.connect(**config)
    cursor = conn.cursor()
    cursor.execute('''show TABLEs like "sdzk_data"''')
    if cursor.fetchall():
        cursor.execute('''drop table sdzk_data''')
    cursor.execute(create_sql)
    cursor.close()

    return conn


def run():
    config = {'host': '127.0.0.1',
              'port': 3306,
              'user': 'web',
              'password': '123',
              'database': 'cuiyanet',
              'charset': 'utf8'
              }
    url = 'http://xkkm.sdzk.cn/zy-manager-web/gxxx/selectAllDq#'

    wd = webdriver.Chrome()
    wd.get(url)
    time.sleep(2)
    print(type(wd))
    traverse_province(wd, connect_mysql(config))


run()
