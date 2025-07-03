from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()

# Exemplo de ferramentas (se seus agentes usarem)
def tool_agent1(input_data: str) -> str:
    return f"Conteúdo processado pelo Agente 1: {input_data}"

def tool_agent2(input_data: str) -> str:
    return f"Conteúdo processado pelo Agente 2: {input_data}"

def tool_agent3(input_data: str) -> str:
    return f"Conteúdo processado pelo Agente 3: {input_data}"

# Defina os subagentes
agent1 = Agent(
    name="AgentX",
    model="gemini-2.0-flash", # ou outro modelo
    description="Agente especializado em análise de dados.",
    instruction="Sua tarefa é analisar dados e fornecer insights detalhados. Utilize a tool_agent1.",
    tools=[tool_agent1]
)

agent2 = Agent(
    name="AgentY",
    model="gemini-2.0-flash",
    description="Agente especializado em geração de texto criativo.",
    instruction="Sua tarefa é gerar texto criativo com base em prompts. Utilize a tool_agent2.",
    tools=[tool_agent2]
)

agent3 = Agent(
    name="AgentZ",
    model="gemini-2.0-flash",
    description="Agente especializado em sumarização de documentos.",
    instruction="Sua tarefa é sumarizar documentos extensos. Utilize a tool_agent3.",
    tools=[tool_agent3]
)

# Defina o agente-raiz que orquestrará os subagentes
# Ele delega com base na descrição dos sub_agents
root_agent = Agent(
    name="OrchestratorAgent",
    model="gemini-2.0-flash",
    description="Agente principal que coordena a equipe de agentes especializados.",
    instruction="Você é um orquestrador. Direcione as consultas aos agentes especializados (AgentX, AgentY, AgentZ) com base na solicitação do usuário. Seja direto e conciso na delegação e na apresentação do resultado final. Não fale sobre as ferramentas internas.",
    sub_agents=[agent1, agent2, agent3] # Aqui você define a hierarquia [8, 16]
)


import asyncio

async def run_and_collect_events(query: str, root_agent: Agent):
    session_service = InMemorySessionService() # Ou DatabaseSessionService para persistência [20]
    app_name = "MultiAgentApp"
    user_id = "your_user_id"
    session_id = "your_session_id" # Use um session_id único por conversa se quiser múltiplos registros

    session = await session_service.create_session(app_name=app_name, user_id=user_id, session_id=session_id)
    runner = Runner(agent=root_agent, app_name=app_name, session_service=session_service)

    collected_content = {
        "user_query": query,
        "events": []
    }

    print(f"\n>>> Consulta do Usuário: {query}")
    content_message = types.Content(role='user', parts=[types.Part(text=query)])

    async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content_message):
        # A API de Eventos do ADK fornece detalhes sobre o tipo de evento e seu autor [12, 21]
        # Isso é crucial para depuração e para capturar o fluxo de execução [21, 22]
        event_info = {
            "id": event.id,
            "timestamp": datetime.fromtimestamp(event.timestamp, tz=timezone.utc).isoformat(),
            "author": event.author,
            "type": type(event).__name__, # Ex: Event, ToolStartEvent, ToolEndEvent, LlmAgentCompletionEvent
            "is_final_response": event.is_final_response()
        }

        if event.content and event.content.parts:
            # Capturar conteúdo textual de qualquer parte do evento
            text_parts = [part.text for part in event.content.parts if hasattr(part, 'text') and part.text is not None]
            if text_parts:
                event_info["content"] = "\n".join(text_parts)
            # Para conteúdo multimodal (ex: imagens), você pode ter uma lógica diferente [19, 23]
            # if "[[IMAGE_DATA:" in event_info.get("content", ""):
            #     # Lógica para extrair e processar dados de imagem

        if event.actions: # Eventos de ação, como transferência de agente [12]
            event_info["actions"] = event.actions.dict()

        if event.get_function_calls(): # Se o evento envolve chamadas de função [12]
            event_info["function_calls"] = [call.dict() for call in event.get_function_calls()]

        if event.get_function_responses(): # Se o evento envolve respostas de função [12]
            event_info["function_responses"] = [resp.dict() for resp in event.get_function_responses()]
        
        collected_content["events"].append(event_info)

        print(f"  [Event] Autor: {event_info.get('author')}, Tipo: {event_info.get('type')}, Final: {event_info.get('is_final_response')}, Conteúdo: {event_info.get('content', '')[:100]}...") # Imprimir apenas os primeiros 100 caracteres do conteúdo
    return collected_content

def generate_markdown_report(data: dict, filename: str = "agent_report.md"):
    markdown_output = []
    markdown_output.append(f"# Relatório de Execução do Agente de IA\n")
    markdown_output.append(f"## Consulta do Usuário\n")
    markdown_output.append(f"```\n{data['user_query']}\n```\n")
    markdown_output.append(f"## Eventos de Execução\n")

    for event in data["events"]:
        markdown_output.append(f"### Evento ID: `{event['id']}`\n")
        markdown_output.append(f"- **Timestamp**: {event['timestamp']}\n")
        markdown_output.append(f"- **Autor**: `{event['author']}`\n")
        markdown_output.append(f"- **Tipo**: `{event['type']}`\n")
        markdown_output.append(f"- **Resposta Final**: `{event['is_final_response']}`\n")

        if "content" in event and event["content"]:
            markdown_output.append(f"- **Conteúdo**:\n")
            markdown_output.append(f"```\n{event['content']}\n```\n")
        
        if "actions" in event and event["actions"]:
            markdown_output.append(f"- **Ações**: `{event['actions']}`\n")
        
        if "function_calls" in event and event["function_calls"]:
            markdown_output.append(f"- **Chamadas de Função**: `{event['function_calls']}`\n")

        if "function_responses" in event and event["function_responses"]:
            markdown_output.append(f"- **Respostas de Função**: `{event['function_responses']}`\n")

        markdown_output.append("---\n") # Separador para clareza entre eventos

    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(markdown_output))
    
    print(f"\nRelatório Markdown gerado em '{filename}'")

# Exemplo de uso:
async def main_process():
    user_query = "Me analise os dados mais recentes de vendas, crie uma poesia sobre IA e me sumarize o artigo sobre computação quântica que você tem acesso."
    # É importante notar que o agente precisa ser instruído para usar as "tools" internas ou subagentes
    # e que as "tools" retornem os dados para o agente, que por sua vez os incluirá nos eventos.
    # O exemplo acima assume que o OrchestratorAgent delega e o conteúdo dos subagentes é refletido nos eventos.
    # Em um cenário real, você pode precisar de um `after_tool_callback` [12] para garantir que os resultados das ferramentas
    # ou dos subagentes sejam capturados e expostos nos eventos do agente-raiz.
    
    report_data = await run_and_collect_events(user_query, root_agent)
    generate_markdown_report(report_data)

if __name__ == "__main__":
    asyncio.run(main_process())