from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class FlowNodeInput(BaseModel):
    name: str
    type: str
    expression: str = Field(default="$.data")

class FlowNodeOutput(BaseModel):
    name: str
    type: str

class FlowNodeConfiguration(BaseModel):
    pass

class FlowNode(BaseModel):
    name: str
    type: str
    inputs: List[FlowNodeInput] = []
    outputs: List[FlowNodeOutput] = []
    configuration: FlowNodeConfiguration

class FlowDataConnectionConfiguration(BaseModel):
    sourceOutput: str
    targetInput: str

class FlowConnection(BaseModel):
    name: str
    source: str
    target: str
    type: str = "Data"
    configuration: Dict[str, FlowDataConnectionConfiguration]

class FlowDefinition(BaseModel):
    nodes: List[FlowNode]
    connections: List[FlowConnection]

class LambdaFunctionFlowNodeConfiguration(FlowNodeConfiguration):
    lambdaArn: str

class PromptFlowNodeConfiguration(FlowNodeConfiguration):
    prompt: Dict[str, Any]

class KnowledgeBaseFlowNodeConfiguration(FlowNodeConfiguration):
    knowledgeBaseId: str

def create_identity_flow() -> FlowDefinition:
    input_node = FlowNode(
        name="Start",
        type="Input",
        outputs=[FlowNodeOutput(name="document", type="String")],
        configuration=FlowNodeConfiguration()
    )
    
    output_node = FlowNode(
        name="End",
        type="Output",
        inputs=[FlowNodeInput(name="document", type="String")],
        configuration=FlowNodeConfiguration()
    )
    
    connection = FlowConnection(
        name="StartToEnd",
        source="Start",
        target="End",
        configuration={
            "data": FlowDataConnectionConfiguration(
                sourceOutput="document",
                targetInput="document"
            )
        }
    )
    
    return FlowDefinition(nodes=[input_node, output_node], connections=[connection])

def create_upcase_flow(lambda_arn: str) -> FlowDefinition:
    input_node = FlowNode(
        name="Start",
        type="Input",
        outputs=[FlowNodeOutput(name="document", type="String")],
        configuration=FlowNodeConfiguration()
    )
    
    upcase_node = FlowNode(
        name="Upcase",
        type="LambdaFunction",
        inputs=[FlowNodeInput(name="input", type="String")],
        outputs=[FlowNodeOutput(name="functionResponse", type="String")],
        configuration=LambdaFunctionFlowNodeConfiguration(lambdaArn=lambda_arn)
    )
    
    output_node = FlowNode(
        name="End",
        type="Output",
        inputs=[FlowNodeInput(name="document", type="String")],
        configuration=FlowNodeConfiguration()
    )
    
    connections = [
        FlowConnection(
            name="StartToUpcase",
            source="Start",
            target="Upcase",
            configuration={
                "data": FlowDataConnectionConfiguration(
                    sourceOutput="document",
                    targetInput="input"
                )
            }
        ),
        FlowConnection(
            name="UpcaseToEnd",
            source="Upcase",
            target="End",
            configuration={
                "data": FlowDataConnectionConfiguration(
                    sourceOutput="functionResponse",
                    targetInput="document"
                )
            }
        )
    ]
    
    return FlowDefinition(nodes=[input_node, upcase_node, output_node], connections=connections)

def create_knowledge_base_flow(knowledge_base_id: str, prompt_arn: str) -> FlowDefinition:
    input_node = FlowNode(
        name="Start",
        type="Input",
        outputs=[FlowNodeOutput(name="document", type="String")],
        configuration=FlowNodeConfiguration()
    )
    
    kb_node = FlowNode(
        name="QueryKnowledgeBase",
        type="KnowledgeBase",
        inputs=[FlowNodeInput(name="retrievalQuery", type="String")],
        outputs=[FlowNodeOutput(name="retrievalResults", type="Array")],
        configuration=KnowledgeBaseFlowNodeConfiguration(knowledgeBaseId=knowledge_base_id)
    )
    
    prompt_node = FlowNode(
        name="GenerateResponse",
        type="Prompt",
        inputs=[
            FlowNodeInput(name="query", type="String"),
            FlowNodeInput(name="context", type="Array")
        ],
        outputs=[FlowNodeOutput(name="modelCompletion", type="String")],
        configuration=PromptFlowNodeConfiguration(
            prompt={
                "sourceConfiguration": {
                    "resource": {
                        "promptArn": prompt_arn
                    }
                }
            }
        )
    )
    
    output_node = FlowNode(
        name="End",
        type="Output",
        inputs=[FlowNodeInput(name="document", type="String")],
        configuration=FlowNodeConfiguration()
    )
    
    connections = [
        FlowConnection(
            name="StartToKB",
            source="Start",
            target="QueryKnowledgeBase",
            configuration={
                "data": FlowDataConnectionConfiguration(
                    sourceOutput="document",
                    targetInput="retrievalQuery"
                )
            }
        ),
        FlowConnection(
            name="StartToPrompt",
            source="Start",
            target="GenerateResponse",
            configuration={
                "data": FlowDataConnectionConfiguration(
                    sourceOutput="document",
                    targetInput="query"
                )
            }
        ),
        FlowConnection(
            name="KBToPrompt",
            source="QueryKnowledgeBase",
            target="GenerateResponse",
            configuration={
                "data": FlowDataConnectionConfiguration(
                    sourceOutput="retrievalResults",
                    targetInput="context"
                )
            }
        ),
        FlowConnection(
            name="PromptToEnd",
            source="GenerateResponse",
            target="End",
            configuration={
                "data": FlowDataConnectionConfiguration(
                    sourceOutput="modelCompletion",
                    targetInput="document"
                )
            }
        )
    ]
    
    return FlowDefinition(nodes=[input_node, kb_node, prompt_node, output_node], connections=connections)
