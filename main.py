from fastapi import FastAPI, File, UploadFile, Request, HTTPException
from fastapi.responses import Response, HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn
import pandas as pd
import io
import re
import html

app = FastAPI()
templates = Jinja2Templates(directory="templates")

def limpar_e_consertar_texto(texto):
    if pd.isna(texto):
        return texto
    
    texto = str(texto)
    texto = html.unescape(texto) 
    texto = re.sub(r'<[^>]+>', ' ', texto) 
    texto = re.sub(r'\s+', ' ', texto).strip() 

    correcoes = {
        'Ãš': 'Ú', 'Ã§': 'ç', 'Ã£': 'ã', 'Ã©': 'é', 
        'Ã\xad': 'í', 'Ãª': 'ê', 'Ã¡': 'á', 'Ãµ': 'õ', 
        'Ã³': 'ó', 'Ã¢': 'â', 'Ã‡': 'Ç', 'Ãƒ': 'Ã', 
        'Ã•': 'Õ', 'Ã‰': 'É', 'Ã ': 'À', 'Ã\x8d': 'Í', 
        'Ã“': 'Ó', 'Ã‚': 'Â', 'ÃŠ': 'Ê'
    }
    for errado, certo in correcoes.items():
        texto = texto.replace(errado, certo)
        
    return texto

@app.get("/", response_class=HTMLResponse)
async def initial_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload")
async def upload_file(archive: UploadFile = File(...)):
    try:
        name = archive.filename.lower()
        content = await archive.read()
        print(f"Lendo arquivo: {name}")

        # 1. LEITURA BRUTA
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
                # O SEGREDO TÁ AQUI: Rastreamos X e Y tanto em Dados (C;) quanto Formatação (F;)
                if linha_texto.startswith('C;') or linha_texto.startswith('F;'):
                    k_val = None
                    meta_part = linha_texto
                    
                    # Extrai o valor K apenas se for uma célula de dados (C;)
                    if linha_texto.startswith('C;') and ';K' in linha_texto:
                        idx = linha_texto.index(';K')
                        meta_part = linha_texto[:idx] # Tudo antes do K
                        k_val = linha_texto[idx+2:]   # Tudo depois do K
                        
                        # Limpa aspas automáticas
                        if k_val.startswith('"') and k_val.endswith('"'):
                            k_val = k_val[1:-1]
                    
                    # Lê em que linha (Y) e coluna (X) o GLPI quer colocar o dado
                    partes = meta_part.split(';')
                    for p in partes:
                        if p.startswith('Y') and p[1:].isdigit():
                            linha_atual = int(p[1:])
                            col_atual = 1 # Toda vez que desce uma linha, volta pro início
                        elif p.startswith('X') and p[1:].isdigit():
                            col_atual = int(p[1:])
                    
                    # Salva na nossa "matriz" virtual
                    if linha_texto.startswith('C;') and k_val is not None:
                        if linha_atual not in dados_slk:
                            dados_slk[linha_atual] = {}
                        dados_slk[linha_atual][col_atual] = k_val
                        # O Excel original avança 1 casa pra direita após preencher
                        col_atual += 1

            # Transforma a matriz virtual num DataFrame do Pandas arrumadinho
            df_bruto = pd.DataFrame.from_dict(dados_slk, orient='index').sort_index(axis=0).sort_index(axis=1)
            tabela = df_bruto.iloc[1:].copy()
            tabela.columns = df_bruto.iloc[0].values
        else:
            tabela = pd.read_csv(io.BytesIO(content), sep=';', encoding='latin-1', on_bad_lines='skip')

        # 2. LIMPEZA E FORMATAÇÃO (O Cordeiro Lavador)
        print("Limpando caracteres zuados e tags HTML...")
        tabela.columns = [limpar_e_consertar_texto(col) for col in tabela.columns]
        colunas_de_texto = tabela.select_dtypes(include=['object', 'string', 'str']).columns
        for col in colunas_de_texto:
            tabela[col] = tabela[col].apply(limpar_e_consertar_texto)

        # 3. EXPORTAÇÃO LIMPA
        print("Gerando arquivo formatado...")
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            tabela.to_excel(writer, index=False, sheet_name='Dados Limpos')
        
        output.seek(0)

        # Retorna na hora para o HTML forçar o Download
        return Response(
            content=output.getvalue(),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=GLPI_Formatado.xlsx"}
        )

    except Exception as e:
        print(f"Erro no processamento: {e}")
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    print("Servidor rodando em http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)