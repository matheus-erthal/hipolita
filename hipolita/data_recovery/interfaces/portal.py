from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from ...types import Dataset

class Portal(ABC):
    """
    Classe base para portais de dados específicos (e.g. Dados.gov.br, Data.gov).
    Gerencia a tradução entre o modelo de dados do Hipólita e a implementação específica do adaptador.
    """

    def __init__(self, **config):
        self.config = config

    @abstractmethod
    async def search(self, query: str) -> List[Dataset]:
        """
        Busca datasets no portal padronizando a saída para o modelo Dataset do Hipólita.
        """
        pass

    @abstractmethod
    async def get_dataset(self, dataset_id: str) -> Optional[Dataset]:
        """
        Obtém dataset detalhado pelo ID.
        """
        pass