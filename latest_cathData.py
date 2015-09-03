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

driver = webdriver.Chrome('C:/Users/BigData/Desktop/chromedriver.exe')
#將已存檔案製成列表

open_judgement=os.listdir (u"c:/judicial/judgement")
open_ruling=os.listdir (u"c:/judicial/ruling")
open_unknown=os.listdir (u"c:/judicial/unknown")
#print open_list[0] #IndexError
list = io.open(u'c:/judicial/list.txt','a+',encoding='utf-8')

for reading in range (0,len(open_judgement)):
    list.write((open_judgement[reading]+'\n'))
for reading in range (0,len(open_ruling)):
    list.write((open_ruling[reading]+'\n'))
for reading in range (0,len(open_unknown)):
    list.write((open_unknown[reading]+'\n'))
#print 'checkpoint1'
#list.seek(0,0)#游標移回開頭讀取
cont=list.read()
list.close()
months=['1','2','3','4','5','6','7','8','9','10','11','12']
days=['31','29','31','30','31','30','31','31','30','31','30','31']
#法院名稱：最高法院,臺灣高等法院,臺灣高等法院 臺中分院,臺灣高等法院 臺南分院,臺灣高等法院 高雄分院,臺灣高等法院 花蓮分院
#臺灣臺北地方法院,*臺灣士林地方法院,臺灣新北地方法院,*臺灣宜蘭地方法院,*臺灣基隆地方法院,臺灣桃園地方法院,臺灣新竹地方法院,臺灣苗栗地方法院
#臺灣臺中地方法院,*臺灣彰化地方法院,臺灣南投地方法院,臺灣雲林地方法院,臺灣嘉義地方法院,臺灣臺南地方法院,臺灣高雄地方法院,*臺灣花蓮地方法院
#臺灣臺東地方法院,*臺灣屏東地方法院,*臺灣澎湖地方法院,福建高等法院金門分院,福建金門地方法院,*福建連江地方法院,臺灣高雄少年及家事法院

court=u'臺灣新北地方法院' #請輸入法院名稱

court_search=re.search(u'臺灣(\D+)法院',court)
court1=court_search.group(1)
#-------------------------------------------------------
for year in range(89,105):
    month=7
    day=1
    interval_month=3 #每次取幾個月，請給可整除剩餘月份的數字，不然會少抓資料
    #print 'checkpoint2'
    for mon in range(0,((12-month+1)/interval_month)):
        driver.get('http://jirs.judicial.gov.tw/FJUD/FJUDQRY01_1.aspx')
        driver.implicitly_wait(30)
        Select(driver.find_element_by_name("v_court")).select_by_visible_text(court)
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
        print '現在抓取'+court.encode('utf-8')+str(year)+'年'+str(month)+'月到'+str(month+interval_month-1)+'月，GoodLuck'
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
            get_date=re.findall(u'>(\d{6,7})<',raw_page)
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
                list = open('c:/judicial/list.txt','r')
                cont=list.read()
                list.close()
                finding=re.findall((court1+u','+get_word[row]+u',裁判日期：'+get_date[row]).encode('utf-8'),cont)
                #print len(finding)
                if(len(finding)==0):
                    #print 'checkpoint8'
                    word=get_word[row]
                    date=get_date[row]
                
                    print word
                    replace_url=re.sub("amp;", "", raw_url[row])
                    #print replace_url
                    final_url=re.sub('^','http://jirs.judicial.gov.tw/FJUD/',replace_url)
                    #print final_url
                    url=final_url
                    res=requests.get(url,headers=head4)

                    ruling=re.findall(u'<pre>[^0-9]+法院(民事|家事)裁定',res.text)
                    judgement=re.findall(u'<pre>[^0-9]+法院(民事|家事)判決',res.text)                 
                    #print res.text
                    soup = BeautifulSoup(res.text.encode('utf-8'))
                    
                    #soup = BeautifulSoup(res.text.encode('utf-8'), "html.parser")
       
                    #print soup
               
                    if len(judgement)==1:
                        f = io.open(u'c:/judicial/judgement/判決,'+court1+u','+word+u',裁判日期：'+date+u'.txt','w',encoding='utf-8')
                        for i in range(5,11):
                            f.write(soup.findAll('td')[i].text)
                            if i % 2 == 0:
                                f.write(u'\n')
                        f.write(soup.findAll('td')[13].text)
                        f.close()
                        list = open('c:/judicial/list.txt','a+')
                        list.write((u'判決,'+court1+u','+word+u',裁判日期：'+date+'\n').encode('utf-8'))
                        list.close()
                        list_judgement = open('c:/judicial/list_judgement.txt','a+')
                        list_judgement.write('判決,'+court1.encode('utf-8')+','+word.encode('utf-8')+',裁判日期：'+date.encode('utf-8')+'\n')
                        list_judgement.close()
                        list_all = open('c:/judicial/list_all.txt','a+')
                        list_all.write('判決,'+court1.encode('utf-8')+','+word.encode('utf-8')+',裁判日期：'+date.encode('utf-8')+'\n')
                        list_all.close()
                    elif len(ruling)==1:
                        f = io.open(u'c:/judicial/ruling/裁定,'+court1+u','+word+u',裁判日期：'+date+u'.txt','w',encoding='utf-8')
                        for i in range(5,11):
                            f.write(soup.findAll('td')[i].text)
                            if i % 2 == 0:
                                f.write(u'\n')
                        f.write(soup.findAll('td')[13].text)
                        f.close()
                        list = open('c:/judicial/list.txt','a+')
                        list.write((u'裁定,'+court1+u','+word+u',裁判日期：'+date+'\n').encode('utf-8'))
                        list.close()         
                        list_ruling = open('c:/judicial/list_ruling.txt','a+')
                        list_ruling.write('裁定,'+court1.encode('utf-8')+','+word.encode('utf-8')+',裁判日期：'+date.encode('utf-8')+'\n')
                        list_ruling.close()
                        list_all = open('c:/judicial/list_all.txt','a+')
                        list_all.write('裁定,'+court1.encode('utf-8')+','+word.encode('utf-8')+',裁判日期：'+date.encode('utf-8')+'\n')
                        list_all.close()
                    else:
                        f = io.open(u'c:/judicial/unknown/未定,'+court1+u','+word+u',裁判日期：'+date+u'.txt','w',encoding='utf-8')
                        
                        for i in range(5,11):
                            f.write(soup.findAll('td')[i].text)
                            if i % 2 == 0:
                                f.write(u'\n')
                        f.write(soup.findAll('td')[13].text)
                        
                        f.close()
                        list = open('c:/judicial/list.txt','a+')
                        list.write((u'未定,'+court1+u','+word+u',裁判日期：'+date+'\n').encode('utf-8'))
                        list.close()         
                        list_known = open('c:/judicial/list_unknown.txt','a+')
                        list_known.write('未定,'+court1.encode('utf-8')+','+word.encode('utf-8')+',裁判日期：'+date.encode('utf-8')+'\n')
                        list_known.close()
                        list_all = open('c:/judicial/list_all.txt','a+')
                        list_all.write('未定,'+court1.encode('utf-8')+','+word.encode('utf-8')+',裁判日期：'+date.encode('utf-8')+'\n')
                        list_all.close()
            if total_page>1 and total_page!=now_page:
                #print 'checkpoint9'
                driver.find_element_by_link_text(u"下一頁").click()
                time.sleep(8)
os.remove("c:/judicial/list.txt")  
print '順利抓完，恭喜'                                 
driver.close()
