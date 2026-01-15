import pytest
from aioresponses import aioresponses
from hipolita import search_data, search_data_async, PortalType

@pytest.mark.asyncio
async def test_search_all_aggregates_results_async():
    """Testa se busca 'ALL' agrega resultados de ambos os portais via função assíncrona."""
    
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
        m.get("https://dados.gov.br/dados/api/publico/conjuntos-dados?isPrivado=false&nomeConjuntoDados=test&pagina=1&registrosPorPagina=10", payload=mock_br_resp)
        m.get("https://catalog.data.gov/api/3/action/package_search?q=test&rows=10", payload=mock_us_resp)
        
        results = await search_data_async("test", PortalType.ALL, api_key="TEST_KEY")
        
        assert len(results) == 2
        titles = [d.title for d in results]
        assert "BR Dataset" in titles
        assert "US Dataset" in titles

def test_search_sync_wrapper():
    """Testa o wrapper síncrono search_data."""
    
    mock_us_resp = {
        "success": True,
        "result": {"results": [{"id": "us1", "title": "US Dataset", "organization": {"title": "Org US"}}]}
    }
    
    with aioresponses() as m:
         m.get("https://catalog.data.gov/api/3/action/package_search?rows=0", status=200)
         m.get("https://catalog.data.gov/api/3/action/package_search?q=sync_test&rows=10", payload=mock_us_resp)
         
         # search_data (sync) utiliza asyncio.run internamente
         results = search_data("sync_test", PortalType.DATA_GOV_US)
         assert len(results) == 1
         assert results[0].title == "US Dataset"

@pytest.mark.asyncio
async def test_pass_auth_config_async():
    """Testa passagem de credenciais na função async."""
    mock_br_resp = {"conjuntosDados": []}
    
    with aioresponses() as m:
        m.get("https://dados.gov.br/", status=200)
        m.get("https://dados.gov.br/dados/api/publico/conjuntos-dados?isPrivado=false&nomeConjuntoDados=authtest&pagina=1&registrosPorPagina=10", payload=mock_br_resp)
        
        await search_data_async("authtest", PortalType.DADOS_GOV_BR, api_key="MY_KEY")

def test_search_invalid_portal():
    """Testa se busca com portal inválido levanta ValueError."""
    with pytest.raises(ValueError) as excinfo:
        search_data("query", portal="portal_inexistente")
    assert "Invalid portal" in str(excinfo.value)

def test_search_by_string_key():
    """Testa se busca funciona passando portal como string."""
    mock_us_resp = {
        "success": True,
        "result": {"results": [{"id": "us1", "title": "US Dataset"}]}
    }
    with aioresponses() as m:
        m.get("https://catalog.data.gov/api/3/action/package_search?rows=0", status=200)
        m.get("https://catalog.data.gov/api/3/action/package_search?q=test&rows=10", payload=mock_us_resp)
        
        # Passando portal como string 'data_gov_us'
        results = search_data("test", portal="data_gov_us")
        assert len(results) == 1
        assert results[0].title == "US Dataset"

def test_search_br_without_key_raises_error():
    """Testa se busca no portal BR sem carregar api_key levanta ValueError."""
    with pytest.raises(ValueError) as excinfo:
        search_data("educação", portal="dados_gov_br")
    assert "requires an 'api_key'" in str(excinfo.value)

def test_search_fails_silently_on():
    """Testa se com fails_silently=True não levanta erro mesmo sem chave BR."""
    # Não deve levantar erro
    results = search_data("educação", portal="dados_gov_br", fails_silently=True)
    assert results == []

def test_search_fails_silently_off():
    """Testa se mantém comportamento de raise quando fails_silently=False (default)."""
    with pytest.raises(ValueError):
        search_data("educação", portal="dados_gov_br", fails_silently=False)



