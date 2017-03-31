import re
import os

file_path = '/home/lee/Spider/logfile'

file_list = os.listdir(file_path)

pattern = re.compile('page_index:(.*?) occur something unexpexted.',re.S)

fre = open(file_path+'/'+'redown_index.txt','w') 

for log_file in file_list:
     f = open(file_path+'/'+log_file,'r')
     lines = f.read()
     lines = lines.split('\n\n')
     for line in lines:
          items = re.findall(pattern,line)
          if items:
               for item in items:
                    fre.write(item)
                    fre.write('\n')
fre.close()