#!/usr/bin/env python3

"""
Generative AI Advisor CLI with Project Assessment

This script provides a command-line interface for getting advice on AI projects
from different C-suite perspectives, decomposes the chosen project, assesses its feasibility,
and coordinates project implementation across teams.
"""

import json
from typing import List, Dict
from itertools import cycle

import click
from pydantic import BaseModel, Field
import boto3
from langchain.chains import MultiPromptChain, LLMChain
from langchain_community.llms import Bedrock
from langchain.prompts import PromptTemplate

class PromptInfo(BaseModel):
    """
    Represents information about a specific prompt.
    """
    name: str
    description: str
    prompt_template: str

class AdvisorConfig(BaseModel):
    """
    Configuration for the Generative AI Advisor.
    """
    model_id: str = Field(default="anthropic.claude-instant-v1")
    prompt_infos: List[PromptInfo] = Field(default_factory=list)

    class Config:
        protected_namespaces = ()

def create_prompt_infos() -> List[PromptInfo]:
    """
    Create a list of PromptInfo objects with predefined C-suite roles.
    
    Returns:
        List[PromptInfo]: A list of PromptInfo objects.
    """
    prompts = [
        PromptInfo(
            name="CTO",
            description="Good for overseeing technological needs and operations, including developing technology strategy, managing IT systems and infrastructure, and directing technology initiatives.",
            prompt_template="""You're the CTO, CIO, and CDO of the company. You oversee all the technological, data needs and operations, including developing technology strategy, managing IT systems and infrastructure, and directing technology initiatives.
Your job is keeping the company technologically updated in an efficient way.
Human: {input}"""
        ),
        PromptInfo(
            name="CFO",
            description="Good for overseeing all financial activities, including financial planning, cash flow management, accounting, reporting, and risk management.",
            prompt_template="""You're the Chief Financial Officer (CFO) of the company. You oversee all financial activities, including financial planning, cash flow management, accounting, reporting, and risk management.
Your job is keeping the company financially profitable while ensuring growth.
Human: {input}"""
        ),
        PromptInfo(
            name="COO",
            description="Good for overseeing day-to-day business operations and corporate strategy implementation.",
            prompt_template="""You're the Chief Operating Officer (COO) of the company. You oversee the day-to-day business operations and corporate strategy implementation.
Your job is ensuring the company operates efficiently and effectively by having a good strategy and culture.
Human: {input}"""
        )
    ]
    return prompts

def create_multi_prompt_chain(config: AdvisorConfig) -> MultiPromptChain:
    """
    Create a MultiPromptChain using the provided configuration.
    
    Args:
        config (AdvisorConfig): The configuration for the advisor.
    
    Returns:
        MultiPromptChain: A configured MultiPromptChain object.
    """
    llm = Bedrock(model_id=config.model_id)
    return MultiPromptChain.from_prompts(
        llm,
        prompt_infos=[prompt_info.dict() for prompt_info in config.prompt_infos],
        verbose=True
    )

def decompose_project(project: str, model_id: str) -> str:
    """
    Decompose the chosen project into smaller, manageable tasks.
    
    Args:
        project (str): The chosen project to decompose.
        model_id (str): The model ID to use for the LLM.
    
    Returns:
        str: A detailed breakdown of the project into smaller tasks.
    """
    llm = Bedrock(model_id=model_id)
    
    decomposer_template = """
    You are a project decomposition specialist. Your task is to break down the following AI project into smaller, manageable tasks:

    Project: {project}

    Please provide a detailed breakdown of this project into:
    1. Main phases
    2. Specific tasks within each phase
    3. Estimated time for each task
    4. Dependencies between tasks

    Your decomposition:
    """
    
    decomposer_prompt = PromptTemplate(
        input_variables=["project"],
        template=decomposer_template
    )
    
    decomposer_chain = LLMChain(llm=llm, prompt=decomposer_prompt)
    return decomposer_chain.run(project=project)

def assess_project(project: str, decomposition: str, model_id: str) -> str:
    """
    Assess the feasibility and potential challenges of the project.
    
    Args:
        project (str): The chosen project to assess.
        decomposition (str): The project decomposition.
        model_id (str): The model ID to use for the LLM.
    
    Returns:
        str: An assessment of the project's feasibility and potential challenges.
    """
    llm = Bedrock(model_id=model_id)
    
    assessor_template = """
    You are a project assessment specialist. Your task is to evaluate the feasibility and potential challenges of the following AI project:

    Project: {project}

    Project Decomposition:
    {decomposition}

    Please provide an assessment that includes:
    1. Overall feasibility of the project
    2. Potential technical challenges
    3. Resource requirements (personnel, technology, time)
    4. Risks and mitigation strategies
    5. Recommendations for successful implementation

    Your assessment:
    """
    
    assessor_prompt = PromptTemplate(
        input_variables=["project", "decomposition"],
        template=assessor_template
    )
    
    assessor_chain = LLMChain(llm=llm, prompt=assessor_prompt)
    return assessor_chain.run(project=project, decomposition=decomposition)

def coordinate_project(project: str, decomposition: str, assessment: str, model_id: str):
    """
    Coordinate the project implementation across different teams.
    
    Args:
        project (str): The chosen project to implement.
        decomposition (str): The project decomposition.
        assessment (str): The project assessment.
        model_id (str): The model ID to use for the LLM.
    """
    llm = Bedrock(model_id=model_id)
    
    teams = [
        "backend-developer",
        "code-architect",
        "database-specialist",
        "devops-engineer",
        "frontend-developer",
        "project-manager",
        "qa-tester",
        "security-specialist",
        "technical-writer"
    ]
    
    coordinator_template = """
    You are the project coordinator for an AI implementation project. The chosen project is: {project}

    Project Decomposition:
    {decomposition}

    Project Assessment:
    {assessment}

    You need to provide specific tasks and guidelines for the {team} team.

    Please outline the key responsibilities, tasks, and considerations for the {team} team in implementing this AI project.
    Be specific and provide actionable items, considering the project decomposition and assessment.

    {team} team tasks and guidelines:
    """
    
    coordinator_prompt = PromptTemplate(
        input_variables=["project", "decomposition", "assessment", "team"],
        template=coordinator_template
    )
    
    coordinator_chain = LLMChain(llm=llm, prompt=coordinator_prompt)
    
    click.echo("\nProject Coordination Plan:")
    for team in teams:
        result = coordinator_chain.run(project=project, decomposition=decomposition, assessment=assessment, team=team)
        click.echo(f"\n{team.upper()}:")
        click.echo(result.strip())

@click.command()
@click.option('--question', default="What are some good initial projects for getting started with AI?", 
              prompt='Enter your question about AI projects', help='The question to ask the advisors')
@click.option('--model', default="anthropic.claude-instant-v1", help='The model ID to use for the LLM')
def main(question: str, model: str):
    """
    Run the Generative AI Advisor CLI with Project Assessment and Team Coordination.
    
    This CLI tool provides advice on AI projects from different C-suite perspectives,
    decomposes the chosen project, assesses its feasibility, and coordinates project 
    implementation across teams.
    """
    config = AdvisorConfig(model_id=model, prompt_infos=create_prompt_infos())
    mpc = create_multi_prompt_chain(config)
    
    result = mpc.run(input=question)
    click.echo(result)
    
    projects = result.split('\n')
    projects = [p.strip() for p in projects if p.strip()]
    
    click.echo("\nSuggested projects:")
    for i, project in enumerate(projects, 1):
        click.echo(f"{i}. {project}")
    
    project_choice = click.prompt("Choose a project number to implement", type=int, default=1)
    chosen_project = projects[project_choice - 1]
    
    click.echo(f"\nYou've chosen to implement: {chosen_project}")
    
    click.echo("\nDecomposing the project...")
    decomposition = decompose_project(chosen_project, model)
    click.echo(decomposition)
    
    click.echo("\nAssessing the project...")
    assessment = assess_project(chosen_project, decomposition, model)
    click.echo(assessment)
    
    coordinate_project(chosen_project, decomposition, assessment, model)

if __name__ == '__main__':
    main()
