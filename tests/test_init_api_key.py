import os
import pytest
from hipolita.core import Hipolita


def test_init_with_api_key_param():
    h = Hipolita(api_key="my-key")
    assert h.api_key == "my-key"


def test_init_with_env_var(monkeypatch):
    monkeypatch.delenv("HIPOLITA_API_KEY", raising=False)
    monkeypatch.setenv("HIPOLITA_API_KEY", "env-key")
    h = Hipolita()
    assert h.api_key == "env-key"


def test_init_raises_when_no_key(monkeypatch):
    monkeypatch.delenv("HIPOLITA_API_KEY", raising=False)
    with pytest.raises(ValueError):
        Hipolita()
