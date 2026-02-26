"""
Testes de integração real — fazem requisições HTTP aos portais.

Executar com: pytest tests/test_integration.py -v
Estes testes validam que os endpoints dos portais ainda estão funcionais.
Podem falhar por indisponibilidade temporária dos portais.
"""

import pytest
import pytest_asyncio

# -- CKAN portals --

@pytest.mark.asyncio(loop_scope="function")
async def test_integration_us_search():
    """Validate US CKAN portal responds to search."""
    from hipolita.data_recovery.portals.portal_data_gov_us import PortalDataGovUS
    portal = PortalDataGovUS()
    results = await portal.search("health")
    assert isinstance(results, list)
    assert len(results) > 0
    assert results[0].title is not None


@pytest.mark.asyncio(loop_scope="function")
async def test_integration_uk_search():
    """Validate UK CKAN portal responds to search."""
    from hipolita.data_recovery.portals.portal_data_gov_uk import PortalDataGovUK
    portal = PortalDataGovUK()
    results = await portal.search("transport")
    assert isinstance(results, list)
    assert len(results) > 0


@pytest.mark.asyncio(loop_scope="function")
async def test_integration_australia_search():
    """Validate Australia CKAN portal responds to search."""
    from hipolita.data_recovery.portals.portal_data_gov_au import PortalDataGovAU
    portal = PortalDataGovAU()
    results = await portal.search("environment")
    assert isinstance(results, list)
    assert len(results) > 0


@pytest.mark.asyncio(loop_scope="function")
async def test_integration_swiss_search():
    """Validate Swiss CKAN portal responds to search."""
    from hipolita.data_recovery.portals.portal_opendata_swiss import PortalOpendataSwiss
    portal = PortalOpendataSwiss()
    results = await portal.search("transport")
    assert isinstance(results, list)
    assert len(results) > 0


@pytest.mark.asyncio(loop_scope="function")
async def test_integration_finland_search():
    """Validate Finland CKAN portal responds to search."""
    from hipolita.data_recovery.portals.portal_avoindata_fi import PortalAvoindataFI
    portal = PortalAvoindataFI()
    results = await portal.search("population")
    assert isinstance(results, list)
    assert len(results) > 0


# -- Custom API portals --

@pytest.mark.asyncio(loop_scope="function")
async def test_integration_france_search():
    """Validate French udata portal responds to search."""
    from hipolita.data_recovery.portals.portal_data_gouv_fr import PortalDataGouvFR
    portal = PortalDataGouvFR()
    results = await portal.search("transport")
    assert isinstance(results, list)
    assert len(results) > 0
    assert results[0].source_portal == "data.gouv.fr"


@pytest.mark.asyncio(loop_scope="function")
async def test_integration_spain_search():
    """Validate Spanish Linked Data portal responds."""
    from hipolita.data_recovery.portals.portal_datos_gob_es import PortalDatosGobES
    portal = PortalDatosGobES()
    results = await portal.search("datos")
    assert isinstance(results, list)
    assert len(results) > 0


@pytest.mark.asyncio(loop_scope="function")
async def test_integration_singapore_search():
    """Validate Singapore portal responds to search."""
    from hipolita.data_recovery.portals.portal_data_gov_sg import PortalDataGovSG
    portal = PortalDataGovSG()
    results = await portal.search("population")
    assert isinstance(results, list)
    assert len(results) > 0


@pytest.mark.asyncio(loop_scope="function")
async def test_integration_india_search():
    """Validate India OGDP portal responds to search."""
    from hipolita.data_recovery.portals.portal_data_gov_in import PortalDataGovIN
    portal = PortalDataGovIN()
    results = await portal.search("population")
    assert isinstance(results, list)
    assert len(results) > 0


# -- get_dataset tests --

@pytest.mark.asyncio(loop_scope="function")
async def test_integration_france_get_dataset():
    """Validate French portal returns individual dataset."""
    from hipolita.data_recovery.portals.portal_data_gouv_fr import PortalDataGouvFR
    portal = PortalDataGouvFR()
    # First search to get a valid ID
    results = await portal.search("transport")
    assert len(results) > 0
    dataset = await portal.get_dataset(results[0].id)
    assert dataset is not None
    assert dataset.id == results[0].id
