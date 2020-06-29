#-*- coding: utf-8 -*-

#Athor : Jisu Kim
'''
python 2.7
pip install requests
'''
from __future__ import print_function
import requests
import json


def num_to_binary(num):
     temp = str(bin(num))[2:]
     temp = '0'*(8-len(temp))+temp
     return temp

def ip_num_ip_binary(ip_info):
    prefix = int(ip_info[1])
    ip_classes = ip_info[0].split('.')
    result = ''
    for ip_class in ip_classes:
        result+=num_to_binary(int(ip_class))
    return result[:prefix]

def getIdxService(aws_ip_ranges, ip):
    result = []
    for idx, r in enumerate(aws_ip_ranges):
        if ip.startswith(r):
            result.append(idx)
    if result:
        return result
    else:
        return [-1]

def main(ip):
    ip+='/32'
    response = requests.get('https://ip-ranges.amazonaws.com/ip-ranges.json')
    ip_ranges = json.loads(response.text)['prefixes']
    aws_ip_ranges = []
    aws_service_region = []
    for ip_range in ip_ranges:
        aws_ip_ranges.append(ip_num_ip_binary(ip_range['ip_prefix'].split('/')))
        aws_service_region.append('{} {}'.format(ip_range['region'], ip_range['service']))
    idx = getIdxService(aws_ip_ranges, ip_num_ip_binary(ip.split('/')))
    if idx[0]==-1:
        print('Not included in the AWS Ranges')
    else:
        for i in idx:
            print(aws_service_region[i])

def search_region_service(region, service):
    response = requests.get('https://ip-ranges.amazonaws.com/ip-ranges.json')
    ip_ranges = json.loads(response.text)['prefixes']
    aws_ip_ranges = []
    aws_service_region = []
    for ip_range in ip_ranges:
        if ip_range['region'] == region and ip_range['service'] == service:
            print(ip_range['ip_prefix'])

if __name__ == '__main__':
    #main(sys.argv[1:])
    main('54.240.253.128')
    #search_region_service("ap-northeast-2", "EC2")
