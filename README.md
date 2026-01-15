# Hipolita

[![Build](https://github.com/matheus-erthal/hipolita/actions/workflows/python-package.yml/badge.svg)](https://github.com/matheus-erthal/hipolita/actions/workflows/python-package.yml)
[![PyPI](https://img.shields.io/pypi/v/hipolita?color=blue)](https://pypi.org/project/hipolita/)
[![License](https://img.shields.io/pypi/l/hipolita)](https://opensource.org/licenses/MIT)

## Description

This project is an implementation of the **Hipolita** framework, originally proposed in [_Hippolyta: a framework to enhance open data interpretability and empower citizens_](https://dl.acm.org/doi/10.1145/3598469.3598559).

Hipolita was designed to facilitate access and interpretation of governmental open data, providing specialized modules for enriching, recovering, and visualizing information.

---

## Hipolita Modules

### 1. Semantic Enrichment Module

This module uses **Natural Language Processing (NLP)**, through **Part-of-Speech (POS) Tagging**, to highlight the most important concepts from user requests.

### 2. Information Retrieval Module

This module connects to various **government databases** to retrieve information, using different connector strategies and implementations.

#### Supported Portals

| Portal | Country | URL | Key | Authentication |
| :--- | :--- | :--- | :--- | :--- |
| **Brazilian Open Data Portal** | Brazil 🇧🇷 | [dados.gov.br](https://dados.gov.br) | `dados_gov_br` | Requires `api_key` |
| **Data.gov** | USA 🇺🇸 | [data.gov](https://data.gov) | `data_gov_us` | Public Access |

### 3. Data Visualization Module

This module presents the data obtained by the **Information Retrieval Module**, formatted according to the visualization rules defined by the data type and format.

---

## Installation

You can install the latest version of Hipolita directly from **PyPI**:

```bash
pip install hipolita
```

---

## How to Use

Hipolita provide a simplified interface for searching data in government portals.

### Basic Example (Synchronous Search)

By default, the `search_data` function is synchronous and blocks execution until the search is complete.

```python
from hipolita import search_data

# Direct synchronous search
datasets = search_data("health", api_key="YOUR_BR_API_KEY")
```

### Error Control (`fails_silently`)

You can use the `fails_silently=True` parameter to prevent exceptions from interrupting your code (useful in loops or automation scripts).

```python
# If the key is wrong or the portal is offline, just log and return []
datasets = search_data(
    "health", 
    portal="dados_gov_br", 
    fails_silently=True
)
```

### Async Example (asyncio)

For applications using `asyncio`, use the `search_data_async` function.

```python
import asyncio
from hipolita import search_data_async, PortalType

async def main():
    # Asynchronous search
    datasets = await search_data_async("education", portal=PortalType.ALL, api_key="...")
    print(f"Found {len(datasets)} datasets.")

if __name__ == "__main__":
    asyncio.run(main())
```

### Searching in a Specific Portal

You can filter the search using the `PortalType` enum.

```python
from hipolita import search_data, PortalType

# Search only in the US portal (Data.gov)
results = search_data("climate", portal=PortalType.DATA_GOV_US)
```

---

## Development and Testing

To contribute or test the project locally:

### Prerequisites
- Python 3.10 or higher
- [Poetry](https://python-poetry.org/) (Dependency manager)

### Setup
Clone the repository and install dependencies:

```bash
poetry install
```

### Running Tests
The project has automated tests to verify connectivity and adapter mapping. To run them:

```bash
poetry run pytest
```

This will run the test suite in `tests/`, covering:
- Connection with API mocks.
- Response parsing.
- JSON-to-`Dataset` mapping.