# Relatório de Interoperabilidade: Portais Nacionais de Dados Abertos Governamentais

## 1. Resumo Executivo

Este relatório documenta os desafios de interoperabilidade encontrados durante a integração de 12 portais nacionais de dados abertos governamentais ao framework Hipólita. Dos 12 países analisados, 8 foram integrados com sucesso e 4 apresentaram barreiras técnicas intransponíveis. A análise revela uma fragmentação significativa nos padrões de API, esquemas de metadados e políticas de acesso, evidenciando os desafios fundamentais da interoperabilidade em dados abertos governamentais.

**Países analisados:** Brasil, Estados Unidos, Chipre, Rússia, França, Espanha, Taiwan, Reino Unido, Singapura, Suíça, Finlândia, Índia, Austrália, Áustria.

**Data da análise:** Fevereiro de 2026.

---

## 2. Metodologia

A análise foi conduzida por meio de:
1. **Descoberta de API:** Tentativa sistemática de localizar endpoints REST/JSON em cada portal, testando padrões CKAN v3, DCAT-AP, e endpoints proprietários.
2. **Teste de conectividade:** Requisições HTTP reais para validar disponibilidade e formato de resposta.
3. **Mapeamento de esquema:** Análise da estrutura de metadados retornada por cada API e mapeamento para um modelo unificado (`Dataset`, `Resource`).
4. **Implementação e testes:** Desenvolvimento de integrações com testes automatizados usando mocks HTTP.

---

## 3. Classificação dos Portais por Padrão de API

### 3.1 Portais CKAN v3 (5 países)

| País | URL Base | Versão CKAN | Status |
|------|----------|-------------|--------|
| Estados Unidos | `catalog.data.gov` | v3 | ✅ Integrado |
| Reino Unido | `ckan.publishing.service.gov.uk` | v3 | ✅ Integrado |
| Suíça | `opendata.swiss` | v3 | ✅ Integrado |
| Finlândia | `www.avoindata.fi/data` | v3 | ✅ Integrado |
| Austrália | `data.gov.au` | v3 | ✅ Integrado |

**Observação:** O CKAN é o padrão de facto mais adotado, porém mesmo entre portais CKAN há variações significativas nos metadados (Seção 5).

### 3.2 Portais com API Proprietária (5 países)

| País | URL Base | Plataforma | Status |
|------|----------|------------|--------|
| Brasil | `dados.gov.br/dados/api/publico/` | API REST (requer API key) | ✅ Integrado |
| França | `www.data.gouv.fr/api/1/` | udata | ✅ Integrado |
| Espanha | `datos.gob.es/apidata/` | Linked Data API | ✅ Integrado |
| Singapura | `api-production.data.gov.sg/v2/` | Custom REST | ✅ Integrado |
| Índia | `data.gov.in/backend/dmspublic/v1/` | OGDP (custom) | ✅ Integrado |

### 3.3 Portais sem Integração Programática (4 países)

| País | URL Base | Problema | Portal Funcional | Status |
|------|----------|----------|------------------|--------|
| Chipre | `data.gov.cy` | Sem API pública (migração para Drupal) | ✅ Navegação HTML manual | ❌ Não integrado |
| Rússia | `data.gov.ru` | SPA-only, sem REST API acessível | ✅ Navegação HTML manual | ❌ Não integrado |
| Áustria | `data.gv.at/katalog/` | CKAN desativado (migração para SPA Vue.js) | ✅ Navegação HTML manual | ❌ Não integrado |
| Taiwan | `data.gov.tw` | API de busca requer API Key (POST); GET retorna 405 | ✅ Navegação HTML manual + API individual | ❌ Não integrado |

**Nota:** Todos os 4 portais acima possuem interfaces web funcionais que permitem a navegação e download manual de datasets por um usuário humano. A barreira é exclusivamente de integração programática — não foi encontrada nenhuma API pública ou endpoint CKAN acessível sem autenticação para operações de busca.

---

## 4. Barreiras Técnicas à Interoperabilidade

### 4.1 Migração de Plataforma sem Manutenção de API (Chipre, Áustria)

**Chipre (data.gov.cy):** O portal nacional cipriota migrou de uma plataforma CKAN para um sistema baseado em Drupal em fevereiro de 2024. A nova plataforma não expõe nenhuma API REST/JSON pública documentada. Todas as tentativas de acesso via CKAN v3 (`/api/3/action/`), JSON:API (`/jsonapi/node/dataset`), e DKAN (`/api/1/datasets`) retornaram HTTP 404. O portal existe e permite navegação e download manual de datasets via interface HTML, mas não oferece nenhuma forma de integração programática via API ou CKAN.

**Áustria (data.gv.at):** O catálogo austríaco (`data.gv.at/katalog/`) foi migrado para uma Single-Page Application (SPA) baseada em Vue.js. Todos os endpoints anteriores da CKAN API (`/katalog/api/3/action/package_search`, `/katalog/api/action/package_search`, etc.) agora retornam o HTML do SPA em vez de respostas JSON. A API CKAN que existia anteriormente foi completamente desativada sem substituto público conhecido. Os dados continuam acessíveis via navegação HTML no portal, porém a obtenção programática é impossível — restando apenas a navegação manual pelo navegador.

**Implicação:** A migração de plataforma sem manutenção de backward compatibility da API é uma das principais causas de perda de interoperabilidade. Portais que mudam de infraestrutura frequentemente quebram integrações existentes de forma silenciosa. Os dados permanecem disponíveis para consumo humano, mas deixam de ser interoperáveis para consumo automatizado.

### 4.2 Arquitetura SPA sem API Backend Acessível (Rússia)

**Rússia (data.gov.ru):** O portal russo de dados abertos é inteiramente uma Single-Page Application JavaScript. O HTML retornado contém apenas um `<div id="app"></div>` e referências a bundles JavaScript. Nenhum endpoint de API REST foi localizado — todos os padrões testados (`/api/json/dataset`, `/api/v1/datasets`, `/api/dataset`) retornaram HTTP 404. Assim como Chipre e Áustria, o portal existe e os dados são navegáveis manualmente via interface web, porém não há qualquer integração via API ou CKAN disponível publicamente.

**Implicação:** Portais que renderizam dados exclusivamente no lado do cliente, sem expor APIs programáticas, são fundamentalmente incompatíveis com integração automatizada. Isso representa um anti-padrão significativo para dados abertos — os dados são tecnicamente "abertos" para humanos, mas fechados para máquinas.

### 4.3 API Parcialmente Funcional (Taiwan)

**Taiwan (data.gov.tw):** A API v2 REST do portal taiwanês apresenta comportamento inconsistente e restritivo:
- **Funcional sem autenticação:** `GET /api/v2/rest/dataset/{id}` retorna metadados detalhados de um dataset específico (HTTP 200, JSON válido).
- **GET bloqueado:** `GET /api/v2/rest/dataset` (listagem/busca) retorna HTTP 405 (Method Not Allowed) para todas as variações de parâmetros testadas (`?limit=`, `?q=`, `?format=json`).
- **POST protegido por API Key:** `POST /api/v2/rest/dataset` retorna `{"success":false,"error":{"error_type":"ER0001:API Key錯誤","message":"API Key錯誤: HTTP 標頭沒設定 Authorization Key"}}`, indicando que o endpoint de listagem/busca **existe** mas requer uma API Key no header `Authorization`.
- **API v1 inexistente:** Todos os endpoints testados sob `/api/v1/` (incluindo `/api/v1/datasets/search?q=`) retornam HTTP 404, indicando que a API v1 foi completamente desativada.

A descoberta de que o `POST` requer autenticação altera a classificação original: Taiwan não possui uma API "parcialmente funcional" — possui uma API completa, porém **protegida por autenticação para operações de listagem/busca**, enquanto o acesso individual permanece aberto. Esse modelo híbrido (detalhe público, busca autenticada) é incomum e não documentado publicamente.

**Implicação:** A combinação de métodos HTTP bloqueados (GET 405), autenticação obrigatória para POST, e ausência de documentação pública cria uma barreira significativa à integração. A mensagem de erro em chinês (`API Key錯誤`) agrava o problema para desenvolvedores internacionais.

### 4.4 Timeout e Indisponibilidade de Rede (Índia)

**Índia (data.gov.in):** O endpoint principal da API (`api.data.gov.in`) apresentou timeouts consistentes durante os testes. Entretanto, um endpoint alternativo (`data.gov.in/backend/dmspublic/v1/resources`) funcionou corretamente. Isso demonstra que a documentação oficial de API pode apontar para endpoints instáveis enquanto endpoints não documentados são os que funcionam.

**Implicação:** A discrepância entre a API documentada e a infraestrutura real dificulta a descoberta programática e a manutenção de integrações.

### 4.5 Autenticação Obrigatória para Leitura (Brasil)

**Brasil (dados.gov.br):** O portal brasileiro exige o envio de um header `chave-api-dados-abertos` com uma API key válida em todas as requisições, inclusive para operações de leitura (busca e acesso individual a datasets). Sem o header, o servidor retorna uma cadeia de redirects HTTP sem mensagem de erro descritiva, dificultando significativamente o diagnóstico.

**Implicação:** A autenticação obrigatória para operações de leitura é uma anti-padrão para dados abertos, pois cria uma barreira de entrada para consumidores programáticos e contradiz o princípio de acesso livre a dados públicos.

---

### 5.1 Mapeamento de Campos para Modelo Unificado

O framework Hipólita utiliza um modelo unificado `Dataset` com os campos: `id`, `title`, `description`, `resources`, `tags`, `organization`, `license`, `source_portal`. A tabela abaixo documenta o mapeamento de cada portal:

| Campo Hipólita | CKAN (US/UK/AU) | CKAN Swiss | CKAN Finland | Brasil (REST) | France (udata) | Spain (LD-API) | Singapore | India (OGDP) |
|----------------|-----------------|------------|--------------|---------------|----------------|----------------|-----------|--------------|
| `id` | `id` | `id` | `id` | `id` | `id` | `_about` (URI) | `datasetId` | `catalog_uuid[0]` |
| `title` | `title` | `title{lang}` | `title` | `title` | `title` | `title[]{_value,_lang}` | `name` | `catalog_title[0]` |
| `description` | `notes` | `notes{lang}` | `notes` | `descricao` | `description` | `description[]{_value,_lang}` | `description` | ❌ Ausente |
| `resources` | `resources[]` | `resources[]` | `resources[]` | `recursos[]` | `resources[]` | `distribution` | Implícito | `datafile[0]` |
| `tags` | `tags[]{name}` | `tags[]{name}` | `keywords{lang}[]` | `palavrasChave[]{termo}` | `tags[]` (strings) | `theme[]{_about}` | ❌ Ausente | `sector_resource[]` |
| `organization` | `organization.title` | `organization.title` | `organization.title` | `nomeOrganizacao` | `organization.name` | `publisher.notation` | `managedByAgencyName` | ❌ Ausente |
| `license` | `license_title` | `license_title` | `license_title` | ❌ Ausente | `license` | ❌ Ausente | ❌ Ausente | ❌ Ausente |

### 5.2 Problemas Críticos Identificados

**5.2.1 Identificadores Heterogêneos**
- **CKAN:** UUIDs padrão (ex: `c1e6282d-b84d-4720-b759-82913c3a287e`)
- **Espanha:** URIs completas (ex: `https://datos.gob.es/catalogo/e05068001-mapas-estrategicos-de-ruido`)
- **Singapura:** IDs com prefixo `d_` + hash (ex: `d_89899f41c73fbf3457c2544c700a3869`)
- **Índia:** UUIDs em arrays (ex: `["a4502c26-caa1-401e-83a2-a794272cf0a9"]`)
- **França:** IDs alfanuméricos (ex: `5369a225a3a729239d206786`)

Não há um padrão universal de identificação de datasets, o que impossibilita referências cruzadas entre portais.

**5.2.2 Valores Escalares vs. Arrays**
A API da Índia (OGDP) encapsula todos os valores em arrays, mesmo quando representam campos escalares:
```json
{"title": ["Resource Title"], "uuid": ["unique-id"], "file_size": [4398]}
```
Isso exige tratamento especial de extração (`value[0]`) que nenhum outro portal requer.

**5.2.3 Ausência de Campos Críticos**
- **Descrição:** Ausente na API da Índia
- **Tags/Categorias:** Ausente em Singapura
- **Licença:** Ausente em Espanha, Singapura e Índia
- **Organização:** Ausente na Índia

A ausência de campos de metadados varia significativamente, o que reduz a qualidade de buscas agregadas cross-portal.

---

## 6. Desafios de Multilinguismo

### 6.1 Três Abordagens Distintas para Campos Multilíngues

**Abordagem 1 — Dicionário por idioma (Suíça):**
```json
{"title": {"de": "Schweizer Datensatz", "fr": "Jeu de données suisse", "en": "Swiss Dataset"}}
```

**Abordagem 2 — Lista de objetos com tag de idioma (Espanha):**
```json
{"title": [{"_value": "Conjunto de datos", "_lang": "es"}, {"_value": "Test Dataset", "_lang": "en"}]}
```

**Abordagem 3 — Keywords/Tags multilíngues como dicionário de listas (Finlândia):**
```json
{"keywords": {"fi": ["terveys", "data"], "en": ["health", "data"]}}
```

Cada abordagem requer lógica de extração diferente, e a escolha do idioma preferido (com fallbacks) precisa ser implementada caso a caso. Não existe um padrão uniforme para campos multilíngues em dados abertos governamentais.

### 6.2 Impacto na Busca

O multilinguismo afeta também a busca: uma query em inglês pode não retornar resultados relevantes em portais com metadados primariamente em outro idioma (francês na Suíça, finlandês na Finlândia, espanhol na Espanha). Não há mecanismo padrão de tradução ou busca cross-linguística.

---

## 7. Desafios na Estrutura de Recursos (Resources/Distributions)

### 7.1 Variações na Representação de Recursos

| Portal | Estrutura | URL Direta | Formato |
|--------|-----------|------------|---------|
| CKAN (4 portais) | Array de objetos com `id`, `url`, `format` | ✅ Sim | String simples |
| França | Array de objetos com `id`, `url`, `format`, `mime` | ✅ Sim | String simples |
| Espanha | `distribution` (objeto ou array) com `accessURL`, `format{label[]}` | ✅ Sim | Aninhado em objeto |
| Singapura | Implícito no dataset (1 recurso = 1 dataset) | ❌ Não (sem URL) | Campo `format` no dataset |
| Índia | Campo `datafile[0]` com URL direta | ✅ Sim | MIME type em `file_format[0]` |

### 7.2 Problemas Identificados

- **Singapura** não fornece URLs de download direto na resposta da API de listagem. O acesso aos dados requer uma segunda chamada à API de detalhe do dataset.
- **Espanha** pode retornar `distribution` como objeto único ou como array, exigindo tratamento condicional.
- **O formato de arquivo** é representado de maneiras incompatíveis: string simples ("CSV"), MIME type ("text/csv"), ou aninhado em objeto JSON.

---

## 8. Capacidade de Busca Textual

| Portal | Busca por Texto | Parâmetro | Observação |
|--------|----------------|-----------|------------|
| CKAN (US, UK, CH, FI, AU) | ✅ Sim | `q=` | Busca full-text no CKAN Solr |
| Brasil | ✅ Sim | `nomeConjuntoDados=` | Filtra por nome, requer API key |
| França | ✅ Sim | `q=` | Busca full-text |
| Espanha | ❌ Não | — | API lista datasets sem filtro por texto |
| Singapura | ✅ Sim | `query=` | Busca por nome |
| Índia | ✅ Parcial | `filters[title]=` | Filtra apenas no campo título |
| Taiwan | ❌ N/A | — | Endpoint de busca retorna 405 |

**Observação crítica:** A Espanha não oferece busca textual na sua Linked Data API. A integração lista os datasets mais recentes sem possibilidade de filtrar por termos de busca, o que reduz significativamente a utilidade para buscas direcionadas.

---

## 9. Análise Comparativa de Padrões Técnicos

### 9.1 Protocolos e Formatos de Resposta

| Aspecto | CKAN v3 | REST BR | udata (FR) | LD-API (ES) | Custom (SG, IN) |
|---------|---------|---------|------------|-------------|-----------------|
| Protocolo | REST/JSON | REST/JSON | REST/JSON | REST/JSON-LD | REST/JSON |
| Autenticação | Opcional | Obrigatória (API key) | Não | Não | Não |
| Paginação | `rows` + `start` | `pagina` + `registrosPorPagina` | `page` + `page_size` | `_page` + `_pageSize` | `page` / `offset+limit` |
| Envelope de resposta | `{success, result{results[]}}` | `{conjuntosDados[]}` | `{data[]}` | `{result{items[]}}` | Variado |
| Content-Type | `application/json` | `application/json` | `application/json` | `application/json` | `application/json` |

### 9.2 Aderência a Padrões Internacionais

| Padrão | Portais que Utilizam |
|--------|---------------------|
| CKAN v3 API | US, UK, Suíça, Finlândia, Austrália (5/14) |
| DCAT-AP | Espanha (parcial via Linked Data) |
| Schema.org | Nenhum diretamente na API |
| OGC/INSPIRE | Nenhum diretamente na API |
| Padrão proprietário | Brasil, França, Singapura, Índia, Taiwan, Rússia, Chipre, Áustria (8/14) |

A maioria dos portais (8 de 14) utiliza alguma forma de API proprietária, evidenciando a baixa adoção de padrões interoperáveis.

---

## 10. Síntese das Dificuldades de Interoperabilidade

### 10.1 Ranking por Nível de Dificuldade

| Nível | Dificuldade | Portais |
|-------|-------------|---------|
| 1 — Trivial | Mesma API (CKAN), mesmos campos | US, UK, Austrália |
| 2 — Baixa | Mesma API (CKAN), campos multilíngues | Suíça, Finlândia |
| 3 — Média | API diferente, boa documentação, campos mapeáveis | França, Brasil |
| 4 — Alta | API diferente, formato não-padrão, campos complexos | Espanha, Singapura, Índia |
| 5 — Inviável | Sem API acessível ou funcional | Chipre, Rússia, Áustria, Taiwan |

### 10.2 Categorias de Problemas

1. **Fragmentação de plataformas:** 6+ plataformas distintas entre 14 países.
2. **Obsolescência silenciosa:** 3 portais com APIs desativadas sem aviso (Chipre, Áustria, Taiwan parcial).
3. **Heterogeneidade de esquema:** Nenhum campo de metadados é representado da mesma forma em todos os portais.
4. **Multilinguismo não padronizado:** 3 abordagens distintas para internacionalização de metadados.
5. **Busca inconsistente:** Capacidade de busca textual varia de full-text a inexistente.
6. **Encapsulamento de valores:** Valores escalares em arrays (Índia), URIs como IDs (Espanha), prefixos de hash (Singapura).
7. **Autenticação obrigatória:** O portal brasileiro exige API key para qualquer operação, inclusive busca.

---

## 11. Acesso Individual a Datasets (`get_dataset`)

### 11.1 Capacidade por Portal

A funcionalidade de buscar metadados de um dataset específico por ID é essencial para integrações profundas. A tabela abaixo documenta o suporte e o endpoint utilizado por cada portal:

| Portal | Suporte | Endpoint | Formato da Resposta |
|--------|---------|----------|---------------------|
| Estados Unidos | ✅ Sim | `GET /api/3/action/package_show?id={id}` | CKAN padrão: `{success, result}` |
| Reino Unido | ✅ Sim | `GET /api/3/action/package_show?id={id}` | CKAN padrão: `{success, result}` |
| Suíça | ✅ Sim | `GET /api/3/action/package_show?id={id}` | CKAN padrão (multilíngue) |
| Finlândia | ✅ Sim | `GET /api/3/action/package_show?id={id}` | CKAN padrão (keywords multilíngues) |
| Austrália | ✅ Sim | `GET /api/3/action/package_show?id={id}` | CKAN padrão: `{success, result}` |
| Brasil | ✅ Sim | `GET /dados/api/publico/conjuntos-dados/{id}` | Objeto JSON direto (requer API key) |
| França | ✅ Sim | `GET /api/1/datasets/{id}/` | Objeto JSON direto (mesmo formato da lista) |
| Espanha | ✅ Sim | `GET /apidata/catalog/dataset/{slug}` | Linked Data: `{result: {items: [...]}}` |
| Singapura | ✅ Sim | `GET /v2/public/api/datasets/{id}/metadata` | `{code: 0, data: {...}}` |
| Índia | ✅ Sim | `GET /backend/dmspublic/v1/resources?filters[uuid]={id}` | Mesma estrutura da busca, filtrada |
| Chipre | ❌ Não | — | Sem API |
| Rússia | ❌ Não | — | Sem API |
| Áustria | ❌ Não | — | API desativada |
| Taiwan | ⚠️ Parcial | `GET /api/v2/rest/dataset/{id}` | Funcional, porém busca retorna 405 |

### 11.2 Variações Significativas

**11.2.1 Tipo de Identificador Requerido**

O tipo de identificador aceito pelo endpoint de detalhe varia entre portais:

| Portal | Tipo de ID | Exemplo |
|--------|-----------|---------|
| CKAN (US, UK, CH, FI, AU) | UUID ou slug | `c1e6282d-b84d-4720-b759-82913c3a287e` |
| Brasil | ID numérico | `12345` |
| França | UUID alfanumérico | `5369a225a3a729239d206786` |
| Espanha | Slug de URL | `e05068001-mapas-estrategicos-de-ruido` |
| Singapura | ID prefixado | `d_89899f41c73fbf3457c2544c700a3869` |
| Índia | UUID | `a4502c26-caa1-401e-83a2-a794272cf0a9` |

A ausência de um padrão universal de identificação impossibilita o uso de um único ID para referenciar o mesmo dataset em portais diferentes.

**11.2.2 Diferenças de Campo na Resposta Individual vs. Busca**

Alguns portais retornam campos diferentes no endpoint de detalhe comparado ao endpoint de busca:

- **Singapura:** O endpoint de busca usa `managedByAgencyName`, enquanto o de detalhe (`/metadata`) usa `managedBy`. Essa inconsistência interna requer normalização na camada de integração.
- **Espanha:** O endpoint de detalhe retorna o mesmo formato Linked Data que a listagem, com o dataset em `result.items[0]`.
- **Índia:** O endpoint de detalhe utiliza o mesmo endpoint da busca com filtro `filters[uuid]`, resultando na mesma estrutura de resposta.

**11.2.3 Sufixos e Construção de URL**

A construção de URLs para acesso individual segue padrões incompatíveis:

- **CKAN:** Parâmetro de query (`?id=`), não path parameter
- **Brasil/França/Espanha:** Path parameter (`/{id}`)
- **Singapura:** Path parameter com sufixo obrigatório (`/{id}/metadata` — sem `/metadata` retorna 404)
- **Índia:** Parâmetro de filtro (`?filters[uuid]=`)

### 11.3 Implicações para Interoperabilidade

Todos os 10 portais integrados suportam acesso individual a datasets, porém com 5 padrões de URL distintos. A funcionalidade `get_dataset()` no framework Hipólita abstrai essas diferenças, apresentando uma interface unificada (`get_dataset(dataset_id, portal)`) que oculta a complexidade de cada implementação.

O caso de Taiwan é notável: o acesso individual funciona (`GET /api/v2/rest/dataset/{id}`), mas a busca falha. Isso sugere que o portal tem capacidade de servir dados individuais mas restringe listagens/buscas, possivelmente por questões de carga.

---

## 12. Recomendações para Padronização

### 12.1 Para Governos e Operadores de Portais

1. **Manter APIs estáveis durante migrações:** Ao migrar de plataforma, manter um período de transição com a API anterior ativa ou fornecer um mapeamento de endpoints.
2. **Adotar DCAT-AP como vocabulário mínimo:** Mesmo com plataformas proprietárias, expor metadados no formato DCAT-AP via endpoint dedicado.
3. **Documentar e versionar APIs:** Fornecer documentação OpenAPI/Swagger e manter versionamento explícito.
4. **Evitar SPAs sem API backend:** Garantir que todo dado visualizável no portal também seja acessível via API programática.
5. **Padronizar multilinguismo:** Adotar uma convenção única (preferencialmente o padrão JSON-LD com `@language`) para campos multilíngues.

### 12.2 Para Pesquisadores e Desenvolvedores de Frameworks

1. **Implementar padrão de adaptadores:** O padrão Adapter usado pelo Hipólita (separação entre adaptador de protocolo e portal específico) demonstrou-se eficaz para isolar variações.
2. **Priorizar CKAN:** Portais CKAN representam o caminho de menor resistência para integração, cobrindo ~33% dos portais testados.
3. **Implementar discovery automático:** Criar mecanismos de detecção automática de tipo de API (CKAN, udata, DCAT-AP) baseados em probing de endpoints conhecidos.
4. **Tratamento robusto de campos ausentes:** Assumir que qualquer campo de metadados pode estar ausente e implementar fallbacks graceful.

---

## 13. Conclusão

A análise de 14 portais nacionais revelou que **a interoperabilidade em dados abertos governamentais permanece um desafio significativo em 2026**. Embora o CKAN sirva como um padrão de facto para uma parcela dos portais (5 de 14), a maioria opera com APIs proprietárias ou, pior, sem API acessível. A fragmentação se manifesta em múltiplos níveis: protocolos de acesso, esquemas de metadados, capacidades de busca, tratamento de multilinguismo e acesso individual a datasets.

A implementação da funcionalidade `get_dataset()` revelou que todos os 10 portais integrados suportam acesso individual, porém com 5 padrões de URL completamente distintos — incluindo um caso (Singapura) onde a inconsistência interna entre campos da API de busca e de detalhe evidencia falhas de design de API.

Os 4 portais que não puderam ser integrados (29% da amostra) representam uma perda significativa de cobertura, especialmente considerando que suas barreiras são puramente técnicas — não relacionadas a restrições legais ou de licenciamento. O caso do Brasil, que é o único portal a exigir autenticação para operações de leitura, demonstra que mesmo portais funcionais podem criar barreiras desnecessárias ao acesso programático.

A recomendação central é que governos tratem suas APIs de dados abertos como infraestrutura pública de longo prazo, com os mesmos padrões de estabilidade e documentação aplicados a serviços digitais críticos.

---

## 14. Limitações e Ameaças à Validade

Esta seção documenta as limitações metodológicas e técnicas deste trabalho, relevantes para avaliar a generalização dos resultados em contexto científico.

### 14.1 Limitações da Amostra

- **Tamanho:** 14 países constituem uma amostra limitada frente aos 193 estados membros da ONU. Portais subnacionais (estaduais, municipais) não foram considerados.
- **Critério de seleção:** Os países foram selecionados por conveniência e disponibilidade, não por um critério sistemático (e.g., índice ODIN de maturidade de dados abertos, PIB, região geográfica). Isso introduz potencial viés de seleção.
- **Cobertura geográfica:** A amostra concentra-se na Europa (7 países) e Ásia (4), com representação limitada da África (0), América Latina (1) e Oceania (1).

### 14.2 Limitações Temporais

- **Snapshot único:** Todas as análises de API foram realizadas em um único período (Fevereiro de 2026). Não há análise longitudinal de disponibilidade, estabilidade ou evolução dos endpoints.
- **Volatilidade de APIs:** APIs governamentais podem ser alteradas, desativadas ou migradas sem aviso prévio. Os resultados refletem o estado dos portais no momento da análise e podem se tornar desatualizados.
- **Ausência de métricas temporais:** Não foram coletadas métricas de tempo de resposta, uptime, taxa de erro ou throughput. A análise é puramente funcional (funciona/não funciona), sem dimensão quantitativa de desempenho.

### 14.3 Limitações Técnicas

- **Testes mock-only:** Os 51 testes automatizados utilizam respostas HTTP mockadas (`aioresponses`). Eles validam a lógica de mapeamento e parsing do código, mas **não validam interoperabilidade real** com os portais. Testes de integração real (incluídos no repositório) devem ser executados separadamente para validar os endpoints.
- **Descoberta ad-hoc de endpoints:** A metodologia de "descoberta de API" consistiu em tentativa e erro com padrões conhecidos (CKAN, DCAT-AP, REST), análise de documentação disponível e inspeção de tráfego de rede. Não há garantia de que todos os endpoints disponíveis foram encontrados — especialmente para portais sem documentação (Chipre, Rússia, Áustria).
- **Busca textual limitada:** O portal espanhol (`datos.gob.es`) não suporta busca textual via API — a função `search()` retorna datasets recentes independentemente do termo de busca. Isso compromete a comparabilidade direta com outros portais.
- **Paginação inconsistente:** O framework busca apenas a primeira página de resultados de cada portal. Não foi analisada a implementação completa de paginação cross-portal.
- **Localização geográfica única:** Todas as requisições foram feitas de uma única localização. Latência, disponibilidade e geo-restrições podem variar conforme a origem da requisição.

### 14.4 Limitações de Análise

- **Sem análise DCAT-AP:** O relatório menciona o padrão DCAT-AP (Data Catalog Vocabulary - Application Profile) mas não analisa sistematicamente se os portais expõem endpoints DCAT ou SPARQL, que poderiam oferecer uma camada adicional de interoperabilidade.
- **Sem análise de qualidade de dados:** O foco é no acesso programático (API), não na qualidade dos dados retornados (completude de metadados, atualidade, acurácia, formato dos arquivos).
- **Sem análise de licenciamento comparativo:** Embora licenças sejam mencionadas como campo de metadados, não há análise comparativa das políticas de licenciamento entre portais.
- **Modelo unificado simplificado:** O modelo `Dataset`/`Resource` utilizado é deliberadamente genérico. Campos específicos de cada portal que não mapeiam para o modelo unificado são descartados, resultando em perda de informação.

### 14.5 Ameaças à Reprodutibilidade

- **Autenticação do portal brasileiro:** O portal `dados.gov.br` requer uma chave de API (`api_key`) para todas as operações, incluindo leitura. Pesquisadores que desejem reproduzir os resultados precisarão obter sua própria chave via cadastro no portal.
- **Dependências de versão:** O `pyproject.toml` utiliza ranges de versão (e.g., `pandas ^2.0.0`) em vez de versões exatas. Comportamentos podem variar com atualizações de dependências.
- **Mudanças de infraestrutura dos portais:** Vários portais analisados (Áustria, Taiwan) demonstraram migração recente de plataforma. Portais atualmente funcionais podem migrar no futuro, invalidando integrações existentes.

### 14.6 Recomendações para Trabalhos Futuros

Para mitigar as limitações acima em trabalhos futuros:
1. **Ampliar amostra:** Utilizar critério sistemático de seleção (e.g., países do Open Government Partnership, top-50 do ODIN ranking).
2. **Análise longitudinal:** Monitorar endpoints periodicamente (e.g., semanal/mensal) para capturar métricas de disponibilidade e estabilidade.
3. **Métricas quantitativas:** Coletar tempo de resposta, completude de metadados (% de campos preenchidos), e conformidade DCAT-AP.
4. **Testes distribuídos:** Executar testes de múltiplas localizações geográficas para detectar geo-restrições.
5. **Análise de qualidade:** Avaliar a qualidade dos dados retornados (não apenas da API), incluindo formato, encoding, e integridade dos arquivos de recurso.

---

## Apêndice A — Endpoints Testados por Portal

### Chipre (data.gov.cy)
- `https://www.data.gov.cy/api/3/action/package_search` → 404
- `https://data.gov.cy/api/3/action/package_search` → 404
- `https://data.gov.cy/api/action/package_search` → 404
- `https://www.data.gov.cy/index.php/api/3/action/package_search` → 404
- `https://www.data.gov.cy/index.php/jsonapi/node/dataset` → 404
- `https://data.gov.cy/el/api/1/datasets` → 404
- `https://ckan.data.gov.cy/api/3/action/package_search` → DNS/Connection failure

### Rússia (data.gov.ru)
- `https://data.gov.ru/api/json/dataset` → 404
- `https://data.gov.ru/api/v1/datasets` → 404
- `https://data.gov.ru/api/dataset` → 404
- Homepage retorna SPA JavaScript (Vue.js) sem API backend acessível.

### Áustria (data.gv.at)
- `https://www.data.gv.at/katalog/api/3/action/package_search` → HTML (SPA)
- `https://data.gv.at/katalog/api/3/action/package_search` → HTML (SPA)
- `https://www.data.gv.at/katalog/api/action/package_search` → HTML (SPA)
- `https://ckan.data.gv.at/api/3/action/package_search` → DNS/Connection failure
- `https://www.data.gv.at/katalog/api/3/action/status_show` → HTML (SPA)
- `https://www.data.gv.at/katalog/api/3/action/package_list` → HTML (SPA)
- Todos os endpoints sob `/katalog/api/` retornam o SPA catch-all.

### Taiwan (data.gov.tw)
- `https://data.gov.tw/api/v2/rest/dataset?limit=1` → 405 Method Not Allowed
- `https://data.gov.tw/api/v2/rest/dataset?q=health&limit=3` → 405
- `https://data.gov.tw/api/v2/rest/dataset?format=json&limit=1` → 405
- `https://data.gov.tw/api/v2/rest/dataset/6564` → 200 ✅ (apenas acesso individual)
- `https://data.gov.tw/api/front/dataset/list` → 405
- `https://data.gov.tw/api/front/dataset/search` → 404
- `POST https://data.gov.tw/api/v2/rest/dataset` → 200, mas `{"success":false,"error":{"error_type":"ER0001:API Key錯誤"}}` (requer Authorization Key)
- `https://data.gov.tw/api/v1/datasets/search?q=health` → 404
- `https://data.gov.tw/api/v1/datasets?q=health` → 404
- `https://data.gov.tw/api/v1/rest/dataset/search?q=health` → 404
- `https://data.gov.tw/api/v1/search/datasets?q=health` → 404
- `https://data.gov.tw/api/datasets?q=health` → 404

### Índia (data.gov.in) — endpoint principal vs. alternativo
- `https://api.data.gov.in/resource?api-key=...&format=json` → Timeout
- `https://api.data.gov.in/lists?format=json` → Connection failure
- `https://data.gov.in/backend/dmspublic/v1/resources?format=json&limit=1` → 200 ✅
