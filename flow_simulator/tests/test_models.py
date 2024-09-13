import pytest
from flow_simulator.models import (
    create_identity_flow,
    create_upcase_flow,
    create_knowledge_base_flow,
)


def test_create_identity_flow():
    flow = create_identity_flow()
    assert len(flow.nodes) == 2
    assert len(flow.connections) == 1


def test_create_upcase_flow():
    lambda_arn = "arn:aws:lambda:us-west-2:123456789012:function:UpcaseFunction"
    flow = create_upcase_flow(lambda_arn)
    assert len(flow.nodes) == 3
    assert len(flow.connections) == 2


def test_create_knowledge_base_flow():
    knowledge_base_id = (
        "arn:aws:bedrock:us-west-2:123456789012:knowledge-base/MyKnowledgeBase"
    )
    prompt_arn = "arn:aws:bedrock:us-west-2:123456789012:prompt/MyResponsePrompt"
    flow = create_knowledge_base_flow(knowledge_base_id, prompt_arn)
    assert len(flow.nodes) == 4
    assert len(flow.connections) == 4
