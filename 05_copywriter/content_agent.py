# content_agent.py
import asyncio
from google.adk import Agent
from a2a_framework import A2AServer, generate_agent_card, AgentSkill

async def run_content_agent():
    AGENT_NAME = "content_agent"
    AGENT_DESCRIPTION = "Agente especializado em criação de copy persuasivo"
    HOST = "0.0.0.0"
    PORT = 12000
    AGENT_URL = f"http://{HOST}:{PORT}"
    
    content_agent = Agent(
        name="content_agent",
        model="gemini-2.0-flash",
        description="Copywriter especialista em conversão",
        instructions="""
        Você é um copywriter expert em conversão. Sua função é:
        
        1. Receber insights de pesquisa do research_agent
        2. Criar copy persuasivo baseado nos dados
        3. Aplicar técnicas comprovadas de copywriting (AIDA, PAS, etc.)
        4. Adaptar tom e linguagem para o público-alvo
        5. Incluir CTAs eficazes
        
        Estruture sua resposta em JSON:
        {
            "headline": "título principal",
            "subheadline": "subtítulo",
            "body_copy": "texto principal",
            "bullet_points": ["benefício 1", "benefício 2"],
            "cta": "call to action",
            "social_proof": "prova social sugerida",
            "urgency_element": "elemento de urgência"
        }
        
        Use as dores do público e insights dos concorrentes para criar copy único e persuasivo.
        """
    )
    
    AGENT_SKILLS = [
        AgentSkill(
            id="COPYWRITING",
            name="copywriting",
            description="Cria copy persuasivo baseado em pesquisa"
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
        endpoint="/content_agent",
        agent_card=AGENT_CARD,
        agent=content_agent
    )
    
    print(f"Iniciando Content Agent em {AGENT_URL}")
    await server.astart()

if __name__ == "__main__":
    asyncio.run(run_content_agent())
