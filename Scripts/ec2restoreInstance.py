import boto3
from datetime import datetime, timezone
import json

# Initialize Boto3 clients
ec2 = boto3.client('ec2')

# Define constants
REGION = "us-east-1"  
INSTANCE_TYPE = "t2.micro"  
AMI_ID = "ami-0453ec754f44f9a4a"  
KEY_NAME = "SKMern"  
SECURITY_GROUP_IDS = ["sg-0d20032821ff97fe0"]  
SUBNET_ID = "subnet-01874c4512136bd62"


def get_latest_snapshot(volume_id):
    """
    Get the most recent snapshot for the specified volume.
    """
    response = ec2.describe_snapshots(
        Filters=[{"Name": "volume-id", "Values": [volume_id]}],
        OwnerIds=["self"]
    )

    if not response["Snapshots"]:
        print("No snapshots found for the volume.")
        return None

    # Find the latest snapshot
    latest_snapshot = max(response["Snapshots"], key=lambda x: x["StartTime"])
    return latest_snapshot["SnapshotId"]


def create_instance_from_snapshot(snapshot_id):
    """
    Create an EC2 instance using a volume from the specified snapshot.
    """
    # Step 1: Create a new volume from the snapshot
    volume = ec2.create_volume(
        SnapshotId=snapshot_id,
        AvailabilityZone=f"{REGION}a",  # Update with the target AZ
        VolumeType="gp2"
    )
    volume_id = volume["VolumeId"]
    print(f"Created volume {volume_id} from snapshot {snapshot_id}.")

    # Wait until the volume is available
    ec2.get_waiter('volume_available').wait(VolumeIds=[volume_id])

    # Step 2: Launch an EC2 instance
    instance = ec2.run_instances(
        ImageId=AMI_ID,
        InstanceType=INSTANCE_TYPE,
        KeyName=KEY_NAME,
        SecurityGroupIds=SECURITY_GROUP_IDS,
        SubnetId=SUBNET_ID,
        MinCount=1,
        MaxCount=1
    )
    instance_id = instance["Instances"][0]["InstanceId"]
    print(f"Launched EC2 instance {instance_id}.")

    # Wait until the instance is running
    ec2.get_waiter('instance_running').wait(InstanceIds=[instance_id])

    # Step 3: Attach the volume to the EC2 instance
    ec2.attach_volume(
        VolumeId=volume_id,
        InstanceId=instance_id,
        Device="/dev/xvdf"  # Specify the device name
    )
    print(f"Attached volume {volume_id} to instance {instance_id}.")


def lambda_handler(event, context):
    # Specify the volume ID for which you want to fetch the latest snapshot
    VOLUME_ID = "vol-0adc44ec754a04e62"  # Replace with your volume ID

    # Step 1: Get the latest snapshot
    snapshot_id = get_latest_snapshot(VOLUME_ID)
    if not snapshot_id:
        print("No snapshot found. Exiting.")
        return

    # Step 2: Create an instance from the snapshot
    create_instance_from_snapshot(snapshot_id)
