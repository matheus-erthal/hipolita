def package_name():
    return "Hipólita"


import os
from typing import Optional


class Hipolita:
    """Núcleo da biblioteca Hipolita.

    Requer uma `api_key` na inicialização ou a variável de ambiente
    `HIPOLITA_API_KEY` deve estar definida.
    """

    def __init__(self, api_key: Optional[str] = None, *, default_base_url: Optional[str] = None, timeout: float = 30.0):
        # Tenta usar o parâmetro, senão fallback para env var
        key = api_key if api_key is not None else os.environ.get("HIPOLITA_API_KEY")
        if key is None or (isinstance(key, str) and key.strip() == ""):
            raise ValueError("api_key obrigatório: passe api_key para Hipolita(...) ou defina HIPOLITA_API_KEY no ambiente")
        self.api_key = key
        self.default_base_url = default_base_url
        self.timeout = float(timeout)

    def __repr__(self) -> str:  # pragma: no cover - trivial
        return f"Hipolita(api_key={'***' if self.api_key else None}, default_base_url={self.default_base_url}, timeout={self.timeout})"