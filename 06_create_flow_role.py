import boto3
import json

# Create IAM client
iam = boto3.client('iam')

# Define the role name
role_name = 'AmazonBedrockExecutionRoleForAgentFlowEval'

# Define the trust relationship policy
trust_relationship = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "bedrock.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}

# Define the role policy
role_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel"
            ],
            "Resource": "*"
        }
    ]
}

def get_or_create_role():
    try:
        # Try to get the role
        existing_role = iam.get_role(RoleName=role_name)
        print(f"The role '{role_name}' already exists.")
        use_existing = input("Do you want to use the existing role? (yes/no): ").lower()
        if use_existing == 'yes':
            return existing_role['Role']['Arn']
        else:
            # Delete the existing role and recreate
            iam.delete_role(RoleName=role_name)
            print(f"Deleted existing role '{role_name}'.")
    except iam.exceptions.NoSuchEntityException:
        pass  # Role doesn't exist, we'll create it

    try:
        # Create the IAM role
        create_role_response = iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_relationship),
            Description='Execution role for Amazon Bedrock Agent Flow'
        )
        print("Role created successfully.")

        # Attach the inline policy to the role
        iam.put_role_policy(
            RoleName=role_name,
            PolicyName='BedrockInvokeModelPolicy',
            PolicyDocument=json.dumps(role_policy)
        )
        print("Policy attached successfully")

        return create_role_response['Role']['Arn']
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

# Get or create the role
role_arn = get_or_create_role()

if role_arn:
    print(f"Role ARN: {role_arn}")
    # Save role details for later use
    with open('role_details.json', 'w') as f:
        json.dump({
            "roleName": role_name,
            "roleArn": role_arn
        }, f)
    print("Role details saved to 'role_details.json'")
else:
    print("Failed to get or create the role.")
