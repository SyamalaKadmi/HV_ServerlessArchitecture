import boto3
import json

def lambda_handler(event, context):
    """
    Detect EC2 instances with specific tags ('Auto-Stop', 'Auto-Start')
    and manage their states by stopping or starting them accordingly.
    """
    # Initialize the EC2 client
    ec2_client = boto3.client('ec2')

    try:
        # Describe all instances with the 'Auto-Stop' or 'Auto-Start' tag
        response = ec2_client.describe_instances(
            Filters=[
                {'Name': 'tag:Action', 'Values': ['Auto-Stop', 'Auto-Start']}
            ]
        )

        # Initialize lists to store instance IDs
        auto_stop_instances = []
        auto_start_instances = []

        # Iterate through the reservations and collect tagged instances
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                instance_id = instance['InstanceId']
                tags = {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}

                # Check the 'Action' tag and classify instances
                if tags.get('Action') == 'Auto-Stop':
                    auto_stop_instances.append(instance_id)
                elif tags.get('Action') == 'Auto-Start':
                    auto_start_instances.append(instance_id)

        # Stop instances with the 'Auto-Stop' tag
        if auto_stop_instances:
            print(f"Stopping instances: {auto_stop_instances}")
            ec2_client.stop_instances(InstanceIds=auto_stop_instances)
        else:
            print("No instances found with the 'Auto-Stop' tag.")

        # Start instances with the 'Auto-Start' tag
        if auto_start_instances:
            print(f"Starting instances: {auto_start_instances}")
            ec2_client.start_instances(InstanceIds=auto_start_instances)
        else:
            print("No instances found with the 'Auto-Start' tag.")

        # Return the affected instances for logging
        return {
            "statusCode": 200,
            "body": json.dumps({
                "Stopped Instances": auto_stop_instances,
                "Started Instances": auto_start_instances
            })
        }

    except Exception as e:
        print(f"Error: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
