import pytest
from aioresponses import aioresponses
from hipolita.core import Hipolita, PortalType

@pytest.fixture
def hipolita_instance():
    return Hipolita()

@pytest.mark.asyncio
async def test_search_all_aggregates_results(hipolita_instance):
    """Testa se busca 'ALL' agrega resultados de ambos os portais."""
    
    # Mock BR response
    mock_br_resp = {
        "conjuntosDados": [{"id": "br1", "title": "BR Dataset", "nomeOrganizacao": "Org BR"}]
    }
    # Mock US response
    mock_us_resp = {
        "success": True,
        "result": {"results": [{"id": "us1", "title": "US Dataset", "organization": {"title": "Org US"}}]}
    }
    
    with aioresponses() as m:
        # Connect checks
        m.get("https://dados.gov.br/", status=200) # BR Connect
        m.get("https://catalog.data.gov/api/3/action/package_search?rows=0", status=200) # US Connect
        
        # Searches
        # BR Endpoint
        m.get("https://dados.gov.br/dados/api/publico/conjuntos-dados?isPrivado=false&nomeConjuntoDados=test&pagina=1&registrosPorPagina=10", payload=mock_br_resp)
        # US Endpoint
        m.get("https://catalog.data.gov/api/3/action/package_search?q=test&rows=10", payload=mock_us_resp)
        
        # Passando api_key no auth_config
        results = await hipolita_instance.search_data("test", PortalType.ALL, api_key="TEST_KEY")
        
        assert len(results) == 2
        titles = [d.title for d in results]
        assert "BR Dataset" in titles
        assert "US Dataset" in titles

@pytest.mark.asyncio
async def test_search_specific_portal(hipolita_instance):
    """Testa filtro por portal específico."""
    
    mock_us_resp = {
        "success": True,
        "result": {"results": [{"id": "us1", "title": "US Dataset", "organization": {"title": "Org US"}}]}
    }
    
    with aioresponses() as m:
         m.get("https://catalog.data.gov/api/3/action/package_search?rows=0", status=200)
         m.get("https://catalog.data.gov/api/3/action/package_search?q=test_us&rows=10", payload=mock_us_resp)
         
         results = await hipolita_instance.search_data("test_us", PortalType.DATA_GOV_US)
         assert len(results) == 1
         assert results[0].source_portal == "data.gov"

@pytest.mark.asyncio
async def test_pass_auth_config():
    """Testa passagem de credenciais específicas."""
    hipolita = Hipolita() 
    
    # Mas passa chave no metodo (para BR)
    mock_br_resp = {"conjuntosDados": []}
    
    with aioresponses() as m:
        m.get("https://dados.gov.br/", status=200)
        m.get("https://dados.gov.br/dados/api/publico/conjuntos-dados?isPrivado=false&nomeConjuntoDados=authtest&pagina=1&registrosPorPagina=10", payload=mock_br_resp)
        
        # Testando api_key_br especificamente
        await hipolita.search_data("authtest", PortalType.DADOS_GOV_BR, api_key_br="MY_SPECIAL_KEY")

