import boto3
import json

region = "us-east-1"
bedrock_agent = boto3.client(service_name="bedrock-agent", region_name=region)

# Read flow details
with open('flow_details.json', 'r') as f:
    flow_details = json.load(f)

flow_id = flow_details['flowId']
flow_name = flow_details['flowName']
flow_version = flow_details.get('flowVersion', '1')  # Default to '1' if not set

try:
    response = bedrock_agent.create_flow_alias(
        flowIdentifier=flow_id,
        name=flow_name,
        description=f"Alias for {flow_name}",
        routingConfiguration=[
            {
                "flowVersion": flow_version
            }
        ]
    )
    print("Flow alias created:")
    print(json.dumps(response, indent=2, default=str))
    
    # Update flow details with the alias information
    flow_details['flowAliasId'] = response['id']
    flow_details['flowAliasArn'] = response['arn']
    with open('flow_details.json', 'w') as f:
        json.dump(flow_details, f, indent=2)
    print("Flow details updated with alias information.")
except Exception as e:
    print(f"An error occurred while creating the flow alias: {str(e)}")
