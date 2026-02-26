import pytest
import aiohttp
from aioresponses import aioresponses
from hipolita.data_recovery.adapters.ckan_adapter import CkanAdapter
from hipolita.data_recovery.adapters.api_adapter import ApiAdapter
from hipolita.data_recovery.portals.portal_data_gov_us import PortalDataGovUS
from hipolita.data_recovery.portals.portal_dados_abertos_br import DadosAbertosBR
from hipolita.data_recovery.portals.portal_data_gov_uk import PortalDataGovUK
from hipolita.data_recovery.portals.portal_opendata_swiss import PortalOpendataSwiss
from hipolita.data_recovery.portals.portal_avoindata_fi import PortalAvoindataFI
from hipolita.data_recovery.portals.portal_data_gov_au import PortalDataGovAU
from hipolita.data_recovery.portals.portal_data_gouv_fr import PortalDataGouvFR
from hipolita.data_recovery.portals.portal_datos_gob_es import PortalDatosGobES
from hipolita.data_recovery.portals.portal_data_gov_sg import PortalDataGovSG
from hipolita.data_recovery.portals.portal_data_gov_in import PortalDataGovIN

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


# Tests for Portal UK (CKAN)
@pytest.mark.asyncio
async def test_portal_uk_structure():
    portal = PortalDataGovUK()

    mock_ckan_resp = {
        "success": True,
        "result": {
            "results": [
                {
                    "id": "uk1",
                    "title": "UK Dataset",
                    "notes": "UK description",
                    "organization": {"title": "UK Org"},
                    "tags": [{"name": "health"}],
                    "license_title": "OGL",
                    "resources": [{"id": "r1", "name": "file.csv", "format": "CSV", "url": "http://example.com/data.csv"}]
                }
            ]
        }
    }

    with aioresponses() as m:
        m.get("https://ckan.publishing.service.gov.uk/api/3/action/package_search?rows=0", status=200)
        m.get("https://ckan.publishing.service.gov.uk/api/3/action/package_search?q=test&rows=10", payload=mock_ckan_resp)

        datasets = await portal.search("test")
        assert len(datasets) == 1
        ds = datasets[0]
        assert ds.title == "UK Dataset"
        assert ds.source_portal == "data.gov.uk"
        assert ds.tags == ["health"]
        assert len(ds.resources) == 1


# Tests for Portal Switzerland (CKAN)
@pytest.mark.asyncio
async def test_portal_swiss_structure():
    portal = PortalOpendataSwiss()

    mock_ckan_resp = {
        "success": True,
        "result": {
            "results": [
                {
                    "id": "ch1",
                    "title": {"de": "Schweizer Datensatz", "en": "Swiss Dataset"},
                    "notes": {"de": "Beschreibung", "en": "Description"},
                    "organization": {"title": "Swiss Org"},
                    "tags": [{"name": "energy"}],
                    "license_title": "CC-BY",
                    "resources": [{"id": "r1", "format": "CSV", "url": "http://example.ch/data.csv"}]
                }
            ]
        }
    }

    with aioresponses() as m:
        m.get("https://opendata.swiss/api/3/action/package_search?rows=0", status=200)
        m.get("https://opendata.swiss/api/3/action/package_search?q=test&rows=10", payload=mock_ckan_resp)

        datasets = await portal.search("test")
        assert len(datasets) == 1
        ds = datasets[0]
        assert ds.title == "Swiss Dataset"
        assert ds.description == "Description"
        assert ds.source_portal == "opendata.swiss"


# Tests for Portal Finland (CKAN)
@pytest.mark.asyncio
async def test_portal_finland_structure():
    portal = PortalAvoindataFI()

    mock_ckan_resp = {
        "success": True,
        "result": {
            "results": [
                {
                    "id": "fi1",
                    "title": "Finnish Dataset",
                    "notes": "Finnish description",
                    "organization": {"title": "Finnish Org"},
                    "tags": [],
                    "keywords": {"fi": ["terveys"], "en": ["health"]},
                    "license_title": "CC-BY-4.0",
                    "resources": [{"id": "r1", "format": "CSV", "url": "http://example.fi/data.csv"}]
                }
            ]
        }
    }

    with aioresponses() as m:
        m.get("https://www.avoindata.fi/data/api/3/action/package_search?rows=0", status=200)
        m.get("https://www.avoindata.fi/data/api/3/action/package_search?q=test&rows=10", payload=mock_ckan_resp)

        datasets = await portal.search("test")
        assert len(datasets) == 1
        ds = datasets[0]
        assert ds.title == "Finnish Dataset"
        assert ds.source_portal == "avoindata.fi"
        assert ds.tags == ["health"]


# Tests for Portal Australia (CKAN)
@pytest.mark.asyncio
async def test_portal_australia_structure():
    portal = PortalDataGovAU()

    mock_ckan_resp = {
        "success": True,
        "result": {
            "results": [
                {
                    "id": "au1",
                    "title": "Australian Dataset",
                    "notes": "AU description",
                    "organization": {"title": "AU Org"},
                    "tags": [{"name": "environment"}],
                    "license_title": "CC-BY-4.0",
                    "resources": [{"id": "r1", "format": "CSV", "url": "http://example.au/data.csv"}]
                }
            ]
        }
    }

    with aioresponses() as m:
        m.get("https://data.gov.au/api/3/action/package_search?rows=0", status=200)
        m.get("https://data.gov.au/api/3/action/package_search?q=test&rows=10", payload=mock_ckan_resp)

        datasets = await portal.search("test")
        assert len(datasets) == 1
        ds = datasets[0]
        assert ds.title == "Australian Dataset"
        assert ds.source_portal == "data.gov.au"


# Tests for Portal France (ApiAdapter)
@pytest.mark.asyncio
async def test_portal_france_structure():
    portal = PortalDataGouvFR()

    mock_fr_resp = {
        "data": [
            {
                "id": "fr1",
                "title": "French Dataset",
                "description": "Description FR",
                "license": "odc-by",
                "organization": {"name": "French Org"},
                "tags": ["sante", "donnees"],
                "resources": [
                    {"id": "r1", "title": "file.csv", "description": "Resource desc", "format": "csv", "url": "http://fr.gov/data.csv", "mime": "text/csv", "filesize": 1234}
                ]
            }
        ]
    }

    with aioresponses() as m:
        m.get("https://www.data.gouv.fr/", status=200)
        m.get("https://www.data.gouv.fr/api/1/datasets/?page_size=10&q=test", payload=mock_fr_resp)

        datasets = await portal.search("test")
        assert len(datasets) == 1
        ds = datasets[0]
        assert ds.title == "French Dataset"
        assert ds.source_portal == "data.gouv.fr"
        assert ds.tags == ["sante", "donnees"]
        assert len(ds.resources) == 1
        assert ds.resources[0].format == "csv"


# Tests for Portal Spain (ApiAdapter)
@pytest.mark.asyncio
async def test_portal_spain_structure():
    portal = PortalDatosGobES()

    mock_es_resp = {
        "format": "linked-data-api",
        "result": {
            "items": [
                {
                    "_about": "https://datos.gob.es/catalogo/test-dataset-1",
                    "title": [
                        {"_value": "Conjunto de datos", "_lang": "es"},
                        {"_value": "Test Dataset", "_lang": "en"}
                    ],
                    "description": [
                        {"_value": "Descripcion", "_lang": "es"},
                        {"_value": "Description", "_lang": "en"}
                    ],
                    "theme": [{"_about": "http://theme.org/environment"}],
                    "publisher": {"_about": "http://pub.org/E00003801", "notation": "E00003801"},
                    "distribution": {
                        "_about": "https://datos.gob.es/dist/r1",
                        "format": {"label": ["CSV"]},
                        "accessURL": "http://example.es/data.csv"
                    }
                }
            ]
        }
    }

    with aioresponses() as m:
        m.get("https://datos.gob.es/", status=200)
        m.get("https://datos.gob.es/apidata/catalog/dataset?_page=0&_pageSize=10", payload=mock_es_resp)

        datasets = await portal.search("test")
        assert len(datasets) == 1
        ds = datasets[0]
        assert ds.title == "Test Dataset"
        assert ds.source_portal == "datos.gob.es"
        assert ds.organization == "E00003801"
        assert len(ds.resources) == 1
        assert ds.resources[0].format == "CSV"


# Tests for Portal Singapore (ApiAdapter)
@pytest.mark.asyncio
async def test_portal_singapore_structure():
    portal = PortalDataGovSG()

    mock_sg_resp = {
        "code": 0,
        "data": {
            "datasets": [
                {
                    "datasetId": "d_sg1",
                    "name": "Singapore Dataset",
                    "description": "SG Description",
                    "status": "active",
                    "format": "CSV",
                    "managedByAgencyName": "SG Agency"
                }
            ]
        }
    }

    with aioresponses() as m:
        m.get("https://api-production.data.gov.sg/", status=200)
        m.get("https://api-production.data.gov.sg/v2/public/api/datasets?page=1&query=test", payload=mock_sg_resp)

        datasets = await portal.search("test")
        assert len(datasets) == 1
        ds = datasets[0]
        assert ds.title == "Singapore Dataset"
        assert ds.source_portal == "data.gov.sg"
        assert ds.organization == "SG Agency"
        assert ds.id == "d_sg1"


# Tests for Portal India (ApiAdapter)
@pytest.mark.asyncio
async def test_portal_india_structure():
    portal = PortalDataGovIN()

    mock_in_resp = {
        "name": "OGDP API",
        "version": "2.0.5",
        "statusCode": 200,
        "total": 1,
        "data": {
            "rows": [
                {
                    "title": ["Health Resource"],
                    "uuid": ["uuid-in-1"],
                    "catalog_title": ["Health Catalog"],
                    "catalog_uuid": ["cat-uuid-1"],
                    "datafile": ["https://data.gov.in/files/data.csv"],
                    "file_format": ["text/csv"],
                    "file_size": [4398],
                    "sector_resource": ["Health"]
                }
            ]
        }
    }

    with aioresponses() as m:
        m.get("https://data.gov.in/", status=200)
        m.get("https://data.gov.in/backend/dmspublic/v1/resources?filters%5Btitle%5D=test&format=json&limit=10&offset=0", payload=mock_in_resp)

        datasets = await portal.search("test")
        assert len(datasets) == 1
        ds = datasets[0]
        assert ds.title == "Health Catalog"
        assert ds.source_portal == "data.gov.in"
        assert ds.tags == ["Health"]
        assert len(ds.resources) == 1
        assert ds.resources[0].url == "https://data.gov.in/files/data.csv"


# ==========================================
# Tests for get_dataset() (individual fetch)
# ==========================================

# CKAN Portals get_dataset tests
@pytest.mark.asyncio
async def test_get_dataset_us():
    portal = PortalDataGovUS()
    mock_resp = {
        "success": True,
        "result": {
            "id": "us1",
            "title": "US Single Dataset",
            "organization": {"title": "US Org"},
            "resources": [{"id": "r1", "format": "CSV", "url": "http://example.com/data.csv"}],
            "tags": [{"name": "health"}],
        }
    }
    with aioresponses() as m:
        m.get("https://catalog.data.gov/api/3/action/package_show?id=us1", payload=mock_resp)
        ds = await portal.get_dataset("us1")
        assert ds is not None
        assert ds.title == "US Single Dataset"
        assert ds.id == "us1"


@pytest.mark.asyncio
async def test_get_dataset_uk():
    portal = PortalDataGovUK()
    mock_resp = {
        "success": True,
        "result": {
            "id": "uk1",
            "title": "UK Single Dataset",
            "notes": "UK description",
            "organization": {"title": "UK Org"},
            "resources": [],
            "tags": [],
        }
    }
    with aioresponses() as m:
        m.get("https://ckan.publishing.service.gov.uk/api/3/action/package_show?id=uk1", payload=mock_resp)
        ds = await portal.get_dataset("uk1")
        assert ds is not None
        assert ds.title == "UK Single Dataset"
        assert ds.source_portal == "data.gov.uk"


@pytest.mark.asyncio
async def test_get_dataset_swiss():
    portal = PortalOpendataSwiss()
    mock_resp = {
        "success": True,
        "result": {
            "id": "ch1",
            "title": {"de": "Schweizer Datensatz", "en": "Swiss Single"},
            "notes": {"en": "English desc"},
            "organization": {"title": "Swiss Org"},
            "resources": [],
            "tags": [],
        }
    }
    with aioresponses() as m:
        m.get("https://opendata.swiss/api/3/action/package_show?id=ch1", payload=mock_resp)
        ds = await portal.get_dataset("ch1")
        assert ds is not None
        assert ds.title == "Swiss Single"


@pytest.mark.asyncio
async def test_get_dataset_finland():
    portal = PortalAvoindataFI()
    mock_resp = {
        "success": True,
        "result": {
            "id": "fi1",
            "title": "Finnish Single",
            "notes": "FI desc",
            "organization": {"title": "FI Org"},
            "resources": [],
            "tags": [],
            "keywords": {"en": ["health"]},
        }
    }
    with aioresponses() as m:
        m.get("https://www.avoindata.fi/data/api/3/action/package_show?id=fi1", payload=mock_resp)
        ds = await portal.get_dataset("fi1")
        assert ds is not None
        assert ds.title == "Finnish Single"
        assert ds.tags == ["health"]


@pytest.mark.asyncio
async def test_get_dataset_australia():
    portal = PortalDataGovAU()
    mock_resp = {
        "success": True,
        "result": {
            "id": "au1",
            "title": "AU Single Dataset",
            "notes": "AU desc",
            "organization": {"title": "AU Org"},
            "resources": [],
            "tags": [],
        }
    }
    with aioresponses() as m:
        m.get("https://data.gov.au/api/3/action/package_show?id=au1", payload=mock_resp)
        ds = await portal.get_dataset("au1")
        assert ds is not None
        assert ds.title == "AU Single Dataset"
        assert ds.source_portal == "data.gov.au"


# ApiAdapter Portals get_dataset tests
@pytest.mark.asyncio
async def test_get_dataset_br():
    portal = DadosAbertosBR(api_key="TEST")
    mock_resp = {
        "id": "br1",
        "title": "BR Single Dataset",
        "descricao": "Descricao",
        "nomeOrganizacao": "Gov BR",
        "recursos": [{"id": "r1", "formato": "CSV", "url": "http://br.gov/data.csv"}],
        "palavrasChave": [],
    }
    with aioresponses() as m:
        m.get("https://dados.gov.br/", status=200)
        m.get("https://dados.gov.br/dados/api/publico/conjuntos-dados/br1", payload=mock_resp)
        ds = await portal.get_dataset("br1")
        assert ds is not None
        assert ds.title == "BR Single Dataset"
        assert ds.source_portal == "dados.gov.br"


@pytest.mark.asyncio
async def test_get_dataset_br_no_key():
    portal = DadosAbertosBR()
    with pytest.raises(ValueError, match="requires an 'api_key'"):
        await portal.get_dataset("br1")


@pytest.mark.asyncio
async def test_get_dataset_france():
    portal = PortalDataGouvFR()
    mock_resp = {
        "id": "fr1",
        "title": "French Single Dataset",
        "description": "FR desc",
        "license": "odc-by",
        "organization": {"name": "French Org"},
        "tags": ["sante"],
        "resources": [],
    }
    with aioresponses() as m:
        m.get("https://www.data.gouv.fr/", status=200)
        m.get("https://www.data.gouv.fr/api/1/datasets/fr1/", payload=mock_resp)
        ds = await portal.get_dataset("fr1")
        assert ds is not None
        assert ds.title == "French Single Dataset"
        assert ds.source_portal == "data.gouv.fr"


@pytest.mark.asyncio
async def test_get_dataset_spain():
    portal = PortalDatosGobES()
    mock_resp = {
        "result": {
            "items": [
                {
                    "_about": "https://datos.gob.es/catalogo/test-dataset-1",
                    "title": [{"_value": "Spanish Single", "_lang": "en"}],
                    "description": [{"_value": "ES desc", "_lang": "en"}],
                    "theme": [],
                    "distribution": [],
                }
            ]
        }
    }
    with aioresponses() as m:
        m.get("https://datos.gob.es/", status=200)
        m.get("https://datos.gob.es/apidata/catalog/dataset/test-dataset-1", payload=mock_resp)
        ds = await portal.get_dataset("test-dataset-1")
        assert ds is not None
        assert ds.title == "Spanish Single"
        assert ds.source_portal == "datos.gob.es"


@pytest.mark.asyncio
async def test_get_dataset_singapore():
    portal = PortalDataGovSG()
    mock_resp = {
        "code": 0,
        "data": {
            "datasetId": "d_sg1",
            "name": "SG Single Dataset",
            "description": "SG desc",
            "format": "CSV",
            "managedBy": "SG Agency",
        }
    }
    with aioresponses() as m:
        m.get("https://api-production.data.gov.sg/", status=200)
        m.get("https://api-production.data.gov.sg/v2/public/api/datasets/d_sg1/metadata", payload=mock_resp)
        ds = await portal.get_dataset("d_sg1")
        assert ds is not None
        assert ds.title == "SG Single Dataset"
        assert ds.organization == "SG Agency"
        assert ds.source_portal == "data.gov.sg"


@pytest.mark.asyncio
async def test_get_dataset_india():
    portal = PortalDataGovIN()
    mock_resp = {
        "statusCode": 200,
        "total": 1,
        "data": {
            "rows": [
                {
                    "title": ["India Single Resource"],
                    "uuid": ["uuid-in-1"],
                    "catalog_title": ["India Catalog"],
                    "catalog_uuid": ["cat-uuid-1"],
                    "datafile": ["https://data.gov.in/files/data.csv"],
                    "file_format": ["text/csv"],
                    "file_size": [1024],
                    "sector_resource": ["Health"],
                }
            ]
        }
    }
    with aioresponses() as m:
        m.get("https://data.gov.in/", status=200)
        m.get("https://data.gov.in/backend/dmspublic/v1/resources?filters%5Buuid%5D=uuid-in-1&format=json&limit=1", payload=mock_resp)
        ds = await portal.get_dataset("uuid-in-1")
        assert ds is not None
        assert ds.title == "India Catalog"
        assert ds.source_portal == "data.gov.in"
