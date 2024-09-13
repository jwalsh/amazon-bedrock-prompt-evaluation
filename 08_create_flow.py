import boto3
import json
import os
from botocore.exceptions import ClientError

# Load configuration
with open("bedrock_config.json", "r") as config_file:
    config = json.load(config_file)

region = config["region"]
modelInvokeId = config["modelInvokeId"]

bedrock_agent = boto3.client(service_name="bedrock-agent", region_name=region)

# Load role and prompt details
with open("role_details.json", "r") as f:
    role_details = json.load(f)
role_arn = role_details["roleArn"]

with open("prompt_details.json", "r") as f:
    prompt_details = json.load(f)
promptEvalArn = prompt_details["promptEvalArn"]


def get_existing_flow(name):
    try:
        response = bedrock_agent.list_flows()
        for flow in response.get("flowSummaries", []):
            if flow["name"] == name:
                return flow["id"], flow["arn"]
    except Exception as e:
        print(f"Error checking for existing flow: {str(e)}")
    return None, None


def create_or_update_flow(name, description, role_arn, prompt_arn):
    flow_id, flow_arn = get_existing_flow(name)

    flow_definition = {
        "nodes": [
            {
                "name": "Start",
                "type": "Input",
                "configuration": {"input": {}},
                "outputs": [{"name": "document", "type": "String"}],
            },
            {
                "name": "End",
                "type": "Output",
                "configuration": {"output": {}},
                "inputs": [
                    {"expression": "$.data", "name": "document", "type": "String"}
                ],
            },
            {
                "name": "Invoke",
                "type": "Prompt",
                "configuration": {
                    "prompt": {
                        "sourceConfiguration": {
                            "inline": {
                                "inferenceConfiguration": {
                                    "text": {"maxTokens": 2000, "temperature": 0}
                                },
                                "modelId": modelInvokeId,
                                "templateConfiguration": {
                                    "text": {
                                        "inputVariables": [{"name": "input"}],
                                        "text": "{{input}}",
                                    }
                                },
                                "templateType": "TEXT",
                            }
                        }
                    }
                },
                "inputs": [{"expression": "$.data", "name": "input", "type": "String"}],
                "outputs": [{"name": "modelCompletion", "type": "String"}],
            },
            {
                "name": "Evaluate",
                "type": "Prompt",
                "configuration": {
                    "prompt": {
                        "sourceConfiguration": {"resource": {"promptArn": prompt_arn}}
                    }
                },
                "inputs": [
                    {"expression": "$.data", "name": "input", "type": "String"},
                    {"expression": "$.data", "name": "output", "type": "String"},
                ],
                "outputs": [{"name": "modelCompletion", "type": "String"}],
            },
        ],
        "connections": [
            {
                "name": "StartToInvoke",
                "source": "Start",
                "target": "Invoke",
                "type": "Data",
                "configuration": {
                    "data": {"sourceOutput": "document", "targetInput": "input"}
                },
            },
            {
                "name": "InvokeToEvaluate",
                "source": "Invoke",
                "target": "Evaluate",
                "type": "Data",
                "configuration": {
                    "data": {"sourceOutput": "modelCompletion", "targetInput": "output"}
                },
            },
            {
                "name": "StartToEvaluate",
                "source": "Start",
                "target": "Evaluate",
                "type": "Data",
                "configuration": {
                    "data": {"sourceOutput": "document", "targetInput": "input"}
                },
            },
            {
                "name": "EvaluateToEnd",
                "source": "Evaluate",
                "target": "End",
                "type": "Data",
                "configuration": {
                    "data": {
                        "sourceOutput": "modelCompletion",
                        "targetInput": "document",
                    }
                },
            },
        ],
    }

    try:
        if flow_id:
            print(f"Updating existing flow '{name}'...")
            response = bedrock_agent.update_flow(
                flowIdentifier=flow_id,
                description=description,
                executionRoleArn=role_arn,
                definition=flow_definition,
            )
        else:
            print(f"Creating new flow '{name}'...")
            response = bedrock_agent.create_flow(
                name=name,
                description=description,
                executionRoleArn=role_arn,
                definition=flow_definition,
            )
        return response["id"], response["arn"]
    except ClientError as e:
        print(f"Error creating/updating flow: {e}")
        return None, None


# Create or update the flow
flow_name = "prompt-eval-flow"
flow_description = "Prompt Flow for evaluating prompts with LLM-as-a-judge."

flow_id, flow_arn = create_or_update_flow(
    flow_name, flow_description, role_arn, promptEvalArn
)

if flow_id and flow_arn:
    print(f"Flow ID: {flow_id}")
    print(f"Flow ARN: {flow_arn}")
    # Save flow details for later use
    with open("flow_details.json", "w") as f:
        json.dump({"flowId": flow_id, "flowArn": flow_arn, "flowName": flow_name}, f)
    print("Flow details saved to 'flow_details.json'")
else:
    print("Failed to create or update flow.")
