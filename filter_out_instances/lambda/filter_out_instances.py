import collections
import boto3


def get_ec2_instances_by_tag(tags):
    client = boto3.client('ec2')
    custom_filter = []
    for tag in tags:
        for key, value in tag.items():
            custom_filter.append({'Name': 'tag:' + key, 'Values': [value]}.copy())

    response = client.describe_instances(
        Filters=custom_filter
    )

    ec2_to_operate = []
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            ec2_to_operate.append(instance['InstanceId'])

    return ec2_to_operate


def get_rds_instances_by_tag(tags):
    client = boto3.client('rds')
    response = client.describe_db_instances()
    rds_to_operate = []

    for tag in tags:
        for key, value in tag.items():
            for instance in response['DBInstances']:
                for rds_tag in instance['TagList']:
                    if rds_tag['Key'] == key and rds_tag['Value'] == value:
                        rds_to_operate.append(instance['DBInstanceIdentifier'])
                else:
                    continue
    rds_to_operate = [item for item, count in collections.Counter(rds_to_operate).items() if count == len(tags)]
    return rds_to_operate


def get_instances_by_tag(tags):
    services = ['ec2', 'rds']
    result = []
    for service in services:
        function_name = 'get_{}_instances_by_tag'.format(service)
        instances_list = eval(function_name + "(tags)")
        if instances_list:
            result.append({"instance_type": service, "instance_ids": instances_list})
    return result


def lambda_handler(event, context):
    return get_instances_by_tag(event['tags'])
