# host_agent.py
import asyncio
from google.adk import Agent
from a2a_framework import A2AServer, generate_agent_card, AgentSkill

async def run_host_agent():
    AGENT_NAME = "copywriter_host"
    AGENT_DESCRIPTION = "Orquestra o processo completo de copywriting"
    HOST = "0.0.0.0"
    PORT = 10000
    AGENT_URL = f"http://{HOST}:{PORT}"
    
    # URLs dos agentes filhos
    agent_urls = [
        "http://localhost:11000/research_agent",
        "http://localhost:12000/content_agent"
    ]
    
    host_agent = Agent(
        name="copywriter_host",
        model="gemini-2.0-flash",
        description="Coordena pesquisa e criação de copy",
        instructions="""
        Você coordena um processo completo de copywriting:
        
        1. Receba o briefing do cliente (produto, público-alvo, objetivo)
        2. Envie para research_agent: pesquisar o produto/nicho
        3. Aguarde os insights de pesquisa
        4. Envie insights para content_agent: criar o copy
        5. Revise e formate o resultado final
        
        Workflow:
        - Input: briefing do cliente
        - Step 1: research_agent -> insights
        - Step 2: content_agent -> copy final
        - Output: copy completo com justificativas
        """,
        is_host_agent=True,
        remote_agent_addresses=agent_urls
    )
    
    AGENT_SKILLS = [
        AgentSkill(
            id="COPYWRITING_ORCHESTRATION",
            name="orchestrate_copywriting",
            description="Orquestra processo completo de copywriting"
        )
    ]
    
    AGENT_CARD = generate_agent_card(
        agent_name=AGENT_NAME,
        agent_description=AGENT_DESCRIPTION,
        agent_url=AGENT_URL,
        agent_version="1.0.0",
        skills=AGENT_SKILLS
    )
    
    server = A2AServer(
        host=HOST,
        port=PORT,
        endpoint="/copywriter_host",
        agent_card=AGENT_CARD,
        agent=host_agent
    )
    
    print(f"Iniciando Host Agent em {AGENT_URL}")
    await server.astart()

if __name__ == "__main__":
    asyncio.run(run_host_agent())
