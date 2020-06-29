#-*- coding: utf-8 -*-
#Athor : Jisu Kim
'''
pip install xlsxwriter boto3
'''
import xlsxwriter
from pprint import pprint
import os
import sys
import boto3




################################################################################
# Input Start
################################################################################
search_tag_key='key'
search_tag_value = "value"
account_name = "acc Name(file name)"#file name
aws_access_key_id = ''
aws_secret_access_key = ''
aws_session_token = ''
################################################################################
# Input End
################################################################################










class ExcelWriter:
    def __init__(self, file_path, account_name, aws_access_key_id, aws_secret_access_key, aws_session_token, search_tag_key, search_tag_value):
        if sys.version_info[0]<3:
            self.make_unicode = self.make_unicode2
        else:
            self.make_unicode = self.make_unicode3
        self.ec2Client = boto3.client(
            service_name='ec2',
            region_name='ap-northeast-2',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token
        )
        self.current_row = 0
        self.search_tag_key = search_tag_key
        self.search_tag_value = search_tag_value
        self.account_name = account_name
        self.security_group = {}
        self.wb = self.create_workbook(file_path)
        self.ws = self.create_worksheet(self.account_name)
        self.create_common_format()
        self.create_taking_over_sheet()
        self.save()

    def create_common_format(self):
        #Default
        self.format_default = self.wb.add_format()
        self.format_default.set_font_name(self.make_unicode('맑은 고딕'))

        #Col Name
        self.format_col_name = self.wb.add_format()
        self.format_col_name.set_align('center')
        self.format_col_name.set_align('vcenter')
        self.format_col_name.set_bg_color('f2f2f2')
        self.format_col_name.set_bold(True)
        self.format_col_name.set_border()
        self.format_col_name.set_font_name(self.make_unicode('맑은 고딕'))

        #info title
        self.format_info_title = self.wb.add_format()
        self.format_info_title.set_align('center')
        self.format_info_title.set_align('vcenter')
        self.format_info_title.set_bold(True)
        self.format_info_title.set_font_size(30)
        self.format_info_title.set_border()
        self.format_info_title.set_font_name(self.make_unicode('맑은 고딕'))

        #info sub title
        self.format_info_sub_title = self.wb.add_format()
        self.format_info_sub_title.set_align('left')
        self.format_info_sub_title.set_align('vcenter')
        self.format_info_sub_title.set_bold(True)
        self.format_info_sub_title.set_font_size(15)
        self.format_info_sub_title.set_border()
        self.format_info_sub_title.set_font_name(self.make_unicode('맑은 고딕'))

        #center
        self.format_center = self.wb.add_format()
        self.format_center.set_align('center')
        self.format_center.set_align('vcenter')
        self.format_center.set_border()
        self.format_center.set_font_name(self.make_unicode('맑은 고딕'))

        #center text wrap
        self.format_center_text_wrap = self.wb.add_format()
        self.format_center_text_wrap.set_align('center')
        self.format_center_text_wrap.set_align('vcenter')
        self.format_center_text_wrap.set_text_wrap()
        self.format_center_text_wrap.set_border()
        self.format_center_text_wrap.set_font_name(self.make_unicode('맑은 고딕'))

        #left
        self.format_left = self.wb.add_format()
        self.format_left.set_align('left')
        self.format_left.set_align('vcenter')
        self.format_left.set_border()
        self.format_left.set_font_name(self.make_unicode('맑은 고딕'))

        #left textwrap
        self.format_left_text_wrap = self.wb.add_format()
        self.format_left_text_wrap.set_align('left')
        self.format_left_text_wrap.set_align('vcenter')
        self.format_left_text_wrap.set_text_wrap()
        self.format_left_text_wrap.set_border()
        self.format_left_text_wrap.set_font_name(self.make_unicode('맑은 고딕'))


    def create_workbook(self, path):
        return xlsxwriter.Workbook(path)


    def create_worksheet(self, sheet_name):
        return self.wb.add_worksheet(sheet_name)


    def make_cell(self, sheet, row, col, value, format):
        return sheet.write(row, col, value, format)


    def make_merge_cell(self, sheet, start_row, start_column, end_row, end_column, value, format):
        returnObj = None
        if start_row == end_row and start_column == end_column:
            returnObj = self.make_cell(sheet, start_row, start_column, value, format)
        else:
            returnObj = sheet.merge_range(start_row, start_column, end_row, end_column, value, format)
        return returnObj

    def create_taking_over_sheet(self):
        '''
        SG
        response = client.describe_security_groups(
            Filters=[
                {
                    'Name': 'string',
                    'Values': [
                        'string',
                    ]
                },
            ],
            GroupIds=[
                'string',
            ],
            GroupNames=[
                'string',
            ],
            DryRun=True|False,
            NextToken='string',
            MaxResults=123
        )
        '''
        ec2List = []

        NextToken=''
        args = {
            "Filters":[
                {
                    'Name': 'tag:{}'.format(self.search_tag_key),
                    'Values': [
                        self.search_tag_value
                    ]
                },
            ],
            "MaxResults":5
        }
        while True:
            response = self.ec2Client.describe_instances(**args)

            temp = []
            if response.get('Reservations'):
                temp = sum([reservation['Instances'] for reservation in response['Reservations']],[])
            ec2List+=temp
            if response.get('NextToken'):
                args['NextToken']=response.get('NextToken')
            else:
                break

        self.ec2List = ec2List
        for instance_info in ec2List:
            if instance_info.get('SecurityGroups'):
                for sg in instance_info['SecurityGroups']:
                    if self.security_group.get(sg['GroupId'])==None:
                        self.security_group[sg['GroupId']]=1
                    else:
                        self.security_group[sg['GroupId']]=self.security_group[sg['GroupId']]+1

        self.make_security_group_info()
        self.make_instances_info()


    def make_unicode2(self, text):
        return unicode(text, "utf-8")

    def make_unicode3(self, text):
        return text

    def make_instances_info(self):
        ws = self.ws
        self.current_row +=2
        self.make_cell(ws, self.current_row, 1, '<EC2>',None)
        self.current_row +=1

        self.make_merge_cell(ws, self.current_row, 1, self.current_row+1, 1, "No.", self.format_col_name)
        self.make_merge_cell(ws, self.current_row, 2, self.current_row, 19, self.make_unicode("필수 사항"), self.format_col_name)
        self.make_merge_cell(ws, self.current_row, 20, self.current_row, 26, self.make_unicode("선택 사항(Optional)"), self.format_col_name)
        self.current_row+=1
        sub_col_name=[self.make_unicode("운영 형태"),
        "Availability Zone",
        "Instance Name",
        "Status",
        "AMI (OS)",
        "Instance Type",
        "Subnet Type",
        "VPC ID",
        "Subnet ID",
        "Instance ID",
        "Private IP",
        "Public IP",
        "EIP",
        "Root Volume ID",
        "Root Volume (GB)",
        "Security Group",
        "IAM role",
        self.make_unicode("용도"),
        "Data Volume ID",
        "Data Volume (GB)",
        "Swap Space(MB)",
        "Instance Store",
        "EBS_Optimized",
        "Userdata",
        self.make_unicode("비고")]
        for ci, cn in enumerate(sub_col_name, start=2):
            self.make_cell(ws, self.current_row, ci, cn, self.format_col_name)
        self.current_row+=1


        for i, instance_info in enumerate(self.ec2List,start=1):
            instance_az = instance_info['Placement']['AvailabilityZone']
            instance_state = instance_info['State']['Name']
            instance_type = instance_info['InstanceType']
            vpc_id = instance_info['VpcId']
            subnet_id = instance_info['SubnetId']
            instance_id = instance_info['InstanceId']
            private_ip = instance_info['PrivateIpAddress']
            instance_volume_ids = [ v['Ebs']['VolumeId'] for v in instance_info['BlockDeviceMappings']]
            volume_response = self.ec2Client.describe_volumes(
                VolumeIds=instance_volume_ids
            )
            instance_volume_infos = volume_response['Volumes']
            instance_volume_infos.sort(key=lambda e: instance_volume_ids.index(e['VolumeId']))
            instance_sg_names = []
            if instance_info.get('SecurityGroups'):
                for sg in instance_info['SecurityGroups']:
                    instance_sg_names.append(sg['GroupName'])
            tags = {}
            for tag in instance_info['Tags']:
                tags[tag['Key']] = tag['Value']

            iamRole = instance_info['IamInstanceProfile']['Arn'].split('/')[1] if instance_info['IamInstanceProfile'] else ''
            self.make_cell(ws, self.current_row, 1, str(i), self.format_center)
            #"운영 형태"
            self.make_cell(ws, self.current_row, 2, self.account_name.split('-')[-1], self.format_center)
            #"Availability Zone",
            self.make_cell(ws, self.current_row, 3, instance_az, self.format_center)
            #"Instance Name",
            self.make_cell(ws, self.current_row, 4, tags['Name'] if tags.get('Name') else 'None', self.format_center)
            #"Status",
            self.make_cell(ws, self.current_row, 5, instance_state, self.format_center)
            #"AMI (OS)",
            self.make_cell(ws, self.current_row, 6, tags['OS'] if tags.get('OS') else 'None', self.format_center)
            #"Instance Type",
            self.make_cell(ws, self.current_row, 7, instance_type, self.format_center)
            #"Subnet Type",
            self.make_cell(ws, self.current_row, 8, 'private', self.format_center)
            #"VPC ID",
            self.make_cell(ws, self.current_row, 9, vpc_id, self.format_center)
            #"Subnet ID",
            self.make_cell(ws, self.current_row, 10, subnet_id, self.format_center)
            #"Instance ID",
            self.make_cell(ws, self.current_row, 11, instance_id, self.format_center)
            #"Private IP",
            self.make_cell(ws, self.current_row, 12, private_ip, self.format_center)
            #"Public IP",
            self.make_cell(ws, self.current_row, 13, "-", self.format_center)
            #"EIP",
            self.make_cell(ws, self.current_row, 14, "-", self.format_center)
            #"Root Volume ID",
            self.make_cell(ws, self.current_row, 15, instance_volume_ids[0], self.format_center)
            #"Root Volume (GB)",
            self.make_cell(ws, self.current_row, 16, instance_volume_infos[0]['Size'], self.format_center)
            #"Security Group",
            self.make_cell(ws, self.current_row, 17, ', '.join(instance_sg_names), self.format_center)
            #"IAM role",
            self.make_cell(ws, self.current_row, 18, iamRole, self.format_center)
            #"용도"
            self.make_cell(ws, self.current_row, 19, iamRole, self.format_center)
            #"Data Volume ID"
            self.make_cell(ws, self.current_row, 20, 'N/A' if len(instance_volume_infos)<2 else ('\n'.join([v['VolumeId'] for v in instance_volume_infos[1:]])), self.format_center_text_wrap)
            #"Data Volume (GB)"
            self.make_cell(ws, self.current_row, 21, 'N/A' if len(instance_volume_infos)<2 else ('\n'.join([str(v['Size']) for v in instance_volume_infos[1:]])), self.format_center_text_wrap)
            #"Swap Space(MB)"
            self.make_cell(ws, self.current_row, 22, "", self.format_center)
            #"Instance Store",
            self.make_cell(ws, self.current_row, 23, "", self.format_center)
            #"EBS_Optimized"
            self.make_cell(ws, self.current_row, 24, "", self.format_center)
            #"Userdata"
            self.make_cell(ws, self.current_row, 25, "", self.format_center)
            #"비고"
            self.make_cell(ws, self.current_row, 26, "", self.format_center)
            self.current_row+=1

    def make_security_group_info(self):
        ws = self.ws
        ws_widths = [8.1,
        22.9,
        19,
        29.5,
        23.3,
        20.7,
        24.5,
        29.7,
        50.7,
        43,
        24.5,
        20,
        25.1,
        10.2,
        11.5,
        17,
        18.8,
        70,
        14,
        19.5,
        22.4,
        16.7]
        for i, w in enumerate(ws_widths):
            ws.set_column(i, i, w)

        sg_list = []
        NextToken=''
        args = {
            "GroupIds":list(self.security_group.keys())
        }
        while True:
            response = self.ec2Client.describe_security_groups(**args)
            if response.get('SecurityGroups'):
                sg_list += response['SecurityGroups']

            if response.get('NextToken'):
                args['NextToken']=response.get('NextToken')
            else:
                sg_list.sort(key=lambda e:-self.security_group[e['GroupId']])
                break

        self.current_row += 1
        for sg in sg_list:
            #[Ingress]
            start_row_num = self.current_row+1
            #SG ID
            self.make_cell(ws, self.current_row, 1, "SG ID", self.format_col_name)
            #Name
            self.make_cell(ws, self.current_row, 2, "Name", self.format_col_name)
            #INBOUND
            self.make_cell(ws, self.current_row, 3, "INBOUND", self.format_col_name)
            #Source IP(s)
            self.make_cell(ws, self.current_row, 4, "Source IP(s)", self.format_col_name)
            #Protocol
            self.make_cell(ws, self.current_row, 5, "Protocol", self.format_col_name)
            #Port
            self.make_cell(ws, self.current_row, 6, "Port", self.format_col_name)
            #Exp
            self.make_cell(ws, self.current_row, 7, "Exp", self.format_col_name)

            if sg['IpPermissions']:
                for ingress_by_protocol in sg['IpPermissions']:
                    protocol = ingress_by_protocol['IpProtocol']
                    port_info = 'All'
                    if protocol == '-1':
                        protocol = 'All'
                    else:
                        protocol = protocol.upper()
                        from_port = ingress_by_protocol['FromPort']
                        to_port = ingress_by_protocol['ToPort']
                        if from_port == to_port:
                            if from_port > -1:
                                port_info = from_port
                        else:
                            port_info = '{} - {}'.format(from_port, to_port)

                    for r in ingress_by_protocol['IpRanges']:
                        self.current_row+=1
                        #Source IP(s)
                        self.make_cell(ws, self.current_row, 4, r['CidrIp'], self.format_left)
                        #Protocol
                        self.make_cell(ws, self.current_row, 5, protocol, self.format_left)
                        #Port
                        self.make_cell(ws, self.current_row, 6, port_info, self.format_left)
                        #Exp
                        self.make_cell(ws, self.current_row, 7, r['Description'] if r.get('Description') else '', self.format_left)

            self.current_row+=1
            #Source IP(s)
            self.make_cell(ws, self.current_row, 4, "", self.format_left)
            #Protocol
            self.make_cell(ws, self.current_row, 5, "", self.format_left)
            #Port
            self.make_cell(ws, self.current_row, 6, "", self.format_left)
            #Exp
            self.make_cell(ws, self.current_row, 7, "", self.format_left)

            self.make_merge_cell(ws, start_row_num, 3, self.current_row, 3, "IN", self.format_center)

            #[Egress]
            self.current_row+=1
            #OUTBOUND
            self.make_cell(ws, self.current_row, 3, "OUTBOUND", self.format_col_name)
            #Destination IP(s)
            self.make_cell(ws, self.current_row, 4, "Destination IP(s)", self.format_col_name)
            #Protocol
            self.make_cell(ws, self.current_row, 5, "Protocol", self.format_col_name)
            #Port
            self.make_cell(ws, self.current_row, 6, "Port", self.format_col_name)
            #Exp
            self.make_cell(ws, self.current_row, 7, "Exp", self.format_col_name)

            start_egress_row_num = self.current_row+1
            if sg['IpPermissionsEgress']:
                for egress_by_protocol in sg['IpPermissionsEgress']:
                        protocol = egress_by_protocol['IpProtocol']
                        port_info = 'All'
                        if protocol == '-1':
                            protocol = 'All'
                        else:
                            protocol = protocol.upper()
                            from_port = egress_by_protocol['FromPort']
                            to_port = egress_by_protocol['ToPort']
                            if from_port == to_port:
                                if from_port > -1:
                                    port_info = from_port
                            else:
                                port_info = '{} - {}'.format(from_port, to_port)

                        for r in egress_by_protocol['IpRanges']:
                            self.current_row+=1
                            #Source IP(s)
                            self.make_cell(ws, self.current_row, 4, r['CidrIp'], self.format_left)
                            #Protocol
                            self.make_cell(ws, self.current_row, 5, protocol, self.format_left)
                            #Port
                            self.make_cell(ws, self.current_row, 6, port_info, self.format_left)
                            #Exp
                            self.make_cell(ws, self.current_row, 7, r['Description'] if r.get('Description') else '', self.format_left)

            self.current_row+=1
            #Source IP(s)
            self.make_cell(ws, self.current_row, 4, "", self.format_left)
            #Protocol
            self.make_cell(ws, self.current_row, 5, "", self.format_left)
            #Port
            self.make_cell(ws, self.current_row, 6, "", self.format_left)
            #Exp
            self.make_cell(ws, self.current_row, 7, "", self.format_left)

            self.make_merge_cell(ws, start_egress_row_num, 3, self.current_row, 3, "OUT", self.format_center)

            self.make_merge_cell(ws, start_row_num, 1, self.current_row, 1, sg['GroupId'], self.format_center)

            self.make_merge_cell(ws, start_row_num, 2, self.current_row, 2, sg['GroupName'], self.format_center)

            self.current_row+=3
    def save(self):
        self.wb.close()

def main():

    resultFolder = os.path.join(sys.path[0], 'results')
    if not os.path.isdir(resultFolder):
        if os.path.isfile(resultFolder):
            os.path.remove(resultFolder)
        os.mkdir(resultFolder)



    file_path = os.path.join(resultFolder, '{}.xlsx'.format(account_name))


    a = ExcelWriter(file_path, account_name, aws_access_key_id, aws_secret_access_key, aws_session_token, search_tag_key, search_tag_value)


if __name__ == '__main__':
    main()
