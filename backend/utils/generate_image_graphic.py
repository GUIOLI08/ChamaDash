from typing import Dict, Any, Union
import matplotlib
import matplotlib.pyplot as plt
import io

# Configura o matplotlib para usar o backend 'Agg' (sem interface gráfica)
matplotlib.use('Agg')

def generate_image_graphic(dados: Dict[str, Union[int, float]], titulo: str, tipo: str = "bar") -> io.BytesIO:
    """
    Gera uma imagem de gráfico (Pizza ou Barra) a partir dos dados fornecidos.

    As proporções são ajustadas para garantir consistência visual no relatório Word.

    Args:
        dados (Dict[str, Union[int, float]]): Dicionário com as categorias (chaves) e valores (quantidades).
        titulo (str): O título que será exibido no topo do gráfico.
        tipo (str, opcional): O tipo de gráfico: "bar" (barra horizontal) ou "pie" (pizza). O padrão é "bar".

    Returns:
        io.BytesIO: Um buffer de memória contendo a imagem PNG gerada.
    """
    buf = io.BytesIO()
    
    # Encurta chaves muito longas para não quebrar o layout
    chaves = [str(k)[:25] + ('...' if len(str(k)) > 25 else '') for k in dados.keys()]
    valores = list(dados.values())
    
    # Paleta de cores personalizada
    cores = ["#4F81BD", "#C0504D", "#9BBB59", "#11B23E", "#9E1FF3", "#E91E63", "#00BCD4", "#795548", "#FF9800", "#607D8B"]
    
    if tipo == "pie":
        fig = plt.figure(figsize=(3.5, 3.0)) 
        wedges, texts, autotexts = plt.pie(
            valores, autopct='%1.0f%%', startangle=90, colors=cores, 
            textprops=dict(color="w", weight="bold", fontname='Verdana', size=7)
        )
        plt.legend(
            wedges, chaves, loc="lower center", bbox_to_anchor=(0.5, -0.15), 
            ncol=1, prop={'family': 'Verdana', 'size': 7}
        )
        plt.title(titulo, pad=15, fontweight='bold', fontsize=9, fontname='Verdana')
        
        # Ajusta margens para caber a legenda
        plt.subplots_adjust(left=0.1, right=0.9, top=0.85, bottom=0.25)
        
        plt.savefig(buf, format='png', dpi=120) 
        
    elif tipo == "bar":
        plt.figure(figsize=(6, 3.2)) 
        # Inverte para que o maior valor fique no topo ou siga a ordem natural
        plt.barh(chaves[::-1], valores[::-1], color='#5B9BD5', height=0.6)
        plt.title(titulo, pad=10, fontweight='bold', fontsize=8, fontname='Verdana')
        plt.yticks(fontsize=7, fontname='Verdana')
        plt.xticks(fontsize=7, fontname='Verdana')
        plt.tight_layout()
        plt.savefig(buf, format='png', dpi=120, bbox_inches='tight')
        
    buf.seek(0)
    plt.close() # Libera a memória da figura
    return buf