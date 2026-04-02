# Parsing: Extraindo Dados de Documentos para I.A.
### 5º Encontro do Grupo de Estudos NLP | INF-UFG / CEIA

---

## Estrutura do Roteiro

Segue o fluxo natural de um pipeline de parsing:
**como o dado chega → pré-tratamento e extração → resultado final com comparações.**

Cada parte introduz um tipo de dado e as ferramentas adequadas para ele,
escalando em complexidade.
---

## ⚙️ Configuração Inicial

- Instalar dependências: `pymupdf`, `pdfplumber`, `pytesseract`, `Pillow`,
  `google-generativeai`, `reportlab`, `beautifulsoup4`, `docling`, `unstructured`
- `apt-get install tesseract-ocr` (para OCR no Colab)
- Importações + config da API Gemini

---

## Parte 1: Como os Dados Chegam

**Cenário:** você vai construir um pipeline de IA (RAG, fine-tuning, análise de contratos).
Antes de qualquer modelo brilhar, você precisa de **dados limpos**.

Mas os dados do mundo real chegam assim:

| Tipo de dado | Exemplo concreto |
|--------------|-----------------|
| HTML / texto com marcações | Páginas web, exports de sistemas, e-mails em HTML |
| PDF nativo (digital) | Contratos gerados por Word, políticas internas |
| PDF com tabelas | Relatórios financeiros, balanços, folha de pagamento |
| PDF complexo (misto) | Documentos com texto, tabelas, imagens, cabeçalhos hierárquicos |
| Documento escaneado | Notas fiscais fotografadas, documentos antigos digitalizados |

> Parsing é a ponte entre o documento bruto e o dado utilizável.
> Um modelo é tão bom quanto os dados que recebe. **Garbage in, garbage out.**

**Bloco 1 — Mostrando os dados brutos:**
Exibir exemplos de cada tipo (HTML cru, uma página de PDF, uma imagem de scan)
para que o público veja o desafio antes de começar a resolver.

---

## Parte 2: HTML e Texto com Marcações → Regex + BeautifulSoup

**Problema:** os dados chegaram como HTML de um sistema web (ou e-mail, ou export).
Têm tags, marcações, entidades HTML misturadas com o conteúdo útil.

### Bloco 2a — BeautifulSoup: parsing de HTML

- Receber HTML bruto (ex: tabela HTML de um sistema, página de produto)
- Usar BeautifulSoup para navegar a árvore de tags
- Extrair texto limpo, links, dados de tabelas HTML
- Mostrar que HTML tem estrutura → BS4 entende essa estrutura

### Bloco 2b — Regex como ferramenta transversal

- Usar regex para **pós-processar** o texto extraído pelo BS4:
  - Encontrar marcadores de rasura (`~~~texto~~~`, `~~riscado~~`)
  - Extrair padrões: CPFs, e-mails, datas, valores monetários
  - Limpar espaços múltiplos, quebras de linha excessivas
- **Enfatizar:** regex não é uma etapa isolada — ele aparece em **todo** pipeline
  como ferramenta de limpeza e extração de padrões

### Trade-offs

| Ferramenta | ✅ Vantagens | ❌ Limitações |
|-----------|-------------|-------------|
| **BeautifulSoup** | Entende a árvore HTML, navega por tags | Só funciona com HTML/XML |
| **Regex** | Rápido, sem dependências, controle total | Frágil com formatos variáveis, não entende semântica |

> **Transição:** HTML está resolvido. Mas a maioria dos documentos
> corporativos está em **PDF**. BS4 não lê PDFs, regex não abre binários.

---

## Parte 3: PDFs Simples → PyMuPDF + pdfplumber

**Problema:** os documentos estão em PDF nativo (digital).
Precisamos extrair texto e tabelas.

Explicar a diferença entre PDF nativo (texto digital) e PDF escaneado (imagem).

### Bloco 3a — PyMuPDF: extração rápida de texto corrido

- Criar um PDF de exemplo (política de home office) com `fitz`
- Extrair texto com `pagina.get_text()` → sai limpo e legível
- Aplicar regex no texto extraído para pegar padrões específicos (datas, artigos)

### Bloco 3b — PyMuPDF falha em tabelas

- Criar um PDF com tabela (relatório salarial) usando `reportlab`
- Extrair com PyMuPDF → tabela vira texto corrido, colunas se misturam
- Mostrar a bagunça: **perdemos a estrutura**

### Bloco 3c — pdfplumber: extração de tabelas

- Mesmo PDF com tabela → `pagina.extract_table()` → estrutura preservada
- Comparação lado a lado: PyMuPDF (bagunça) vs pdfplumber (estruturado)

### Trade-offs

| Ferramenta | ✅ Vantagens | ❌ Limitações |
|-----------|-------------|-------------|
| **PyMuPDF** | Muito rápido, texto limpo | Perde estrutura de tabelas, não faz OCR |
| **pdfplumber** | Preserva tabelas, exporta para pandas | Mais lento, falha em tabelas sem bordas, não faz OCR |

> **Na prática, PyMuPDF e pdfplumber se complementam** para PDFs simples.
> Mas para documentos complexos — com hierarquia, seções, cabeçalhos,
> mix de texto e tabelas — eles perdem a **estrutura semântica** do documento.
> Um título vira texto igual a um parágrafo.

---

## Parte 4: PDFs e Documentos Complexos → Docling + Unstructured

**Problema:** documentos reais têm hierarquia (títulos, subtítulos, seções),
misturam texto corrido com tabelas, e a **estrutura importa** para o pipeline
downstream (chunking semântico, RAG com contexto hierárquico).
PyMuPDF e pdfplumber não distinguem um título de um parágrafo.

### Bloco 4a — Docling (nativo): parsing com hierarquia em Markdown

- Processar o mesmo PDF complexo com Docling
- Docling gera saída em **Markdown**, respeitando a hierarquia do documento:
  - `#` para títulos, `##` para subtítulos
  - Tabelas em formato Markdown
  - Separação clara entre seções
- Comparar: PyMuPDF (texto flat) vs Docling (Markdown hierárquico)
- Mostrar como essa hierarquia facilita chunking semântico no RAG

### Bloco 4b — Docling com small model: documentos mais complexos

- Usar Docling configurado com um modelo pequeno (layout model)
- Demonstrar ganho em documentos com layout complicado:
  - Colunas múltiplas
  - Cabeçalhos/rodapés que devem ser ignorados
  - Figuras e legendas
- Comparar: Docling nativo vs Docling + small model

### Bloco 4c — Unstructured: particionamento inteligente

- Processar o mesmo documento com Unstructured
- Unstructured detecta automaticamente o tipo de cada bloco:
  - `Title`, `NarrativeText`, `Table`, `ListItem`, `Image`
- Mostrar a tipagem dos elementos e como isso ajuda no pipeline
- Comparar abordagens: Docling (Markdown) vs Unstructured (elementos tipados)

### Bloco 4d — Regex no pós-processamento

- Mesmo com Docling/Unstructured, regex continua útil:
  - Encontrar marcadores no Markdown gerado (`~~rasura~~`, `**negrito**`)
  - Extrair padrões do texto limpo (CPFs, datas, valores)
  - Limpar artefatos residuais do parsing

### Trade-offs

| Ferramenta | ✅ Vantagens | ❌ Limitações |
|-----------|-------------|-------------|
| **Docling (nativo)** | Markdown hierárquico, rápido, respeita estrutura | Pode errar em layouts muito complexos |
| **Docling + model** | Melhor detecção de layout, colunas, figuras | Mais lento, requer modelo adicional |
| **Unstructured** | Auto-detecção de tipos de bloco, flexível | Configuração mais verbosa, resultado varia por estratégia |

> **Docling e Unstructured são para sistemas que precisam de estrutura.**
> Para um script rápido, PyMuPDF basta. Para um RAG em produção
> que precisa de chunking semântico, Docling/Unstructured fazem diferença.
>
> **Mas todos assumem que o PDF tem texto digital.**
> E quando o documento é uma **imagem escaneada**?

---

## Parte 5: Documentos Escaneados → OCR (Tesseract vs LLM)

**Problema:** PDFs escaneados são imagens, não texto.
PyMuPDF, pdfplumber, Docling e Unstructured retornam string vazia.
Precisamos de **OCR** — converter a imagem em texto.

### Bloco 5a — OCR com Tesseract (tradicional)

- Criar imagem simulando documento escaneado (uma página só, nota fiscal)
- `pytesseract.image_to_string()` → texto sai razoável na imagem limpa
- Degradar a imagem (ruído, blur, rotação) → erros aparecem
- Mostrar: caracteres trocados, palavras quebradas, valores errados

### Bloco 5b — OCR via LLM (Gemini com visão)

- Enviar a **mesma imagem** diretamente para o Gemini (multimodal)
- Prompt: "extraia todo o texto dessa imagem"
- Comparar resultado: Tesseract vs LLM
- **Destaque:** leitura de tabelas na imagem — a LLM é **muito melhor**
  que o Tesseract para entender e preservar a estrutura de tabelas em imagens

### Bloco 5c — Pipeline de produção: Tesseract → LLM (correção)

- Pipeline em dois estágios (padrão de produção real):
  1. Rodar Tesseract na imagem → obter texto bruto (rápido, barato)
  2. Enviar para a LLM: **imagem + resultado do Tesseract**
  3. Prompt: "corrija o OCR abaixo usando a imagem como referência, sem inventar"
- A LLM usa o texto do Tesseract como **âncora** e a imagem como **ground truth**
- Mostrar que isso reduz alucinação comparado com LLM pura

### Bloco 5d — Comparação dos três métodos

- Tabela comparativa com o mesmo documento:
  - Tesseract puro
  - LLM pura (visão)
  - Pipeline Tesseract + LLM
- Métricas: precisão do texto, preservação de tabelas, custo, latência

### Trade-offs

| Método | ✅ Vantagens | ❌ Limitações |
|--------|-------------|-------------|
| **Tesseract** | Gratuito, offline, rápido | Erros frequentes, não preserva layout |
| **LLM (visão)** | Entende contexto, ótimo para tabelas | Custo por token, pode alucinar |
| **Tesseract + LLM** | Melhor dos dois mundos, menos alucinação | Dois estágios, custo da LLM |

> O pipeline Tesseract → LLM é o padrão usado em projetos reais:
> o OCR tradicional dá a base, a LLM refina.

---

## Parte 6: Extração Estruturada → LLM (JSON)

**Problema:** já temos texto limpo (de qualquer etapa anterior).
Agora precisamos transformar texto livre em **dados estruturados** (JSON)
para alimentar bancos de dados, APIs ou o próximo passo do pipeline.

### Bloco 6a — LLM para extração estruturada

- Pegar o texto extraído (nota fiscal / relatório RH) e enviar ao Gemini
- Prompt: "extraia em JSON com campos: empresa, cnpj, itens, total..."
- Mostrar que a LLM normaliza automaticamente:
  - Datas para ISO 8601
  - Valores monetários para float
  - Campos opcionais como null

### Bloco 6b — Comparação: Regex vs LLM na mesma tarefa

- O mesmo texto bruto da Parte 2 → extrair dados de funcionários
- Lado a lado: resultado do regex (manual, frágil) vs resultado da LLM (automático)
- Mostrar que a LLM lida com inconsistências que regex não consegue

### Trade-offs

| ✅ Vantagens | ❌ Limitações |
|-------------|-------------|
| Entende contexto e semântica | Custo por token em escala |
| Normaliza automaticamente | Latência: segundos vs milissegundos |
| Zero configuração de padrões | Pode alucinar (inventar dados) |
| Flexível com qualquer formato | Não-determinístico: respostas variam |

---

## Conclusão — Comparações e Sistemas Híbridos

### Quando usar cada ferramenta?

| Ferramenta | Melhor para | Evitar quando |
|-----------|------------|---------------|
| **Regex** | Pós-processamento, padrões em texto limpo | Como ferramenta primária de parsing |
| **BeautifulSoup** | HTML / XML estruturado | Documentos não-HTML |
| **PyMuPDF** | PDF nativo, texto corrido, velocidade | Tabelas ou escaneados |
| **pdfplumber** | Tabelas em PDF nativo | Escaneados ou docs sem bordas |
| **Docling** | Docs complexos com hierarquia (RAG) | Scripts simples e rápidos |
| **Unstructured** | Particionamento automático de docs variados | Quando precisa de controle fino |
| **Tesseract** | OCR gratuito / offline | Precisão crítica sem pós-processamento |
| **LLM (visão)** | OCR de tabelas, docs difíceis | Volume alto com orçamento limitado |
| **Tesseract + LLM** | OCR em produção com qualidade | Orçamento zero |
| **LLM (texto)** | Extração estruturada, correção, normalização | Volume massivo sem budget |

### Pipeline híbrido de produção

```
Documento chega
  │
  ├─ É HTML?
  │    └─ BeautifulSoup → Regex (limpeza) → texto limpo
  │
  ├─ É PDF nativo?
  │    ├─ Simples (texto corrido) → PyMuPDF → Regex (padrões)
  │    ├─ Com tabelas → pdfplumber → pandas
  │    └─ Complexo (hierarquia) → Docling / Unstructured → Markdown
  │
  ├─ É PDF escaneado / imagem?
  │    └─ Tesseract (OCR) → LLM (correção com imagem) → texto limpo
  │
  └─ Pós-processamento final
       └─ LLM → extração estruturada (JSON) → banco de dados / RAG
```

> **Regex aparece em todas as etapas** como ferramenta de limpeza e extração de padrões.
> Nenhuma ferramenta resolve tudo sozinha. O poder está na **combinação**.

---