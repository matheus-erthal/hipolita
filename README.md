![Símbolo da amazona Hipólita](./logo.jpg)

# Hipólita 1.0.0

Este projeto é uma implementação do framework Hipólita, proposto inicialmente em _[Hippolyta: a framework to enhance open data interpretability and empower citizens](https://dl.acm.org/doi/10.1145/3598469.3598559)_.

## Introdução

Esta implementação está divida em duas partes:
- Aplicação frontend, para testes dos conceitos
- Aplicação backend, na qual o Hipólita está implementado em módulos

## Estruturação dos módulos

Os módulos do hipólita, conceitualmente definidos de acordo com a IMAGEM, estão implementados da seguinte forma:

1. **Módulo de Enriquecimento Semântico**

Este módulo utiliza Processamento de Linguagem Natural (PLN), por meio do processo de Part-of-Speech (POS) Tagging, para ressaltar os conceitos mais importantes das solicitações dos usuários.

2. **Módulo de Recuperação da Informação**

Este módulo faz conexão com a [API de Dados Abertos](https://dados.gov.br/home) do governo brasileiro. Para utilizá-la, é necessário obter uma chave de API por meio da aba [Minha Conta no gov.br](https://dados.gov.br/auth/minha-conta) e colocar a chave no ```.env``` do back-end.

3. **Módulo de Visualização de Dados**

Este módulo apresenta os dados obtidos pelo Módulo de Recuperação da Informação, formatados dentro da visualização definida pelo tipo e formato de dados retornados.

## Tecnologias utilizadas

### Front-end

A aplicação front-end foi desenvolvida usando [Next.js](https://nextjs.org/) e os componentes da biblioteca [shadcn/ui](https://ui.shadcn.com/), apenas para validar alguns conceitos. Os módulos do Hipólita são implementados no back-end.

### Back-end

A aplicação back-end foi desenvolvida com Python, usando o framework [Flask](https://flask.palletsprojects.com/), para criação das rotas para consumo via API REST.

## Como rodar o projeto - em construção

A aplicação pode ser reproduzida configurando o ```.env``` do projeto e rodando os seguintes comandos:

Obs: o comando ```make setup``` deve ser usado somente na primeira vez, ou ao haver alguma mudança relevante na aplicação.

```
make setup
make start
```
