# Importing Modules
import os
import sys
import boto3
import time
import yaml
import SourceFiles

#Boto3 resource
ec2=boto3.resource('ec2')

#Generating a key pair
outfile = open('ec2-keypair1.pem', 'w')
key_pair = ec2.create_key_pair(KeyName='ec2-keypair1')
KeyPairOut = str(key_pair.key_material)


# Change the mode of file to read only
with os.fdopen(os.open("ec2-keypair1.pem", os.O_WRONLY | os.O_CREAT, 0o400), "w+") as handle:
    handle.write(KeyPairOut)

#Read YAML file
with open ( "test.yaml", "rt" ) as f:
    data = yaml.safe_load ( f )

#Creation of VPC

    vpc = ec2.create_vpc (
        CidrBlock='192.168.2.0/24',
        TagSpecifications=[
            {
                'ResourceType': 'vpc',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': 'DevOps VPC'
                    }
                ]
            }
        ]
    )

    # Subnet
    subnet = ec2.create_subnet (
        TagSpecifications=[
            {
                'ResourceType': 'subnet',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': 'DevOps Subnet'
                    }
                ]
            }
        ],
        AvailabilityZone=data["server"]["availability_zone"],
        CidrBlock='192.168.2.0/26',
        VpcId=vpc.id
    )
    # Internet Gateway
    internet_gateway = ec2.create_internet_gateway (
        TagSpecifications=[
            {
                'ResourceType': 'internet-gateway',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': 'DevOps Internet-gateway'
                    }
                ]
            }
        ]
    )

    attach_IG = vpc.attach_internet_gateway (
        InternetGatewayId=internet_gateway.id
    )

    # Route Table
    route_table = ec2.create_route_table (
        VpcId=vpc.id,
        TagSpecifications=[
            {
                'ResourceType': 'route-table',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': 'DevOps Route-Table'
                    }
                ]
            }
        ]
    )
    # Associate Route Table
    attach_route_table = route_table.associate_with_subnet (
        SubnetId=subnet.id
    )

    # Route
    # Warning
    route = route_table.create_route (
        DestinationCidrBlock='0.0.0.0/0',
        GatewayId=internet_gateway.id
    )

    # Security Group
    security_group = ec2.create_security_group (
        Description="Allow SSH ",
        GroupName='Allow SSH and TCP',
        VpcId=vpc.id,
        TagSpecifications=[
            {
                'ResourceType': 'security-group',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': 'DevOps Security-group'
                    }
                ]
            }
        ]
    )
    # Authorzing inbound traffic from port and cidr IP
    inbound_traffic = security_group.authorize_ingress (
        CidrIp='0.0.0.0/0',
        IpProtocol='tcp',
        FromPort=22,
        ToPort=22
    )

    # Creates Instance with required specifications
    instance = ec2.create_instances (
        BlockDeviceMappings=[
            {
                'DeviceName': data["server"]["volumes"][0]["device"],
                'Ebs': {
                    'VolumeSize': data["server"]["volumes"][0]["size_gb"]
                }
            },
            {
                'DeviceName': data["server"]["volumes"][1]["device"],
                'Ebs': {
                    'VolumeSize': data["server"]["volumes"][1]["size_gb"]
                }
            }
        ],
        InstanceType=data["server"]["instance_type"],
        KeyName="ec2-keypair1",
        ImageId=data["server"]["image_id"],
        MinCount=data["server"]["min_count"],
        MaxCount=data["server"]["max_count"],
        NetworkInterfaces=[
            {
                'AssociatePublicIpAddress': True,
                'DeviceIndex': 0,
                'Groups': [
                    security_group.id
                ],
                'SubnetId': subnet.id
            }
        ],
        Placement={
            'AvailabilityZone': data["server"]["availability_zone"]
        },
        UserData = '''
            #!/bin/bash
            [-d ~/.ssh ] || mkdir -p ~/.ssh
            cd .ssh
            cp ~/.ssh/ec2-keypair1.pub authorized_keys
            sudo adduser user1 --disabled-password
            sudo adduser user2 --disabled-password
            sudo su -user1
            mkdir /home/user1/.ssh/
            chmod 700 /home/user1/.ssh/
            touch /home/user1/.ssh/authorized_keys
            chmod 700 /home/user1/.ssh/authorized_keys
            cp ~/.ssh/ec2-keypair1.pub 700 /home/user1/.ssh/authorized_keys
            sudo su -user2
            mkdir /home/user2/.ssh/
            chmod 700 .ssh
            touch .ssh/authorized_keys
            chmod 700 .ssh/authorized_keys
            cp ~/.ssh/ec2-keypair1.pub 700 /home/user1/.ssh/authorized_keys
            sudo su ec2-user
            sudo mkfs /dev/xvda -t ext4
            sudo mount /dev/xvda /
            sudo mkfs /dev/xvdf -t xfs
            sudo mkdir /data
            sudo mount /dev/xvdf /data
        ''',
        TagSpecifications = [
        {
            'ResourceType': 'instance',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': 'DevOps_EC2'
                }
            ]
        }
    ]
    )