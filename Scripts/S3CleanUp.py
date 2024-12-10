import boto3
import datetime
import json

def lambda_handler(event, context):
    # Replace with your S3 bucket name
    bucket_name = "your-bucket-name"

    # Initialize the S3 client
    s3_client = boto3.client('s3')

    try:
        # List objects in the bucket
        response = s3_client.list_objects_v2(Bucket=bucket_name)
        if 'Contents' not in response:
            print("Bucket is empty or does not exist.")
            return {
                "statusCode": 200,
                "body": json.dumps({"message": "Bucket is empty or no objects to delete."})
            }

        # Get the current date
        current_date = datetime.datetime.now(datetime.timezone.utc)

        # List to store deleted objects for logging
        deleted_objects = []

        # Iterate through the objects in the bucket
        for obj in response['Contents']:
            obj_key = obj['Key']
            obj_last_modified = obj['LastModified']

            # Calculate the age of the file in days
            file_age_in_days = (current_date - obj_last_modified).days

            # If the file is older than 30 days, delete it
            if file_age_in_days > 30:
                print(f"Deleting object: {obj_key}, Last Modified: {obj_last_modified}")
                s3_client.delete_object(Bucket=bucket_name, Key=obj_key)
                deleted_objects.append(obj_key)

        # Return the deleted objects for logging
        return {
            "statusCode": 200,
            "body": json.dumps({
                "Deleted Objects": deleted_objects,
                "Message": "Older objects deleted successfully."
            })
        }

    except Exception as e:
        print(f"Error: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
