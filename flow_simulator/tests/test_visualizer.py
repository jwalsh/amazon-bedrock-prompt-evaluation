import pytest
from flow_simulator.visualizer import generate_mermaid
from flow_simulator.models import (
    create_identity_flow,
    create_upcase_flow,
    create_knowledge_base_flow,
)


def test_generate_mermaid_identity():
    flow = create_identity_flow()
    mermaid_code = generate_mermaid(flow)
    assert "graph TD" in mermaid_code
    assert "Start" in mermaid_code
    assert "End" in mermaid_code
    assert "Start --> |StartToEnd| End" in mermaid_code


def test_generate_mermaid_upcase():
    lambda_arn = "arn:aws:lambda:us-west-2:123456789012:function:UpcaseFunction"
    flow = create_upcase_flow(lambda_arn)
    mermaid_code = generate_mermaid(flow)
    assert "graph TD" in mermaid_code
    assert "Start" in mermaid_code
    assert "Upcase" in mermaid_code
    assert "End" in mermaid_code
    assert "Start --> |StartToUpcase| Upcase" in mermaid_code
    assert "Upcase --> |UpcaseToEnd| End" in mermaid_code


def test_generate_mermaid_knowledge_base():
    knowledge_base_id = (
        "arn:aws:bedrock:us-west-2:123456789012:knowledge-base/MyKnowledgeBase"
    )
    prompt_arn = "arn:aws:bedrock:us-west-2:123456789012:prompt/MyResponsePrompt"
    flow = create_knowledge_base_flow(knowledge_base_id, prompt_arn)
    mermaid_code = generate_mermaid(flow)
    assert "graph TD" in mermaid_code
    assert "Start" in mermaid_code
    assert "QueryKnowledgeBase" in mermaid_code
    assert "GenerateResponse" in mermaid_code
    assert "End" in mermaid_code
    assert "Start --> |StartToKB| QueryKnowledgeBase" in mermaid_code
    assert "Start --> |StartToPrompt| GenerateResponse" in mermaid_code
    assert "QueryKnowledgeBase --> |KBToPrompt| GenerateResponse" in mermaid_code
    assert "GenerateResponse --> |PromptToEnd| End" in mermaid_code
