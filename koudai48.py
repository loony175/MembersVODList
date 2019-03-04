#!/usr/bin/env python3

import argparse
import arrow
import base64
import functools
import json
import logging
import multiprocessing
import operator
import os
import pathlib
import re
import requests
from urllib import parse

def process(dict):
    info={}
    info['title']=dict['title']
    sub_title={}
    sub_title['raw']=dict['subTitle']
    sub_title['base64']=base64.b64encode(dict['subTitle'].encode()).decode()
    info['subTitle']=sub_title
    info['picPath']=['https://source.48.cn%s'%obj for obj in dict['picPath'].split(',')]
    datetime=arrow.get(dict['startTime']/1000).to('Asia/Shanghai')
    start_time={}
    start_time['timestamp']=dict['startTime']
    start_time['datetime']=datetime.strftime('%Y-%m-%dT%H:%M:%SZ')
    info['startTime']=start_time
    info['memberId']=dict['memberId']
    info['liveType']=dict['liveType']
    info['streamPath']=dict['streamPath'].replace('http://','https://')
    if parse.urlparse(info['streamPath']).hostname=='alcdn.hls.xiaoka.tv':
        date=re.match(r'^.*/(\d{6,8})/.*$',info['streamPath']).group(1)
        date_=datetime.format('YYYYMD')
        if date_!=date:
            info['streamPath']=info['streamPath'].replace(date,date_)
    return info

def dump(data,json_data,member):
    member_id=json_data[member]
    file='%s-%s.json'%('%06d'%member_id,member)
    output_normal=pathlib.Path('normal')/file
    output_quiet=pathlib.Path('quiet')/file
    info=[dict for dict in data if dict['memberId']==member_id]
    f=open(output_normal,'w')
    f.write(json.dumps(info,indent=2,ensure_ascii=False))
    f.write('\n')
    f.close()
    logging.info('[normal] %d objects written in %s'%(len(info),output_normal))
    urls={}
    for dict in info:
        urls[dict['startTime']['datetime']]=dict['streamPath']
    f=open(output_quiet,'w')
    f.write(json.dumps(urls,indent=2,ensure_ascii=False))
    f.write('\n')
    f.close()
    logging.info('[quiet] %d objects written in %s'%(len(urls),output_quiet))

def main():
    parser=argparse.ArgumentParser()
    add=parser.add_argument
    add('-j','--jobs',type=int,default=os.cpu_count())
    args=parser.parse_args()
    logging.basicConfig(level=logging.INFO,format='%(levelname)s: %(message)s')
    pathlib.Path('normal').mkdir(exist_ok=True)
    pathlib.Path('quiet').mkdir(exist_ok=True)
    resp=requests.post('https://plive.48.cn/livesystem/api/live/v1/memberLivePage',headers={'Content-Type':'application/json','version':'5.3.2','os':'android'},json={'lastTime':0,'groupId':0,'memberId':0,'limit':40000}).json()
    review_list=resp['content']['reviewList']
    data=[]
    members=[]
    for dict in sorted(review_list,key=operator.itemgetter('memberId')):
        if dict['memberId'] not in members:
            data.append(dict)
            members.append(dict['memberId'])
    json_data={}
    for dict in data:
        if dict['memberId']==4:
            member_name='呵呵姐'
        elif dict['memberId']==530431:
            member_name='呵呵妹'
        else:
            member_name=re.match(r'^(.*)的.*（回放生成中）$',dict['title']).group(1)
        json_data[member_name]=dict['memberId']
    pool=multiprocessing.Pool(args.jobs)
    data=pool.map(process,review_list)
    pool.close()
    pool.join()
    work=functools.partial(dump,data,json_data)
    pool=multiprocessing.Pool(args.jobs)
    pool.map(work,json_data.keys())
    pool.close()
    pool.join()

if __name__=='__main__':
    main()
