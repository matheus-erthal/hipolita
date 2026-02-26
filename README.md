# Hipólita

[![Build](https://github.com/matheus-erthal/hipolita/actions/workflows/python-package.yml/badge.svg)](https://github.com/matheus-erthal/hipolita/actions/workflows/python-package.yml)
[![PyPI](https://img.shields.io/pypi/v/hipolita?color=blue)](https://pypi.org/project/hipolita/)
[![License](https://img.shields.io/pypi/l/hipolita)](https://opensource.org/licenses/MIT)

## Descrição

Implementação do framework **Hipólita**, proposto originalmente em [_Hippolyta: a framework to enhance open data interpretability and empower citizens_](https://dl.acm.org/doi/10.1145/3598469.3598559).

Hipólita facilita o acesso e a interpretação de dados governamentais abertos, fornecendo uma interface unificada para buscar, recuperar e consumir datasets de múltiplos portais nacionais — cada um com APIs, padrões de metadados e formatos de resposta diferentes.

> 📄 Para uma análise detalhada dos desafios de interoperabilidade encontrados durante a integração dos portais, consulte o [Relatório de Interoperabilidade](INTEROPERABILITY_REPORT.md).

---

## Portais Suportados

| Portal | País | URL | Chave (`PortalType`) | Plataforma / API | Autenticação |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Portal de Dados Abertos** | Brasil 🇧🇷 | [dados.gov.br](https://dados.gov.br) | `DADOS_GOV_BR` | REST API própria | Requer `api_key` |
| **Data.gov** | EUA 🇺🇸 | [data.gov](https://catalog.data.gov) | `DATA_GOV_US` | CKAN v3 | Acesso público |
| **CKAN Publishing** | Reino Unido 🇬🇧 | [ckan.publishing.service.gov.uk](https://ckan.publishing.service.gov.uk) | `DATA_GOV_UK` | CKAN v3 | Acesso público |
| **opendata.swiss** | Suíça 🇨🇭 | [opendata.swiss](https://opendata.swiss) | `OPENDATA_SWISS` | CKAN v3 (multilíngue) | Acesso público |
| **Avoindata.fi** | Finlândia 🇫🇮 | [avoindata.fi](https://www.avoindata.fi) | `AVOINDATA_FI` | CKAN v3 | Acesso público |
| **data.gov.au** | Austrália 🇦🇺 | [data.gov.au](https://data.gov.au) | `DATA_GOV_AU` | CKAN v3 | Acesso público |
| **data.gouv.fr** | França 🇫🇷 | [data.gouv.fr](https://www.data.gouv.fr) | `DATA_GOUV_FR` | udata REST API | Acesso público |
| **datos.gob.es** | Espanha 🇪🇸 | [datos.gob.es](https://datos.gob.es) | `DATOS_GOB_ES` | Linked Data API | Acesso público |
| **data.gov.sg** | Singapura 🇸🇬 | [data.gov.sg](https://data.gov.sg) | `DATA_GOV_SG` | REST API v2 | Acesso público |
| **data.gov.in** | Índia 🇮🇳 | [data.gov.in](https://data.gov.in) | `DATA_GOV_IN` | OGDP REST API | Acesso público |

### Portais Investigados (Sem Integração Programática)

| Portal | País | Motivo |
| :--- | :--- | :--- |
| data.gov.cy | Chipre 🇨🇾 | Portal Drupal sem API REST pública |
| data.gov.ru | Rússia 🇷🇺 | SPA Vue.js sem endpoint de API acessível |
| data.gv.at | Áustria 🇦🇹 | Migrou para SPA; CKAN API desativada |
| data.gov.tw | Taiwan 🇹🇼 | API v1 desativada; v2 requer chave de autenticação |

---

## Instalação

```bash
pip install hipolita
```

Requer **Python 3.10+**. Dependências: `pandas`, `numpy`, `aiohttp`.

---

## Como Usar

### Busca de Datasets (`search_data`)

Busca datasets por texto em um ou mais portais simultaneamente.

```python
from hipolita import search_data, PortalType

# Busca em todos os portais públicos (BR requer api_key)
datasets = search_data("saúde", portal=PortalType.ALL, api_key="SUA_CHAVE_BR")

# Busca em um portal específico
datasets = search_data("climate", portal=PortalType.DATA_GOV_US)

# Também aceita string no lugar do enum
datasets = search_data("education", portal="data_gov_uk")
```

#### Controle de erros (`fails_silently`)

```python
# Se o portal estiver offline ou a chave for inválida, retorna [] ao invés de lançar exceção
datasets = search_data("health", portal=PortalType.DADOS_GOV_BR, fails_silently=True)
```

### Busca de Dataset Individual (`get_dataset`)

Recupera os metadados completos de um dataset específico pelo seu ID.

```python
from hipolita import get_dataset, PortalType

# Buscar um dataset por ID
dataset = get_dataset("dataset-id-123", portal=PortalType.DATA_GOV_US)

if dataset:
    print(dataset.title)
    print(dataset.description)
    for resource in dataset.resources:
        print(f"  {resource.name} ({resource.format}): {resource.url}")
```

### Download e Parse de Dados (`fetch_dataset_data`)

Busca um dataset e, se houver um recurso em formato parseável (CSV, TSV, XLS, XLSX, JSON), retorna os dados como `pandas.DataFrame`.

```python
from hipolita import fetch_dataset_data, PortalType

result = fetch_dataset_data("dataset-id-123", portal=PortalType.DATA_GOV_AU)

if not result.df.empty:
    # Dados parseados com sucesso
    print(result.df.head())
    print(f"Formato: {result.meta['format']}")
    print(f"URL: {result.meta['resource_url']}")
else:
    # Sem recurso parseável — metadados disponíveis com links
    print(f"Dataset: {result.meta.get('title')}")
    for link in result.meta.get("resource_links", []):
        print(f"  {link['name']} ({link['format']}): {link['url']}")
```

### Uso Assíncrono (`asyncio`)

Todas as funções possuem versão assíncrona com sufixo `_async`:

```python
import asyncio
from hipolita import search_data_async, get_dataset_async, fetch_dataset_data_async, PortalType

async def main():
    # Busca assíncrona em todos os portais
    datasets = await search_data_async("education", portal=PortalType.ALL)
    
    # Recuperar dataset individual
    dataset = await get_dataset_async("abc-123", portal=PortalType.DATA_GOUV_FR)
    
    # Baixar e parsear dados
    result = await fetch_dataset_data_async("abc-123", portal=PortalType.DATA_GOUV_FR)

asyncio.run(main())
```

### Classe `Hipolita`

Para quem prefere orientação a objetos, as mesmas operações estão disponíveis como métodos estáticos:

```python
from hipolita.core import Hipolita
from hipolita import PortalType

datasets = Hipolita.search_data("climate", portal=PortalType.DATA_GOV_UK)
dataset = Hipolita.get_dataset("id-123", portal=PortalType.DATA_GOV_UK)
result = Hipolita.fetch_dataset_data("id-123", portal=PortalType.DATA_GOV_UK)
```

---

## Modelo de Dados

### `Dataset`

Representa um conjunto de dados com metadados normalizados de qualquer portal.

| Campo | Tipo | Descrição |
| :--- | :--- | :--- |
| `id` | `str` | Identificador único no portal de origem |
| `title` | `str \| None` | Título do dataset |
| `description` | `str \| None` | Descrição textual |
| `resources` | `list[Resource]` | Arquivos/endpoints disponíveis |
| `tags` | `list[str]` | Palavras-chave / categorias |
| `organization` | `str \| None` | Organização publicadora |
| `license` | `str \| None` | Licença de uso |
| `source_portal` | `str \| None` | Portal de origem |

### `Resource`

Representa um arquivo ou endpoint de dados dentro de um dataset.

| Campo | Tipo | Descrição |
| :--- | :--- | :--- |
| `id` | `str` | Identificador do recurso |
| `name` | `str \| None` | Nome do arquivo/recurso |
| `format` | `str \| None` | Formato (CSV, JSON, XML, etc.) |
| `url` | `str \| None` | URL de download |

### `DataFrameWithMeta`

Retornado por `fetch_dataset_data()`. Combina dados tabulares com metadados.

| Campo | Tipo | Descrição |
| :--- | :--- | :--- |
| `df` | `pd.DataFrame` | Dados parseados (vazio se não parseável) |
| `meta` | `dict` | Metadados: `title`, `format`, `resource_url`, `resource_links` |

---

## Arquitetura

```
hipolita/
├── __init__.py              # Exports públicos
├── core.py                  # API principal (search, get_dataset, fetch_dataset_data)
├── types.py                 # Dataset, Resource, DataFrameWithMeta, PortalType
└── data_recovery/
    ├── interfaces/
    │   ├── adapter.py       # DataAdapter (ABC)
    │   └── portal.py        # Portal (ABC) + fetch_dataset_data (concreto)
    ├── adapters/
    │   ├── ckan_adapter.py  # Adaptador CKAN v3 (UK, US, CH, FI, AU)
    │   └── api_adapter.py   # Adaptador REST genérico (BR, FR, ES, SG, IN)
    └── portals/
        ├── portal_dados_abertos_br.py
        ├── portal_data_gov_us.py
        ├── portal_data_gov_uk.py
        ├── portal_opendata_swiss.py
        ├── portal_avoindata_fi.py
        ├── portal_data_gov_au.py
        ├── portal_data_gouv_fr.py
        ├── portal_datos_gob_es.py
        ├── portal_data_gov_sg.py
        └── portal_data_gov_in.py
```

A arquitetura segue o padrão **Strategy**: cada portal implementa a lógica de mapeamento de endpoints e campos, delegando operações HTTP a um adaptador compartilhado (`CkanAdapter` ou `ApiAdapter`).

---

## Desenvolvimento e Testes

### Pré-requisitos
- Python 3.10+
- [Poetry](https://python-poetry.org/) (gerenciador de dependências)

### Setup

```bash
git clone https://github.com/matheus-erthal/hipolita.git
cd hipolita
poetry install
```

### Executando Testes

```bash
poetry run pytest
```

A suíte de testes inclui **51 testes** cobrindo:
- Conectividade e parsing de resposta de cada adaptador (CKAN, API genérica)
- Busca (`search()`) em todos os 10 portais com mocks HTTP
- Recuperação individual (`get_dataset()`) para todos os portais
- Download e parse de dados (`fetch_dataset_data()`) com CSV, JSON, recursos não parseáveis
- Integração via `core.py` (funções síncronas e assíncronas)

### Testes de Integração (APIs Reais)

Para validar que os endpoints dos portais ainda estão funcionais:

```bash
poetry run pytest tests/test_integration.py -v
```

> ⚠️ Estes testes fazem requisições HTTP reais e podem falhar por indisponibilidade temporária dos portais.

## Licença

Este projeto é distribuído sob a licença [MIT](LICENSE).