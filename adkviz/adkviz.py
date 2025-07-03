from pyvis.network import Network
from google.adk.agents import SequentialAgent, LlmAgent, ParallelAgent

def visualize_agent_flow(root_agent: SequentialAgent, filename="agent_flow.html"):
    """
    Gera uma visualização interativa do fluxo de agentes em um SequentialAgent do Google ADK.

    Args:
        root_agent (SequentialAgent): O agente raiz SequentialAgent a ser visualizado.
        filename (str, optional): O nome do arquivo HTML de saída. Padrão para "agent_flow.html".
    """
    net = Network(notebook=True, height="750px", width="100%", bgcolor="#222222", font_color="white", cdn_resources='remote')
    net.barnes_hut() # Use a physics layout

    nodes = {}
    previous_agent_name = None

    for i, agent in enumerate(root_agent.sub_agents):
        agent_name = agent.name
        agent_description = agent.description.strip().split('\n')[0] # Take first line of description
        node_id = f"agent_{i}_{agent_name}"
        
        nodes[agent_name] = node_id # Store node_id for edge creation

        net.add_node(node_id, label=agent_name, title=agent_description, color="#007bff")

        if previous_agent_name:
            net.add_edge(nodes[previous_agent_name], node_id, title=f"Flow from {previous_agent_name} to {agent_name}", color="#6c757d")
        
        previous_agent_name = agent_name

    net.show(filename)
    print(f"Agent flow visualization saved to {filename}")
