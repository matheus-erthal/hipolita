def package_name():
    return "Hipólita"


from typing import Optional
import asyncio
from .types import PortalType, Dataset, DataFrameWithMeta
from .data_recovery.portals.portal_dados_abertos_br import DadosAbertosBR
from .data_recovery.portals.portal_data_gov_us import PortalDataGovUS
from .data_recovery.portals.portal_data_gov_uk import PortalDataGovUK
from .data_recovery.portals.portal_opendata_swiss import PortalOpendataSwiss
from .data_recovery.portals.portal_avoindata_fi import PortalAvoindataFI
from .data_recovery.portals.portal_data_gov_au import PortalDataGovAU
from .data_recovery.portals.portal_data_gouv_fr import PortalDataGouvFR
from .data_recovery.portals.portal_datos_gob_es import PortalDatosGobES
from .data_recovery.portals.portal_data_gov_sg import PortalDataGovSG
from .data_recovery.portals.portal_data_gov_in import PortalDataGovIN


async def search_data_async(
    query: str, 
    portal: PortalType | str = PortalType.ALL, 
    fails_silently: bool = False,
    **auth_config
) -> list[Dataset]:
    """
    Busca dados em portais governamentais de forma assíncrona.
    
    Args:
        query: Termo de busca.
        portal: PortalType, ou string ('all', 'dados_gov_br', 'data_gov_us').
        fails_silently: Se True, erros são apenas logados e retorna lista (parcial ou vazia).
        **auth_config: Credenciais extras (ex: api_key para Portal BR).
    """
    # Normalização do portal
    if isinstance(portal, str):
        try:
            # Tenta converter string para PortalType (match pelo valor da string no enum)
            portal = PortalType(portal.lower())
        except ValueError:
            valid_options = [p.value for p in PortalType]
            msg = f"Invalid portal: '{portal}'. Valid options: {valid_options}"
            if fails_silently:
                print(msg)
                return []
            raise ValueError(msg) from None

    portals_to_search = []
    
    if portal == PortalType.DADOS_GOV_BR or portal == PortalType.ALL:
        portals_to_search.append(DadosAbertosBR(**auth_config))
        
    if portal == PortalType.DATA_GOV_US or portal == PortalType.ALL:
        portals_to_search.append(PortalDataGovUS(**auth_config))

    if portal == PortalType.DATA_GOV_UK or portal == PortalType.ALL:
        portals_to_search.append(PortalDataGovUK(**auth_config))

    if portal == PortalType.OPENDATA_SWISS or portal == PortalType.ALL:
        portals_to_search.append(PortalOpendataSwiss(**auth_config))

    if portal == PortalType.AVOINDATA_FI or portal == PortalType.ALL:
        portals_to_search.append(PortalAvoindataFI(**auth_config))

    if portal == PortalType.DATA_GOV_AU or portal == PortalType.ALL:
        portals_to_search.append(PortalDataGovAU(**auth_config))

    if portal == PortalType.DATA_GOUV_FR or portal == PortalType.ALL:
        portals_to_search.append(PortalDataGouvFR(**auth_config))

    if portal == PortalType.DATOS_GOB_ES or portal == PortalType.ALL:
        portals_to_search.append(PortalDatosGobES(**auth_config))

    if portal == PortalType.DATA_GOV_SG or portal == PortalType.ALL:
        portals_to_search.append(PortalDataGovSG(**auth_config))

    if portal == PortalType.DATA_GOV_IN or portal == PortalType.ALL:
        portals_to_search.append(PortalDataGovIN(**auth_config))
        
    results = []
    tasks = [p.search(query) for p in portals_to_search]
    search_results = await asyncio.gather(*tasks, return_exceptions=True)
    
    for res in search_results:
        if isinstance(res, list):
            results.extend(res)
        elif isinstance(res, Exception):
            # Se fails_silently é False e (pediu portal específico ou erro de validação), lança
            # Note: ValueError de validação do portal ja foi tratado acima ou deve ser repassado.
            if not fails_silently and (portal != PortalType.ALL or isinstance(res, ValueError)):
                raise res
            
            # Otherwise, just log and continue
            print(f"Search error: {res}")
            
    return results


def search_data(
    query: str, 
    portal: PortalType | str = PortalType.ALL, 
    fails_silently: bool = False,
    **auth_config
) -> list[Dataset]:
    """
    Busca dados em portais governamentais de forma síncrona.
    """
    return asyncio.run(search_data_async(query, portal, fails_silently, **auth_config))


async def get_dataset_async(
    dataset_id: str,
    portal: PortalType | str,
    fails_silently: bool = False,
    **auth_config
) -> Optional[Dataset]:
    """
    Busca um dataset individual por ID em um portal específico (assíncrono).

    Args:
        dataset_id: ID do dataset no portal.
        portal: PortalType ou string do portal (não aceita 'all').
        fails_silently: Se True, erros são logados e retorna None.
        **auth_config: Credenciais extras (ex: api_key para Portal BR).
    """
    if isinstance(portal, str):
        try:
            portal = PortalType(portal.lower())
        except ValueError:
            valid_options = [p.value for p in PortalType if p != PortalType.ALL]
            msg = f"Invalid portal: '{portal}'. Valid options: {valid_options}"
            if fails_silently:
                print(msg)
                return None
            raise ValueError(msg) from None

    if portal == PortalType.ALL:
        msg = "get_dataset requires a specific portal. PortalType.ALL is not supported."
        if fails_silently:
            print(msg)
            return None
        raise ValueError(msg)

    portal_map = {
        PortalType.DADOS_GOV_BR: DadosAbertosBR,
        PortalType.DATA_GOV_US: PortalDataGovUS,
        PortalType.DATA_GOV_UK: PortalDataGovUK,
        PortalType.OPENDATA_SWISS: PortalOpendataSwiss,
        PortalType.AVOINDATA_FI: PortalAvoindataFI,
        PortalType.DATA_GOV_AU: PortalDataGovAU,
        PortalType.DATA_GOUV_FR: PortalDataGouvFR,
        PortalType.DATOS_GOB_ES: PortalDatosGobES,
        PortalType.DATA_GOV_SG: PortalDataGovSG,
        PortalType.DATA_GOV_IN: PortalDataGovIN,
    }

    portal_cls = portal_map.get(portal)
    if not portal_cls:
        msg = f"Unsupported portal: {portal}"
        if fails_silently:
            print(msg)
            return None
        raise ValueError(msg)

    try:
        portal_instance = portal_cls(**auth_config)
        return await portal_instance.get_dataset(dataset_id)
    except Exception as e:
        if not fails_silently:
            raise
        print(f"get_dataset error: {e}")
        return None


def get_dataset(
    dataset_id: str,
    portal: PortalType | str,
    fails_silently: bool = False,
    **auth_config
) -> Optional[Dataset]:
    """
    Busca um dataset individual por ID em um portal específico (síncrono).
    """
    return asyncio.run(get_dataset_async(dataset_id, portal, fails_silently, **auth_config))


async def fetch_dataset_data_async(
    dataset_id: str,
    portal: PortalType | str,
    fails_silently: bool = False,
    **auth_config
) -> DataFrameWithMeta:
    """
    Busca um dataset e tenta baixar o primeiro recurso parseável como DataFrame (assíncrono).

    Se o dataset possuir um recurso em formato parseável (CSV, TSV, XLS, XLSX, JSON),
    retorna DataFrameWithMeta com o DataFrame preenchido.
    Caso contrário, retorna DataFrameWithMeta com DataFrame vazio e metadados com links de acesso.

    Args:
        dataset_id: ID do dataset no portal.
        portal: PortalType ou string do portal (não aceita 'all').
        fails_silently: Se True, erros são logados e retorna DataFrameWithMeta vazio.
        **auth_config: Credenciais extras (ex: api_key para Portal BR).
    """
    import pandas as pd

    if isinstance(portal, str):
        try:
            portal = PortalType(portal.lower())
        except ValueError:
            valid_options = [p.value for p in PortalType if p != PortalType.ALL]
            msg = f"Invalid portal: '{portal}'. Valid options: {valid_options}"
            if fails_silently:
                print(msg)
                return DataFrameWithMeta(df=pd.DataFrame(), meta={"error": msg})
            raise ValueError(msg) from None

    if portal == PortalType.ALL:
        msg = "fetch_dataset_data requires a specific portal. PortalType.ALL is not supported."
        if fails_silently:
            print(msg)
            return DataFrameWithMeta(df=pd.DataFrame(), meta={"error": msg})
        raise ValueError(msg)

    portal_map = {
        PortalType.DADOS_GOV_BR: DadosAbertosBR,
        PortalType.DATA_GOV_US: PortalDataGovUS,
        PortalType.DATA_GOV_UK: PortalDataGovUK,
        PortalType.OPENDATA_SWISS: PortalOpendataSwiss,
        PortalType.AVOINDATA_FI: PortalAvoindataFI,
        PortalType.DATA_GOV_AU: PortalDataGovAU,
        PortalType.DATA_GOUV_FR: PortalDataGouvFR,
        PortalType.DATOS_GOB_ES: PortalDatosGobES,
        PortalType.DATA_GOV_SG: PortalDataGovSG,
        PortalType.DATA_GOV_IN: PortalDataGovIN,
    }

    portal_cls = portal_map.get(portal)
    if not portal_cls:
        msg = f"Unsupported portal: {portal}"
        if fails_silently:
            print(msg)
            return DataFrameWithMeta(df=pd.DataFrame(), meta={"error": msg})
        raise ValueError(msg)

    try:
        portal_instance = portal_cls(**auth_config)
        return await portal_instance.fetch_dataset_data(dataset_id)
    except Exception as e:
        if not fails_silently:
            raise
        print(f"fetch_dataset_data error: {e}")
        return DataFrameWithMeta(df=pd.DataFrame(), meta={"error": str(e)})


def fetch_dataset_data(
    dataset_id: str,
    portal: PortalType | str,
    fails_silently: bool = False,
    **auth_config
) -> DataFrameWithMeta:
    """
    Busca um dataset e tenta baixar o primeiro recurso parseável como DataFrame (síncrono).
    """
    return asyncio.run(fetch_dataset_data_async(dataset_id, portal, fails_silently, **auth_config))


class Hipolita:
    """Núcleo da biblioteca Hipolita."""

    def __init__(self):
        pass

    @staticmethod
    async def search_data_async(
        query: str, 
        portal: PortalType | str = PortalType.ALL, 
        fails_silently: bool = False,
        **auth_config
    ) -> list[Dataset]:
        """Busca dados em portais governamentais (Método estático assíncrono)."""
        return await search_data_async(query, portal, fails_silently, **auth_config)

    @staticmethod
    def search_data(
        query: str, 
        portal: PortalType | str = PortalType.ALL, 
        fails_silently: bool = False,
        **auth_config
    ) -> list[Dataset]:
        """Busca dados em portais governamentais (Método estático síncrono)."""
        return search_data(query, portal, fails_silently, **auth_config)

    @staticmethod
    async def get_dataset_async(
        dataset_id: str,
        portal: PortalType | str,
        fails_silently: bool = False,
        **auth_config
    ) -> Optional[Dataset]:
        """Busca um dataset individual por ID (assíncrono)."""
        return await get_dataset_async(dataset_id, portal, fails_silently, **auth_config)

    @staticmethod
    def get_dataset(
        dataset_id: str,
        portal: PortalType | str,
        fails_silently: bool = False,
        **auth_config
    ) -> Optional[Dataset]:
        """Busca um dataset individual por ID (síncrono)."""
        return get_dataset(dataset_id, portal, fails_silently, **auth_config)

    @staticmethod
    async def fetch_dataset_data_async(
        dataset_id: str,
        portal: PortalType | str,
        fails_silently: bool = False,
        **auth_config
    ) -> DataFrameWithMeta:
        """Busca dataset e baixa primeiro recurso parseável como DataFrame (assíncrono)."""
        return await fetch_dataset_data_async(dataset_id, portal, fails_silently, **auth_config)

    @staticmethod
    def fetch_dataset_data(
        dataset_id: str,
        portal: PortalType | str,
        fails_silently: bool = False,
        **auth_config
    ) -> DataFrameWithMeta:
        """Busca dataset e baixa primeiro recurso parseável como DataFrame (síncrono)."""
        return fetch_dataset_data(dataset_id, portal, fails_silently, **auth_config)