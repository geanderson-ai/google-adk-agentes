from dis import Instruction
from dotenv import load_dotenv
import os
from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent
from google.adk.tools import google_search
from adviz.adkviz import visualize_agent_flow

load_dotenv()

def get_fii_data(tickers: dict) -> dict:
    """
    Retrieves the current data for multiple Brazilian Real Estate Investment Funds (FIIs).

    Args:
        tickers: Dictionary of FII ticker symbols (e.g., {'HGLG11', 'KNRI11', 'XPLG11'})

    Returns:
        Dictionary with ticker symbols as keys and their respective information as values,
        including current price, daily high/low, dividend yield and fund name.
    """
    result = {}
    
    for ticker in tickers:
        try:
            import yfinance as yf
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
    name="pesquisador",
    model="gemini-2.5-flash",
    description="""
    Você é um assistente de pesquisa que busca a partir de entidades.
    """,
    instruction="""
    Você é um assistente de pesquisa que busca dados de fundos imobiliários
    IMPORTANT: Sua resposta DEVE ser um JSON válido correspondendo a esta estrutura:
    
    {ticker1, ticker2, ticker3}
    """,
    tools=[google_search],
    output_key="pesquisa",
) 

get_fii_informacoes = LlmAgent(
    name="get_fii_data",
    model="gemini-2.5-flash",
    description="""
    Retorna os dados de um FII.
    """,
    instruction="""
    Você é um assistente de pesquisa que busca a partir da demanda do usuário que vem de {pesquisa}.
    """,
    tools=[get_fii_data],
    output_key="informacoes",
)

writer = LlmAgent(
    name="writer",
    model="gemini-2.5-flash",
    description="""
    Você é um assistente de escrita.
    """,
    instruction="""
    Você é um assistente de escrita que escreve o relatório de fundos a partir de {informacoes}.
    """,
)

root_agent = SequentialAgent(
    name="fii_advisor",
    description="""
    Você é um assistente de análise de fundos imobiliários.
    """,
    sub_agents=[pesquisador_financeiro, get_fii_informacoes, writer]
) 

visualize_agent_flow(root_agent)


