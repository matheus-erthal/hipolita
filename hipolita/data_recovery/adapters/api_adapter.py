from typing import Any, Dict, List, Optional
import aiohttp
import pandas as pd
import io
from ..interfaces.adapter import DataAdapter

class ApiAdapter(DataAdapter):
    """
    Adaptador genérico para APIs REST.
    Permite fazer requisições GET/POST arbitrárias.
    """

    async def connect(self) -> bool:
        """
        Testa conexão básica com a URL base.
        """
        if not self.session:
            return False
            
        try:
            # Tenta GET na raiz
            async with self.session.get(self.base_url) as response:
                 # Aceita qualquer status que indique servidor online (mesmo 404/403/400)
                 # Se der erro de conexão (DNS, timeout), lança exceção capturada abaixo
                 return True
        except:
            return False

    async def fetch_resource(self, resource_url: str) -> pd.DataFrame:
        if not self.session:
             raise RuntimeError("Session not initialized")
        
        async with self.session.get(resource_url) as response:
            if response.status == 200:
                content = await response.read()
                try:
                    return pd.read_csv(io.BytesIO(content), sep=';') 
                except:
                     try:
                        return pd.read_csv(io.BytesIO(content))
                     except:
                        return pd.DataFrame()
        return pd.DataFrame()
