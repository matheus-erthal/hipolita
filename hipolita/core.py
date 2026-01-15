def package_name():
    return "Hipólita"


import os
from typing import Optional
import asyncio
from .types import PortalType, Dataset
from .data_recovery.portals.portal_dados_abertos_br import DadosAbertosBR
from .data_recovery.portals.portal_data_gov_us import PortalDataGovUS


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