import pytest
import aiohttp
from aioresponses import aioresponses
from hipolita.data_recovery.adapters.ckan_adapter import CkanAdapter
from hipolita.data_recovery.adapters.api_adapter import ApiAdapter
from hipolita.data_recovery.portals.portal_data_gov_us import PortalDataGovUS
from hipolita.data_recovery.portals.portal_dados_abertos_br import DadosAbertosBR

# Fixtures for Adapters
@pytest.fixture
def ckan_adapter():
    return CkanAdapter("https://mock-ckan.org")

@pytest.fixture
def api_adapter():
    return ApiAdapter("https://mock-br.gov.br")

# Tests for CkanAdapter
@pytest.mark.asyncio
async def test_ckan_connect_success(ckan_adapter):
    with aioresponses() as m:
        # Mock package_search for connect check
        m.get("https://mock-ckan.org/api/3/action/package_search?rows=0", status=200)
        
        async with ckan_adapter as ad:
            assert await ad.connect() == True

@pytest.mark.asyncio
async def test_ckan_connect_fail(ckan_adapter):
    with aioresponses() as m:
        m.get("https://mock-ckan.org/api/3/action/package_search?rows=0", status=500)
        async with ckan_adapter as ad:
            assert await ad.connect() == False

@pytest.mark.asyncio
async def test_ckan_search_packages(ckan_adapter):
    mock_response = {
        "success": True,
        "result": {
            "results": [
                {"id": "pkg1", "title": "Test Package 1", "organization": {"title": "Org 1"}},
                {"id": "pkg2", "title": "Test Package 2"}
            ]
        }
    }
    
    with aioresponses() as m:
        m.get("https://mock-ckan.org/api/3/action/package_search?q=health&rows=10", payload=mock_response)
        
        async with ckan_adapter as ad:
            results = await ad.search_packages("health")
            assert len(results) == 2
            assert results[0]["id"] == "pkg1"

# Tests for ApiAdapter
@pytest.mark.asyncio
async def test_api_adapter_get(api_adapter):
    mock_response = {"success": True}
    with aioresponses() as m:
        m.get("https://mock-br.gov.br/test", payload=mock_response)
        async with api_adapter as ad:
            resp = await ad.get("https://mock-br.gov.br/test")
            assert resp["success"] == True

# Tests for Portals (End-to-End Logic)
@pytest.mark.asyncio
async def test_portal_us_structure():
    portal = PortalDataGovUS()
    
    mock_ckan_resp = {
        "success": True,
        "result": {
            "results": [
                {
                    "id": "us1", 
                    "title": "US Dataset", 
                    "organization": {"title": "US Org"},
                    "resources": [{"format": "CSV", "url": "http://example.com/data.csv"}]
                }
            ]
        }
    }
    
    with aioresponses() as m:
        m.get("https://catalog.data.gov/api/3/action/package_search?rows=0", status=200) # connect check
        m.get("https://catalog.data.gov/api/3/action/package_search?q=test&rows=10", payload=mock_ckan_resp) # search
        
        datasets = await portal.search("test")
        assert len(datasets) == 1
        ds = datasets[0]
        assert ds.title == "US Dataset"

@pytest.mark.asyncio
async def test_portal_br_structure():
    portal = DadosAbertosBR(api_key="TEST")
    
    mock_br_resp = {
        "conjuntosDados": [
            {
                "id": "br_ds_1",
                "title": "Dataset Brasileiro",
                "descricao": "Descricao teste",
                "nomeOrganizacao": "Gov BR",
                "recursos": [{"id": "r1", "formato": "CSV", "url": "http://br.gov/data.csv"}]
            }
        ]
    }
    
    with aioresponses() as m:
         # connect check (using ApiAdapter base connect which hits base_url)
         m.get("https://dados.gov.br/", status=200)
         
         # search - specific logic now in Portal
         m.get("https://dados.gov.br/dados/api/publico/conjuntos-dados?isPrivado=false&nomeConjuntoDados=teste&pagina=1&registrosPorPagina=10", payload=mock_br_resp)
         
         datasets = await portal.search("teste")
         assert len(datasets) == 1
         ds = datasets[0]
         assert ds.title == "Dataset Brasileiro"
