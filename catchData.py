# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import unittest, time, re, sys
from bs4 import BeautifulSoup
import requests
import os, io

driver = webdriver.Chrome('C:\Users\BigData\Desktop\chromedriver.exe')
#將已存檔案製成列表
if os.path.isfile("C:/judicial/list2.txt"):
    os.remove("C:/judicial/list2.txt") 
open_list=os.listdir (u"C:/judicial/")
#print open_list[0] #IndexError
list = io.open(u'C:/judicial/list.txt','a+',encoding='utf-8')

for reading in range (0,len(open_list)):
    list.write((open_list[reading]+'\n'))
    #print 'checkpoint1'
#list.seek(0,0)#游標移回開頭讀取
cont=list.read()
list.close()
months=['1','2','3','4','5','6','7','8','9','10','11','12']
days=['31','29','31','30','31','30','31','31','30','31','30','31']
#-------------------------------------------------------
for year in range(89,105):
    month=1
    day=1
    interval_month=3 #每次取幾個月，請給可整除12個月的數字，不然會少抓資料
    #print 'checkpoint2'
    for mon in range(1,((12/interval_month)+1)):
        driver.get('http://jirs.judicial.gov.tw/FJUD/FJUDQRY01_1.aspx')
        driver.implicitly_wait(30)
        Select(driver.find_element_by_name("v_court")).select_by_visible_text(u"臺灣彰化地方法院")
        driver.find_elements_by_name('v_sys')[1].click()
        driver.find_element_by_id("jt").clear()
        driver.find_element_by_id("jt").send_keys(u"離婚")
        driver.find_element_by_name("dy1").clear()
        driver.find_element_by_name("dy1").send_keys(str(year))
        driver.find_element_by_name("dm1").clear()
        driver.find_element_by_name("dm1").send_keys(str(month))
        driver.find_element_by_name("dd1").clear()
        driver.find_element_by_name("dd1").send_keys("1")
        driver.find_element_by_name("dy2").clear()
        driver.find_element_by_name("dy2").send_keys(str(year))
        driver.find_element_by_name("dm2").clear()
        driver.find_element_by_name("dm2").send_keys(str(month+interval_month-1))
        driver.find_element_by_name("dd2").clear()
        driver.find_element_by_name("dd2").send_keys(str(days[month+interval_month-2]))
        print '現在抓取'+str(year)+'年'+str(month)+'月到'+str(month+interval_month-1)+'月，GoodLuck'
        time.sleep(5)
        driver.find_element_by_name("Button").click()
        month=month+interval_month
        time.sleep(5)
        raw_page=driver.page_source
        #範圍錯誤處理
        over_num=re.findall(u'超出 200 筆',raw_page)
        #print 'checkpoint3'
        if(len(over_num)!=0):
            print (u'請修正範圍')
            driver.close()
            print('check2')
            sys.exit()
        page=re.search(u'共\s+(\d+)\s+筆 / 每頁\s+(\d+)\s+筆 / 共\s+(\d+)\s+頁 / 現在第\s+(\d+)\s+頁',raw_page)
        total_page=int(page.group(3))
        #print 'checkpoint4'
        for pages in range(0,total_page):
            #print 'checkpoint5'
            time.sleep(5)
            raw_page=driver.page_source
            page=re.search(u'共\s+(\d+)\s+筆 / 每頁\s+(\d+)\s+筆 / 共\s+(\d+)\s+頁 / 現在第\s+(\d+)\s+頁',raw_page)
            total_page=int(page.group(3))
            now_page=int(page.group(4))
            #n=re.findall(u"裁判\D",raw_page)
            #print n[0]
            get_word=re.findall(u'\d{2,3},\D{1,5},\d{1,5}',raw_page)
            #print get_word[0]
            index=len(get_word) #get_word的長度
            #標記連結
            #for i in range(0,index):
            #    print get_word[i]
            raw_url=re.findall('FJUDQRY03_1.aspx\?id=\S{4,300}cw=0',raw_page)
            #print raw_url[index]
            #確認檔案是否抓過

            head4={
            'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0',
            'Referer':'http://jirs.judicial.gov.tw/FJUD/FJUDQRY02_1.aspx',
            'Host':'jirs.judicial.gov.tw',
            'Connection':'keep-alive',
            'Accept-Language':'zh-TW,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding':'gzip, deflate',
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            }
            #print 'checkpoint6'
            for row in range(0,index):
                #print 'checkpoint7'
                list = open('C:/judicial/list.txt','r')
                cont=list.read()
                list.close()
                finding=re.findall(((get_word[row])+".txt").encode('utf-8'),cont)
                #print len(finding)
                if(len(finding)==0):
                    #print 'checkpoint8'
                    name=get_word[row]
                    print name
                    replace_url=re.sub("amp;", "", raw_url[row])
                    #print replace_url
                    final_url=re.sub('^','http://jirs.judicial.gov.tw/FJUD/',replace_url)
                    #print final_url
                    url=final_url
                    res=requests.get(url,headers=head4)
                    error=re.findall(u'裁判字號',res.text)
                    ruling=re.findall(u'<pre>[^0-9]{6,10}法院民事裁定　',res.text)
                    judgement=re.findall(u'<pre>[^0-9]{6,10}法院民事判決　',res.text)
                    if len(error)==0:
                        driver.close()
                        print ('check3')
                        print (name.encode('utf-8'))
                        sys.exit()
                    #print res.text
                    soup = BeautifulSoup(res.text.encode('utf-8'))
                    
                    #soup = BeautifulSoup(res.text.encode('utf-8'), "html.parser")
       
                    #print soup
               
                    if len(judgement)==1:
                        f = open('C:/judicial/%s.txt' %(soup.findAll('td')[6].text), 'w')
                        for i in range(5,11):
                            f.write(soup.findAll('td')[i].text.encode('utf-8'))
                            if i % 2 == 0:
                                f.write('\n')
                        f.write(soup.findAll('td')[13].text.encode('utf-8'))
                        f.close()
                        list = open('C:/judicial/list.txt','a+')
                        list.write((name+'.txt').encode('utf-8')+'\n')
                        list.close()
                        list2 = open('C:/judicial/list2.txt','a+')
                        list2.write((name+'.txt').encode('utf-8')+'\n')
                        list2.close()
                    elif len(ruling)==1:
                        list_ruling = open('C:/judicial/list_ruling.txt','a+')
                        list_ruling.write((name+'.txt').encode('utf-8')+'\n')
                    else:
                        print 'checkprocess'
            if total_page>1 and total_page!=now_page:
                #print 'checkpoint9'
                driver.find_element_by_link_text(u"下一頁").click()
                time.sleep(8)

os.remove("C:/judicial/list.txt")  
driver.close()
