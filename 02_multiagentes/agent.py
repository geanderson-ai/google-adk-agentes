from dotenv import load_dotenv
import os
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.tools import google_search

load_dotenv()

extracao_entidade = LlmAgent(
    name="extrator_de_entidade",
    model="gemini-2.0-flash",
    description="""
    Você é um assistente de extração de entidade.
    """,
    instruction="""
    A cada requisição do usuário extraia a entidade que o mesmo esta pesquisando.
    """,
    output_key="entidade",
)

pesquisador = LlmAgent(
    name="pesquisador",
    model="gemini-2.0-flash",
    description="""
    Você é um assistente de pesquisa que busca a partir de entidades.
    """,
    instruction="""
    Você é um assistente de pesquisa que busca a partir de {entidade}.
    """,
    tools=[google_search],
    output_key="pesquisa",
) 


sumarizador = LlmAgent(
    name="sumarizador",
    model="gemini-2.0-flash",
    description="""
    Você é um assistente de sumarização.
    """,
    instruction="""
    Você é um assistente de sumarização que resumir a partir de {pesquisa}.
    """,
    output_key="sumario"
) 


root_agent = SequentialAgent(
    name="Pesquisador",
    description="""
    Você é um assistente de pesquisa.
    """,
    sub_agents=[extracao_entidade, pesquisador, sumarizador]
) 
