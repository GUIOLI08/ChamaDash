from fastapi import FastAPI, File, UploadFile, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn
import pandas as pd
import io
import base64
import traceback

from clean_and_fix_text import clean_and_fix_text

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def initial_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload")
async def upload_file(archive: UploadFile = File(...)):
    try:
        name = archive.filename.lower()
        content = await archive.read()
        print(f"Reading file: {name}")

        if name.endswith(".xlsx"):
            print("Reading .xlsx file...")
            tabela = pd.read_excel(io.BytesIO(content), engine="openpyxl")
        elif name.endswith(".xls"):
            print("Reading .xls file...")
            tabela = pd.read_excel(io.BytesIO(content), engine="xlrd")
        elif name.endswith(".slk"):
            print("Reading .slk file...")
            texto_slk = content.decode("latin-1", errors="ignore")
            dados_slk = {}
            linha_atual = 1
            col_atual = 1

            for linha_texto in texto_slk.splitlines():
                if linha_texto.startswith("C;") or linha_texto.startswith("F;"):
                    k_val = None
                    meta_part = linha_texto

                    if linha_texto.startswith("C;") and ";K" in linha_texto:
                        idx = linha_texto.index(";K")
                        meta_part = linha_texto[:idx]
                        k_val = linha_texto[idx + 2 :]

                        if k_val.startswith('"') and k_val.endswith('"'):
                            k_val = k_val[1:-1]

                    partes = meta_part.split(";")
                    for p in partes:
                        if p.startswith("Y") and p[1:].isdigit():
                            linha_atual = int(p[1:])
                            col_atual = 1
                        elif p.startswith("X") and p[1:].isdigit():
                            col_atual = int(p[1:])

                    if linha_texto.startswith("C;") and k_val is not None:
                        if linha_atual not in dados_slk:
                            dados_slk[linha_atual] = {}
                        dados_slk[linha_atual][col_atual] = k_val
                        col_atual += 1

            df_bruto = (
                pd.DataFrame.from_dict(dados_slk, orient="index")
                .sort_index(axis=0)
                .sort_index(axis=1)
            )
            tabela = df_bruto.iloc[1:].copy()
            tabela.columns = df_bruto.iloc[0].values
            
        elif name.endswith(".csv"):
            print("Reading .csv file...")
            sucesso = False
            encodings = ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252']
            separators = [';', ',', '\t', '|']
            
            for enc in encodings:
                for sep in separators:
                    try:
                        tabela_temp = pd.read_csv(
                            io.BytesIO(content), sep=sep, encoding=enc,
                            on_bad_lines="skip", dtype=str, keep_default_na=False
                        )
                        if len(tabela_temp.columns) > 3:
                            tabela = tabela_temp
                            sucesso = True
                            print(f"CSV read successfully! Encoding: {enc} | Separator: '{sep}'")
                            break
                    except Exception:
                        continue
                if sucesso:
                    break
                    
            if not sucesso:
                raise ValueError("The CSV file seems to be empty or corrupted.")
        else:
            raise HTTPException(status_code=400, detail="Invalid file type")

        print("Cleaning invalid characters and HTML tags...")
        print(f"  Columns: {list(tabela.columns)}")
        print(f"  Dtypes: {tabela.dtypes.to_dict()}")
        tabela.columns = [str(col) for col in tabela.columns]
        tabela.columns = [clean_and_fix_text(col) or f"Coluna_Vazia_{i}" for i, col in enumerate(tabela.columns)]
        
        colunas_de_texto = tabela.select_dtypes(include=["object", "string"]).columns
        print(f"  Text columns: {list(colunas_de_texto)}")
        for col in colunas_de_texto:
            tabela[col] = tabela[col].astype(str).apply(clean_and_fix_text)

        print("Merging duplicate tickets...")
        coluna_id = "ID"

        if coluna_id in tabela.columns:
            funcoes_de_agrupamento = {}
            for col in tabela.columns:
                if col == coluna_id:
                    continue
                elif str(tabela[col].dtype) in ["object", "string"]:
                    funcoes_de_agrupamento[col] = lambda x: "\n---\n".join(
                        [v for v in pd.Series(x).astype(str).unique() if v not in ("", "nan", "None")]
                    )
                else:
                    funcoes_de_agrupamento[col] = "first"

            tabela = tabela.groupby(coluna_id, as_index=False).agg(
                funcoes_de_agrupamento
            )

        print("Building Dashboard...")
        output = io.BytesIO()

        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            tabela.to_excel(writer, index=False, sheet_name="Dados GLPI")
            workbook = writer.book
            aba_dados = writer.sheets["Dados GLPI"]

            formato_texto_quebrado = workbook.add_format(
                {"text_wrap": True, "valign": "top"}
            )
            for col_idx, col_name in enumerate(tabela.columns):
                if not tabela.empty:
                    tamanho_maximo = max(
                        tabela[col_name].astype(str).map(len).fillna(0).max(), len(str(col_name))
                    )
                else:
                    tamanho_maximo = len(str(col_name))
                largura_ideal = min(tamanho_maximo + 2, 60)
                aba_dados.set_column(
                    col_idx, col_idx, largura_ideal, formato_texto_quebrado
                )

            aba_dash = workbook.add_worksheet("📊 DASHBOARD")
            aba_motor = workbook.add_worksheet("Motor_Oculto")
            aba_motor.hide()

            workbook.worksheets_objs.insert(
                0,
                workbook.worksheets_objs.pop(workbook.worksheets_objs.index(aba_dash)),
            )
            aba_dash.hide_gridlines(2)

            formato_titulo = workbook.add_format(
                {"bold": True, "font_size": 22, "font_color": "#1f497d"}
            )
            fmt_cabecalho_top = workbook.add_format(
                {
                    "bold": True,
                    "bg_color": "#244062",
                    "font_color": "white",
                    "border": 1,
                    "align": "center",
                    "valign": "vcenter",
                }
            )
            fmt_cabecalho_sub = workbook.add_format(
                {
                    "bold": True,
                    "bg_color": "#4F81BD",
                    "font_color": "white",
                    "border": 1,
                    "align": "center",
                    "valign": "vcenter",
                }
            )
            fmt_cel_centro = workbook.add_format(
                {"border": 1, "align": "center", "valign": "vcenter"}
            )
            fmt_cel_esq = workbook.add_format(
                {"border": 1, "align": "left", "valign": "vcenter"}
            )
            fmt_ans = workbook.add_format(
                {
                    "border": 1,
                    "align": "center",
                    "valign": "vcenter",
                    "num_format": "0%",
                }
            )
            fmt_ans_ruim = workbook.add_format(
                {
                    "border": 1,
                    "align": "center",
                    "valign": "vcenter",
                    "num_format": "0%",
                    "font_color": "#C0504D",
                    "bold": True,
                }
            )

            aba_dash.set_column("A:B", 2)
            aba_dash.set_column("C:C", 18)
            aba_dash.set_column("D:Z", 12)

            aba_dash.write(
                "C2", "Visão Geral de Chamados - Painel Executivo", formato_titulo
            )

            linha_inicio = 6
            col_matriz = 2

            aba_dash.merge_range(
                linha_inicio - 2,
                col_matriz,
                linha_inicio - 2,
                col_matriz + 12,
                "📊 MATRIZ GERAL DE CHAMADOS E DESEMPENHO (SLA)",
                fmt_cabecalho_top,
            )

            aba_dash.merge_range(linha_inicio, col_matriz, linha_inicio, col_matriz + 1, "Chamados", fmt_cabecalho_top)
            aba_dash.merge_range(linha_inicio, col_matriz + 2, linha_inicio, col_matriz + 4, "Baixa", fmt_cabecalho_top)
            aba_dash.merge_range(linha_inicio, col_matriz + 5, linha_inicio, col_matriz + 7, "Média", fmt_cabecalho_top)
            aba_dash.merge_range(linha_inicio, col_matriz + 8, linha_inicio, col_matriz + 10, "Alta", fmt_cabecalho_top)
            aba_dash.merge_range(linha_inicio, col_matriz + 11, linha_inicio, col_matriz + 12, "Total", fmt_cabecalho_top)

            linha_sub = linha_inicio + 1
            colunas_sub = [
                "Tipos", "Qtd", "No Prazo", "Fora", "ANS", "No Prazo", "Fora", "ANS",
                "No Prazo", "Fora", "ANS", "No Prazo", "Fora",
            ]
            for c_idx, nome_col in enumerate(colunas_sub):
                aba_dash.write(linha_sub, col_matriz + c_idx, nome_col, fmt_cabecalho_sub)

            def agrupar_prioridade(p):
                p = str(p).lower()
                if "baixa" in p or "baixo" in p: return "Baixa"
                if "alta" in p or "alto" in p: return "Alta"
                return "Média"

            if "Prioridade" in tabela.columns:
                tabela["Prio_Agrupada"] = tabela["Prioridade"].apply(agrupar_prioridade)
            else:
                tabela["Prio_Agrupada"] = "Média"

            col_tipo = "Tipo" if "Tipo" in tabela.columns else None
            col_sla = (
                "Tempo para solução excedido"
                if "Tempo para solução excedido" in tabela.columns
                else None
            )

            tipos_para_tabela = [
                ("Incidente", "Incidentes"),
                ("Requisição", "Solicitações"),
                ("Problema", "Problemas"),
            ]
            linha_dados = linha_sub + 1
            totais_gerais = {
                "qtd": 0, "baixa_no": 0, "baixa_fora": 0, "media_no": 0, "media_fora": 0, "alta_no": 0, "alta_fora": 0,
            }

            tipos_gerais = {}
            inc_prio = {}
            req_prio = {}
            top_cat = {}
            top_setor = {}
            grupos_dict = {}
            sla_dict = {}

            for tipo_glpi, tipo_nome in tipos_para_tabela:
                if col_tipo and col_sla:
                    df_tipo = tabela[tabela[col_tipo] == tipo_glpi]

                    def calc_prio(df, prioridade):
                        df_p = df[df["Prio_Agrupada"] == prioridade]
                        no_prazo = len(df_p[df_p[col_sla] == "Não"])
                        fora = len(df_p[df_p[col_sla] == "Sim"])
                        ans = (
                            (no_prazo / (no_prazo + fora))
                            if (no_prazo + fora) > 0
                            else 1.0
                        )
                        return no_prazo, fora, ans

                    b_no, b_fora, b_ans = calc_prio(df_tipo, "Baixa")
                    m_no, m_fora, m_ans = calc_prio(df_tipo, "Média")
                    a_no, a_fora, a_ans = calc_prio(df_tipo, "Alta")

                    t_no = b_no + m_no + a_no
                    t_fora = b_fora + m_fora + a_fora
                    qtd_total = t_no + t_fora

                    totais_gerais["qtd"] += qtd_total
                    totais_gerais["baixa_no"] += b_no
                    totais_gerais["baixa_fora"] += b_fora
                    totais_gerais["media_no"] += m_no
                    totais_gerais["media_fora"] += m_fora
                    totais_gerais["alta_no"] += a_no
                    totais_gerais["alta_fora"] += a_fora

                    dados_linha = [
                        tipo_nome, qtd_total, b_no, b_fora, b_ans, m_no, m_fora, m_ans, a_no, a_fora, a_ans, t_no, t_fora,
                    ]
                    for i, valor in enumerate(dados_linha):
                        col_atual = col_matriz + i
                        if i == 0:
                            aba_dash.write(linha_dados, col_atual, valor, fmt_cel_esq)
                        elif i in [4, 7, 10]:
                            aba_dash.write(
                                linha_dados, col_atual, valor, fmt_ans if valor >= 0.8 else fmt_ans_ruim,
                            )
                        else:
                            aba_dash.write(
                                linha_dados, col_atual, valor, fmt_cel_centro
                            )
                    linha_dados += 1

            t_b_no = totais_gerais["baixa_no"]
            t_b_fora = totais_gerais["baixa_fora"]
            t_m_no = totais_gerais["media_no"]
            t_m_fora = totais_gerais["media_fora"]
            t_a_no = totais_gerais["alta_no"]
            t_a_fora = totais_gerais["alta_fora"]

            t_no_total = t_b_no + t_m_no + t_a_no
            t_fora_total = t_b_fora + t_m_fora + t_a_fora
            t_b_ans = (t_b_no / (t_b_no + t_b_fora)) if (t_b_no + t_b_fora) > 0 else 1.0
            t_m_ans = (t_m_no / (t_m_no + t_m_fora)) if (t_m_no + t_m_fora) > 0 else 1.0
            t_a_ans = (t_a_no / (t_a_no + t_a_fora)) if (t_a_no + t_a_fora) > 0 else 1.0

            linha_total = [
                "Total", totais_gerais["qtd"], t_b_no, t_b_fora, t_b_ans, t_m_no, t_m_fora, t_m_ans,
                t_a_no, t_a_fora, t_a_ans, t_no_total, t_fora_total,
            ]
            for i, valor in enumerate(linha_total):
                col_atual = col_matriz + i
                if i == 0:
                    aba_dash.write(linha_dados, col_atual, valor, fmt_cabecalho_sub)
                elif i in [4, 7, 10]:
                    aba_dash.write(
                        linha_dados, col_atual, valor, fmt_ans if valor >= 0.8 else fmt_ans_ruim,
                    )
                else:
                    aba_dash.write(linha_dados, col_atual, valor, fmt_cabecalho_sub)

            if col_tipo:
                counts = tabela[col_tipo].value_counts()
                aba_motor.write_column("A1", counts.index)
                aba_motor.write_column("B1", counts.values)
                g_tipo = workbook.add_chart({"type": "pie"})
                g_tipo.add_series(
                    {
                        "categories": ["Motor_Oculto", 0, 0, len(counts) - 1, 0],
                        "values": ["Motor_Oculto", 0, 1, len(counts) - 1, 1],
                        "data_labels": {"percentage": True},
                    }
                )
                g_tipo.set_title({"name": "1. Distribuição por Tipo"})
                g_tipo.set_style(10)
                g_tipo.set_chartarea({"border": {"none": True}})
                g_tipo.set_size({"width": 380, "height": 260})
                aba_dash.insert_chart("C14", g_tipo, {"x_offset": 5})
                tipos_gerais = counts.to_dict()

            if col_tipo and "Prio_Agrupada" in tabela.columns:
                counts_inc = tabela[tabela[col_tipo] == "Incidente"]["Prio_Agrupada"].value_counts()
                aba_motor.write_column("D1", counts_inc.index)
                aba_motor.write_column("E1", counts_inc.values)
                g_inc = workbook.add_chart({"type": "pie"})
                g_inc.add_series(
                    {
                        "categories": ["Motor_Oculto", 0, 3, len(counts_inc) - 1, 3],
                        "values": ["Motor_Oculto", 0, 4, len(counts_inc) - 1, 4],
                        "data_labels": {"percentage": True},
                    }
                )
                g_inc.set_title({"name": "2. Incidentes por Prioridade"})
                g_inc.set_style(10)
                g_inc.set_chartarea({"border": {"none": True}})
                g_inc.set_size({"width": 380, "height": 260})
                aba_dash.insert_chart("H14", g_inc, {"x_offset": 5})
                inc_prio = counts_inc.to_dict()

                counts_req = tabela[tabela[col_tipo] == "Requisição"]["Prio_Agrupada"].value_counts()
                aba_motor.write_column("G1", counts_req.index)
                aba_motor.write_column("H1", counts_req.values)
                g_req = workbook.add_chart({"type": "pie"})
                g_req.add_series(
                    {
                        "categories": ["Motor_Oculto", 0, 6, len(counts_req) - 1, 6],
                        "values": ["Motor_Oculto", 0, 7, len(counts_req) - 1, 7],
                        "data_labels": {"percentage": True},
                    }
                )
                g_req.set_title({"name": "3. Solicitações por Prioridade"})
                g_req.set_style(10)
                g_req.set_chartarea({"border": {"none": True}})
                g_req.set_size({"width": 380, "height": 260})
                aba_dash.insert_chart("M14", g_req, {"x_offset": 5})
                req_prio = counts_req.to_dict()

            def desenhar_tabela(
                aba, linha_ini, col_ini, col_span, titulo_geral, titulo_col1, serie_dados,
            ):
                col_fim_nome = col_ini + col_span - 1
                col_qtd = col_ini + col_span
                aba.merge_range(
                    linha_ini, col_ini, linha_ini, col_qtd, titulo_geral, fmt_cabecalho_top,
                )
                if col_span > 1:
                    aba.merge_range(
                        linha_ini + 1, col_ini, linha_ini + 1, col_fim_nome, titulo_col1, fmt_cabecalho_sub,
                    )
                else:
                    aba.write(linha_ini + 1, col_ini, titulo_col1, fmt_cabecalho_sub)
                aba.write(linha_ini + 1, col_qtd, "Qtd", fmt_cabecalho_sub)
                l_atual = linha_ini + 2
                for index, valor in serie_dados.items():
                    if col_span > 1:
                        aba.merge_range(
                            l_atual, col_ini, l_atual, col_fim_nome, str(index), fmt_cel_esq,
                        )
                    else:
                        aba.write(l_atual, col_ini, str(index), fmt_cel_esq)
                    aba.write(l_atual, col_qtd, valor, fmt_cel_centro)
                    l_atual += 1

            if "Categoria" in tabela.columns:
                cat_counts = tabela["Categoria"].value_counts().head(10)
                desenhar_tabela(
                    aba_dash, 31, 2, 3, "🏆 TOP 10 CATEGORIAS", "Categoria", cat_counts
                )
                aba_motor.write_column("J1", cat_counts.index)
                aba_motor.write_column("K1", cat_counts.values)
                g_cat = workbook.add_chart({"type": "bar"})
                g_cat.add_series(
                    {
                        "categories": ["Motor_Oculto", 0, 9, len(cat_counts) - 1, 9],
                        "values": ["Motor_Oculto", 0, 10, len(cat_counts) - 1, 10],
                        "fill": {"color": "#C0504D"},
                    }
                )
                g_cat.set_title({"name": "Gráfico - Top Categorias"})
                g_cat.set_legend({"none": True})
                g_cat.set_style(10)
                g_cat.set_chartarea({"border": {"none": True}})
                g_cat.set_size({"width": 450, "height": 300})
                aba_dash.insert_chart("G32", g_cat, {"x_offset": 15, "y_offset": 5})
                top_cat = cat_counts.to_dict()

            if "Localização" in tabela.columns:
                setor_counts = tabela["Localização"].value_counts().head(10)
                desenhar_tabela(
                    aba_dash, 31, 12, 3, "🏢 TOP 10 SETORES", "Setor", setor_counts
                )
                aba_motor.write_column("M1", setor_counts.index)
                aba_motor.write_column("N1", setor_counts.values)
                g_setor = workbook.add_chart({"type": "bar"})
                g_setor.add_series(
                    {
                        "categories": [
                            "Motor_Oculto", 0, 12, len(setor_counts) - 1, 12,
                        ],
                        "values": ["Motor_Oculto", 0, 13, len(setor_counts) - 1, 13],
                        "fill": {"color": "#4F81BD"},
                    }
                )
                g_setor.set_title({"name": "Gráfico - Top Setores"})
                g_setor.set_legend({"none": True})
                g_setor.set_style(10)
                g_setor.set_chartarea({"border": {"none": True}})
                g_setor.set_size({"width": 450, "height": 300})
                aba_dash.insert_chart("Q32", g_setor, {"x_offset": 15, "y_offset": 5})
                top_setor = setor_counts.to_dict()

            linha_s3 = 54
            
            col_usuario = 'Requerente' if 'Requerente' in tabela.columns else ('Usuário' if 'Usuário' in tabela.columns else None)
            if col_usuario:
                top_usu = tabela[col_usuario].value_counts().head(10)
                desenhar_tabela(aba_dash, linha_s3-1, 2, 2, '👤 TOP 10 USUÁRIOS', 'Usuário', top_usu)
            
            col_tecnico = 'Atribuído para - Técnico' if 'Atribuído para - Técnico' in tabela.columns else None
            if col_tecnico:
                todos_tec = tabela[col_tecnico].value_counts() 
                desenhar_tabela(aba_dash, linha_s3-1, 6, 3, '🛠️ TÉCNICOS (TODOS)', 'Técnico', todos_tec)

            col_grupo = 'Atribuído para - Grupo técnico'
            if col_grupo in tabela.columns:
                grupos = tabela[col_grupo].value_counts().head(8)
                aba_motor.write_column('P1', grupos.index); aba_motor.write_column('Q1', grupos.values)
                g_grupo = workbook.add_chart({'type': 'pie'})
                g_grupo.add_series({'categories': ['Motor_Oculto', 0, 15, len(grupos)-1, 15], 'values': ['Motor_Oculto', 0, 16, len(grupos)-1, 16], 'data_labels': {'percentage': True}})
                g_grupo.set_title({'name': 'Grupo Técnico'})
                g_grupo.set_style(10); g_grupo.set_chartarea({'border': {'none': True}})
                g_grupo.set_size({'width': 360, 'height': 260})
                aba_dash.insert_chart(f'L{linha_s3}', g_grupo, {'x_offset': 15, 'y_offset': 5})
                grupos_dict = grupos.to_dict()

            if col_sla:
                sla = tabela[col_sla].value_counts()
                aba_motor.write_column('S1', sla.index); aba_motor.write_column('T1', sla.values)
                g_sla = workbook.add_chart({'type': 'pie'})
                g_sla.add_series({'categories': ['Motor_Oculto', 0, 18, len(sla)-1, 18], 'values': ['Motor_Oculto', 0, 19, len(sla)-1, 19], 'data_labels': {'percentage': True}})
                g_sla.set_title({'name': 'SLA Geral'})
                g_sla.set_style(10); g_sla.set_chartarea({'border': {'none': True}})
                g_sla.set_size({'width': 360, 'height': 260})
                aba_dash.insert_chart(f'Q{linha_s3}', g_sla, {'x_offset': 15, 'y_offset': 5})
                sla_dict = sla.to_dict()

        output.seek(0)

        excel_b64 = base64.b64encode(output.getvalue()).decode("utf-8")

        dados_dashboard = {
            "tipos_gerais": {str(k): int(v) for k, v in tipos_gerais.items()},
            "inc_prio": {str(k): int(v) for k, v in inc_prio.items()},
            "req_prio": {str(k): int(v) for k, v in req_prio.items()},
            "top_categorias": {str(k): int(v) for k, v in top_cat.items()},
            "top_setores": {str(k): int(v) for k, v in top_setor.items()},
            "grupos_tecnicos": {str(k): int(v) for k, v in grupos_dict.items()},
            "sla_geral": {str(k): int(v) for k, v in sla_dict.items()}
        }

        return JSONResponse(
            content={
                "mensagem": "Chamadash gerado com sucesso!",
                "dados": dados_dashboard,
                "arquivo_excel": excel_b64,
            }
        )

    except Exception as e:
        traceback.print_exc()
        print(f"Erro de processamento: {e}")
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))
    print(f"ChamaDash rodando na porta {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)