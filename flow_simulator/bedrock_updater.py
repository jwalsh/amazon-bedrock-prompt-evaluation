import boto3
from .models import FlowDefinition

class BedrockFlowUpdater:
    def __init__(self):
        self.bedrock_agent = boto3.client('bedrock-agent')
    
    def create_or_update_flow(self, flow: FlowDefinition, flow_name: str, role_arn: str):
        try:
            # Try to get the existing flow
            existing_flow = self.bedrock_agent.get_flow(
                flowIdentifier=flow_name
            )
            
            # If the flow exists, update it
            response = self.bedrock_agent.update_flow(
                flowIdentifier=flow_name,
                definition=flow.dict()
            )
            print(f"Flow updated: {response['flowArn']}")
        
        except self.bedrock_agent.exceptions.ResourceNotFoundException:
            # If the flow doesn't exist, create a new one
            response = self.bedrock_agent.create_flow(
                name=flow_name,
                description=f"Flow: {flow_name}",
                executionRoleArn=role_arn,
                definition=flow.dict()
            )
            print(f"Flow created: {response['flowArn']}")
        
        return response['flowArn']
