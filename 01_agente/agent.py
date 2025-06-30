from dotenv import load_dotenv
import os
from google.adk.agents import LlmAgent
from google.adk.tools import google_search

load_dotenv()



root_agent = LlmAgent(
    name="Pesquisador",
    model="gemini-2.0-flash",
    description="""
    Você é um assistente de pesquisa.
    """,
    instruction="""
    Você é um assistente de pesquisa.
    """,
    tools=[google_search]
) 
