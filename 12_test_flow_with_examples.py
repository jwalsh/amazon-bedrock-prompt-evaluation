import boto3
import json
import time
from botocore.exceptions import ClientError

# Assuming you're using the same region as before
region = "us-east-1"
bedrock_agent_runtime = boto3.client(
    service_name="bedrock-agent-runtime", region_name=region
)

# Read flow details
with open("flow_details.json", "r") as f:
    flow_details = json.load(f)

flow_id = flow_details["flowId"]
flow_alias_id = flow_details.get("flowAliasId")  # Use the alias if available


def invoke_flow(input_text, timeout=300):  # 5 minutes timeout
    try:
        response = bedrock_agent_runtime.invoke_flow(
            flowIdentifier=flow_id,
            flowAliasIdentifier=flow_alias_id,
            inputs=[
                {
                    "content": {"document": input_text},
                    "nodeName": "Start",
                    "nodeOutputName": "document",
                }
            ],
        )

        event_stream = response["responseStream"]
        result = ""
        start_time = time.time()
        for event in event_stream:
            if time.time() - start_time > timeout:
                print(f"Flow invocation timed out after {timeout} seconds.")
                return None
            if "flowOutputEvent" in event:
                result += event["flowOutputEvent"]["content"]["document"]

        return json.loads(result)
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        error_message = e.response["Error"]["Message"]
        print(f"AWS Error: {error_code} - {error_message}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        return None


def read_prompt(file_path):
    with open(file_path, "r") as file:
        return file.read().strip()


# Test the flow with good and bad prompts
good_prompt = read_prompt("prompts/evaluation_good_prompt.tmpl")
bad_prompt = read_prompt("prompts/evaluation_bad_prompt.tmpl")

for prompt_type, prompt in [("Good", good_prompt), ("Bad", bad_prompt)]:
    print(f"\nTesting {prompt_type} Prompt:")
    print("-" * 40)
    print(f"Prompt: {prompt[:100]}...")  # Print first 100 characters of the prompt
    print("Invoking flow... This may take a few minutes.")
    result = invoke_flow(prompt)

    if result:
        print("\nFlow invocation result:")
        print(f"Prompt Score: {result.get('prompt-score', 'N/A')}")
        print(f"Answer Score: {result.get('answer-score', 'N/A')}")
        print(
            f"\nJustification: {result.get('justification', 'N/A')[:200]}..."
        )  # Print first 200 characters
        print(
            f"\nPrompt Recommendations: {result.get('prompt-recommendations', 'N/A')[:200]}..."
        )  # Print first 200 characters
    else:
        print("Failed to get a result from the flow.")

    print("\n" + "=" * 50 + "\n")
