import boto3
from types_boto3_autoscaling import AutoScalingClient
from types_boto3_ec2 import EC2Client


def get_instance_ids_for_asg(asg_name: str, region: str, client: AutoScalingClient | None=None) -> list[str]:
    if client is None:
        client = boto3.client("autoscaling")

    client = boto3.client("autoscaling")

    response = client.describe_auto_scaling_groups(AutoScalingGroupNames=[asg_name])
    assert 1 == len(response["AutoScalingGroups"])

    group = response["AutoScalingGroups"][0]
    return sorted([i["InstanceId"] for i in group["Instances"]])


def get_public_ip_of_ec2_instance(instance_id: str, region: str, client: EC2Client|None=None) -> str:
    if client is None:
        client = boto3.client("ec2")

    response = client.describe_instances(InstanceIds=[instance_id])

    assert 1 == len(response["Reservations"])
    assert 1 == len(response["Reservations"][0]["Instances"])

    return response["Reservations"][0]["Instances"][0]["PublicIpAddress"]
