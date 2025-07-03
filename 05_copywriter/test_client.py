# test_client.py
import asyncio
import aiohttp
import json

async def test_copywriter_system():
    """Testa o sistema completo de copywriting"""
    
    briefing = {
        "produto": "Curso online de Python para iniciantes",
        "publico_alvo": "Profissionais que querem migrar para tech",
        "objetivo": "Aumentar conversões na landing page",
        "tom": "Profissional mas acessível"
    }
    
    url = "http://localhost:10000/copywriter_host"
    
    async with aiohttp.ClientSession() as session:
        payload = {
            "message": f"Crie copy para: {json.dumps(briefing, ensure_ascii=False)}",
            "session_id": "test_session_001"
        }
        
        async with session.post(url, json=payload) as response:
            result = await response.json()
            print("=== RESULTADO DO COPYWRITING ===")
            print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(test_copywriter_system())
