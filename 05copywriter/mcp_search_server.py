# mcp_search_server.py
from mcp import FastMCP
import requests
import os
from bs4 import BeautifulSoup

mcp = FastMCP("Web Search Server")

@mcp.tool()
def search_google(query: str, n_results: int = 5) -> list:
    """
    Busca no Google usando API de busca
    :param query: termo de busca
    :param n_results: número de resultados
    :return: lista de resultados com título, URL e snippet
    """
    # Simulação de busca - substitua pela sua API preferida
    results = []
    try:
        # Aqui você integraria com Serper.dev, Google Custom Search, etc.
        # Para demonstração, retornamos dados mockados
        for i in range(n_results):
            results.append({
                "title": f"Resultado {i+1} para '{query}'",
                "url": f"https://example{i+1}.com",
                "snippet": f"Informação relevante sobre {query} encontrada no site {i+1}"
            })
    except Exception as e:
        return [{"error": f"Erro na busca: {str(e)}"}]
    
    return results

@mcp.tool()
def scrape_content(url: str) -> str:
    """
    Extrai conteúdo textual de uma página web
    :param url: URL para extrair conteúdo
    :return: texto extraído da página
    """
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (compatible; Research Bot)'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove scripts e estilos
        for script in soup(["script", "style"]):
            script.decompose()
            
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text[:2000]  # Limita o tamanho
    except Exception as e:
        return f"Erro ao extrair conteúdo: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport='stdio')
