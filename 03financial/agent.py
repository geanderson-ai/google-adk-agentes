from dotenv import load_dotenv
from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent
from google.adk.tools import google_search

load_dotenv()

def get_fii_data(tickers_string: str) -> dict:
    """
    Retrieves the current data for multiple Brazilian Real Estate Investment Funds (FIIs).

    Args:
        tickers_string: A string with FII ticker symbols separated by commas (e.g., "HGLG11,KNRI11,XPLG11")

    Returns:
        Dictionary with ticker symbols as keys and their respective information as values,
        including current price, daily high/low, dividend yield and fund name.
    """
    import yfinance as yf
    result = {}
    tickers = [ticker.strip() for ticker in tickers_string.split(',')]
    
    for ticker in tickers:
        if not ticker:
            continue
        try:
            fii = yf.Ticker(f"{ticker}.SA")
            info = fii.info
            price_data = fii.history(period="1d")

            result[ticker] = {
                "fund_name": info.get('longName', 'Unknown'),
                "current_price": float(price_data['Close'].iloc[-1]),
                "daily_high": float(price_data['High'].iloc[-1]),
                "daily_low": float(price_data['Low'].iloc[-1]),
                "dividend_yield": info.get('dividendYield', 0.0),
                "currency": "BRL",
                "ticker": ticker
            }
        except Exception as e:
            result[ticker] = {
                "error": f"Failed to retrieve FII information: {str(e)}",
                "ticker": ticker
            }
    
    return result


pesquisador_financeiro = LlmAgent(
    name="pesquisador_financeiro",
    model="gemini-2.5-flash",
    description="""
    Você é um assistente de pesquisa que identifica tickers de fundos imobiliários (FIIs)
    com base em uma consulta do usuário.
    """,
    instruction="""
    Com base na consulta do usuário, pesquise na web para encontrar os tickers de FIIs relevantes.
    Sua resposta DEVE ser uma string única contendo os tickers encontrados, separados por vírgula.
    Exemplo de saída: 'HGLG11,KNRI11,XPLG11'
    Não inclua nenhuma outra informação ou formatação na sua resposta, apenas a string de tickers.
    """,
    tools=[google_search],
    output_key="tickers_string",
)

analista_financeiro = LlmAgent(
    name="analista_financeiro",
    model="gemini-2.5-flash",
    description="""
    Você é um especialista em FIIs que obtém dados de mercado atualizados para uma lista de tickers.
    """,
    instruction="""
    Utilize a ferramenta 'get_fii_data' para buscar as informações dos tickers de FIIs fornecidos em '{tickers_string}'.
    """,
    tools=[get_fii_data],
    output_key="informacoes_fiis",
)

redator_relatorio = LlmAgent(
    name="redator_relatorio",
    model="gemini-2.5-flash",
    description="""
    Você é um assistente de escrita que cria relatórios financeiros detalhados.
    """,
    instruction="""
    Com base nos dados financeiros de FIIs em '{informacoes_fiis}', crie um relatório claro e conciso.
    O relatório deve apresentar os dados de cada FII de forma organizada, incluindo nome, preço atual,
    máxima e mínima do dia e dividend yield.
    Finalize com um breve resumo comparativo.
    """,
    output_key="relatorio_final",
)

root_agent = SequentialAgent(
    name="fii_advisor_agent",
    description="Um agente sequencial que pesquisa FIIs, analisa os dados e gera um relatório.",
    sub_agents=[pesquisador_financeiro, analista_financeiro, redator_relatorio],
)