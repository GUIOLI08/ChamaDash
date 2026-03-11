import os
import sys
import pandas as pd
import win32com.client as win32
import tkinter as tk
from tkinter import filedialog, messagebox

def obter_pasta_atual():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

def consertar_texto(texto):
    if isinstance(texto, str):
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

def processar_arquivo():
    caminho_entrada = filedialog.askopenfilename(
        title="Selecione o arquivo",
        filetypes=[("Arquivos suportados", "*.slk *.csv *.xlsx"), ("Todos os arquivos", "*.*")]
    )
    
    if not caminho_entrada:
        return 

    caminho_entrada = os.path.normpath(caminho_entrada)
    
    extensao = os.path.splitext(caminho_entrada)[1].lower()
    tabela = None
    pasta_destino = obter_pasta_atual()
    caminho_saida = os.path.join(pasta_destino, 'dashboard_dados_formatados.xlsx')

    try:
        if extensao == '.slk':
            excel = win32.Dispatch('Excel.Application')
            excel.Visible = False
            
            caminho_temp = caminho_entrada.replace('.slk', '_temp.xlsx')
            
            wb = excel.Workbooks.Open(caminho_entrada)
            wb.SaveAs(caminho_temp, FileFormat=51)
            wb.Close()
            excel.Quit()
            
            tabela = pd.read_excel(caminho_temp)
            os.remove(caminho_temp)

        elif extensao == '.csv':
            tabela = pd.read_csv(caminho_entrada, sep=';', encoding='utf-8')

        elif extensao == '.xlsx':
            tabela = pd.read_excel(caminho_entrada)

        else:
            messagebox.showwarning("Formato Inválido", f"O formato {extensao} não é suportado!")
            return
        
        if tabela is not None:
            tabela.columns = [consertar_texto(col) for col in tabela.columns]
            tabela = tabela.map(consertar_texto)

            colunas_de_data = [
                'Data de abertura', 'Última atualização', 'Tempo para solução', 
                'Data da solução', 'Aprovação - Data da validação'
            ]
            for col in colunas_de_data:
                if col in tabela.columns:
                    tabela[col] = pd.to_datetime(tabela[col], dayfirst=True, errors='coerce')

            with pd.ExcelWriter(caminho_saida, engine='openpyxl') as writer:
                tabela.to_excel(writer, index=False, sheet_name='Dados GLPI')
                planilha = writer.sheets['Dados GLPI']
                
                for coluna in planilha.columns:
                    tamanho_maximo = 0
                    letra_coluna = coluna[0].column_letter
                    for celula in coluna:
                        try:
                            if len(str(celula.value)) > tamanho_maximo:
                                tamanho_maximo = len(str(celula.value))
                        except:
                            pass
                    planilha.column_dimensions[letra_coluna].width = tamanho_maximo + 2

            messagebox.showinfo("Sucesso!", f"Arquivo formatado com sucesso!\nSalvo em:\n{caminho_saida}")

    except Exception as e:
        messagebox.showerror("Erro Oculto", f"Ops, deu um erro no processamento:\n{e}")

janela = tk.Tk()
janela.title("Formatador de Arquivos")
janela.geometry("400x200")
janela.eval('tk::PlaceWindow . center')

label_instrucao = tk.Label(janela, text="Bem-vindo ao Formatador de arquivos do GLPI.\n\nClique no botão abaixo para escolher o arquivo\n(.slk, .csv ou .xlsx)", pady=20)
label_instrucao.pack()

botao_selecionar = tk.Button(janela, text="Selecionar Arquivo", command=processar_arquivo, bg="#146EF5", fg="white", font=("Arial", 12, "bold"), padx=10, pady=5)
botao_selecionar.pack()

janela.mainloop()