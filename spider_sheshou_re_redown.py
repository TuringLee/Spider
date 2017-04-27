# -*- coding:utf-8 -*-

import urllib
import urllib2
import time
from bs4 import BeautifulSoup
import argparse
import os


def get_downloaded_ids(file_downloaded_path):
    ids_downloaded = []
    file_list = os.list(file_downloaded_path):
    for file in file_list:
        id = file.split('_')[0]
        if id not in ids_downloaded:
            ids_downloaded.append(int(id))
    ids_downloaded = list(set(ids_downloaded))

    return ids_downloaded



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
            if os.path.getsize(filePath)/1000 < 10:
                os.remove(filePath)
                return True
            else:
                return None

user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.98 Safari/537.36'
headers = {"User-Agent" : user_agent}
origin_url = "http://assrt.net"

parser = argparse.ArgumentParser()
parser.add_argument('file_path')
parser.add_argument('ids_downloaded_path')
args = parser.parse_args()
file_path = args.file_path
ids_downloaded_path = args.ids_downloaded_path

num_of_download = 0
time_interval = 3

spider = Spider(origin_url)
log_file_path = file_path + '/log_file.txt'

f = open(index_file,'r')
index_list = f.readlines()

ids_downloaded = get_downloaded_ids(ids_downloaded_path)
page_index = 610676

while(page_index > 300000)
    page_index = int(page_index)
    if page_index in ids_downloaded:
        page_index -= 1 
        continue
    spider.getUrl(page_index)
    res = spider.getPage(headers)
    if type(res) != list or len(res) != 2:
        f = open(log_file_path,'a')
        f.write(str(spider.getCurrentTime())+' page_index:'+str(page_index)+' occur something unexpexted_1.\n')
        f.write('Ignore this page!\n\n')
        f.close()
        time.sleep(time_interval*20)
        continue
    page,error_code = res
    if page:
        down_load_url,file_format = spider.getDownloadUrl(page)
        if down_load_url:
            flag = spider.getCaptions(down_load_url,file_path,file_format)
    else:
        f = open(log_file_path,'a')
        f.write(str(spider.getCurrentTime())+'Can not get the page , page_index:'+str(page_index)\
            +'\nError code is :'+str(error_code)+' .\n\n')
        f.close()
        time.sleep(time_interval*20)
        continue
    if flag == None:
        num_of_download += 1
        f = open(log_file_path,'a')
        f.write(str(spider.getCurrentTime())+' page_index:'+str(page_index)+' has been downloaded.\n')
        f.write(str(num_of_download)+' files has been downloaded\n\n')
        f.close()
        time.sleep(time_interval)

    elif flag == True:
        f = open(log_file_path,'a')
        f.write(str(spider.getCurrentTime())+' page_index:'+str(page_index)+" occur something unexpexted_2.\n")
        f.write('Igore this page.\n\n')
        f.close()
        time.sleep(time_interval*20)
    else:
        f = open(log_file_path,'a')
        f.write(str(spider.getCurrentTime())+' page_index:'+str(page_index)+" is forbidden,try again after 180 second.\n")
        f.write(str(num_of_download)+' files has been downloaded\n\n')
        f.close()
        time.sleep(180)

print "Down"

