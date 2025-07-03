# research_agent.py
import asyncio
from google.adk import Agent
from google.adk.tools.mcp import MCPToolset, StdioServerParameters
from a2a_framework import A2AServer, generate_agent_card, AgentSkill

async def get_mcp_tools():
    """Conecta ao servidor MCP e retorna as ferramentas"""
    tools, exit_stack = await MCPToolset.from_server(
        connection_params=StdioServerParameters(
            command="python",
            args=["mcp_search_servver.py"],
            env={"PYTHONPATH": "."}
        )
    )
    return tools, exit_stack

async def run_research_agent():
    AGENT_NAME = "research_agent"
    AGENT_DESCRIPTION = "Agente especializado em pesquisa web para copywriting"
    HOST = "0.0.0.0"
    PORT = 11000
    AGENT_URL = f"http://{HOST}:{PORT}"
    
    # Conecta às ferramentas MCP
    mcp_tools, exit_stack = await get_mcp_tools()
    
    # Cria o agente de pesquisa
    research_agent = Agent(
        name="research_agent",
        model="gemini-2.0-flash",
        description="Especialista em pesquisa web para copywriting",
        tools=mcp_tools,
        instructions="""
        Você é um pesquisador especializado em copywriting. Sua função é:
        
        1. Receber tópicos ou produtos para pesquisar
        2. Usar search_google para encontrar informações relevantes
        3. Usar scrape_content para extrair detalhes importantes
        4. Analisar concorrentes, tendências e pontos de dor do público
        5. Retornar insights estruturados em JSON:
        
        {
            "topic": "tópico pesquisado",
            "key_insights": ["insight 1", "insight 2"],
            "competitor_analysis": ["análise 1", "análise 2"],
            "target_audience_pain_points": ["dor 1", "dor 2"],
            "trending_keywords": ["palavra 1", "palavra 2"],
            "sources": ["url1", "url2"]
        }
        """
    )
    
    # Configuração A2A
    AGENT_SKILLS = [
        AgentSkill(
            id="WEB_RESEARCH",
            name="web_research",
            description="Pesquisa informações na web para copywriting"
        )
    ]
    
    AGENT_CARD = generate_agent_card(
        agent_name=AGENT_NAME,
        agent_description=AGENT_DESCRIPTION,
        agent_url=AGENT_URL,
        agent_version="1.0.0",
        skills=AGENT_SKILLS
    )
    
    # Cria servidor A2A
    server = A2AServer(
        host=HOST,
        port=PORT,
        endpoint="/research_agent",
        agent_card=AGENT_CARD,
        agent=research_agent
    )
    
    print(f"Iniciando Research Agent em {AGENT_URL}")
    await server.astart()

if __name__ == "__main__":
    asyncio.run(run_research_agent())
