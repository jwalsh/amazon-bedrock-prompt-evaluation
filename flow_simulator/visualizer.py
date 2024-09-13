from .models import FlowDefinition


def generate_mermaid(flow: FlowDefinition) -> str:
    mermaid_code = ["graph TD"]

    for node in flow.nodes:
        mermaid_code.append(f"    {node.name}[{node.name} <br> Type: {node.type}]")

    for conn in flow.connections:
        mermaid_code.append(f"    {conn.source} --> |{conn.name}| {conn.target}")

    return "\n".join(mermaid_code)
