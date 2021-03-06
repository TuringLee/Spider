# -*- coding:utf-8 -*-

import urllib
import urllib2
import time
from bs4 import BeautifulSoup
import argparse
import os

class Spider(object):
    """Spider for sheshou"""
    def __init__(self,originUrl):
        self.originUrl = originUrl
        
    def getUrl(self,pageIndex):
        self.pageIndex = pageIndex
        self.url = self.originUrl+'/xml/sub/'+str(pageIndex/1000)+'/'+str(pageIndex)+'.xml'

    def getCurrentTime(self):
        return time.strftime('[%Y-%m-%d %H-%M-%S]',time.localtime(time.time()))

    def getPage(self,headers):
        print self.getCurrentTime()+' '+self.url
        request = urllib2.Request(self.url,headers=headers)
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
        
    def getCaptions(self,downLoadUrl,filePath,fileFormat):
        filePath = filePath+'/'+str(self.pageIndex)+'.'+str(fileFormat)
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

parser = argparse.ArgumentParser()
parser.add_argument('page_index')
parser.add_argument('file_path')
args = parser.parse_args()
page_index = int(args.page_index)
file_path = args.file_path

num_of_download = 0
time_interval = 2

spider = Spider(origin_url)
log_file_path = file_path + '/log_file.txt'

while(page_index > 267855):
    spider.getUrl(page_index)
    res = spider.getPage(headers)
    if type(res) != list or len(res) != 2:
        f = open(log_file_path,'a')
        f.write(str(spider.getCurrentTime())+' page_index:'+str(page_index)+' occur something unexpexted.\n')
        f.write('Ignore this page!')
        f.close()
        page_index -= 5
        time.sleep(time_interval*10)
        continue
    page,error_code = res
    if page:
        down_load_url,file_format = spider.getDownloadUrl(page)
        if down_load_url:
            flag = spider.getCaptions(down_load_url,file_path,file_format)
    else:
        page_index -= 5
        f = open(log_file_path,'a')
        f.write(str(spider.getCurrentTime())+'Can not get the page , page_index:'+str(page_index)\
            +'\nError code is :'+str(error_code)+' .\n\n')
        f.close()
        time.sleep(time_interval)
        continue
    if flag == None:
        num_of_download += 1
        f = open(log_file_path,'a')
        f.write(str(spider.getCurrentTime())+' page_index:'+str(page_index)+' has been downloaded.\n')
        f.write(str(num_of_download)+' files has been downloaded\n\n')
        f.close()
        page_index -= 5
        time.sleep(time_interval)
    elif flag == True:
        f = open(log_file_path,'a')
        f.write(str(spider.getCurrentTime())+' page_index:'+str(page_index)+" occur something unexpexted.\n")
        f.write('Igore this page.\n\n')
        f.close()
        page_index -= 5
        time.sleep(time_interval)
    else:
        f = open(log_file_path,'a')
        f.write(str(spider.getCurrentTime())+' page_index:'+str(page_index)+" is forbidden,try again after 180 second.\n")
        f.write(str(num_of_download)+' files has been downloaded\n\n')
        f.close()
        time.sleep(180)

print "Down"

