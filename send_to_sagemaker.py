import boto3
import json
import sys
import os

def send_to_sagemaker(log_file):
    if not os.path.isfile(log_file):
        print(f"Error: File '{log_file}' does not exist.")
        return

    try:
        with open(log_file, encoding='utf-8') as f:
            log = f.read()[:2000]

        client = boto3.client('sagemaker-runtime', region_name='us-east-2')
        response = client.invoke_endpoint(
            EndpointName='log-analyzer-endpoint',
            ContentType='application/json',
            Body=json.dumps({'inputs': log})
        )

        print("SageMaker Response:")
        print(response['Body'].read().decode('utf-8'))

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <log_file>")
    else:
        send_to_sagemaker(sys.argv[1])

