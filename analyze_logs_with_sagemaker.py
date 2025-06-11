import boto3
import json
import sys
import os

# Get environment variables from Jenkins
ENDPOINT_NAME = os.getenv("SAGEMAKER_ENDPOINT")
REGION_NAME = os.getenv("AWS_REGION", "us-east-1")

# Initialize the SageMaker runtime client
runtime = boto3.client("sagemaker-runtime", region_name=REGION_NAME)

def query_sagemaker_endpoint(prompt):
    response = runtime.invoke_endpoint(
        EndpointName=ENDPOINT_NAME,
        ContentType="application/json",
        Body=json.dumps({"inputs": prompt})
    )

    result = json.loads(response["Body"].read().decode("utf-8"))
    # Adjust based on model output structure
    if isinstance(result, list) and "generated_text" in result[0]:
        return result[0]["generated_text"]
    else:
        return str(result)

def main():
    log_input = sys.stdin.read()

    # You can truncate if logs are very long
    if len(log_input) > 4000:
        log_input = log_input[-4000:]

    prompt = f"""You are a CI/CD assistant.
Analyze the following Jenkins build log, identify possible causes of failure, and suggest actionable fixes:

{log_input}
"""

    try:
        analysis = query_sagemaker_endpoint(prompt)
        print("\n==== LLM SUGGESTIONS ====\n")
        print(analysis)
        print("\n=========================\n")
    except Exception as e:
        print(f"Error querying SageMaker endpoint: {e}")

if __name__ == "__main__":
    main()
