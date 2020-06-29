import pandas as pd
from ipwhois import IPWhois
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

def aws_service_mapper(ip_ranges):
    tmp = []
    for ir in ip_ranges:
        tmp_dict={}
        tmp_dict['ip_prefix']=ip_num_ip_binary(ir['ip_prefix'].split('/'))
        tmp_dict['region']=ir['region']
        tmp_dict['service']=ir['service']
        tmp.append(tmp_dict)
    tmp.sort(key=lambda e:e['ip_prefix'])
    return tmp

def search_aws_service_by_ip_binary(ip_binary, service_infos):
    result = ''
    aws_infos = []
    for si in service_infos:
        prefix = si['ip_prefix']
        #print("{}  {}  {}".format(prefix, si['region'], si['service']))
        if prefix > ip_binary:
            break
        if ip_binary.startswith(prefix):
            aws_infos.append('{}:{}'.format(si['region'], si['service']))
    if aws_infos:
        result+= 'AWS '
        result+=', '.join(aws_infos)
    return result

def whois_search(ip32, aws_service_infos, known_ip_ranges):
    ip_bin = ip_num_ip_binary([ip32,'32'])
    for ki in known_ip_ranges:
        if ip_bin.startswith(ki):
            return ''

    for i in range(5):
        try:
            ip_obj = IPWhois(ip32.split('/')[0])
            asn = ip_obj.lookup_whois()['asn_description']
            if 'amazon' in asn.lower():
                aws_infos = search_aws_service_by_ip_binary(ip_bin, aws_service_infos)
                if aws_infos:
                    asn = aws_infos
            return "\"{}\"".format(asn)
        except:
            continue
    return ''

def get_value(stringV):
    stringV = str(stringV)
    if '=' in stringV:
        return stringV.split('=')[1]
    else:
        return stringV


def main(input_path, output_path, known_ip_ranges):
    response = requests.get('https://ip-ranges.amazonaws.com/ip-ranges.json')

    #print(ip_binary)
    ip_ranges = json.loads(response.text)['prefixes']
    aws_service_infos = aws_service_mapper(ip_ranges)


    f = pd.read_csv(input_path)

    print(len(f.values))

    aaa = f.values

    temp = set([])
    source_ip_idx=None
    dst_ip_idx=None
    dst_port_idx=None
    service_idx=None
    protocol_idx=None
    for i in range(len(aaa[0])):
        t = str(aaa[0][i])
        if t.startswith('srcip='):
            source_ip_idx = i
            continue
        elif t.startswith('dstport='):
            dst_port_idx = i
            continue
        elif t.startswith('dstip='):
            dst_ip_idx = i
            continue
        elif t.startswith('service='):
            service_idx = i
            continue
        elif t.startswith('proto='):
            protocol_idx = i
            continue

    for v in aaa:
        '''
        47 srcip=1.2.3.4
        23 dstport=443
        21 dstip=2.3.4.5
        42 service=HTTPS
        38 proto=6
        '''
        srcip = get_value(v[source_ip_idx])
        dstport = get_value(v[dst_port_idx])
        dstip= get_value(v[dst_ip_idx])
        proto= get_value(v[protocol_idx])
        service= get_value(v[service_idx])
        a = (proto,srcip, dstport, dstip, service)
        temp.add(a)

    import heapq
    temp = list(temp)
    print(len(temp))

    heapq.heapify(temp)
    f = open(output_path,'w')
    f.write("srcip,dstip,proto,dstport,service,src_info,dst_info\n")
    while temp:
        t = heapq.heappop(temp)
        f.write('{},{},{},{},{},{},{}\n'.format(t[1],t[3],t[0],t[2], t[4], whois_search(t[1], aws_service_infos, known_ip_ranges), whois_search(t[3], aws_service_infos, known_ip_ranges)))
    f.close()

if __name__ == '__main__':
    known_ip_ranges = []
    known_ip_ranges.append(ip_num_ip_binary('123.123.0.0/16'))
    known_ip_ranges.append(ip_num_ip_binary('12.12.0.0/15'))


    input_path = "C:\\2020-06-22_11_19_57_to_2020-06-23_11_19_56.csv.log"
    output_path = "C:\\result1.csv"
    main(input_path, output_path, known_ip_ranges)

    input_path = "C:\\2020-06-22_11_20_04_to_2020-06-23_11_20_03.csv.log"
    output_path = "C:\\result2.csv"
    main(input_path, output_path, known_ip_ranges)
