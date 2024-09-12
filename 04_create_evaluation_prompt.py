import boto3
import json
import os

# Load configuration
with open('bedrock_config.json', 'r') as config_file:
    config = json.load(config_file)

region = config['region']
modelEvalId = config['modelEvalId']

bedrock_agent = boto3.client(service_name="bedrock-agent", region_name=region)

def get_existing_prompt(name):
    try:
        response = bedrock_agent.list_prompts()
        for prompt in response.get('promptSummaries', []):
            if prompt['name'] == name:
                return prompt['id'], prompt['arn']
    except Exception as e:
        print(f"Error checking for existing prompt: {str(e)}")
    return None, None

def create_prompt(name):
    with open('03_ai_prompt_answer_evaluator.tmpl', 'r') as file:
        template = file.read()

    try:
        response = bedrock_agent.create_prompt(
            name=name,
            description="Prompt template for evaluating prompt responses with LLM-as-a-judge",
            variants=[
                {
                    "inferenceConfiguration": {
                        "text": {
                            "maxTokens": 2000,
                            "temperature": 0,
                        }
                    },
                    "modelId": modelEvalId,
                    "name": "variantOne",
                    "templateConfiguration": {
                        "text": {
                            "inputVariables": [
                                {"name": "input"},
                                {"name": "output"}
                            ],
                            "text": template
                        }
                    },
                    "templateType": "TEXT"
                }
            ],
            defaultVariant="variantOne"
        )
        return response["id"], response["arn"]
    except Exception as e:
        print(f"Error creating prompt: {str(e)}")
        return None, None

def get_or_create_prompt():
    prompt_name = "prompt-evaluator"
    prompt_id, prompt_arn = get_existing_prompt(prompt_name)

    if prompt_id:
        print(f"A prompt with the name '{prompt_name}' already exists.")
        use_existing = input("Do you want to use the existing prompt? (yes/no): ").lower()
        if use_existing == 'yes':
            return prompt_id, prompt_arn
        else:
            new_name = input("Enter a new name for the prompt: ")
            prompt_name = new_name if new_name else f"{prompt_name}-new"
            return create_prompt(prompt_name)
    else:
        print(f"Creating new prompt '{prompt_name}'...")
        return create_prompt(prompt_name)

prompt_id, prompt_arn = get_or_create_prompt()

if prompt_id and prompt_arn:
    print(f"Prompt ID: {prompt_id}")
    print(f"Prompt ARN: {prompt_arn}")
    # Save prompt details for later use
    with open('prompt_details.json', 'w') as f:
        json.dump({
            "promptEvalId": prompt_id,
            "promptEvalArn": prompt_arn
        }, f)
    print("Prompt details saved to 'prompt_details.json'")
else:
    print("Failed to get or create prompt.")
