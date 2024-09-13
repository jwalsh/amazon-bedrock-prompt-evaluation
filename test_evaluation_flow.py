import pytest
from unittest.mock import MagicMock
import boto3
import json

@pytest.fixture
def mock_bedrock_agent_runtime():
    with pytest.MonkeyPatch.context() as mp:
        mock_client = MagicMock()
        mp.setattr(boto3, "client", lambda service_name, region_name: mock_client)
        yield mock_client

def test_evaluate_prompt(mock_bedrock_agent_runtime):
    mock_bedrock_agent_runtime.invoke_flow.return_value = {
        "responseStream": [
            {
                "flowOutputEvent": {
                    "content": {
                        "document": json.dumps({"result": "Mocked response"})
                    }
                }
            }
        ]
    }

    result = evaluatePrompt("What is cloud computing in a single paragraph?", "mock_flow_id", "mock_alias_id", "mock_model_invoke_id", "mock_model_eval_id")
    
    assert result == {"result": "Mocked response", "modelInvoke": "mock_model_invoke_id", "modelEval": "mock_model_eval_id"}

def evaluatePrompt(prompt, flowEvalId, flowEvalAliasId, modelInvokeId, modelEvalId):
    bedrock_agent_runtime = boto3.client(service_name='bedrock-agent-runtime', region_name='us-east-1')
    
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

