from fastapi import FastAPI, File, UploadFile, Request, HTTPException
from fastapi.responses import Response, HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn
import pandas as pd
import io
from openpyxl.styles import Alignment
from clean_and_fix_text import clean_and_fix_text

app = FastAPI()
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

        if name.endswith('.xlsx'):
            tabela = pd.read_excel(io.BytesIO(content), engine='openpyxl')
        elif name.endswith('.xls'):
            tabela = pd.read_excel(io.BytesIO(content), engine='xlrd')
        elif name.endswith('.slk'):
            texto_slk = content.decode('latin-1', errors='ignore')
            dados_slk = {}
            linha_atual = 1
            col_atual = 1

            for linha_texto in texto_slk.splitlines():
                if linha_texto.startswith('C;') or linha_texto.startswith('F;'):
                    k_val = None
                    meta_part = linha_texto
                    
                    if linha_texto.startswith('C;') and ';K' in linha_texto:
                        idx = linha_texto.index(';K')
                        meta_part = linha_texto[:idx]
                        k_val = linha_texto[idx+2:]
                        
                        if k_val.startswith('"') and k_val.endswith('"'):
                            k_val = k_val[1:-1]
                    
                    partes = meta_part.split(';')
                    for p in partes:
                        if p.startswith('Y') and p[1:].isdigit():
                            linha_atual = int(p[1:])
                            col_atual = 1
                        elif p.startswith('X') and p[1:].isdigit():
                            col_atual = int(p[1:])
                    
                    if linha_texto.startswith('C;') and k_val is not None:
                        if linha_atual not in dados_slk:
                            dados_slk[linha_atual] = {}
                        dados_slk[linha_atual][col_atual] = k_val
                        col_atual += 1

            df_bruto = pd.DataFrame.from_dict(dados_slk, orient='index').sort_index(axis=0).sort_index(axis=1)
            tabela = df_bruto.iloc[1:].copy()
            tabela.columns = df_bruto.iloc[0].values
        else:
            tabela = pd.read_csv(io.BytesIO(content), sep=';', encoding='latin-1', on_bad_lines='skip')

        print("Cleaning invalid characters and HTML tags...")
        tabela.columns = [clean_and_fix_text(col) for col in tabela.columns]
        colunas_de_texto = tabela.select_dtypes(include=['object', 'string', 'str']).columns
        for col in colunas_de_texto:
            tabela[col] = tabela[col].apply(clean_and_fix_text)

        print("Generating formatted file and adjusting columns...")
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            tabela.to_excel(writer, index=False, sheet_name='Dados Limpos')
            
            worksheet = writer.sheets['Dados Limpos']
            
            for col_idx, col_name in enumerate(tabela.columns, 1):
                tamanho_maximo = max(
                    tabela[col_name].astype(str).map(len).max(),
                    len(str(col_name))
                )
                
                largura_ideal = min(tamanho_maximo + 2, 60)
                
                letra_coluna = worksheet.cell(row=1, column=col_idx).column_letter
                worksheet.column_dimensions[letra_coluna].width = largura_ideal
                
                for row_idx in range(1, len(tabela) + 2):
                    celula = worksheet.cell(row=row_idx, column=col_idx)
                    celula.alignment = Alignment(wrap_text=True, vertical='top')

        output.seek(0)

        return Response(
            content=output.getvalue(),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=GLPI_Formatado.xlsx"}
        )

    except Exception as e:
        print(f"Processing error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    print("Server running at http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)