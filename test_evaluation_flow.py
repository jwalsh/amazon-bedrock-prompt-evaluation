import boto3
import json

def evaluatePrompt(prompt, flowEvalId, flowEvalAliasId, modelInvokeId, modelEvalId):
    bedrock_agent_runtime = boto3.client(service_name='bedrock-agent-runtime', region_name='us-east-1')  # Adjust region as needed
    
    response = bedrock_agent_runtime.invoke_flow(
        flowIdentifier=flowEvalId,
        flowAliasIdentifier=flowEvalAliasId,
        inputs=[
            {
                "content": {
                    "document": prompt
                },
                "nodeName": "Start",
                "nodeOutputName": "document"
            }
        ]
    )
    
    event_stream = response["responseStream"]
    evalResponse = None
    
    for event in event_stream:
        if "flowOutputEvent" in event:
            evalResponse = json.loads(event["flowOutputEvent"]["content"]["document"])
    
    if evalResponse:
        evalResponse["modelInvoke"] = modelInvokeId
        evalResponse["modelEval"] = modelEvalId
        return evalResponse
    
    return None

# Example usage
flowEvalId = "your_flow_eval_id"
flowEvalAliasId = "your_flow_eval_alias_id"
modelInvokeId = "your_model_invoke_id"
modelEvalId = "your_model_eval_id"

result = evaluatePrompt("What is cloud computing in a single paragraph?", flowEvalId, flowEvalAliasId, modelInvokeId, modelEvalId)
print(json.dumps(result, indent=2))
