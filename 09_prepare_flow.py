import boto3
import json
import time

# Assuming you're using the same region as before
region = "us-east-1"
bedrock_agent = boto3.client(service_name="bedrock-agent", region_name=region)

# Read flow details
with open('flow_details.json', 'r') as f:
    flow_details = json.load(f)

flow_id = flow_details['flowId']

try:
    response = bedrock_agent.prepare_flow(
        flowIdentifier=flow_id
    )
    print("Flow preparation started:")
    print(json.dumps(response, indent=2, default=str))
except Exception as e:
    print(f"An error occurred while preparing the flow: {str(e)}")

# Poll the flow status until it's prepared
max_attempts = 30
attempts = 0
while attempts < max_attempts:
    try:
        response = bedrock_agent.get_flow(
            flowIdentifier=flow_id
        )
        status = response['status']
        print(f"Current flow status: {status}")
        if status == 'Prepared':
            print("Flow is prepared and ready to use!")
            break
        elif status == 'Failed':
            print("Flow preparation failed. Check the AWS console for more details.")
            break
    except Exception as e:
        print(f"An error occurred while checking flow status: {str(e)}")
        break
    
    time.sleep(10)  # Wait for 10 seconds before checking again
    attempts += 1

if attempts == max_attempts:
    print("Flow preparation timed out. Please check the AWS console for more information.")
