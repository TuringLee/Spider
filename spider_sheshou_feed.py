# -*- conding:utf-8 -*-

import urllib
import urllib2
from bs4 import BeautifulSoup
import time
import re
import argparse
import os

week_dict = {'mon':1,'Tue':2,'Wed':3,'Thu':4,'Fri':5,'Sat':6,'Sun':7}

class Spider(object):
    """Spider for sheshou"""
    def __init__(self,originUrl,feedUrl):
        self.originUrl = originUrl
        self.feedUrl = feedUrl

    def getUrlList(self):
        try:
            response = urllib2.urlopen(self.feedUrl)
        except Exception , e:
            if hasattr(e, 'code'):
                print self.getCurrentTime(),"Faild in get the page,Error code:",e.code
                if hasattr(e, 'reason'):
                    print "Error info:",e.reason
                if (e.code == 404):
                    return [None,e.code]
                else:
                    time.sleep(180)
                return [None,e.code]     #if the spider be forbidden , try again after 300 seconds.
            else:
                return None
        else:
            page = response.read()
            soup = BeautifulSoup(page,'lxml')


            cur_time = time.strftime("%a, %d %b %Y",time.gmtime())

            week_to_num = {1:'Mon','Tue':2,'Wed':3,'Thu':4,'Fri':5,'Sat':6,'Sun':0}
            num_to_week = {1:'Mon',2:'Tue',3:'Wed',4:'Thu',5:'Fri',6:'Sat',0:'Sun'}

            cur_time = time.strftime("%a, %d %b %Y",time.gmtime())

            ct = cur_time.split(' ')

            ct[0] = ct[0].split(',')[0]
            ct[0] = (week_to_num[ct[0]]+7-1)%7
            ct[0] = str(num_to_week[ct[0]])+','

            ct[1] = str(int(ct[1]) -1)

            cur_time = ct[0]+' '+ct[1]+' '+ct[2]+' '+ct[3]

            pattern_time = re.compile(cur_time)
            pattern_guid = re.compile('<guid>(.*?)</guid>')

            downUrlList = []

            for item in  soup.find_all('item'):
                pubdate = str(item.find('pubdate'))
                if re.search(pattern_time, pubdate):
                    guid = str(item.find('guid'))
                    match = re.search(pattern_guid, guid)
                    if match :
                        downUrl = self.originUrl + match.group(1)
                        downUrlList.append(downUrl)
            return downUrlList

    def getCurrentTime(self):
        return time.strftime('[%Y-%m-%d %H-%M-%S]',time.localtime(time.time()))

    def getPage(self,headers,downUrl):
        print self.getCurrentTime()+' '+downUrl
        request = urllib2.Request(downUrl,headers=headers)
        try:
            response = urllib2.urlopen(request)
        except Exception , e:
            if hasattr(e, 'code'):
                print self.getCurrentTime(),"Faild in get the page,Error code:",e.code
                if hasattr(e, 'reason'):
                    print "Error info:",e.reason
                if (e.code == 404):
                    return [None,e.code]
                else:
                    time.sleep(300)
                return [None,e.code]     #if the spider be forbidden , try again after 300 seconds.
            else:
                return None
        else:
            page = response.read()
            return [page,None]
            
    def getDownloadUrl(self,page):
        soup = BeautifulSoup(page,'lxml')
        downLoadUrl = soup.find(id="btn_download")['href']
        fileFormat = downLoadUrl.split('.')[-1]
        downLoadUrl = self.originUrl + downLoadUrl
        return downLoadUrl,fileFormat
        
    def getCaptions(self,downLoadUrl,filePath,fileFormat,pageIndex):
        filePath = filePath+'/'+str(pageIndex)+'.'+str(fileFormat)
        try:
            urllib.urlretrieve(downLoadUrl,filePath)
        except Exception,e:  
            if hasattr(e, 'code'):
                print self.getCurrentTime(),"Faild in get the caption,Error code:",e.code
                if hasattr(e, 'reason'):
                    print "Faile in get the caption,Error info:",e.reason            
                return e.code
            else:
                return True
        else:
            if os.path.getsize(filePath) == 0:
                os.remove(filePath)
                return True
            else:
                return None


user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.98 Safari/537.36'
headers = {"User-Agent" : user_agent}
origin_url = "http://assrt.net"
seed_url = 'http://assrt.net/feed.xml'

parser = argparse.ArgumentParser()
parser.add_argument('file_path')
args = parser.parse_args()
file_path = args.file_path

num_of_download = 0
time_interval = 1

spider = Spider(origin_url,seed_url)
log_file_path = file_path + '/log_file.txt'

num_cur_day = 0
down_url_list = spider.getUrlList()

for down_url in down_url_list :
    page_index = down_url.split('/')[-1].split('.')[0]
    res = spider.getPage(headers,down_url)
    if type(res) != list or len(res) != 2:
        f = open(log_file_path,'a')
        f.write(str(spider.getCurrentTime())+' page_index:'+str(page_index)+' occur something unexpexted.\n')
        f.write('Ignore this page!')
        f.close()
        time.sleep(time_interval*5)
        continue
    page,error_code = res
    if page:
        down_load_url,file_format = spider.getDownloadUrl(page)
        if down_load_url:
            flag = spider.getCaptions(down_load_url,file_path,file_format,page_index)
    else:
        f = open(log_file_path,'a')
        f.write(str(spider.getCurrentTime())+'Can not get the page , page_index:'+str(page_index)\
            +'\nError code is :'+str(error_code)+' .\n\n')
        f.close()
        time.sleep(time_interval)
        continue
    if flag == None:
        num_of_download += 1
        num_cur_day += 1
        f = open(log_file_path,'a')
        f.write(str(spider.getCurrentTime())+' page_index:'+str(page_index)+' has been downloaded.\n')
        f.write(str(num_of_download)+' files has been downloaded\n\n')
        f.close()
        time.sleep(time_interval)
    elif flag == True:
        f = open(log_file_path,'a')
        f.write(str(spider.getCurrentTime())+' page_index:'+str(page_index)+" occur something unexpexted.\n")
        f.write('Igore this page.\n\n')
        f.close()
        time.sleep(time_interval)
    else:
        f = open(log_file_path,'a')
        f.write(str(spider.getCurrentTime())+' page_index:'+str(page_index)+" is forbidden,try again after 180 second.\n")
        f.write(str(num_of_download)+' files has been downloaded\n\n')
        f.close()
        time.sleep(180)
f = open(log_file_path,'a')
f.write(str(spider.getCurrentTime())+' '+ str(num_cur_day) +' files has been downloaded \n')
f.write('*******************************************************************************\n\n')
f.close()
print str(spider.getCurrentTime())+' '+ str(num_cur_day) +' files has been downloaded today !'
print '****************************************************************\n\n'

