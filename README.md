# Hipólita

[![Build](https://github.com/matheus-erthal/hipolita/actions/workflows/python-package.yml/badge.svg)](https://github.com/matheus-erthal/hipolita/actions/workflows/python-package.yml)
[![PyPI](https://img.shields.io/pypi/v/hipolita?color=blue)](https://pypi.org/project/hipolita/)
[![License](https://img.shields.io/pypi/l/hipolita)](https://opensource.org/licenses/MIT)

## Descrição

Este projeto é uma implementação do framework **Hipólita**, proposto inicialmente em [_Hippolyta: a framework to enhance open data interpretability and empower citizens_](https://dl.acm.org/doi/10.1145/3598469.3598559).

O Hipólita foi projetado para facilitar o acesso e interpretação de dados abertos governamentais, fornecendo módulos especializados para enriquecer, recuperar e visualizar informações.

---

## Módulos do Hipólita

### 1. Módulo de Enriquecimento Semântico

Este módulo utiliza **Processamento de Linguagem Natural (PLN)**, por meio do processo de **Part-of-Speech (POS) Tagging**, para ressaltar os conceitos mais importantes das solicitações dos usuários.

### 2. Módulo de Recuperação da Informação

Este módulo faz conexão com diversas **bases de dados governamentais** para recuperar as informações, utilizando diferentes estratégias e implementações de conectores.

### 3. Módulo de Visualização de Dados

Este módulo apresenta os dados obtidos pelo **Módulo de Recuperação da Informação**, formatados dentro da visualização definida pelo tipo e formato de dados retornados.

---

## Instalação

Você pode instalar a versão mais recente do Hipólita diretamente do **PyPI**:

```bash
pip install hipolita
```