"""
Gera os notebooks Collab_parsing_pt2.ipynb até Collab_parsing_pt6.ipynb.
Cada notebook é auto-contido (instala dependências e cria seus dados).
Execute: python gerar_notebooks.py
"""
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def create_notebook(filename, cells_data):
    cells = []
    for cell_type, source in cells_data:
        lines = source.split("\n")
        source_list = []
        for i, line in enumerate(lines):
            if i < len(lines) - 1:
                source_list.append(line + "\n")
            else:
                if line:
                    source_list.append(line)
        cell = {"cell_type": cell_type, "metadata": {}, "source": source_list}
        if cell_type == "code":
            cell["outputs"] = []
            cell["execution_count"] = None
        cells.append(cell)

    notebook = {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {"name": "python", "version": "3.10.0"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    filepath = os.path.join(BASE_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(notebook, f, ensure_ascii=False, indent=1)
    print(f"  Criado: {filename}")


# ================================================================
# PARTE 2 — HTML e Regex
# ================================================================

pt2 = [
    (
        "markdown",
        "# Parsing de Documentos — Parte 2: HTML e Regex\n"
        "\n"
        "**Problema:** os dados chegaram como HTML de um sistema web.\n"
        "Têm tags, marcações, entidades HTML misturadas com o conteúdo útil.\n"
        "\n"
        "**Ferramentas:**\n"
        "- `BeautifulSoup` — navega a árvore de tags HTML\n"
        "- `Regex` — pós-processa o texto extraído, encontra padrões",
    ),
    ("code", "!pip install beautifulsoup4 -q"),
    ("code", "from bs4 import BeautifulSoup\nimport re"),
    (
        "markdown",
        "---\n"
        "## Bloco 2a — BeautifulSoup: parsing de HTML\n"
        "\n"
        "HTML tem **estrutura**: tags aninhadas formam uma árvore.\n"
        "BeautifulSoup entende essa árvore e permite navegar por ela.",
    ),
    # ---------- HTML bruto ----------
    (
        "code",
        r'''# HTML bruto de um sistema de RH (exemplo realista)
html_bruto = """
<!DOCTYPE html>
<html>
<head>
    <title>Relatório de Funcionários - RH</title>
    <style>
        body { font-family: Arial; }
        .demitido { text-decoration: line-through; color: #999; }
        .destaque { background-color: #ffffcc; font-weight: bold; }
    </style>
</head>
<body>
    <h1>Relatório de Funcionários &mdash; Março/2026</h1>
    <p>Gerado em: 28/03/2026 às 14:30 | Responsável:
       <a href="mailto:maria.silva@empresa.com.br">maria.silva@empresa.com.br</a></p>

    <!-- Seção atualizada pelo jurídico em 25/03/2026 -->
    <h2>Equipe de Desenvolvimento</h2>
    <table border="1">
        <tr><th>Nome</th><th>CPF</th><th>Cargo</th><th>Salário</th><th>Status</th></tr>
        <tr>
            <td>Ana Paula Costa</td>
            <td>123.456.789-00</td>
            <td>Analista Sênior</td>
            <td>R$&nbsp;8.500,00</td>
            <td>Ativo</td>
        </tr>
        <tr>
            <td class="demitido">Bruno Martins</td>
            <td>987.654.321-00</td>
            <td>Desenvolvedor Jr</td>
            <td>R$&nbsp;4.200,00</td>
            <td><span class="demitido">~~Desligado em 15/02/2026~~</span></td>
        </tr>
        <tr>
            <td><span class="destaque">Carla Rodrigues</span></td>
            <td>456.789.123-00</td>
            <td>Gestora de Produto</td>
            <td>R$&nbsp;12.000,00</td>
            <td>Ativo — promovida</td>
        </tr>
    </table>

    <h2>Contatos</h2>
    <ul>
        <li>RH: rh@empresa.com.br | Tel: (62) 3333-4444</li>
        <li>TI: suporte@empresa.com.br</li>
        <li>Jurídico: juridico@empresa.com.br</li>
    </ul>
    <p><small>Sistema RH v3.2 — Documento interno, não distribuir.</small></p>
</body>
</html>
"""

print("=" * 60)
print("HTML BRUTO — o que chega do sistema de RH")
print("=" * 60)
print(html_bruto[:600])
print(f"\n... ({len(html_bruto)} caracteres no total)")''',
    ),
    # ---------- BS4 texto limpo ----------
    (
        "code",
        r'''# Parsing com BeautifulSoup
soup = BeautifulSoup(html_bruto, 'html.parser')

# 1. Texto limpo — sem nenhuma tag
print("=" * 60)
print("TEXTO LIMPO (soup.get_text)")
print("=" * 60)
texto_limpo = soup.get_text(separator='\n', strip=True)
print(texto_limpo)''',
    ),
    # ---------- BS4 navegar árvore ----------
    (
        "code",
        r'''# 2. Navegar a árvore: encontrar elementos específicos
print("=" * 60)
print("NAVEGANDO A ÁRVORE HTML")
print("=" * 60)

titulo = soup.find('h1')
print(f"Título: {titulo.get_text()}")

print("\nSeções (h2):")
for h2 in soup.find_all('h2'):
    print(f"  → {h2.get_text()}")

print("\nLinks encontrados:")
for a in soup.find_all('a', href=True):
    print(f"  {a['href']} → {a.get_text()}")

print("\nItens de lista:")
for li in soup.find_all('li'):
    print(f"  • {li.get_text()}")''',
    ),
    # ---------- BS4 extrair tabela ----------
    (
        "code",
        r'''# 3. Extrair tabela HTML → dados estruturados
print("=" * 60)
print("TABELA EXTRAÍDA COM BS4")
print("=" * 60)

tabela = soup.find('table')
dados = []
for linha in tabela.find_all('tr'):
    celulas = [td.get_text(strip=True) for td in linha.find_all(['th', 'td'])]
    dados.append(celulas)

for i, linha in enumerate(dados):
    if i == 0:
        print(' | '.join(f'{c:20s}' for c in linha))
        print('-' * 115)
    else:
        print(' | '.join(f'{c:20s}' for c in linha))

print(f"\n→ BS4 preservou a estrutura da tabela: {len(dados)-1} funcionários encontrados.")''',
    ),
    (
        "markdown",
        "---\n"
        "## Bloco 2b — Regex como ferramenta transversal\n"
        "\n"
        "Regex não é uma etapa isolada — ele aparece em **todo** pipeline\n"
        "como ferramenta de limpeza e extração de padrões.\n"
        "\n"
        "Vamos pós-processar o texto que o BS4 extraiu.",
    ),
    # ---------- Regex padrões ----------
    (
        "code",
        r'''# Extrair padrões do texto limpo com regex
texto = soup.get_text(separator='\n', strip=True)

print("=" * 60)
print("EXTRAINDO PADRÕES COM REGEX")
print("=" * 60)

# CPFs
cpfs = re.findall(r'\d{3}\.\d{3}\.\d{3}-\d{2}', texto)
print(f"\nCPFs encontrados:      {cpfs}")

# E-mails
emails = re.findall(r'[\w.+-]+@[\w-]+\.[\w.-]+', texto)
print(f"E-mails encontrados:   {emails}")

# Datas (dd/mm/aaaa)
datas = re.findall(r'\d{2}/\d{2}/\d{4}', texto)
print(f"Datas encontradas:     {datas}")

# Valores monetários
valores = re.findall(r'R\$\s?[\d.\xa0]+,\d{2}', texto)
print(f"Valores monetários:    {valores}")

# Telefones
telefones = re.findall(r'\(\d{2}\)\s?\d{4,5}-\d{4}', texto)
print(f"Telefones:             {telefones}")''',
    ),
    # ---------- Regex rasuras + limpeza ----------
    (
        "code",
        r'''# Detectar marcadores de rasura e limpeza
print("=" * 60)
print("RASURAS E LIMPEZA")
print("=" * 60)

# Texto rasurado com marcadores ~~texto~~
rasuras = re.findall(r'~~(.+?)~~', texto)
print(f"\nTexto rasurado (~~texto~~): {rasuras}")

# Elementos com classe 'demitido' — BS4 + regex juntos
demitidos = soup.find_all(class_='demitido')
print("\nElementos marcados como 'demitido' (via BS4):")
for elem in demitidos:
    print(f"  ✗ {elem.get_text(strip=True)}")

# Limpeza: espaços múltiplos, quebras excessivas, entidades HTML residuais
texto_processado = re.sub(r'\n{3,}', '\n\n', texto)
texto_processado = re.sub(r' {2,}', ' ', texto_processado)
texto_processado = re.sub(r'\xa0', ' ', texto_processado)  # &nbsp;
print(f"\nTexto original: {len(texto)} chars → Limpo: {len(texto_processado)} chars")
print("\n--- TEXTO FINAL LIMPO ---")
print(texto_processado)''',
    ),
    (
        "markdown",
        "---\n"
        "## Trade-offs\n"
        "\n"
        "| Ferramenta | ✅ Vantagens | ❌ Limitações |\n"
        "|---|---|---|\n"
        "| **BeautifulSoup** | Entende a árvore HTML, navega por tags, preserva tabelas | Só funciona com HTML/XML |\n"
        "| **Regex** | Rápido, sem dependências, controle total sobre padrões | Frágil com formatos variáveis, não entende semântica |\n"
        "\n"
        "> **Na prática:** BS4 extrai o conteúdo, regex refina e encontra padrões.\n"
        "> São ferramentas complementares.\n"
        ">\n"
        "> **Próximo desafio:** HTML está resolvido. Mas a maioria dos documentos\n"
        "> corporativos está em **PDF**. BS4 não lê PDFs, regex não abre binários.",
    ),
]

# ================================================================
# PARTE 3 — PDFs Simples (PyMuPDF + pdfplumber)
# ================================================================

pt3 = [
    (
        "markdown",
        "# Parsing de Documentos — Parte 3: PDFs Simples\n"
        "\n"
        "**Problema:** documentos em PDF nativo (digital). Precisamos extrair texto e tabelas.\n"
        "\n"
        "**Diferença fundamental:**\n"
        "- **PDF nativo** (digital): gerado por Word/sistema — o texto existe como dados\n"
        "- **PDF escaneado**: é uma imagem — só pixels, sem texto\n"
        "\n"
        "**Ferramentas:**\n"
        "- `PyMuPDF (fitz)` — extração rápida de texto corrido\n"
        "- `pdfplumber` — extração de tabelas com estrutura preservada",
    ),
    ("code", "!pip install PyMuPDF pdfplumber reportlab -q"),
    (
        "code",
        "import fitz  # PyMuPDF\n"
        "import pdfplumber\n"
        "import io\n"
        "import re\n"
        "from reportlab.pdfgen import canvas\n"
        "from reportlab.lib.pagesizes import A4\n"
        "from reportlab.lib import colors\n"
        "from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer\n"
        "from reportlab.lib.styles import getSampleStyleSheet",
    ),
    (
        "markdown",
        "---\n"
        "## Bloco 3a — PyMuPDF: extração rápida de texto corrido\n"
        "\n"
        "PyMuPDF é muito rápido para extrair texto de PDFs nativos.\n"
        "Vamos criar um PDF de política interna e extrair o conteúdo.",
    ),
    # ---------- Criar PDF texto + extrair com PyMuPDF ----------
    (
        "code",
        r'''# Criar PDF de exemplo: política interna de home office
buffer = io.BytesIO()
c = canvas.Canvas(buffer, pagesize=A4)
largura, altura = A4

c.setFont("Helvetica-Bold", 16)
c.drawString(72, altura - 72, "POLÍTICA DE HOME OFFICE")

c.setFont("Helvetica", 10)
c.drawString(72, altura - 95, "Versão 2.1  |  Vigência: 01/01/2026  |  Classificação: Interno")

paragrafos = [
    ("1. OBJETIVO", True),
    ("Esta política estabelece as diretrizes para o regime de trabalho remoto (home office)", False),
    ("aplicável a todos os colaboradores da Empresa XYZ Ltda (CNPJ: 12.345.678/0001-99).", False),
    ("", False),
    ("2. ELEGIBILIDADE", True),
    ("2.1 São elegíveis colaboradores com mais de 6 meses de empresa.", False),
    ("2.2 O gestor direto deve aprovar a adesão ao regime remoto.", False),
    ("2.3 Estagiários não são elegíveis para home office integral.", False),
    ("", False),
    ("3. JORNADA DE TRABALHO", True),
    ("3.1 A jornada permanece de 8 horas diárias, das 09:00 às 18:00.", False),
    ("3.2 Intervalo obrigatório de 1 hora para almoço.", False),
    ("3.3 Horas extras devem ser previamente autorizadas pelo gestor.", False),
    ("", False),
    ("4. EQUIPAMENTOS", True),
    ("A empresa fornecerá: notebook corporativo, headset e auxílio mensal de R$ 150,00", False),
    ("para despesas de internet e energia elétrica.", False),
    ("", False),
    ("5. SEGURANÇA DA INFORMAÇÃO", True),
    ("5.1 É obrigatório o uso de VPN corporativa para acesso aos sistemas.", False),
    ("5.2 Documentos confidenciais não devem ser impressos em ambiente doméstico.", False),
    ("5.3 Incidentes de segurança devem ser reportados em até 24 horas.", False),
]

y = altura - 130
for texto, negrito in paragrafos:
    if negrito:
        c.setFont("Helvetica-Bold", 11)
    else:
        c.setFont("Helvetica", 10)
    c.drawString(72, y, texto)
    y -= 16

c.save()
pdf_texto_bytes = buffer.getvalue()
print(f"PDF criado em memória: {len(pdf_texto_bytes):,} bytes")''',
    ),
    (
        "code",
        r'''# Extrair texto com PyMuPDF
doc = fitz.open(stream=pdf_texto_bytes, filetype="pdf")
pagina = doc[0]
texto_extraido = pagina.get_text()
doc.close()

print("=" * 60)
print("TEXTO EXTRAÍDO COM PyMuPDF")
print("=" * 60)
print(texto_extraido)

# Aplicar regex para encontrar padrões
print("\n" + "=" * 60)
print("PADRÕES ENCONTRADOS COM REGEX")
print("=" * 60)
cnpjs = re.findall(r'\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}', texto_extraido)
valores = re.findall(r'R\$\s?[\d.,]+', texto_extraido)
horarios = re.findall(r'\d{2}:\d{2}', texto_extraido)
print(f"CNPJs:     {cnpjs}")
print(f"Valores:   {valores}")
print(f"Horários:  {horarios}")''',
    ),
    (
        "markdown",
        "PyMuPDF extraiu o texto limpo e na ordem correta. Perfeito para texto corrido.\n"
        "\n"
        "---\n"
        "## Bloco 3b — PyMuPDF falha em tabelas\n"
        "\n"
        "Agora vamos criar um PDF com tabela (folha de pagamento) e ver o que acontece\n"
        "quando PyMuPDF tenta extrair.",
    ),
    # ---------- Criar PDF com tabela ----------
    (
        "code",
        r'''# Criar PDF com tabela: folha de pagamento
buffer_tab = io.BytesIO()
doc_tab = SimpleDocTemplate(buffer_tab, pagesize=A4)
styles = getSampleStyleSheet()

dados_tabela = [
    ["Funcionário",     "Cargo",             "Salário Base", "Desconto INSS", "Líquido"],
    ["Ana Paula Costa", "Analista Sênior",   "R$ 8.500,00",  "R$ 935,00",    "R$ 7.565,00"],
    ["Bruno Martins",   "Desenvolvedor Jr",  "R$ 4.200,00",  "R$ 462,00",    "R$ 3.738,00"],
    ["Carla Rodrigues", "Gestora de Produto","R$ 12.000,00", "R$ 1.320,00",  "R$ 10.680,00"],
    ["Diego Ferreira",  "Estagiário",        "R$ 1.800,00",  "R$ 0,00",      "R$ 1.800,00"],
    ["TOTAL",           "",                  "R$ 26.500,00", "R$ 2.717,00",  "R$ 23.783,00"],
]

tabela = Table(dados_tabela, colWidths=[120, 110, 85, 85, 85])
tabela.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
    ('TEXTCOLOR',  (0, 0), (-1, 0), colors.white),
    ('FONTNAME',   (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE',   (0, 0), (-1, -1), 9),
    ('GRID',       (0, 0), (-1, -1), 0.5, colors.grey),
    ('ALIGN',      (2, 0), (-1, -1), 'RIGHT'),
    ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#bdc3c7')),
    ('FONTNAME',   (0, -1), (-1, -1), 'Helvetica-Bold'),
]))

titulo = Paragraph("<b>FOLHA DE PAGAMENTO — MARÇO/2026</b>", styles['Title'])
doc_tab.build([titulo, Spacer(1, 20), tabela])
pdf_tabela_bytes = buffer_tab.getvalue()
print(f"PDF com tabela criado: {len(pdf_tabela_bytes):,} bytes")''',
    ),
    (
        "code",
        r'''# Tentar extrair a tabela com PyMuPDF
doc = fitz.open(stream=pdf_tabela_bytes, filetype="pdf")
texto_pymupdf = doc[0].get_text()
doc.close()

print("=" * 60)
print("PyMuPDF TENTANDO EXTRAIR A TABELA")
print("=" * 60)
print(texto_pymupdf)
print("\n⚠️  As colunas se misturaram! PyMuPDF lê texto na ordem do PDF,")
print("   mas não entende a estrutura de grade da tabela.")
print("   'Salário Base' pode ficar colado com 'Cargo', valores perdem alinhamento.")''',
    ),
    (
        "markdown",
        "---\n"
        "## Bloco 3c — pdfplumber: extração de tabelas\n"
        "\n"
        "pdfplumber analisa as linhas/bordas do PDF para reconstruir a grade da tabela.",
    ),
    # ---------- pdfplumber ----------
    (
        "code",
        r'''# Salvar PDF temporariamente para o pdfplumber (precisa de arquivo)
caminho_pdf = '/content/folha_pagamento.pdf'
with open(caminho_pdf, 'wb') as f:
    f.write(pdf_tabela_bytes)

# Extrair tabela com pdfplumber
with pdfplumber.open(caminho_pdf) as pdf:
    pagina = pdf.pages[0]
    tabela_extraida = pagina.extract_table()

print("=" * 60)
print("pdfplumber — TABELA EXTRAÍDA COM ESTRUTURA")
print("=" * 60)
if tabela_extraida:
    for i, linha in enumerate(tabela_extraida):
        if i == 0:
            print(' | '.join(f'{str(c):20s}' for c in linha))
            print('-' * 115)
        else:
            print(' | '.join(f'{str(c):20s}' for c in linha))
    print(f"\n✓ Estrutura preservada: {len(tabela_extraida)-1} linhas de dados")
else:
    print("Nenhuma tabela detectada.")''',
    ),
    # ---------- Comparação lado a lado ----------
    (
        "code",
        r'''# Comparação lado a lado
print("=" * 60)
print("COMPARAÇÃO: PyMuPDF vs pdfplumber")
print("=" * 60)

print("\n--- PyMuPDF (texto corrido, sem estrutura) ---")
print(texto_pymupdf[:400])

print("\n--- pdfplumber (tabela estruturada) ---")
if tabela_extraida:
    for linha in tabela_extraida[:3]:
        print(linha)
    print("...")

print("\n" + "=" * 60)
print("CONCLUSÃO:")
print("• PyMuPDF: rápido para texto corrido, perde estrutura de tabelas")
print("• pdfplumber: preserva tabelas, mas mais lento")
print("• Na prática, use os dois: PyMuPDF para texto, pdfplumber para tabelas")''',
    ),
    (
        "markdown",
        "---\n"
        "## Trade-offs\n"
        "\n"
        "| Ferramenta | ✅ Vantagens | ❌ Limitações |\n"
        "|---|---|---|\n"
        "| **PyMuPDF** | Muito rápido, texto limpo, leve | Perde estrutura de tabelas, não faz OCR |\n"
        "| **pdfplumber** | Preserva tabelas, exporta para pandas | Mais lento, falha em tabelas sem bordas, não faz OCR |\n"
        "\n"
        "> Na prática, PyMuPDF e pdfplumber **se complementam** para PDFs simples.\n"
        "> Mas para documentos complexos (hierarquia, seções, mix texto+tabelas),\n"
        "> eles perdem a **estrutura semântica** — um título vira texto igual a um parágrafo.\n"
        ">\n"
        "> **Próximo passo:** ferramentas que entendem a hierarquia do documento.",
    ),
]

# ================================================================
# PARTE 4 — Documentos Complexos (Docling + Unstructured)
# ================================================================

pt4 = [
    (
        "markdown",
        "# Parsing de Documentos — Parte 4: Documentos Complexos\n"
        "\n"
        "**Problema:** documentos reais têm hierarquia (títulos, subtítulos, seções),\n"
        "misturam texto com tabelas, e a **estrutura importa** para o pipeline downstream\n"
        "(chunking semântico, RAG com contexto hierárquico).\n"
        "\n"
        "PyMuPDF e pdfplumber não distinguem um título de um parágrafo.\n"
        "\n"
        "**Ferramentas:**\n"
        "- `Docling` — converte documentos em Markdown hierárquico\n"
        "- `Unstructured` — particiona documentos em blocos tipados",
    ),
    (
        "code",
        "!pip install PyMuPDF reportlab docling unstructured -q",
    ),
    (
        "code",
        "import fitz\n"
        "import io\n"
        "import re\n"
        "from reportlab.pdfgen import canvas\n"
        "from reportlab.lib.pagesizes import A4\n"
        "from reportlab.lib import colors\n"
        "from reportlab.platypus import (\n"
        "    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, ListFlowable, ListItem\n"
        ")\n"
        "from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle\n"
        "from reportlab.lib.enums import TA_CENTER",
    ),
    (
        "markdown",
        "---\n"
        "### Criando um PDF complexo para teste\n"
        "\n"
        "Vamos criar um documento com hierarquia real: títulos, subtítulos, parágrafos,\n"
        "listas e tabela — tudo no mesmo PDF.",
    ),
    # ---------- Criar PDF complexo ----------
    (
        "code",
        r'''# Criar PDF complexo com hierarquia
buffer = io.BytesIO()
doc = SimpleDocTemplate(buffer, pagesize=A4,
                        topMargin=50, bottomMargin=50,
                        leftMargin=60, rightMargin=60)
styles = getSampleStyleSheet()

# Estilos customizados
titulo_style = ParagraphStyle('TituloPrincipal', parent=styles['Title'],
                               fontSize=18, spaceAfter=20, alignment=TA_CENTER)
h2_style = ParagraphStyle('H2', parent=styles['Heading2'],
                           fontSize=14, spaceBefore=16, spaceAfter=8)
h3_style = ParagraphStyle('H3', parent=styles['Heading3'],
                           fontSize=12, spaceBefore=12, spaceAfter=6)
body_style = ParagraphStyle('Body', parent=styles['Normal'],
                             fontSize=10, spaceAfter=8, leading=14)

conteudo = []

# Título
conteudo.append(Paragraph("RELATÓRIO TRIMESTRAL DE DESEMPENHO", titulo_style))
conteudo.append(Paragraph("Empresa XYZ Ltda — Q1/2026", styles['Normal']))
conteudo.append(Spacer(1, 20))

# Seção 1
conteudo.append(Paragraph("1. Resumo Executivo", h2_style))
conteudo.append(Paragraph(
    "O primeiro trimestre de 2026 apresentou crescimento de 15% na receita líquida "
    "em comparação ao Q4/2025. A margem operacional manteve-se estável em 22%, "
    "refletindo o controle efetivo de custos implementado no segundo semestre de 2025.",
    body_style))
conteudo.append(Paragraph(
    "Os principais destaques incluem a expansão para o mercado nordestino e o "
    "lançamento de 3 novos produtos na linha premium.",
    body_style))

# Seção 2 com subseções
conteudo.append(Paragraph("2. Indicadores Financeiros", h2_style))
conteudo.append(Paragraph("2.1 Receita por Região", h3_style))
conteudo.append(Paragraph(
    "A região Sudeste continua como principal mercado, representando 58% da receita total. "
    "O Nordeste foi destaque com crescimento de 32% após a abertura de 2 filiais.",
    body_style))

# Tabela
dados = [
    ["Região",    "Q4/2025",       "Q1/2026",       "Variação"],
    ["Sudeste",   "R$ 4.200.000",  "R$ 4.830.000",  "+15%"],
    ["Sul",       "R$ 1.800.000",  "R$ 1.980.000",  "+10%"],
    ["Nordeste",  "R$ 950.000",    "R$ 1.254.000",  "+32%"],
    ["Centro-Oeste","R$ 600.000",  "R$ 660.000",    "+10%"],
    ["TOTAL",     "R$ 7.550.000",  "R$ 8.724.000",  "+15.5%"],
]
t = Table(dados, colWidths=[100, 100, 100, 70])
t.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#34495e')),
    ('TEXTCOLOR', (0,0), (-1,0), colors.white),
    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
    ('FONTSIZE', (0,0), (-1,-1), 9),
    ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
    ('ALIGN', (1,0), (-1,-1), 'RIGHT'),
    ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#ecf0f1')),
    ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
]))
conteudo.append(Spacer(1, 10))
conteudo.append(t)
conteudo.append(Spacer(1, 10))

# Subseção 2.2
conteudo.append(Paragraph("2.2 Margem Operacional", h3_style))
conteudo.append(Paragraph(
    "A margem operacional de 22% reflete a política de contenção de custos: "
    "redução de 8% em despesas administrativas e renegociação de contratos de fornecedores. "
    "O custo de aquisição de clientes (CAC) reduziu de R$ 340 para R$ 285.",
    body_style))

# Seção 3
conteudo.append(Paragraph("3. Recursos Humanos", h2_style))
conteudo.append(Paragraph(
    "O quadro de funcionários cresceu de 142 para 158 colaboradores (+11%). "
    "Principais movimentações:",
    body_style))

items = [
    "12 novas contratações na área de tecnologia",
    "4 contratações na equipe comercial (Nordeste)",
    "Turnover voluntário: 3.2% (meta: < 5%)",
    "Programa de desenvolvimento: 89% de adesão",
]
lista = ListFlowable(
    [ListItem(Paragraph(item, body_style)) for item in items],
    bulletType='bullet', start='•'
)
conteudo.append(lista)

# Seção 4
conteudo.append(Paragraph("4. Próximos Passos", h2_style))
conteudo.append(Paragraph(
    "Para o Q2/2026, as prioridades são: consolidar operação no Nordeste, "
    "lançar plataforma digital de vendas B2B (previsão: junho/2026), e "
    "implementar sistema de CRM integrado (orçamento aprovado: R$ 450.000).",
    body_style))

doc.build(conteudo)
pdf_complexo_bytes = buffer.getvalue()

# Salvar em disco
caminho_complexo = '/content/relatorio_trimestral.pdf'
with open(caminho_complexo, 'wb') as f:
    f.write(pdf_complexo_bytes)
print(f"PDF complexo criado: {len(pdf_complexo_bytes):,} bytes → {caminho_complexo}")''',
    ),
    # ---------- PyMuPDF no doc complexo (flat) ----------
    (
        "code",
        r'''# Primeiro, ver como PyMuPDF extrai (tudo flat, sem hierarquia)
doc_mu = fitz.open(caminho_complexo)
texto_flat = doc_mu[0].get_text()
doc_mu.close()

print("=" * 60)
print("PyMuPDF — TEXTO FLAT (sem hierarquia)")
print("=" * 60)
print(texto_flat)
print("\n⚠️  Títulos, parágrafos e itens de lista estão todos no mesmo nível.")
print("   Não há como distinguir 'Resumo Executivo' (seção) de um parágrafo comum.")''',
    ),
    (
        "markdown",
        "---\n"
        "## Bloco 4a — Docling: parsing com hierarquia em Markdown\n"
        "\n"
        "Docling analisa o layout do documento e gera saída em **Markdown**,\n"
        "respeitando a hierarquia: `#` para títulos, `##` para subtítulos, tabelas formatadas.",
    ),
    # ---------- Docling nativo ----------
    (
        "code",
        r'''from docling.document_converter import DocumentConverter

converter = DocumentConverter()
resultado = converter.convert(caminho_complexo)
markdown_docling = resultado.document.export_to_markdown()

print("=" * 60)
print("DOCLING — MARKDOWN HIERÁRQUICO")
print("=" * 60)
print(markdown_docling)''',
    ),
    (
        "code",
        r'''# Comparação: PyMuPDF (flat) vs Docling (hierárquico)
print("=" * 60)
print("COMPARAÇÃO: PyMuPDF vs Docling")
print("=" * 60)

# Contar níveis de hierarquia no Markdown
titulos_md = re.findall(r'^(#{1,4})\s+(.+)$', markdown_docling, re.MULTILINE)
print("\nHierarquia detectada pelo Docling:")
for nivel, titulo in titulos_md:
    indent = "  " * (len(nivel) - 1)
    print(f"  {indent}{nivel} {titulo}")

print(f"\n→ PyMuPDF: texto corrido, 0 níveis de hierarquia")
print(f"→ Docling: {len(titulos_md)} títulos/subtítulos detectados com hierarquia")
print(f"\nPor que isso importa para RAG?")
print(f"  Com hierarquia, o chunking pode manter cada seção como um chunk semântico,")
print(f"  preservando contexto (ex: '2.1 Receita por Região' + sua tabela).")''',
    ),
    (
        "markdown",
        "---\n"
        "## Bloco 4b — Docling com modelo de layout\n"
        "\n"
        "Para documentos mais complexos (colunas múltiplas, cabeçalhos/rodapés,\n"
        "figuras com legendas), Docling pode usar um modelo pequeno de detecção de layout.",
    ),
    # ---------- Docling com modelo ----------
    (
        "code",
        r'''from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

# Configurar pipeline com detecção de layout via modelo
pipeline_options = PdfPipelineOptions()
pipeline_options.do_table_structure = True    # modelo para estrutura de tabelas

converter_model = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    }
)

resultado_model = converter_model.convert(caminho_complexo)
markdown_model = resultado_model.document.export_to_markdown()

print("=" * 60)
print("DOCLING + MODELO DE LAYOUT")
print("=" * 60)
print(markdown_model)

# Comparar com o nativo
print("\n" + "=" * 60)
print("COMPARAÇÃO: Docling nativo vs Docling + modelo")
print("=" * 60)
print(f"Docling nativo:  {len(markdown_docling)} chars")
print(f"Docling + model: {len(markdown_model)} chars")
print("\nO modelo pode detectar melhor tabelas, separar cabeçalhos de rodapés,")
print("e lidar com layouts de múltiplas colunas — ao custo de mais tempo de processamento.")''',
    ),
    (
        "markdown",
        "---\n"
        "## Bloco 4c — Unstructured: particionamento inteligente\n"
        "\n"
        "Unstructured detecta automaticamente o **tipo** de cada bloco do documento:\n"
        "`Title`, `NarrativeText`, `Table`, `ListItem`, `Image`, etc.",
    ),
    # ---------- Unstructured ----------
    (
        "code",
        r'''from unstructured.partition.pdf import partition_pdf

# Processar o mesmo documento
elementos = partition_pdf(caminho_complexo, strategy="auto")

print("=" * 60)
print("UNSTRUCTURED — ELEMENTOS TIPADOS")
print("=" * 60)
for i, elem in enumerate(elementos):
    tipo = type(elem).__name__
    texto = str(elem)[:100]
    print(f"[{i:2d}] {tipo:20s} | {texto}")

print(f"\n→ Total de elementos: {len(elementos)}")

# Contar por tipo
from collections import Counter
tipos = Counter(type(e).__name__ for e in elementos)
print("\nDistribuição por tipo:")
for tipo, qtd in tipos.most_common():
    print(f"  {tipo:20s}: {qtd}")''',
    ),
    (
        "code",
        r'''# Comparar abordagens: Docling (Markdown) vs Unstructured (elementos)
print("=" * 60)
print("COMPARAÇÃO: Docling vs Unstructured")
print("=" * 60)

print("\n--- Docling: saída em Markdown hierárquico ---")
print(markdown_docling[:500])
print("...")

print("\n--- Unstructured: elementos tipados ---")
for elem in elementos[:8]:
    print(f"  [{type(elem).__name__}] {str(elem)[:80]}")
print("...")

print("\n→ Docling: ideal para gerar Markdown pronto para chunking semântico em RAG")
print("→ Unstructured: ideal quando você precisa filtrar por tipo (só tabelas, só títulos)")''',
    ),
    (
        "markdown",
        "---\n"
        "## Bloco 4d — Regex no pós-processamento\n"
        "\n"
        "Mesmo com Docling/Unstructured, regex continua útil para refinar o resultado.",
    ),
    # ---------- Regex pós-processamento ----------
    (
        "code",
        r'''# Pós-processamento com regex no Markdown do Docling
print("=" * 60)
print("REGEX NO PÓS-PROCESSAMENTO")
print("=" * 60)

# Extrair valores monetários do Markdown
valores = re.findall(r'R\$\s?[\d.,]+', markdown_docling)
print(f"\nValores monetários encontrados: {valores}")

# Extrair percentuais
percentuais = re.findall(r'[+-]?\d+[.,]?\d*%', markdown_docling)
print(f"Percentuais: {percentuais}")

# Extrair todos os títulos de seção do Markdown
secoes = re.findall(r'^#+\s+(.+)$', markdown_docling, re.MULTILINE)
print(f"Seções do documento: {secoes}")

# Limpar artefatos comuns de parsing
texto_limpo = markdown_docling
texto_limpo = re.sub(r'\n{3,}', '\n\n', texto_limpo)       # quebras excessivas
texto_limpo = re.sub(r'[ \t]+$', '', texto_limpo, flags=re.MULTILINE)  # espaços finais
print(f"\nMarkdown original: {len(markdown_docling)} chars")
print(f"Markdown limpo:    {len(texto_limpo)} chars")''',
    ),
    (
        "markdown",
        "---\n"
        "## Trade-offs\n"
        "\n"
        "| Ferramenta | ✅ Vantagens | ❌ Limitações |\n"
        "|---|---|---|\n"
        "| **Docling (nativo)** | Markdown hierárquico, rápido, respeita estrutura | Pode errar em layouts muito complexos |\n"
        "| **Docling + modelo** | Melhor detecção de layout, colunas, figuras | Mais lento, requer modelo adicional |\n"
        "| **Unstructured** | Auto-detecção de tipos de bloco, flexível | Configuração mais verbosa, resultado varia por estratégia |\n"
        "\n"
        "> Docling e Unstructured são para sistemas que **precisam de estrutura**.\n"
        "> Para um script rápido, PyMuPDF basta. Para um RAG em produção\n"
        "> com chunking semântico, Docling/Unstructured fazem diferença.\n"
        ">\n"
        "> **Mas todos assumem que o PDF tem texto digital.**\n"
        "> E quando o documento é uma **imagem escaneada**?",
    ),
]

# ================================================================
# PARTE 5 — OCR (Tesseract + LLM)
# ================================================================

pt5 = [
    (
        "markdown",
        "# Parsing de Documentos — Parte 5: OCR (Documentos Escaneados)\n"
        "\n"
        "**Problema:** PDFs escaneados são imagens, não texto.\n"
        "PyMuPDF, pdfplumber, Docling e Unstructured retornam string vazia.\n"
        "Precisamos de **OCR** — converter a imagem em texto.\n"
        "\n"
        "**Ferramentas:**\n"
        "- `Tesseract` — OCR tradicional, gratuito, offline\n"
        "- `Gemini (visão)` — LLM multimodal que \"lê\" imagens\n"
        "- **Pipeline Tesseract → LLM** — o padrão de produção",
    ),
    (
        "code",
        "!apt-get install tesseract-ocr tesseract-ocr-por -y -qq\n"
        "!pip install pytesseract Pillow google-generativeai -q",
    ),
    (
        "code",
        "import pytesseract\n"
        "from PIL import Image, ImageDraw, ImageFilter\n"
        "import random\n"
        "import numpy as np\n"
        "from IPython.display import display\n"
        "import google.generativeai as genai\n"
        "from google.colab import userdata",
    ),
    (
        "code",
        r'''# Configurar Gemini
genai.configure(api_key=userdata.get('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-2.0-flash')
print("Gemini configurado.")''',
    ),
    (
        "markdown",
        "---\n"
        "## Bloco 5a — OCR com Tesseract (tradicional)\n"
        "\n"
        "Tesseract é o motor de OCR open-source mais usado.\n"
        "Funciona bem em imagens limpas, mas degrada com ruído.",
    ),
    # ---------- Criar imagem + Tesseract ----------
    (
        "code",
        r'''# Criar imagem simulando nota fiscal escaneada
random.seed(42)
largura, altura = 620, 500
img = Image.new('RGB', (largura, altura), color=(248, 244, 230))
draw = ImageDraw.Draw(img)

draw.rectangle([15, 15, largura-15, altura-15], outline=(160, 140, 120), width=2)

# Nota: usamos apenas ASCII porque a fonte default do Pillow
# nao renderiza acentos corretamente em todos os ambientes
linhas_doc = [
    (40,  40,  "NOTA FISCAL No 00.123 - 2a VIA"),
    (40,  70,  "Emitente: COMERCIO SAO PEDRO LTDA"),
    (40,  95,  "CNPJ: 12.345.678/0001-99    IE: 123.456.789.000"),
    (40, 120,  "End: Rua das Flores, 500 - Centro - Sao Paulo/SP"),
    (40, 155,  "-" * 60),
    (40, 175,  "DESCRICAO                  QTD   UNIT       TOTAL"),
    (40, 195,  "-" * 60),
    (40, 215,  "Cimento CP-II 50kg          10   R$32,00   R$320,00"),
    (40, 235,  "Areia media (saco 20kg)      5   R$18,00    R$90,00"),
    (40, 255,  "Tijolo ceramico (cx 50un)    3   R$95,00   R$285,00"),
    (40, 275,  "Tinta acrilica branca 18L    2  R$120,00   R$240,00"),
    (40, 295,  "-" * 60),
    (40, 320,  "TOTAL GERAL:                             R$935,00"),
    (40, 350,  "Forma de pgto: DINHEIRO    Data: 28/03/2026"),
    (40, 385,  "Assinatura: _____________________________"),
]

for x, y, texto in linhas_doc:
    ox, oy = random.randint(-1, 1), random.randint(-1, 1)
    tom = random.randint(15, 45)
    draw.text((x+ox, y+oy), texto, fill=(tom, tom, tom+5))

# Ruído de scanner
pixels = img.load()
for _ in range(1200):
    rx, ry = random.randint(0, largura-1), random.randint(0, altura-1)
    v = random.randint(130, 210)
    pixels[rx, ry] = (v, v-5, v-10)

img.save('/content/nota_fiscal_scan.png', dpi=(150, 150))
print("Imagem da nota fiscal criada:")
display(img)''',
    ),
    (
        "code",
        r'''# OCR com Tesseract na imagem limpa
texto_tesseract = pytesseract.image_to_string(img, lang='por')

print("=" * 60)
print("TESSERACT — IMAGEM LIMPA")
print("=" * 60)
print(texto_tesseract)''',
    ),
    (
        "code",
        r'''# Degradar a imagem: blur + ruído + rotação leve
img_degradada = img.copy()

# Blur
img_degradada = img_degradada.filter(ImageFilter.GaussianBlur(radius=1.5))

# Rotação leve (simula scan torto)
img_degradada = img_degradada.rotate(2, expand=False, fillcolor=(240, 235, 220))

# Mais ruído
pixels_deg = img_degradada.load()
for _ in range(4000):
    rx = random.randint(0, img_degradada.width - 1)
    ry = random.randint(0, img_degradada.height - 1)
    v = random.randint(80, 200)
    pixels_deg[rx, ry] = (v, v, v)

img_degradada.save('/content/nota_fiscal_degradada.png', dpi=(150, 150))
print("Imagem degradada:")
display(img_degradada)

# Tesseract na imagem degradada
texto_degradado = pytesseract.image_to_string(img_degradada, lang='por')

print("\n" + "=" * 60)
print("TESSERACT — IMAGEM DEGRADADA")
print("=" * 60)
print(texto_degradado)
print("\n⚠️  Erros aparecem: caracteres trocados, palavras quebradas, valores errados.")''',
    ),
    (
        "markdown",
        "---\n"
        "## Bloco 5b — OCR via LLM (Gemini com visão)\n"
        "\n"
        "A LLM multimodal recebe a **imagem diretamente** e entende o contexto.\n"
        "Especialmente para tabelas, é **muito melhor** que OCR tradicional.",
    ),
    # ---------- Gemini visão ----------
    (
        "code",
        r'''# Enviar a MESMA imagem degradada para o Gemini
img_degradada_pil = Image.open('/content/nota_fiscal_degradada.png')

prompt_visao = """Extraia TODO o texto desta imagem de nota fiscal.
Preserve a estrutura da tabela.
Não invente dados — transcreva exatamente o que está visível."""

resposta_llm = model.generate_content([prompt_visao, img_degradada_pil])
texto_llm = resposta_llm.text

print("=" * 60)
print("GEMINI (VISÃO) — MESMA IMAGEM DEGRADADA")
print("=" * 60)
print(texto_llm)''',
    ),
    (
        "markdown",
        "---\n"
        "## Bloco 5c — Pipeline de produção: Tesseract → LLM\n"
        "\n"
        "O padrão de produção é um pipeline em dois estágios:\n"
        "1. Tesseract extrai texto bruto (rápido, barato)\n"
        "2. LLM recebe **imagem + texto do Tesseract** e corrige\n"
        "\n"
        "A LLM usa o texto do Tesseract como **âncora** e a imagem como **ground truth**.\n"
        "Isso reduz alucinação comparado com LLM pura.",
    ),
    # ---------- Pipeline ----------
    (
        "code",
        r'''# Pipeline: Tesseract → LLM (correção com âncora)
prompt_correcao = f"""Você recebeu o resultado de um OCR (Tesseract) de uma nota fiscal.
O OCR pode conter erros. Use a IMAGEM como referência para corrigir.

REGRAS:
- Corrija erros de OCR (caracteres trocados, palavras quebradas)
- Preserve a estrutura original (tabela, campos)
- NÃO invente dados que não estão na imagem
- Se não conseguir ler algo, marque como [ilegível]

TEXTO DO OCR (Tesseract):
{texto_degradado}

Corrija o texto acima usando a imagem como referência."""

resposta_pipeline = model.generate_content([prompt_correcao, img_degradada_pil])
texto_pipeline = resposta_pipeline.text

print("=" * 60)
print("PIPELINE: TESSERACT → LLM (CORREÇÃO)")
print("=" * 60)
print(texto_pipeline)''',
    ),
    (
        "markdown",
        "---\n"
        "## Bloco 5d — Comparação dos três métodos",
    ),
    # ---------- Comparação ----------
    (
        "code",
        r'''# Comparação lado a lado
print("=" * 60)
print("COMPARAÇÃO DOS 3 MÉTODOS (mesma imagem degradada)")
print("=" * 60)

print("\n" + "-" * 40)
print("1. TESSERACT PURO")
print("-" * 40)
print(texto_degradado[:500])

print("\n" + "-" * 40)
print("2. LLM PURA (Gemini visão)")
print("-" * 40)
print(texto_llm[:500])

print("\n" + "-" * 40)
print("3. PIPELINE: TESSERACT → LLM")
print("-" * 40)
print(texto_pipeline[:500])

print("\n" + "=" * 60)
print("ANÁLISE")
print("=" * 60)
print("""
| Método           | Custo    | Latência | Precisão | Tabelas |
|------------------|----------|----------|----------|---------|
| Tesseract puro   | Gratuito | ~ms      | Baixa*   | Ruim    |
| LLM pura (visão) | $$       | ~seg     | Alta     | Ótima   |
| Tesseract + LLM  | $        | ~seg     | Muito alta| Ótima  |

* Em imagens degradadas. Em imagens limpas, Tesseract é razoável.

→ O pipeline Tesseract → LLM é o padrão em produção:
  OCR dá a base, LLM refina com contexto visual.
""")''',
    ),
    (
        "markdown",
        "---\n"
        "## Trade-offs\n"
        "\n"
        "| Método | ✅ Vantagens | ❌ Limitações |\n"
        "|---|---|---|\n"
        "| **Tesseract** | Gratuito, offline, rápido | Erros em imagens ruins, não preserva layout |\n"
        "| **LLM (visão)** | Entende contexto, ótimo para tabelas | Custo por token, pode alucinar |\n"
        "| **Tesseract + LLM** | Melhor dos dois mundos, menos alucinação | Dois estágios, custo da LLM |\n"
        "\n"
        "> O pipeline **Tesseract → LLM** é o padrão de produção real:\n"
        "> o OCR tradicional dá a base, a LLM refina.",
    ),
]

# ================================================================
# PARTE 6 — Extração Estruturada (LLM → JSON)
# ================================================================

pt6 = [
    (
        "markdown",
        "# Parsing de Documentos — Parte 6: Extração Estruturada com LLM\n"
        "\n"
        "**Problema:** já temos texto limpo (de qualquer etapa anterior).\n"
        "Agora precisamos transformar texto livre em **dados estruturados** (JSON)\n"
        "para alimentar bancos de dados, APIs ou o próximo passo do pipeline.\n"
        "\n"
        "**Ferramenta:** LLM (Gemini) com prompt de extração estruturada.",
    ),
    (
        "code",
        "!pip install google-generativeai -q",
    ),
    (
        "code",
        "import google.generativeai as genai\n"
        "from google.colab import userdata\n"
        "import json\n"
        "import re",
    ),
    (
        "code",
        r'''genai.configure(api_key=userdata.get('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-2.0-flash')
print("Gemini configurado.")''',
    ),
    (
        "markdown",
        "---\n"
        "## Bloco 6a — LLM para extração estruturada\n"
        "\n"
        "Vamos pegar textos extraídos nas partes anteriores e transformar em JSON.",
    ),
    # ---------- Extração de nota fiscal ----------
    (
        "code",
        r'''# Texto de uma nota fiscal (como seria extraído por OCR + limpeza)
texto_nota = """
NOTA FISCAL Nº 00.123
Emitente: COMÉRCIO SÃO PEDRO LTDA
CNPJ: 12.345.678/0001-99
End: Rua das Flores, 500 - Centro - São Paulo/SP

DESCRIÇÃO                  QTD   UNIT       TOTAL
Cimento CP-II 50kg          10   R$32,00   R$320,00
Areia média (saco 20kg)      5   R$18,00    R$90,00
Tijolo cerâmico (cx 50un)    3   R$95,00   R$285,00
Tinta acrílica branca 18L    2  R$120,00   R$240,00

TOTAL GERAL:                             R$935,00
Forma de pgto: DINHEIRO    Data: 28/03/2026
"""

prompt_json = f"""Extraia os dados da nota fiscal abaixo em formato JSON.

Campos esperados:
- numero_nota (string)
- emitente (string)
- cnpj (string)
- endereco (string)
- data (string, formato ISO 8601: YYYY-MM-DD)
- forma_pagamento (string)
- itens (lista de objetos com: descricao, quantidade (int), valor_unitario (float), valor_total (float))
- total_geral (float)

REGRAS:
- Converta valores monetários para float (R$ 32,00 → 32.00)
- Converta datas para ISO 8601
- Se um campo não existir, use null
- Retorne APENAS o JSON, sem markdown ou explicação

TEXTO DA NOTA FISCAL:
{texto_nota}"""

resposta = model.generate_content(prompt_json)
json_nota = resposta.text

# Limpar possíveis marcadores de código
json_nota = re.sub(r'^```json\s*', '', json_nota.strip())
json_nota = re.sub(r'\s*```$', '', json_nota.strip())

print("=" * 60)
print("EXTRAÇÃO ESTRUTURADA — NOTA FISCAL → JSON")
print("=" * 60)
print(json_nota)

# Validar que é JSON válido
try:
    dados = json.loads(json_nota)
    print("\n✓ JSON válido!")
    print(f"  Emitente: {dados.get('emitente')}")
    print(f"  CNPJ: {dados.get('cnpj')}")
    print(f"  Itens: {len(dados.get('itens', []))}")
    print(f"  Total: {dados.get('total_geral')}")
    print(f"  Data: {dados.get('data')}")
except json.JSONDecodeError as e:
    print(f"\n✗ Erro no JSON: {e}")''',
    ),
    # ---------- Extração de relatório de RH ----------
    (
        "code",
        r'''# Texto do relatório de RH (como extraído pelo BS4 na Parte 2)
texto_rh = """
Relatório de Funcionários — Março/2026
Gerado em: 28/03/2026 às 14:30

Equipe de Desenvolvimento:
- Ana Paula Costa, CPF 123.456.789-00, Analista Sênior, salário R$ 8.500,00, status: Ativo
- Bruno Martins, CPF 987.654.321-00, Desenvolvedor Jr, salário R$ 4.200,00, ~~Desligado em 15/02/2026~~
- Carla Rodrigues, CPF 456.789.123-00, Gestora de Produto, salário R$ 12.000,00, Ativo — promovida

Contatos:
- RH: rh@empresa.com.br | Tel: (62) 3333-4444
- TI: suporte@empresa.com.br
- Jurídico: juridico@empresa.com.br
"""

prompt_rh = f"""Extraia os dados dos funcionários do relatório abaixo em JSON.

Estrutura esperada:
{{
  "data_relatorio": "YYYY-MM-DD",
  "funcionarios": [
    {{
      "nome": "string",
      "cpf": "string",
      "cargo": "string",
      "salario": float,
      "status": "ativo" | "desligado" | "promovido",
      "data_desligamento": "YYYY-MM-DD" ou null,
      "observacoes": "string" ou null
    }}
  ],
  "contatos": [
    {{
      "departamento": "string",
      "email": "string",
      "telefone": "string" ou null
    }}
  ]
}}

REGRAS:
- Converta salários para float
- Datas para ISO 8601
- Texto rasurado (~~texto~~) indica desligamento — extraia a data
- Retorne APENAS o JSON

TEXTO:
{texto_rh}"""

resposta_rh = model.generate_content(prompt_rh)
json_rh = resposta_rh.text
json_rh = re.sub(r'^```json\s*', '', json_rh.strip())
json_rh = re.sub(r'\s*```$', '', json_rh.strip())

print("=" * 60)
print("EXTRAÇÃO ESTRUTURADA — RELATÓRIO RH → JSON")
print("=" * 60)
print(json_rh)

try:
    dados_rh = json.loads(json_rh)
    print("\n✓ JSON válido!")
    for f in dados_rh.get('funcionarios', []):
        print(f"  {f.get('nome'):25s} | {f.get('cargo'):20s} | {f.get('status')}")
except json.JSONDecodeError as e:
    print(f"\n✗ Erro: {e}")''',
    ),
    (
        "markdown",
        "A LLM normalizou automaticamente:\n"
        "- Datas para ISO 8601\n"
        "- Valores monetários para float\n"
        "- Campos opcionais como null\n"
        "- Texto rasurado interpretado como desligamento\n"
        "\n"
        "---\n"
        "## Bloco 6b — Comparação: Regex vs LLM na mesma tarefa\n"
        "\n"
        "O mesmo texto bruto → extrair dados de funcionários.\n"
        "Regex (manual) vs LLM (automático).",
    ),
    # ---------- Regex vs LLM ----------
    (
        "code",
        r'''# === ABORDAGEM 1: REGEX (manual, passo a passo) ===
print("=" * 60)
print("ABORDAGEM 1: REGEX")
print("=" * 60)

# Cada padrão precisa ser escrito manualmente
linhas_func = re.findall(
    r'- (.+?), CPF (\d{3}\.\d{3}\.\d{3}-\d{2}), (.+?), salário (R\$ [\d.,]+), (.+)',
    texto_rh
)

print("\nFuncionários extraídos por regex:")
resultado_regex = []
for nome, cpf, cargo, salario, status_raw in linhas_func:
    # Interpretar status
    if '~~' in status_raw:
        status = 'desligado'
        data_desl = re.search(r'(\d{2}/\d{2}/\d{4})', status_raw)
        data_desl = data_desl.group(1) if data_desl else None
    elif 'promovid' in status_raw.lower():
        status = 'promovido'
        data_desl = None
    else:
        status = 'ativo'
        data_desl = None

    # Converter salário
    salario_float = float(salario.replace('R$ ', '').replace('.', '').replace(',', '.'))

    func = {
        'nome': nome,
        'cpf': cpf,
        'cargo': cargo,
        'salario': salario_float,
        'status': status,
        'data_desligamento': data_desl
    }
    resultado_regex.append(func)
    print(f"  {nome:25s} | {cargo:20s} | {status}")

print(f"\n→ Regex encontrou {len(resultado_regex)} funcionários")
print("→ Foram necessárias ~20 linhas de código com padrões específicos")''',
    ),
    (
        "code",
        r'''# === ABORDAGEM 2: LLM (já executada acima) ===
print("=" * 60)
print("ABORDAGEM 2: LLM (Gemini)")
print("=" * 60)

# Já temos o resultado em dados_rh
print(f"\nFuncionários extraídos pela LLM:")
for f in dados_rh.get('funcionarios', []):
    print(f"  {f.get('nome', '?'):25s} | {f.get('cargo', '?'):20s} | {f.get('status', '?')}")

print(f"\n→ LLM encontrou {len(dados_rh.get('funcionarios', []))} funcionários")
print("→ Foram necessárias ~5 linhas de código + prompt descritivo")''',
    ),
    (
        "code",
        r'''# Comparação final
print("=" * 60)
print("REGEX vs LLM — COMPARAÇÃO")
print("=" * 60)
print("""
| Critério               | Regex              | LLM                    |
|------------------------|--------------------|------------------------|
| Linhas de código       | ~20+ (padrões)     | ~5 (prompt)            |
| Tempo de dev           | Minutos a horas    | Segundos               |
| Flexibilidade          | Frágil (formato)   | Robusta (contexto)     |
| Inconsistências        | Quebra             | Interpreta             |
| Custo de execução      | Zero               | $$ (tokens)            |
| Latência               | Microsegundos      | Segundos               |
| Determinismo           | 100%               | Varia entre chamadas   |
| Alucinação             | Impossível         | Possível               |

QUANDO USAR CADA UM:
• Regex: padrões simples e repetitivos em alto volume (CPFs, e-mails, datas)
• LLM: extração semântica de dados variáveis (relatórios, contratos, e-mails)
• Combinação: LLM extrai → regex valida (ex: verificar formato de CPF no JSON)
""")''',
    ),
    (
        "markdown",
        "---\n"
        "## Trade-offs — Extração Estruturada\n"
        "\n"
        "| ✅ Vantagens | ❌ Limitações |\n"
        "|---|---|\n"
        "| Entende contexto e semântica | Custo por token em escala |\n"
        "| Normaliza automaticamente | Latência: segundos vs milissegundos |\n"
        "| Zero configuração de padrões | Pode alucinar (inventar dados) |\n"
        "| Flexível com qualquer formato | Não-determinístico: respostas variam |",
    ),
    (
        "markdown",
        "---\n"
        "## Conclusão — Pipeline Híbrido de Produção\n"
        "\n"
        "```\n"
        "Documento chega\n"
        "  │\n"
        "  ├─ É HTML?\n"
        "  │    └─ BeautifulSoup → Regex (limpeza) → texto limpo\n"
        "  │\n"
        "  ├─ É PDF nativo?\n"
        "  │    ├─ Simples (texto corrido) → PyMuPDF → Regex (padrões)\n"
        "  │    ├─ Com tabelas → pdfplumber → pandas\n"
        "  │    └─ Complexo (hierarquia) → Docling / Unstructured → Markdown\n"
        "  │\n"
        "  ├─ É PDF escaneado / imagem?\n"
        "  │    └─ Tesseract (OCR) → LLM (correção com imagem) → texto limpo\n"
        "  │\n"
        "  └─ Pós-processamento final\n"
        "       └─ LLM → extração estruturada (JSON) → banco de dados / RAG\n"
        "```\n"
        "\n"
        "> **Regex aparece em todas as etapas** como ferramenta de limpeza e extração.\n"
        "> Nenhuma ferramenta resolve tudo sozinha. O poder está na **combinação**.\n"
        "\n"
        "| Ferramenta | Melhor para | Evitar quando |\n"
        "|---|---|---|\n"
        "| **Regex** | Pós-processamento, padrões em texto limpo | Como ferramenta primária de parsing |\n"
        "| **BeautifulSoup** | HTML / XML estruturado | Documentos não-HTML |\n"
        "| **PyMuPDF** | PDF nativo, texto corrido, velocidade | Tabelas ou escaneados |\n"
        "| **pdfplumber** | Tabelas em PDF nativo | Escaneados ou docs sem bordas |\n"
        "| **Docling** | Docs complexos com hierarquia (RAG) | Scripts simples e rápidos |\n"
        "| **Unstructured** | Particionamento automático de docs variados | Quando precisa de controle fino |\n"
        "| **Tesseract** | OCR gratuito / offline | Precisão crítica sem pós-processamento |\n"
        "| **LLM (visão)** | OCR de tabelas, docs difíceis | Volume alto com orçamento limitado |\n"
        "| **Tesseract + LLM** | OCR em produção com qualidade | Orçamento zero |\n"
        "| **LLM (texto)** | Extração estruturada, correção, normalização | Volume massivo sem budget |",
    ),
]

# ================================================================
# GERAR TODOS OS NOTEBOOKS
# ================================================================

print("Gerando notebooks...")
create_notebook("Collab_parsing_pt2.ipynb", pt2)
create_notebook("Collab_parsing_pt3.ipynb", pt3)
create_notebook("Collab_parsing_pt4.ipynb", pt4)
create_notebook("Collab_parsing_pt5.ipynb", pt5)
create_notebook("Collab_parsing_pt6.ipynb", pt6)
print("\nTodos os notebooks gerados com sucesso!")
