import boto3
import pandas as pd
import xlsxwriter
from botocore.exceptions import NoCredentialsError

def describe_instances_and_asgs(session):
    try:
        # Create EC2 and ASG clients using the provided session
        ec2_client = session.client('ec2')
        asg_client = session.client('autoscaling')

        # Describe EC2 instances
        instance_data = []
        response = ec2_client.describe_instances()
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                instance_id = instance['InstanceId']
                tags = {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
                instance_data.append({
                    'Instance ID': instance_id,
                    **tags
                })

        # Describe Auto Scaling Groups
        asg_data = []
        response = asg_client.describe_auto_scaling_groups()
        for asg in response['AutoScalingGroups']:
            asg_name = asg['AutoScalingGroupName']
            tags = {tag['Key']: tag['Value'] for tag in asg.get('Tags', [])}
            asg_data.append({
                'ASG Name': asg_name,
                **tags
            })

        return instance_data, asg_data

    except NoCredentialsError:
        print("Error: AWS credentials not available or invalid.")

def export_to_excel(instance_data, asg_data, output_file='aws_resources.xlsx'):
    instance_df = pd.DataFrame(instance_data)
    asg_df = pd.DataFrame(asg_data)

    # Export DataFrames to an Excel file
    with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
        instance_df.to_excel(writer, sheet_name='EC2 Instances', index=False)
        asg_df.to_excel(writer, sheet_name='Auto Scaling Groups', index=False)

    print(f"Data exported to {output_file}")

def main():
    #Boto3 session
    session=boto3.Session(profile_name='cloudadmin',region_name='ap-southeast-1')

    # Describe instances and ASGs
    instance_data, asg_data = describe_instances_and_asgs(session)

    # Export data to Excel
    export_to_excel(instance_data, asg_data)

if __name__ == "__main__":
    main()
