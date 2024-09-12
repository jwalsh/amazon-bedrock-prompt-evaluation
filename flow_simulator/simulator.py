from .models import FlowDefinition, FlowNode, FlowConnection
import boto3
import json

class FlowSimulator:
    def __init__(self, flow: FlowDefinition):
        self.flow = flow
        self.node_map = {node.name: node for node in flow.nodes}
        self.connection_map = {conn.source: conn for conn in flow.connections}
        self.lambda_client = boto3.client('lambda')
        self.bedrock_runtime = boto3.client('bedrock-runtime')
        self.bedrock_agent = boto3.client('bedrock-agent-runtime')
    
    def simulate(self, input_data: str) -> str:
        current_node = self.node_map["Start"]
        data = input_data
        
        while current_node.type != "Output":
            connection = self.connection_map[current_node.name]
            next_node = self.node_map[connection.target]
            data = self._process_node(next_node, data)
            current_node = next_node
        
        return data
    
    def _process_node(self, node: FlowNode, data: str) -> str:
        if node.type == "LambdaFunction":
            return self._invoke_lambda(node, data)
        elif node.type == "Prompt":
            return self._invoke_prompt(node, data)
        elif node.type == "KnowledgeBase":
            return self._query_knowledge_base(node, data)
        else:
            return data  # Pass-through for other node types
    
    def _invoke_lambda(self, node: FlowNode, data: str) -> str:
        lambda_arn = node.configuration.lambdaArn
        response = self.lambda_client.invoke(
            FunctionName=lambda_arn,
            Payload=json.dumps({"input": data}).encode()
        )
        return json.loads(response['Payload'].read())['output']
    
    def _invoke_prompt(self, node: FlowNode, data: str) -> str:
        prompt_config = node.configuration.prompt
        model_id = prompt_config['sourceConfiguration']['resource'].get('modelId', 'anthropic.claude-v2')
        prompt_text = f"{prompt_config['sourceConfiguration']['resource']['promptArn']}\n\nInput: {data}"
        
        response = self.bedrock_runtime.invoke_model(
            modelId=model_id,
            contentType='application/json',
            accept='application/json',
            body=json.dumps({
                "prompt": prompt_text,
                "max_tokens_to_sample": 500,
                "temperature": 0.7,
                "top_p": 1,
                "top_k": 250,
                "stop_sequences": ["\n\nHuman:"]
            })
        )
        
        return json.loads(response['body'].read())['completion']
    
    def _query_knowledge_base(self, node: FlowNode, data: str) -> str:
        kb_id = node.configuration.knowledgeBaseId
        response = self.bedrock_agent.retrieve(
            knowledgeBaseId=kb_id,
            retrievalQuery=data,
            numberOfResults=5
        )
        return json.dumps(response['retrievalResults'])
