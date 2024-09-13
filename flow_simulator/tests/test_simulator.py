import pytest
from unittest.mock import MagicMock
from flow_simulator.simulator import FlowSimulator
from flow_simulator.models import (
    create_identity_flow,
    create_upcase_flow,
    create_knowledge_base_flow,
)


def test_flow_simulator_identity():
    flow = create_identity_flow()
    simulator = FlowSimulator(flow)

    # Mock the AWS clients
    simulator.lambda_client = MagicMock()
    simulator.bedrock_runtime = MagicMock()
    simulator.bedrock_agent = MagicMock()

    result = simulator.simulate("Test input")
    assert result == "Test input"


def test_flow_simulator_upcase():
    lambda_arn = "arn:aws:lambda:us-west-2:123456789012:function:UpcaseFunction"
    flow = create_upcase_flow(lambda_arn)
    simulator = FlowSimulator(flow)

    # Mock the AWS clients
    simulator.lambda_client = MagicMock()
    simulator.lambda_client.invoke.return_value = {
        "Payload": MagicMock(read=lambda: '{"output": "TEST INPUT"}')
    }
    simulator.bedrock_runtime = MagicMock()
    simulator.bedrock_agent = MagicMock()

    result = simulator.simulate("Test input")
    assert result == "TEST INPUT"


def test_flow_simulator_knowledge_base():
    knowledge_base_id = (
        "arn:aws:bedrock:us-west-2:123456789012:knowledge-base/MyKnowledgeBase"
    )
    prompt_arn = "arn:aws:bedrock:us-west-2:123456789012:prompt/MyResponsePrompt"
    flow = create_knowledge_base_flow(knowledge_base_id, prompt_arn)
    simulator = FlowSimulator(flow)

    # Mock the AWS clients
    simulator.lambda_client = MagicMock()
    simulator.bedrock_runtime = MagicMock()
    simulator.bedrock_runtime.invoke_model.return_value = {
        "body": MagicMock(read=lambda: '{"completion": "Mocked response"}')
    }
    simulator.bedrock_agent = MagicMock()
    simulator.bedrock_agent.retrieve.return_value = {
        "retrievalResults": [{"content": "Mocked KB result"}]
    }

    result = simulator.simulate("Test question")
    assert result == "Mocked response"
