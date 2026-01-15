def package_name():
    return "Hipólita"


import os
from typing import Optional
import asyncio
from .types import PortalType, Dataset
from .data_recovery.portals.portal_dados_abertos_br import DadosAbertosBR
from .data_recovery.portals.portal_data_gov_us import PortalDataGovUS


class Hipolita:
    """Núcleo da biblioteca Hipolita.

    A `api_key` é opcional na inicialização, mas pode ser necessária para alguns
    portais (ex: Dados Abertos BR) durante a busca.
    """

    def __init__(self):
        pass

    async def search_data(self, query: str, portal: PortalType = PortalType.ALL, **auth_config) -> list[Dataset]:
        """
        Busca dados em portais governamentais.
        
        Args:
            query: Termo de busca.
            portal: Portal específico ou PortalType.ALL para todos.
            **auth_config: Credenciais extras (ex: api_key para Portal BR).
        """
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
            else:
                # Logar erro se necessario
                print(f"Erro na busca: {res}")
                
        return results