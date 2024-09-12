import json
from .models import FlowDefinition

def save_flow_to_json(flow: FlowDefinition, filename: str):
    with open(filename, 'w') as f:
        json.dump(flow.dict(), f, indent=2)

def load_flow_from_json(filename: str) -> FlowDefinition:
    with open(filename, 'r') as f:
        data = json.load(f)
    return FlowDefinition(**data)
