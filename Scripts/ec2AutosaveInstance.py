import boto3
import json
import time

ec2 = boto3.client('ec2')
s3 = boto3.client('s3')

def create_ami(instance_id):
    """
    Create an AMI (Amazon Machine Image) from an EC2 instance.
    """
    timestamp = time.strftime("%Y%m%d%H%M%S")
    ami_name = f"Backup-{instance_id}-{timestamp}"
    
    response = ec2.create_image(
        InstanceId=instance_id,
        Name=ami_name,
        NoReboot=True  # Avoid rebooting for a faster process
    )
    return response['ImageId']

def lambda_handler(event, context):
    # Parse the event for EC2 instance information
    detail = event.get('detail', {})
    instance_id = detail.get('instance-id', None)
    
    if not instance_id:
        print("No instance ID found in event.")
        return

    print(f"Detected termination for instance: {instance_id}")
    
    # Step 1: Create an AMI
    ami_id = create_ami(instance_id)
    print(f"Created AMI: {ami_id}")
    
    # Step 2: Save the AMI metadata to S3
    bucket_name = "skbatch8"  # Replace with your bucket name
    metadata = {
        "InstanceId": instance_id,
        "AMIId": ami_id,
        "Timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    file_name = f"{instance_id}/backup-metadata.json"
    s3.put_object(
        Bucket=bucket_name,
        Key=file_name,
        Body=json.dumps(metadata),
        ContentType="application/json"
    )
    
    print(f"Saved metadata to S3: {bucket_name}/{file_name}")
