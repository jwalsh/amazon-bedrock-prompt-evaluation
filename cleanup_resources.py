import boto3


def cleanup_resources(flowEvalId, flowEvalAliasId, promptEvalId):
    bedrock_agent = boto3.client("bedrock-agent")
    iam = boto3.client("iam")

    # Delete flow alias
    bedrock_agent.delete_flow_alias(
        flowIdentifier=flowEvalId, aliasIdentifier=flowEvalAliasId
    )
    print(f"Deleted flow alias: {flowEvalAliasId}")

    # Delete flow version
    bedrock_agent.delete_flow_version(flowIdentifier=flowEvalId, flowVersion="1")
    print(f"Deleted flow version 1 for flow: {flowEvalId}")

    # Delete flow
    bedrock_agent.delete_flow(flowIdentifier=flowEvalId)
    print(f"Deleted flow: {flowEvalId}")

    # Delete prompt
    bedrock_agent.delete_prompt(promptIdentifier=promptEvalId)
    print(f"Deleted prompt: {promptEvalId}")

    # Detach role policy
    iam.detach_role_policy(
        RoleName="MyBedrockFlowsRole",
        PolicyArn="arn:aws:iam::aws:policy/AmazonBedrockFullAccess",
    )
    print("Detached AmazonBedrockFullAccess policy from MyBedrockFlowsRole")

    # Delete role
    iam.delete_role(RoleName="MyBedrockFlowsRole")
    print("Deleted MyBedrockFlowsRole")

    print("Cleanup completed successfully.")


# Example usage
# cleanup_resources("your_flow_eval_id", "your_flow_eval_alias_id", "your_prompt_eval_id")
