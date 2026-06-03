# -*- coding: utf-8 -*-
"""
EXPRESS CONSUMO OC — By Maicon
Versão Android corrigida para não usar URI content://tree como caminho comum.
"""

import os
import re
import sys
import math
import shutil
import unicodedata
import traceback
from pathlib import Path
from datetime import datetime

from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import StringProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.utils import platform

KV = r'''
<RootUI>:
    orientation: "vertical"
    padding: dp(14)
    spacing: dp(8)
    canvas.before:
        Color:
            rgba: 0.02, 0.04, 0.10, 1
        Rectangle:
            pos: self.pos
            size: self.size

    BoxLayout:
        orientation: "vertical"
        size_hint_y: None
        height: dp(150)
        spacing: dp(4)
        Label:
            text: "EXPRESS CONSUMO OC"
            font_size: "31sp"
            bold: True
            color: 1, 1, 1, 1
            halign: "center"
            valign: "middle"
            text_size: self.size
        Label:
            text: "Cálculo de Consumo • Conferência de Ordem de Compra"
            font_size: "16sp"
            bold: True
            color: 0.95, 0.65, 0.13, 1
            halign: "center"
            valign: "middle"
            text_size: self.size
        BoxLayout:
            size_hint_y: None
            height: dp(42)
            spacing: dp(12)
            TextInput:
                id: data_ini
                text: root.data_inicio
                hint_text: "dd/mm/aaaa"
                multiline: False
                font_size: "18sp"
                foreground_color: 1,1,1,1
                background_color: 0,0,0,0
                cursor_color: 0.95,0.65,0.13,1
            TextInput:
                id: data_fim
                text: root.data_fim
                hint_text: "dd/mm/aaaa"
                multiline: False
                font_size: "18sp"
                foreground_color: 1,1,1,1
                background_color: 0,0,0,0
                cursor_color: 0.95,0.65,0.13,1

    Button:
        text: "📄 Escolher PDF Analítico"
        size_hint_y: None
        height: dp(56)
        font_size: "18sp"
        bold: True
        background_normal: ""
        background_color: 0.02, 0.31, 0.72, 1
        on_release: root.escolher_analitico()

    Button:
        text: "🧾 Escolher PDF Ordem de Compra"
        size_hint_y: None
        height: dp(56)
        font_size: "18sp"
        bold: True
        background_normal: ""
        background_color: 0.02, 0.31, 0.72, 1
        on_release: root.escolher_oc()

    Button:
        text: "📁 Usar pasta automática segura"
        size_hint_y: None
        height: dp(56)
        font_size: "18sp"
        bold: True
        background_normal: ""
        background_color: 0.02, 0.31, 0.72, 1
        on_release: root.definir_pasta_automatica()

    Button:
        text: "📊 Gerar consumo semanal"
        size_hint_y: None
        height: dp(56)
        font_size: "18sp"
        bold: True
        background_normal: ""
        background_color: 0.02, 0.31, 0.72, 1
        on_release: root.gerar_consumo()

    Button:
        text: "✅ Conferir Ordem de Compra"
        size_hint_y: None
        height: dp(56)
        font_size: "18sp"
        bold: True
        background_normal: ""
        background_color: 0.02, 0.31, 0.72, 1
        on_release: root.conferir_oc()

    ScrollView:
        do_scroll_x: False
        Label:
            id: status
            text: root.status
            size_hint_y: None
            height: max(self.texture_size[1] + dp(30), dp(220))
            font_size: "14sp"
            color: 0.88, 0.90, 0.95, 1
            halign: "left"
            valign: "top"
            text_size: self.width, None

    Label:
        text: root.rodape
        size_hint_y: None
        height: dp(26)
        font_size: "14sp"
        color: 0.72, 0.74, 0.80, 1
        halign: "right"
        valign: "middle"
        text_size: self.size
'''

Builder.load_string(KV)


def hoje_br() -> str:
    return datetime.now().strftime("%d/%m/%Y")


def normalizar_nome(txt: str) -> str:
    if not txt:
        return ""
    txt = unicodedata.normalize("NFKD", txt)
    txt = "".join(c for c in txt if not unicodedata.combining(c))
    txt = txt.upper().strip()
    txt = re.sub(r"[^A-Z0-9 KGUNLT/.-]+", " ", txt)
    palavras_remover = {
        "KG", "UN", "UND", "LT", "L", "CX", "PCT", "PACOTE", "CAIXA",
        "CONGELADO", "RESFRIADO", "NAO", "PERECIVEL", "PERECIVEIS"
    }
    partes = [p for p in txt.split() if p not in palavras_remover]
    return " ".join(partes)


def parse_qtd(valor: str) -> float:
    if valor is None:
        return 0.0
    s = str(valor).strip()
    s = re.sub(r"[^0-9,.-]", "", s)
    if not s:
        return 0.0
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")
    else:
        s = s.replace(",", ".")
    try:
        return float(s)
    except Exception:
        return 0.0


def fmt_qtd(v: float) -> str:
    try:
        if abs(v - round(v)) < 0.001:
            return str(int(round(v)))
        return f"{v:.3f}".replace(".", ",").rstrip("0").rstrip(",")
    except Exception:
        return str(v)


def extrair_texto_pdf(caminho_pdf: str) -> str:
    texto = ""
    try:
        import pdfplumber
        with pdfplumber.open(caminho_pdf) as pdf:
            for page in pdf.pages:
                texto += (page.extract_text() or "") + "\n"
    except Exception as e:
        raise RuntimeError(f"Falha ao ler PDF: {e}")
    return texto


def extrair_analitico(caminho_pdf: str, data_ini: str, data_fim: str):
    """Extrator tolerante para relatório analítico: produto, unidade, quantidade e data."""
    texto = extrair_texto_pdf(caminho_pdf)
    linhas = [l.strip() for l in texto.splitlines() if l.strip()]
    itens = []
    data_atual = ""
    servico_atual = ""

    for linha in linhas:
        m_data = re.search(r"(?:Data|DATA)\s*[:\-]?\s*(\d{2}/\d{2}/\d{4})", linha)
        if m_data:
            data_atual = m_data.group(1)

        m_serv = re.search(r"\b(ALMO[CÇ]O|JANTAR|JANTA|CEIA)\b", linha, re.I)
        if m_serv:
            servico_atual = m_serv.group(1).upper().replace("Ç", "C")

        # Padrão comum: código + descrição + qtd + unidade
        m = re.search(
            r"(?P<cod>\d+\.\d+\.\d+(?:\.\d+)*)\s+(?P<nome>.+?)\s+(?P<qtd>\d{1,6}(?:[\.,]\d{1,3})?)\s+(?P<un>KG|UN|UND|LT|L|CX|PCT)\b",
            linha,
            re.I,
        )
        if m:
            nome = m.group("nome").strip(" -")
            qtd = parse_qtd(m.group("qtd"))
            un = m.group("un").upper().replace("UND", "UN").replace("L", "LT")
            if nome and qtd > 0:
                itens.append({
                    "codigo": m.group("cod"),
                    "produto": nome.upper(),
                    "chave": normalizar_nome(nome),
                    "unidade": un,
                    "necessario": qtd,
                    "data": data_atual,
                    "turno": servico_atual,
                    "origem": "ANALITICO",
                })

    if not itens:
        # fallback: linhas com nome e quantidade/unidade sem código
        for linha in linhas:
            m = re.search(r"(?P<nome>[A-Za-zÁ-Úá-ú0-9 /.-]{4,})\s+(?P<qtd>\d{1,6}(?:[\.,]\d{1,3})?)\s+(?P<un>KG|UN|UND|LT|L|CX|PCT)\b", linha, re.I)
            if m:
                nome = m.group("nome").strip(" -")
                qtd = parse_qtd(m.group("qtd"))
                if qtd > 0:
                    itens.append({
                        "codigo": "",
                        "produto": nome.upper(),
                        "chave": normalizar_nome(nome),
                        "unidade": m.group("un").upper().replace("UND", "UN").replace("L", "LT"),
                        "necessario": qtd,
                        "data": data_atual,
                        "turno": servico_atual,
                        "origem": "ANALITICO",
                    })

    return consolidar_itens(itens, campo_qtd="necessario")


def extrair_oc(caminho_pdf: str):
    """Extrator tolerante para Ordem de Compra: produto, unidade, quantidade, entrega/utilização."""
    texto = extrair_texto_pdf(caminho_pdf)
    linhas = [l.strip() for l in texto.splitlines() if l.strip()]
    itens = []

    for linha in linhas:
        # Modelo esperado: Produto UN Quantidade Entrega Utilização
        m = re.search(
            r"(?P<nome>[A-Za-zÁ-Úá-ú0-9 /().,-]{4,}?)\s+(?P<un>KG|UN|UND|LT|L|CX|PCT)\s+(?P<qtd>\d{1,6}(?:[\.,]\d{1,3})?)\s*(?P<resto>.*)$",
            linha,
            re.I,
        )
        if m:
            nome = m.group("nome").strip(" -")
            if any(x in nome.upper() for x in ["PRODUTO", "QUANTIDADE", "SOLICITACAO", "FILIAL"]):
                continue
            qtd = parse_qtd(m.group("qtd"))
            if qtd <= 0:
                continue
            datas = re.findall(r"\d{2}/\d{2}/\d{4}", m.group("resto"))
            itens.append({
                "produto": nome.upper(),
                "chave": normalizar_nome(nome),
                "unidade": m.group("un").upper().replace("UND", "UN").replace("L", "LT"),
                "comprado": qtd,
                "entrega": datas[0] if len(datas) >= 1 else "",
                "utilizacao": datas[-1] if datas else "",
                "origem": "OC",
            })

    return consolidar_itens(itens, campo_qtd="comprado")


def consolidar_itens(itens, campo_qtd: str):
    consol = {}
    for it in itens:
        chave = f"{it.get('chave','')}|{it.get('unidade','')}|{it.get('data') or it.get('utilizacao') or ''}"
        if chave not in consol:
            consol[chave] = dict(it)
        else:
            consol[chave][campo_qtd] = consol[chave].get(campo_qtd, 0) + it.get(campo_qtd, 0)
            # mantém nome mais comprido, geralmente mais descritivo
            if len(it.get("produto", "")) > len(consol[chave].get("produto", "")):
                consol[chave]["produto"] = it.get("produto", "")
    return list(consol.values())


def comparar_consumo_oc(consumo, oc):
    oc_por_chave = {}
    for item in oc:
        base = item["chave"]
        oc_por_chave.setdefault(base, []).append(item)

    faltantes = []
    sobras = []
    conferidos = []
    usados_oc = set()

    for nec in consumo:
        chave = nec["chave"]
        candidatos = oc_por_chave.get(chave, [])
        # busca aproximada simples
        if not candidatos:
            for k, vals in oc_por_chave.items():
                if chave and (chave in k or k in chave):
                    candidatos = vals
                    break
        comprado = sum(c.get("comprado", 0) for c in candidatos)
        for c in candidatos:
            usados_oc.add(id(c))
        necessario = nec.get("necessario", 0)
        diff = comprado - necessario
        linha = {
            "produto": nec.get("produto", ""),
            "unidade": nec.get("unidade", ""),
            "necessario": necessario,
            "comprado": comprado,
            "data": nec.get("data", ""),
            "observacao": "OK" if diff >= -0.001 else "FALTA CRÍTICA PARA DATA DE CONSUMO",
        }
        conferidos.append(linha)
        if diff < -0.001:
            linha["faltante"] = abs(diff)
            faltantes.append(linha)
        elif diff > 0.001:
            linha["sobra"] = diff
            sobras.append(linha)

    # itens comprados sem consumo identificado entram como sobra/excedente
    for item in oc:
        if id(item) not in usados_oc:
            sobras.append({
                "produto": item.get("produto", ""),
                "unidade": item.get("unidade", ""),
                "necessario": 0,
                "comprado": item.get("comprado", 0),
                "sobra": item.get("comprado", 0),
                "data": item.get("utilizacao", ""),
                "observacao": "ITEM NA OC SEM CONSUMO IDENTIFICADO NO ANALÍTICO",
            })
    return faltantes, sobras, conferidos


def gerar_pdf_tabela(titulo, subtitulo, linhas, colunas, caminho):
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

    doc = SimpleDocTemplate(caminho, pagesize=landscape(A4), rightMargin=0.8*cm, leftMargin=0.8*cm, topMargin=0.8*cm, bottomMargin=0.8*cm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleExpress", parent=styles["Title"], fontSize=18, leading=22, alignment=1)
    sub_style = ParagraphStyle("SubExpress", parent=styles["Normal"], fontSize=9, alignment=1)
    cell_style = ParagraphStyle("Cell", parent=styles["Normal"], fontSize=7, leading=8)

    story = [Paragraph(titulo, title_style), Paragraph(subtitulo, sub_style), Spacer(1, 0.25*cm)]
    dados = [[Paragraph(str(c), cell_style) for c in colunas]]
    for i, row in enumerate(linhas, start=1):
        dados.append([Paragraph(str(row.get(c, "")), cell_style) for c in colunas])

    tabela = Table(dados, repeatRows=1)
    tabela.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#D9EAF7")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F6F8FA")]),
    ]))
    story.append(tabela)
    story.append(Spacer(1, 0.25*cm))
    story.append(Paragraph(f"{hoje_br()} - By Maicon", sub_style))
    doc.build(story)


def gerar_excel(conferidos, faltantes, sobras, caminho):
    import pandas as pd
    with pd.ExcelWriter(caminho, engine="openpyxl") as writer:
        pd.DataFrame(conferidos).to_excel(writer, sheet_name="Conferencia", index=False)
        pd.DataFrame(faltantes).to_excel(writer, sheet_name="Faltantes", index=False)
        pd.DataFrame(sobras).to_excel(writer, sheet_name="Sobras", index=False)


class RootUI(BoxLayout):
    status = StringProperty("Pronto. Escolha os PDFs e gere os relatórios.\n")
    data_inicio = StringProperty("11/06/2026")
    data_fim = StringProperty("17/06/2026")
    rodape = StringProperty(f"{hoje_br()} - By Maicon")
    analitico_path = StringProperty("")
    oc_path = StringProperty("")
    output_dir = StringProperty("")
    busy = BooleanProperty(False)

    def log(self, msg):
        self.status += f"\n{msg}"

    def set_status(self, msg):
        self.status = msg

    def get_output_dir(self):
        if platform == "android":
            try:
                from android.storage import app_storage_path
                base = app_storage_path()
            except Exception:
                base = os.getcwd()
        else:
            base = os.path.join(os.getcwd(), "saida")
        pasta = os.path.join(base, "relatorios")
        os.makedirs(pasta, exist_ok=True)
        self.output_dir = pasta
        return pasta

    def definir_pasta_automatica(self):
        pasta = self.get_output_dir()
        self.set_status(
            "Pasta de saída OK.\n"
            "Esta versão não usa content://tree como caminho comum, evitando o erro Invalid URI.\n\n"
            f"Relatórios serão salvos em:\n{pasta}"
        )

    def escolher_analitico(self):
        self._escolher_pdf("analitico")

    def escolher_oc(self):
        self._escolher_pdf("oc")

    def _escolher_pdf(self, tipo):
        try:
            from plyer import filechooser
            filechooser.open_file(on_selection=lambda selection: self._on_pdf_selection(selection, tipo), filters=[("PDF", "*.pdf")])
        except Exception as e:
            self.log(f"Erro ao abrir seletor de PDF: {e}")

    def _on_pdf_selection(self, selection, tipo):
        if not selection:
            self.log("Nenhum arquivo selecionado.")
            return
        uri = selection[0]
        try:
            caminho = self.copiar_uri_para_cache(uri, tipo)
            if tipo == "analitico":
                self.analitico_path = caminho
                self.log(f"Analítico OK:\n{caminho}")
            else:
                self.oc_path = caminho
                self.log(f"Ordem de Compra OK:\n{caminho}")
        except Exception as e:
            self.log(f"Erro ao preparar arquivo {tipo}: {e}")

    def copiar_uri_para_cache(self, uri, prefixo):
        """Copia content:// para arquivo real no cache interno. Corrige o erro Invalid URI."""
        uri = str(uri)
        cache_dir = os.path.join(self.get_output_dir(), "cache")
        os.makedirs(cache_dir, exist_ok=True)
        destino = os.path.join(cache_dir, f"{prefixo}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")

        if uri.startswith("content://") and platform == "android":
            from jnius import autoclass
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            Uri = autoclass("android.net.Uri")
            activity = PythonActivity.mActivity
            resolver = activity.getContentResolver()
            input_stream = resolver.openInputStream(Uri.parse(uri))
            if input_stream is None:
                raise RuntimeError("Android não liberou leitura deste arquivo.")
            from jnius import jarray
            buffer = jarray("b")(8192)
            with open(destino, "wb") as out:
                while True:
                    n = input_stream.read(buffer)
                    if n == -1 or n == 0:
                        break
                    out.write(bytes((buffer[i] & 0xFF) for i in range(n)))
            input_stream.close()
            return destino

        if uri.startswith("file://"):
            origem = uri.replace("file://", "")
        else:
            origem = uri
        if not os.path.exists(origem):
            raise RuntimeError(f"Arquivo não encontrado: {origem}")
        shutil.copyfile(origem, destino)
        return destino

    def _datas_tela(self):
        di = self.ids.data_ini.text.strip()
        df = self.ids.data_fim.text.strip()
        for d in [di, df]:
            if not re.match(r"^\d{2}/\d{2}/\d{4}$", d):
                raise ValueError("Datas devem estar no formato dd/mm/aaaa.")
        return di, df

    def gerar_consumo(self):
        if self.busy:
            return
        Clock.schedule_once(lambda dt: self._gerar_consumo_exec(), 0.1)

    def _gerar_consumo_exec(self):
        try:
            self.busy = True
            self.set_status("Processando consumo semanal...")
            if not self.analitico_path:
                raise RuntimeError("Escolha primeiro o PDF Analítico.")
            di, df = self._datas_tela()
            itens = extrair_analitico(self.analitico_path, di, df)
            if not itens:
                raise RuntimeError("Nenhum item foi extraído do analítico. Verifique se o PDF tem texto selecionável.")
            pasta = self.get_output_dir()
            linhas = []
            for it in itens:
                linhas.append({
                    "PRODUTO": it.get("produto", ""),
                    "UN": it.get("unidade", ""),
                    "NECESSÁRIO": fmt_qtd(it.get("necessario", 0)),
                    "DATA": it.get("data", ""),
                    "TURNO": it.get("turno", ""),
                    "OBSERVAÇÃO": "CONSUMO PREVISTO DO ANALÍTICO",
                })
            caminho_pdf = os.path.join(pasta, "RELATORIO_CONSUMO_SEMANAL.pdf")
            gerar_pdf_tabela(
                "RELATÓRIO DE CONSUMO SEMANAL",
                f"Período: {di} a {df}",
                linhas,
                ["PRODUTO", "UN", "NECESSÁRIO", "DATA", "TURNO", "OBSERVAÇÃO"],
                caminho_pdf,
            )
            self.set_status(f"Consumo semanal gerado com sucesso.\n\nItens extraídos: {len(itens)}\nArquivo:\n{caminho_pdf}")
        except Exception as e:
            self.set_status(f"ERRO ao gerar consumo semanal:\n{e}\n\nDetalhe técnico:\n{traceback.format_exc()[-1200:]}")
        finally:
            self.busy = False

    def conferir_oc(self):
        if self.busy:
            return
        Clock.schedule_once(lambda dt: self._conferir_oc_exec(), 0.1)

    def _conferir_oc_exec(self):
        try:
            self.busy = True
            self.set_status("Conferindo Ordem de Compra...")
            if not self.analitico_path:
                raise RuntimeError("Escolha primeiro o PDF Analítico.")
            if not self.oc_path:
                raise RuntimeError("Escolha primeiro o PDF da Ordem de Compra.")
            di, df = self._datas_tela()
            consumo = extrair_analitico(self.analitico_path, di, df)
            oc = extrair_oc(self.oc_path)
            if not consumo:
                raise RuntimeError("Nenhum item foi extraído do Analítico.")
            if not oc:
                raise RuntimeError("Nenhum item foi extraído da Ordem de Compra.")
            faltantes, sobras, conferidos = comparar_consumo_oc(consumo, oc)
            pasta = self.get_output_dir()

            faltantes_pdf = os.path.join(pasta, "RELATORIO_ITENS_FALTANTES.pdf")
            sobras_pdf = os.path.join(pasta, "RELATORIO_ITENS_SOBRAS.pdf")
            excel = os.path.join(pasta, "CONFERENCIA_CONSUMO_X_OC.xlsx")

            linhas_f = [{
                "PRODUTO": x["produto"], "UN": x["unidade"],
                "NECESSÁRIO": fmt_qtd(x["necessario"]), "COMPRADO": fmt_qtd(x["comprado"]),
                "FALTANTE": fmt_qtd(x.get("faltante", 0)), "DATA": x.get("data", ""),
                "OBSERVAÇÃO": x.get("observacao", ""),
            } for x in faltantes]
            linhas_s = [{
                "PRODUTO": x["produto"], "UN": x["unidade"],
                "NECESSÁRIO": fmt_qtd(x["necessario"]), "COMPRADO": fmt_qtd(x["comprado"]),
                "SOBRA": fmt_qtd(x.get("sobra", 0)), "DATA": x.get("data", ""),
                "OBSERVAÇÃO": x.get("observacao", ""),
            } for x in sobras]

            if not linhas_f:
                linhas_f = [{"PRODUTO": "SEM FALTANTES", "UN": "", "NECESSÁRIO": "", "COMPRADO": "", "FALTANTE": "", "DATA": "", "OBSERVAÇÃO": "Nenhum item faltante identificado."}]
            if not linhas_s:
                linhas_s = [{"PRODUTO": "SEM SOBRAS", "UN": "", "NECESSÁRIO": "", "COMPRADO": "", "SOBRA": "", "DATA": "", "OBSERVAÇÃO": "Nenhuma sobra identificada."}]

            gerar_pdf_tabela(
                "RELATÓRIO DE ITENS FALTANTES",
                f"Conferência Consumo Necessário x Ordem de Compra | {di} a {df}",
                linhas_f,
                ["PRODUTO", "UN", "NECESSÁRIO", "COMPRADO", "FALTANTE", "DATA", "OBSERVAÇÃO"],
                faltantes_pdf,
            )
            gerar_pdf_tabela(
                "RELATÓRIO DE ITENS COM SOBRA",
                f"Conferência Consumo Necessário x Ordem de Compra | {di} a {df}",
                linhas_s,
                ["PRODUTO", "UN", "NECESSÁRIO", "COMPRADO", "SOBRA", "DATA", "OBSERVAÇÃO"],
                sobras_pdf,
            )
            gerar_excel(conferidos, faltantes, sobras, excel)

            self.set_status(
                "Conferência concluída com sucesso.\n\n"
                f"Itens consumo: {len(consumo)}\n"
                f"Itens OC: {len(oc)}\n"
                f"Faltantes: {max(0, len(faltantes))}\n"
                f"Sobras/excedentes: {max(0, len(sobras))}\n\n"
                f"PDF faltantes:\n{faltantes_pdf}\n\n"
                f"PDF sobras:\n{sobras_pdf}\n\n"
                f"Excel conferência:\n{excel}"
            )
        except Exception as e:
            self.set_status(f"ERRO na conferência:\n{e}\n\nDetalhe técnico:\n{traceback.format_exc()[-1400:]}")
        finally:
            self.busy = False


class ExpressConsumoOCApp(App):
    def build(self):
        self.title = "EXPRESS CONSUMO OC"
        return RootUI()


if __name__ == "__main__":
    ExpressConsumoOCApp().run()
