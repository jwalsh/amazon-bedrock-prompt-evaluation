from .models import create_identity_flow, create_upcase_flow, create_knowledge_base_flow
from .simulator import FlowSimulator
from .utils import save_flow_to_json, load_flow_from_json
from .visualizer import generate_mermaid
from .bedrock_updater import BedrockFlowUpdater

def main():
    # Example 1: Identity Flow
    identity_flow = create_identity_flow()
    save_flow_to_json(identity_flow, "identity_flow.json")
    
    print("Identity Flow:")
    print(generate_mermaid(identity_flow))
    
    identity_simulator = FlowSimulator(identity_flow)
    identity_result = identity_simulator.simulate("Hello, Bedrock!")
    print(f"Identity Flow Result: {identity_result}")
    
    # Example 2: Upcase Flow
    lambda_arn = "arn:aws:lambda:us-west-2:123456789012:function:UpcaseFunction"
    upcase_flow = create_upcase_flow(lambda_arn)
    save_flow_to_json(upcase_flow, "upcase_flow.json")
    
    print("\nUpcase Flow:")
    print(generate_mermaid(upcase_flow))
    
    upcase_simulator = FlowSimulator(upcase_flow)
    upcase_result = upcase_simulator.simulate("Hello, Bedrock!")
    print(f"Upcase Flow Result: {upcase_result}")
    
    # Example 3: Knowledge Base Flow
    knowledge_base_id = "arn:aws:bedrock:us-west-2:123456789012:knowledge-base/MyKnowledgeBase"
    prompt_arn = "arn:aws:bedrock:us-west-2:123456789012:prompt/MyResponsePrompt"
    kb_flow = create_knowledge_base_flow(knowledge_base_id, prompt_arn)
    save_flow_to_json(kb_flow, "knowledge_base_flow.json")
    
    print("\nKnowledge Base Flow:")
    print(generate_mermaid(kb_flow))
    
    kb_simulator = FlowSimulator(kb_flow)
    kb_result = kb_simulator.simulate("What is Amazon Bedrock?")
    print(f"Knowledge Base Flow Result: {kb_result}")
    
    # Update flows in Bedrock
    updater = BedrockFlowUpdater()
    role_arn = "arn:aws:iam::123456789012:role/BedrockFlowRole"
    
    identity_flow_arn = updater.create_or_update_flow(identity_flow, "IdentityFlow", role_arn)
    upcase_flow_arn = updater.create_or_update_flow(upcase_flow, "UpcaseFlow", role_arn)
    kb_flow_arn = updater.create_or_update_flow(kb_flow, "KnowledgeBaseFlow", role_arn)
    
    print("\nUpdated Flow ARNs:")
    print(f"Identity Flow ARN: {identity_flow_arn}")
    print(f"Upcase Flow ARN: {upcase_flow_arn}")
    print(f"Knowledge Base Flow ARN: {kb_flow_arn}")

if __name__ == "__main__":
    main()
