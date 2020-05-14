import boto3


def get_instance_ids_for_asg(asg_name, region, client=None):
    if client is None:
        client = boto3.client('autoscaling')

    response = client.describe_auto_scaling_groups(AutoScalingGroupNames=[asg_name])
    assert 1 == len(response["AutoScalingGroups"])

    group = response["AutoScalingGroups"][0]
    return sorted([i['InstanceId'] for i in group["Instances"]])


def get_public_ip_of_ec2_instance(instance_id, region, client=None):
    if client is None:
        client = boto3.client('ec2')

    response = client.describe_instances(InstanceIds=[instance_id])

    assert 1 == len(response["Reservations"])
    assert 1 == len(response["Reservations"][0]["Instances"])

    return response["Reservations"][0]["Instances"][0]["PublicIpAddress"]
