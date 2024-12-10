# HV_ServerlessArchitecture


# 1: Automated Instance Management Using AWS Lambda and Boto3

## Objective
This demonstrates how to automate the stopping and starting of EC2 instances based on their tags using **AWS Lambda** and **Boto3**, Amazon's SDK for Python.

---

## Instructions

### 1. EC2 Setup
1. **Create EC2 Instances**:
   - Navigate to the [EC2 Dashboard].
   - Create **two t2.micro instances** .

2. **Add Tags**:
   - For the first instance:
     - Key: `Action`
     - Value: `Auto-Stop`
   - For the second instance:
     - Key: `Action`
     - Value: `Auto-Start`

---

### 2. Lambda IAM Role Setup
1. **Navigate to IAM Dashboard**:
   - Open the [IAM Console].
   - Create a new **IAM Role** for **AWS Lambda**.

2. **Attach Permissions**:
   - Attach the **AmazonEC2FullAccess** policy to the role.

---

### 3. Lambda Function Setup
1. **Create a New Function**:
   - Go to the [Lambda Console].
   - Click **Create function** and select:
     - **Author from scratch**.
     - Runtime: **Python 3.13**.
     - Assign the IAM role created earlier.

2. **Write the Lambda Code**:
   Use the following Python code for the Lambda function:

   ```python
   import boto3

   def lambda_handler(event, context):
       ec2 = boto3.client('ec2')

       # Fetch all instances
       instances = ec2.describe_instances(Filters=[{'Name': 'tag:Action', 'Values': ['Auto-Stop', 'Auto-Start']}])

       # Iterate through instances
       for reservation in instances['Reservations']:
           for instance in reservation['Instances']:
               instance_id = instance['InstanceId']
               action = next(tag['Value'] for tag in instance['Tags'] if tag['Key'] == 'Action')

               if action == 'Auto-Stop' and instance['State']['Name'] != 'stopped':
                   print(f"Stopping instance: {instance_id}")
                   ec2.stop_instances(InstanceIds=[instance_id])
               elif action == 'Auto-Start' and instance['State']['Name'] != 'running':
                   print(f"Starting instance: {instance_id}")
                   ec2.start_instances(InstanceIds=[instance_id])

       return "Lambda function executed successfully"
   ```

3. **Save and Deploy**:
   - Save the code and click **Deploy**.

---

### 4. Testing
1. **Manually Invoke the Function**:
   - In the Lambda Console, select the function and click **Test**.
   - Configure a test event (e.g., leave the default "Hello World" event).

2. **Verify Changes**:
   - Go to the [EC2 Dashboard](https://console.aws.amazon.com/ec2/).
   - Check the state of the two instances:
     - The instance tagged `Auto-Stop` should transition to **stopped**.
     - The instance tagged `Auto-Start` should transition to **running**.

---

## Output
The Lambda function logs will include:
- Instance IDs that were stopped or started.
- Any errors encountered during execution.

---

## Notes
- Ensure that the EC2 instances and Lambda function are in the same AWS region.
- For production scenarios, use more restrictive IAM policies to improve security.

---

Let me know if you need any additional assistance!
