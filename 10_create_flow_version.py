import boto3
import json

region = "us-east-1"
bedrock_agent = boto3.client(service_name="bedrock-agent", region_name=region)

# Read flow details
with open('flow_details.json', 'r') as f:
    flow_details = json.load(f)

flow_id = flow_details['flowId']

try:
    response = bedrock_agent.create_flow_version(
        flowIdentifier=flow_id
    )
    print("Flow version created:")
    print(json.dumps(response, indent=2, default=str))
    
    # Update flow details with the new version
    flow_details['flowVersion'] = response['version']
    with open('flow_details.json', 'w') as f:
        json.dump(flow_details, f, indent=2)
    print("Flow details updated with new version.")
except Exception as e:
    print(f"An error occurred while creating the flow version: {str(e)}")
